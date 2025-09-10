#!/usr/bin/env python3
"""
Base API Client for Providers
Provides shared utilities and patterns for all external API integrations
Migrated from src/apis/base_client.py to new provider structure
"""

import json
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

from src.utils.logging_config import ICONS, get_logger

logger = get_logger("providers.base")


@dataclass
class APIResponse:
    """Standard response format for all API calls"""

    success: bool
    data: Any = None
    error_message: str = ""
    status_code: int | None = None
    retry_after: int | None = None


class APIError(Exception):
    """Custom exception for API-related errors"""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        retry_after: int | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.retry_after = retry_after


class BaseAPIClient(ABC):
    """Abstract base class for all API clients in providers"""

    _shared_config = None  # Class-level shared config

    @classmethod
    def load_config(cls, config_path: Path | None = None) -> dict[str, Any]:
        """Load configuration once and share across all clients"""
        if cls._shared_config is None:
            if config_path is None:
                # Updated path for new structure - look for config in project root
                config_path = Path(__file__).parents[3] / "config.json"

            try:
                with open(config_path, encoding="utf-8") as f:
                    cls._shared_config = json.load(f)
                logger.debug(f"Loaded shared config from {config_path}")
            except Exception as e:
                logger.warning(
                    f"{ICONS['warning']} Config file not found at {config_path}, using empty config: {e}"
                )
                cls._shared_config = {}

        return cls._shared_config or {}

    def __init__(self, service_name: str):
        self.config = self.load_config()
        self.service_name = service_name
        self.logger = get_logger(f"providers.{service_name.lower()}")
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self) -> None:
        """Configure the requests session with common settings"""
        # Handle both old and new config structure during migration
        if "apis" in self.config and "base" in self.config["apis"]:
            base_config = self.config["apis"]["base"]
        elif "providers" in self.config and "base" in self.config["providers"]:
            base_config = self.config["providers"]["base"]
        else:
            # Default fallback config
            base_config = {"user_agent": "FluentForever/2.0", "timeout": 30}

        self.session.headers.update(
            {
                "User-Agent": base_config.get("user_agent", "FluentForever/2.0"),
                "Accept": "application/json",
            }
        )
        # Store timeout for use in requests
        self.timeout = base_config.get("timeout", 30)

    def _load_api_key(self, env_var: str) -> str:
        """Load API key from environment variable"""
        api_key = os.getenv(env_var)
        if not api_key:
            # For tests and development, provide a more graceful fallback
            logger.warning(
                f"{ICONS['warning']} API key not found: {env_var} environment variable not set, using placeholder for testing"
            )
            return f"test_key_{env_var.lower()}"
        return api_key

    def _make_request(
        self, method: str, url: str, max_retries: int | None = None, **kwargs: Any
    ) -> APIResponse:
        """
        Make HTTP request with retry logic and error handling

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            max_retries: Maximum number of retry attempts (defaults to config value)
            **kwargs: Additional arguments passed to requests

        Returns:
            APIResponse object with success status and data/error info
        """
        if max_retries is None:
            # Handle config structure differences during migration
            if "apis" in self.config and "base" in self.config["apis"]:
                max_retries = self.config["apis"]["base"].get("max_retries", 3)
            elif "providers" in self.config and "base" in self.config["providers"]:
                max_retries = self.config["providers"]["base"].get("max_retries", 3)
            else:
                max_retries = 3

        last_exception = None

        for attempt in range(max_retries):
            try:
                self.logger.debug(
                    f"Making {method} request to {url} (attempt {attempt + 1}/{max_retries})"
                )

                response = self.session.request(
                    method, url, timeout=self.timeout, **kwargs
                )

                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    self.logger.warning(
                        f"{ICONS['warning']} Rate limited by {self.service_name}. Waiting {retry_after}s..."
                    )

                    if attempt < max_retries - 1:  # Don't wait on last attempt
                        time.sleep(retry_after)
                        continue

                    return APIResponse(
                        success=False,
                        error_message=f"Rate limited by {self.service_name}",
                        status_code=429,
                        retry_after=retry_after,
                    )

                # Handle successful responses
                if response.status_code < 400:
                    try:
                        data = response.json() if response.content else None
                        self.logger.debug(f"{ICONS['check']} Request successful")
                        return APIResponse(
                            success=True, data=data, status_code=response.status_code
                        )
                    except json.JSONDecodeError:
                        # Return raw content for non-JSON responses
                        return APIResponse(
                            success=True,
                            data=response.content,
                            status_code=response.status_code,
                        )

                # Handle client/server errors
                error_msg = (
                    f"{self.service_name} API error (HTTP {response.status_code})"
                )
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg += f": {error_data['error']}"
                    elif "message" in error_data:
                        error_msg += f": {error_data['message']}"
                except Exception:
                    error_msg += f": {response.text[:200]}"

                # Don't retry on 4xx client errors (except rate limiting)
                if 400 <= response.status_code < 500:
                    return APIResponse(
                        success=False,
                        error_message=error_msg,
                        status_code=response.status_code,
                    )

                # Retry on 5xx server errors
                self.logger.warning(
                    f"{ICONS['warning']} Server error (HTTP {response.status_code}), retrying..."
                )
                last_exception = APIError(error_msg, response.status_code)

            except requests.exceptions.Timeout:
                error_msg = f"Timeout connecting to {self.service_name}"
                self.logger.warning(f"{ICONS['warning']} {error_msg}, retrying...")
                last_exception = APIError(error_msg)

            except requests.exceptions.ConnectionError:
                error_msg = f"Connection error to {self.service_name}"
                self.logger.warning(f"{ICONS['warning']} {error_msg}, retrying...")
                last_exception = APIError(error_msg)

            except Exception as e:
                error_msg = f"Unexpected error calling {self.service_name}: {e}"
                self.logger.error(f"{ICONS['cross']} {error_msg}")
                return APIResponse(success=False, error_message=error_msg)

            # Wait before retry with exponential backoff
            if attempt < max_retries - 1:
                wait_time = 2**attempt  # 1s, 2s, 4s, etc.
                self.logger.debug(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)

        # All retries exhausted
        final_error = (
            f"Failed to connect to {self.service_name} after {max_retries} attempts"
        )
        if last_exception:
            final_error += f": {last_exception}"

        self.logger.error(f"{ICONS['cross']} {final_error}")
        return APIResponse(success=False, error_message=final_error)

    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the API service is available and authentication works"""
        pass

    @abstractmethod
    def get_service_info(self) -> dict[str, Any]:
        """Get information about the API service (version, limits, etc.)"""
        pass


# Utility functions for provider system
def ensure_media_directories(config: dict[str, Any]) -> None:
    """Ensure media directories exist"""
    # Handle both old and new config structure
    if "paths" in config:
        media_folder = Path(config["paths"].get("media_folder", "media"))
    else:
        media_folder = Path("media")

    directories = [media_folder, media_folder / "images", media_folder / "audio"]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {directory}")


def validate_file_extension(filepath: Path, allowed_extensions: list[str]) -> bool:
    """Validate file has allowed extension"""
    return filepath.suffix.lower() in [ext.lower() for ext in allowed_extensions]
