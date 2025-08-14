#!/usr/bin/env python3
"""
Forvo API Client
Handles pronunciation audio downloads for Spanish vocabulary
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import requests
from apis.base_client import BaseAPIClient, APIResponse, APIError
from utils.logging_config import get_logger, ICONS

logger = get_logger('apis.forvo')

class ForvoClient(BaseAPIClient):
    """Forvo API client for Spanish pronunciation audio"""
    
    def __init__(self):
        super().__init__("Forvo")
        self.api_config = self.config["apis"]["forvo"]
        self.api_key = self._load_api_key(self.api_config["env_var"])
        self.base_url = self.api_config["base_url"]
        
        # Priority order from config
        self.country_priorities = self.api_config["country_priorities"]
        # Grouped prioritization now comes from config['priority_groups']
        cfg_groups = self.api_config.get("priority_groups", [])
        # Sanitize groups to include only countries present in global priorities (preserve order)
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
        
    def test_connection(self) -> bool:
        """Test Forvo API connection"""
        try:
            # Test with a simple word lookup
            response = self._make_request(
                "GET",
                f"{self.base_url}/key/{self.api_key}/format/json/action/word-pronunciations/word/hola/language/es/country/MX"
            )
            
            if response.success:
                self.logger.info(f"{ICONS['check']} Forvo API connection successful")
                return True
            else:
                self.logger.error(f"{ICONS['cross']} Forvo API connection failed: {response.error_message}")
                return False
        except Exception as e:
            self.logger.error(f"{ICONS['cross']} Forvo API test failed: {e}")
            return False
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get Forvo service information"""
        return {
            "service": "Forvo Pronunciation Dictionary",
            "language": "Spanish (es)",
            "priority_countries": self.country_priorities[:3],  # Top 3
            "total_countries": len(self.country_priorities)
        }
    
    def download_pronunciation(self, word: str, filename: str, save_path: Optional[Path] = None) -> APIResponse:
        """
        Download pronunciation audio for a Spanish word
        
        Args:
            word: Spanish word to get pronunciation for
            filename: Name for saved audio file
            save_path: Optional custom path to save audio (defaults to config media folder)
            
        Returns:
            APIResponse with success status and saved file path
        """
        try:
            self.logger.info(f"{ICONS['gear']} Downloading pronunciation: {word}")

            # Get full list of available pronunciations with metadata
            info = self.get_word_info(word)
            if not info.success or not info.data or not info.data.get('pronunciations'):
                error_msg = f"No pronunciations available for '{word}'"
                self.logger.warning(f"{ICONS['warning']} {error_msg}")
                return APIResponse(success=False, error_message=error_msg)

            pronunciations = info.data['pronunciations']

            def select_best(group: list[str]):
                # Filter pronunciations to those whose country in group
                cand = [p for p in pronunciations if p.get('country') in group and p.get('audio_url')]
                # Rank by num_positive_votes desc, then num_votes desc
                cand.sort(key=lambda p: (int(p.get('num_positive_votes', 0)), int(p.get('num_votes', 0))), reverse=True)
                return cand[0] if cand else None

            # Try groups in order
            best = select_best(self.group1) or select_best(self.group2) or select_best(self.group3)
            if not best:
                error_msg = f"No pronunciation found for '{word}' in prioritized groups"
                self.logger.warning(f"{ICONS['warning']} {error_msg}")
                return APIResponse(success=False, error_message=error_msg)

            chosen_country = best.get('country', '')
            audio_url = best.get('audio_url', '')
            self.logger.info(f"{ICONS['info']} Selected pronunciation {word} from {chosen_country} (votes+={best.get('num_positive_votes',0)}/{best.get('num_votes',0)})")

            download_response = self._download_audio(audio_url, filename, save_path, chosen_country)
            if download_response.success:
                self.logger.info(f"{ICONS['check']} Pronunciation downloaded ({chosen_country}): {filename}")
                return download_response
            else:
                self.logger.debug(f"Download failed for {chosen_country}: {download_response.error_message}")
                # Fall back to next groups if possible (simple retry across groups other than the chosen one)
                tried_countries = {chosen_country}
                for group in [self.group1, self.group2, self.group3]:
                    for cand in sorted([p for p in pronunciations if p.get('country') in group and p.get('audio_url')],
                                        key=lambda p: (int(p.get('num_positive_votes', 0)), int(p.get('num_votes', 0))), reverse=True):
                        ctry = cand.get('country', '')
                        if ctry in tried_countries:
                            continue
                        resp = self._download_audio(cand.get('audio_url',''), filename, save_path, ctry)
                        tried_countries.add(ctry)
                        if resp.success:
                            self.logger.info(f"{ICONS['check']} Pronunciation downloaded ({ctry}) on fallback: {filename}")
                            return resp
                error_msg = f"Failed to download pronunciation for '{word}' from prioritized countries"
                return APIResponse(success=False, error_message=error_msg)
            
        except Exception as e:
            error_msg = f"Failed to download pronunciation for {word}: {e}"
            self.logger.error(f"{ICONS['cross']} {error_msg}")
            return APIResponse(success=False, error_message=error_msg)
    
    def _get_pronunciation_url(self, word: str, country_code: str) -> Optional[str]:
        """Get pronunciation URL for word from specific country"""
        try:
            url = f"{self.base_url}/key/{self.api_key}/format/json/action/word-pronunciations/word/{word}/language/es/country/{country_code}"
            
            response = self._make_request("GET", url)
            
            if response.success and response.data:
                items = response.data.get('items', [])
                if items and len(items) > 0:
                    # Get the first (usually best rated) pronunciation
                    return items[0].get('pathmp3')
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Error getting pronunciation URL for {word} ({country_code}): {e}")
            return None
    
    def _download_audio(self, audio_url: str, filename: str, save_path: Optional[Path] = None, country_code: str = "") -> APIResponse:
        """Download audio from URL and save to file"""
        try:
            # Determine save path
            if save_path is None:
                media_folder = Path(self.config["paths"]["media_folder"])
                save_path = media_folder / "audio" / filename
            else:
                save_path = save_path / filename
                
            # Ensure directory exists
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download audio
            self.logger.debug(f"Downloading audio from: {audio_url}")
            audio_response = requests.get(audio_url, timeout=30)
            
            if audio_response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(audio_response.content)
                
                self.logger.debug(f"Audio saved to: {save_path}")
                return APIResponse(
                    success=True, 
                    data={
                        "file_path": str(save_path),
                        "country_code": country_code,
                        "file_size": len(audio_response.content)
                    }
                )
            else:
                error_msg = f"Failed to download audio (HTTP {audio_response.status_code})"
                return APIResponse(success=False, error_message=error_msg, status_code=audio_response.status_code)
                
        except Exception as e:
            error_msg = f"Error downloading audio: {e}"
            self.logger.error(f"{ICONS['cross']} {error_msg}")
            return APIResponse(success=False, error_message=error_msg)
    
    def get_word_info(self, word: str) -> APIResponse:
        """
        Get detailed information about word pronunciations available
        
        Args:
            word: Spanish word to query
            
        Returns:
            APIResponse with pronunciation info from all countries
        """
        try:
            all_pronunciations = []
            
            for country_code in self.country_priorities:
                url = f"{self.base_url}/key/{self.api_key}/format/json/action/word-pronunciations/word/{word}/language/es/country/{country_code}"
                
                response = self._make_request("GET", url)
                
                if response.success and response.data:
                    items = response.data.get('items', [])
                    for item in items:
                        all_pronunciations.append({
                            "country": country_code,
                            "username": item.get('username', 'unknown'),
                            "sex": item.get('sex', 'unknown'),
                            "num_votes": item.get('num_votes', 0),
                            "num_positive_votes": item.get('num_positive_votes', 0),
                            "audio_url": item.get('pathmp3', '')
                        })
            
            return APIResponse(
                success=True,
                data={
                    "word": word,
                    "total_pronunciations": len(all_pronunciations),
                    "countries_available": list(set(p["country"] for p in all_pronunciations)),
                    "pronunciations": all_pronunciations
                }
            )
            
        except Exception as e:
            error_msg = f"Failed to get word info for {word}: {e}"
            self.logger.error(f"{ICONS['cross']} {error_msg}")
            return APIResponse(success=False, error_message=error_msg)
    