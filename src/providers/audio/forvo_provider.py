#!/usr/bin/env python3
"""
Clean Forvo Media Provider
Handles pronunciation audio downloads with config injection and no fallback logic
"""

from pathlib import Path
from typing import Any, cast

import requests

from src.providers.base.media_provider import MediaProvider, MediaRequest, MediaResult
from src.utils.logging_config import ICONS, get_logger

logger = get_logger("providers.media.forvo")


class APIError(Exception):
    """API error for Forvo provider"""

    pass


class ForvoProvider(MediaProvider):
    """Clean Forvo media provider for Spanish pronunciation audio"""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize provider with config injection"""
        super().__init__(config)

    @property
    def supported_types(self) -> list[str]:
        """Media types supported by Forvo provider"""
        return ["audio"]

    def validate_config(self, config: dict[str, Any]) -> None:
        """Validate Forvo provider configuration with fail-fast pattern"""
        # Check for required api_key
        if "api_key" not in config or not config["api_key"]:
            raise ValueError("Missing required Forvo config key: api_key")

        # Check for required country_priorities
        if "country_priorities" not in config:
            raise ValueError("Missing required Forvo config key: country_priorities")

        # Validate country_priorities is not empty
        if not config["country_priorities"] or len(config["country_priorities"]) == 0:
            raise ValueError("country_priorities cannot be empty")

    def _setup_from_config(self) -> None:
        """Setup provider from validated configuration"""
        self.api_key = self.config["api_key"]
        self.country_priorities = self.config["country_priorities"]
        self.base_url = self.config.get("base_url", "https://apifree.forvo.com")

        # Set up priority groups from config
        priority_groups = self.config.get("priority_groups", [])
        priorities_set = list(dict.fromkeys(self.country_priorities))

        def sanitize_group(group: list[str]) -> list[str]:
            return [c for c in group if c in priorities_set]

        if priority_groups:
            groups = [sanitize_group(g) for g in priority_groups if isinstance(g, list)]
        else:
            # Default grouping: split country_priorities into 3 groups
            third = len(priorities_set) // 3
            groups = [
                priorities_set[:third] if third > 0 else [],
                priorities_set[third : third * 2] if third > 0 else [],
                priorities_set[third * 2 :] if third > 0 else priorities_set,
            ]

        # Ensure we have 3 groups
        while len(groups) < 3:
            groups.append([])

        self.group1, self.group2, self.group3 = groups[:3]

        # Rate limiting configuration
        self._rate_limit_delay = self.config.get(
            "rate_limit_delay", 0.5
        )  # Default 0.5s for Forvo

    def _make_request(self, method: str, url: str, **kwargs: Any) -> Any:
        """Make HTTP request with basic error handling"""
        try:
            response = requests.request(method, url, timeout=30, **kwargs)
            response.raise_for_status()

            # Return a simple object with success and data
            result = type("APIResponse", (), {})()
            result.success = True
            result.data = response.json() if response.content else {}
            return result
        except Exception as e:
            result = type("APIResponse", (), {})()
            result.success = False
            result.data = {}
            result.error = str(e)
            return result

    def test_connection(self) -> bool:
        """Test Forvo API connection"""
        try:
            # Test with a simple word lookup
            response = self._make_request(
                "GET",
                f"{self.base_url}/key/{self.api_key}/format/json/action/word-pronunciations/word/hola/language/es/country/MX",
            )
            return response.success  # type: ignore[no-any-return]
        except Exception as e:
            logger.error(f"{ICONS['cross']} Forvo connection test failed: {e}")
            return False

    def get_service_info(self) -> dict[str, Any]:
        """Get Forvo API service information"""
        return {
            "service": "Forvo",
            "type": "audio_provider",
            "supported_languages": ["es"],
            "supported_countries": self.country_priorities,
        }

    def _generate_media_impl(self, request: MediaRequest) -> MediaResult:
        """
        Generate audio media using Forvo API

        Args:
            request: MediaRequest with type='audio', content=word, params with language/country

        Returns:
            MediaResult with success status and file path or error
        """
        if request.type != "audio":
            return MediaResult(
                success=False,
                file_path=None,
                metadata={},
                error=f"Unsupported media type: {request.type}. Forvo only supports 'audio'.",
            )

        word = request.content.strip()
        if not word:
            return MediaResult(
                success=False,
                file_path=None,
                metadata={},
                error="Empty word provided for audio generation",
            )

        language = request.params.get("language", "es")
        preferred_country = request.params.get("country")

        try:
            # Get pronunciations for the word
            pronunciations = self._get_pronunciations(word, language, preferred_country)

            if not pronunciations:
                return MediaResult(
                    success=False,
                    file_path=None,
                    metadata={"word": word, "language": language},
                    error=f"No pronunciations found for word: {word}",
                )

            # Select best pronunciation based on country priorities
            best_pronunciation = self._select_best_pronunciation(pronunciations)

            # Download the audio file
            file_path = self._download_audio(
                word, best_pronunciation, request.output_path
            )

            metadata = {
                "word": word,
                "language": language,
                "country": best_pronunciation.get("country"),
                "username": best_pronunciation.get("username"),
                "votes": best_pronunciation.get("votes", 0),
            }

            return MediaResult(success=True, file_path=file_path, metadata=metadata)

        except Exception as e:
            logger.error(f"{ICONS['cross']} Error generating audio for '{word}': {e}")
            return MediaResult(
                success=False,
                file_path=None,
                metadata={"word": word, "language": language},
                error=str(e),
            )

    def estimate_cost(self, request: MediaRequest) -> float:
        """Estimate cost for Forvo request (free API has rate limits)"""
        # Forvo free API - no direct cost but rate limited
        return 0.0

    def get_cost_estimate(self, requests: list[MediaRequest]) -> dict[str, float]:
        """Get cost estimate for batch of requests"""
        total_cost = sum(
            self.estimate_cost(req)
            for req in requests
            if req.type in self.supported_types
        )
        return {
            "total_cost": total_cost,
            "per_request": 0.0,  # Free API
            "requests_count": len(
                [req for req in requests if req.type in self.supported_types]
            ),
        }

    def _get_pronunciations(
        self, word: str, language: str = "es", preferred_country: str | None = None
    ) -> list[dict[str, Any]]:
        """Get pronunciations for a word"""
        # Try specific country first if provided
        if preferred_country:
            response = self._make_request(
                "GET",
                f"{self.base_url}/key/{self.api_key}/format/json/action/word-pronunciations/word/{word}/language/{language}/country/{preferred_country}",
            )
            if response.success and response.data.get("items"):
                return cast("list[dict[str, Any]]", response.data["items"])

        # Try without country filter to get all pronunciations
        response = self._make_request(
            "GET",
            f"{self.base_url}/key/{self.api_key}/format/json/action/word-pronunciations/word/{word}/language/{language}",
        )

        if response.success and response.data.get("items"):
            return cast("list[dict[str, Any]]", response.data["items"])

        return []

    def _select_best_pronunciation(
        self, pronunciations: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Select best pronunciation based on country priorities and votes"""
        # Group by priority levels
        group1_pronunciations = [
            p for p in pronunciations if p.get("country") in self.group1
        ]
        group2_pronunciations = [
            p for p in pronunciations if p.get("country") in self.group2
        ]
        group3_pronunciations = [
            p for p in pronunciations if p.get("country") in self.group3
        ]
        other_pronunciations = [
            p
            for p in pronunciations
            if p.get("country") not in (self.group1 + self.group2 + self.group3)
        ]

        # Try each group in priority order
        for group in [
            group1_pronunciations,
            group2_pronunciations,
            group3_pronunciations,
            other_pronunciations,
        ]:
            if group:
                # Sort by votes (descending) and return the best
                group.sort(key=lambda x: x.get("votes", 0), reverse=True)
                return group[0]

        # Fallback to first pronunciation if no matches
        return pronunciations[0] if pronunciations else {}

    def _download_audio(
        self, word: str, pronunciation: dict[str, Any], output_path: Path | None = None
    ) -> Path:
        """Download audio file for pronunciation"""
        audio_url = pronunciation.get("pathmp3")
        if not audio_url:
            raise APIError(f"No audio URL found for pronunciation of '{word}'")

        # Determine output path
        if output_path is None:
            # Create safe filename
            safe_word = "".join(c for c in word if c.isalnum() or c in "._-").strip()
            country = pronunciation.get("country", "unknown")
            output_path = Path(f"media/audio/{safe_word}_{country}.mp3")

        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Download the file
        logger.debug(f"Downloading audio from {audio_url}")
        response = requests.get(audio_url, stream=True, timeout=30)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.debug(f"{ICONS['check']} Audio downloaded to {output_path}")
        return output_path
