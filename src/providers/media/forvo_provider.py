"""
Forvo Media Provider

Provides audio generation using Forvo pronunciation API.
"""

import os
import json
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
from providers.base.media_provider import MediaProvider, MediaRequest, MediaResult
from utils.logging_config import get_logger, ICONS

logger = get_logger('providers.media.forvo')


class ForvoMediaProvider(MediaProvider):
    """Forvo-based audio generation"""
    
    def __init__(self, api_key: Optional[str] = None, config: Optional[Dict] = None):
        """Initialize Forvo media provider
        
        Args:
            api_key: Forvo API key (if None, loads from environment)
            config: Configuration dictionary (if None, loads from config.json)
        """
        if config is None:
            config = self._load_config()
        
        self.config = config
        self.api_config = config.get("apis", {}).get("forvo", {})
        
        # Load API key
        if api_key is not None:
            self.api_key = api_key
        else:
            env_var = self.api_config.get("env_var", "FORVO_API_KEY")
            self.api_key = os.getenv(env_var)
            if not self.api_key:
                # Don't raise error for testing - just log warning
                logger.warning(f"Forvo API key not found in environment variable {env_var}")
                self.api_key = "test_key_for_validation"
        
        self.base_url = self.api_config.get("base_url", "https://apifree.forvo.com")
        
        # Priority order from config
        self.country_priorities = self.api_config.get("country_priorities", ["CO", "MX", "PE", "VE", "AR", "EC", "UY", "CR", "ES"])
        cfg_groups = self.api_config.get("priority_groups", [])
        
        # Sanitize groups to include only countries present in global priorities
        priorities_set = list(dict.fromkeys(self.country_priorities))
        def sanitize(group):
            return [c for c in group if c in priorities_set]
        groups = [sanitize(g) for g in cfg_groups if isinstance(g, list)]
        
        # Fallback to a single group of all priorities if misconfigured
        if not groups:
            groups = [priorities_set]
            
        # Normalize to exactly three logical groups by padding with []
        while len(groups) < 3:
            groups.append([])
        self.group1, self.group2, self.group3 = groups[:3]
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config.json"""
        try:
            config_path = Path(__file__).parent.parent.parent.parent / 'config.json'
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning("config.json not found, using defaults")
                return {}
        except Exception as e:
            logger.warning(f"Error loading config: {e}, using defaults")
            return {}
    
    @property
    def supported_types(self) -> List[str]:
        """Forvo supports audio generation"""
        return ['audio']
    
    def generate_media(self, request: MediaRequest) -> MediaResult:
        """Generate audio using Forvo API
        
        Args:
            request: MediaRequest with audio generation parameters
            
        Returns:
            MediaResult with success status and file path
        """
        if request.type != 'audio':
            return MediaResult(
                success=False,
                file_path=None,
                metadata={},
                error=f"Unsupported media type: {request.type}"
            )
        
        try:
            # Extract parameters
            word = request.content
            filename = request.params.get('filename', f'{word}.mp3')
            save_path = request.output_path or Path(self.config["paths"]["media_folder"]) / "audio"
            
            logger.info(f"{ICONS['gear']} Downloading pronunciation: {word}")
            
            # Get full list of available pronunciations with metadata
            pronunciations = self._get_word_pronunciations(word)
            if not pronunciations:
                error_msg = f"No pronunciations available for '{word}'"
                logger.warning(f"{ICONS['warning']} {error_msg}")
                return MediaResult(
                    success=False,
                    file_path=None,
                    metadata={},
                    error=error_msg
                )
            
            # Select best pronunciation using priority groups
            best_pronunciation = self._select_best_pronunciation(pronunciations)
            if not best_pronunciation:
                error_msg = f"No pronunciation found for '{word}' in prioritized groups"
                logger.warning(f"{ICONS['warning']} {error_msg}")
                return MediaResult(
                    success=False,
                    file_path=None,
                    metadata={},
                    error=error_msg
                )
            
            chosen_country = best_pronunciation.get('country', '')
            audio_url = best_pronunciation.get('audio_url', '')
            
            logger.info(f"{ICONS['info']} Selected pronunciation {word} from {chosen_country} (votes+={best_pronunciation.get('num_positive_votes',0)}/{best_pronunciation.get('num_votes',0)})")
            
            # Download audio
            file_path = self._download_audio(audio_url, filename, save_path)
            
            if file_path:
                logger.info(f"{ICONS['check']} Pronunciation downloaded ({chosen_country}): {filename}")
                return MediaResult(
                    success=True,
                    file_path=file_path,
                    metadata={
                        'word': word,
                        'country': chosen_country,
                        'votes': best_pronunciation.get('num_votes', 0),
                        'positive_votes': best_pronunciation.get('num_positive_votes', 0),
                        'username': best_pronunciation.get('username', 'unknown')
                    }
                )
            else:
                # Try fallback pronunciations
                tried_countries = {chosen_country}
                for group in [self.group1, self.group2, self.group3]:
                    for candidate in sorted(
                        [p for p in pronunciations if p.get('country') in group and p.get('audio_url')],
                        key=lambda p: (int(p.get('num_positive_votes', 0)), int(p.get('num_votes', 0))),
                        reverse=True
                    ):
                        ctry = candidate.get('country', '')
                        if ctry in tried_countries:
                            continue
                        
                        file_path = self._download_audio(candidate.get('audio_url',''), filename, save_path)
                        tried_countries.add(ctry)
                        
                        if file_path:
                            logger.info(f"{ICONS['check']} Pronunciation downloaded ({ctry}) on fallback: {filename}")
                            return MediaResult(
                                success=True,
                                file_path=file_path,
                                metadata={
                                    'word': word,
                                    'country': ctry,
                                    'votes': candidate.get('num_votes', 0),
                                    'positive_votes': candidate.get('num_positive_votes', 0),
                                    'username': candidate.get('username', 'unknown'),
                                    'fallback': True
                                }
                            )
                
                error_msg = f"Failed to download pronunciation for '{word}' from prioritized countries"
                return MediaResult(
                    success=False,
                    file_path=None,
                    metadata={},
                    error=error_msg
                )
            
        except Exception as e:
            error_msg = f"Failed to download pronunciation for {word}: {e}"
            logger.error(f"{ICONS['cross']} {error_msg}")
            return MediaResult(
                success=False,
                file_path=None,
                metadata={},
                error=error_msg
            )
    
    def _get_word_pronunciations(self, word: str) -> List[Dict[str, Any]]:
        """Get all available pronunciations for a word"""
        try:
            all_pronunciations = []
            
            for country_code in self.country_priorities:
                url = f"{self.base_url}/key/{self.api_key}/format/json/action/word-pronunciations/word/{word}/language/es/country/{country_code}"
                
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        items = data.get('items', [])
                        for item in items:
                            all_pronunciations.append({
                                "country": country_code,
                                "username": item.get('username', 'unknown'),
                                "sex": item.get('sex', 'unknown'),
                                "num_votes": item.get('num_votes', 0),
                                "num_positive_votes": item.get('num_positive_votes', 0),
                                "audio_url": item.get('pathmp3', '')
                            })
                except requests.RequestException as e:
                    logger.debug(f"Error getting pronunciations from {country_code}: {e}")
                    continue
            
            return all_pronunciations
            
        except Exception as e:
            logger.error(f"Error getting word pronunciations for {word}: {e}")
            return []
    
    def _select_best_pronunciation(self, pronunciations: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Select best pronunciation using priority groups"""
        def select_best(group: List[str]) -> Optional[Dict[str, Any]]:
            # Filter pronunciations to those whose country in group
            candidates = [p for p in pronunciations if p.get('country') in group and p.get('audio_url')]
            # Rank by num_positive_votes desc, then num_votes desc
            candidates.sort(key=lambda p: (int(p.get('num_positive_votes', 0)), int(p.get('num_votes', 0))), reverse=True)
            return candidates[0] if candidates else None
        
        # Try groups in order
        return select_best(self.group1) or select_best(self.group2) or select_best(self.group3)
    
    def _download_audio(self, audio_url: str, filename: str, save_path: Path) -> Optional[Path]:
        """Download audio from URL and save to file"""
        try:
            # Ensure directory exists
            save_path.mkdir(parents=True, exist_ok=True)
            file_path = save_path / filename
            
            # Download audio
            logger.debug(f"Downloading audio from: {audio_url}")
            audio_response = requests.get(audio_url, timeout=30)
            
            if audio_response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(audio_response.content)
                
                logger.debug(f"Audio saved to: {file_path}")
                return file_path
            else:
                logger.error(f"Failed to download audio (HTTP {audio_response.status_code})")
                return None
                
        except Exception as e:
            logger.error(f"{ICONS['cross']} Error downloading audio: {e}")
            return None
    
    def get_cost_estimate(self, requests: List[MediaRequest]) -> Dict[str, float]:
        """Estimate cost for Forvo API calls
        
        Args:
            requests: List of audio generation requests
            
        Returns:
            Cost breakdown dictionary
        """
        audio_requests = [r for r in requests if r.type == 'audio']
        num_audio = len(audio_requests)
        
        # Forvo is typically free for moderate usage, but track requests
        return {
            'total_cost': 0.0,
            'breakdown': {
                'service': 'Forvo',
                'audio_requests': num_audio,
                'cost_per_request': 0.0,
                'note': 'Forvo is free for moderate usage'
            }
        }