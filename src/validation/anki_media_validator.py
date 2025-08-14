#!/usr/bin/env python3
"""
Anki Media Validator
Validates that Anki media collection matches local media files
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from anki.connection import AnkiConnection
from utils.logging_config import get_logger, ICONS

logger = get_logger('validation.anki_media')

@dataclass
class MediaSyncResult:
    missing_images: List[str]
    missing_audio: List[str]
    
    def has_missing_files(self) -> bool:
        return len(self.missing_images) > 0 or len(self.missing_audio) > 0
    
    def total_missing(self) -> int:
        return len(self.missing_images) + len(self.missing_audio)

def load_config() -> dict:
    """Load configuration"""
    config_path = Path(__file__).parent.parent.parent / 'config.json'
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"{ICONS['cross']} Failed to load config.json: {e}")
        raise

def get_local_media_files() -> Tuple[Set[str], Set[str]]:
    """Get sets of local image and audio files"""
    project_root = Path(__file__).parent.parent.parent
    images_dir = project_root / 'media' / 'images'
    audio_dir = project_root / 'media' / 'audio'
    
    # Get image files
    local_images = set()
    if images_dir.exists():
        local_images = {f.name for f in images_dir.glob('*.png')}
    
    # Get audio files  
    local_audio = set()
    if audio_dir.exists():
        local_audio = {f.name for f in audio_dir.glob('*.mp3')}
    
    return local_images, local_audio

def get_anki_media_files(anki_conn: AnkiConnection) -> Tuple[Set[str], Set[str]]:
    """Get sets of Anki media files"""
    try:
        # Get image files from Anki
        anki_images = set(anki_conn.request("getMediaFilesNames", {"pattern": "*.png"}))
        
        # Get audio files from Anki
        anki_audio = set(anki_conn.request("getMediaFilesNames", {"pattern": "*.mp3"}))
        
        return anki_images, anki_audio
        
    except Exception as e:
        logger.error(f"{ICONS['cross']} Failed to get Anki media files: {e}")
        return set(), set()

def validate_anki_vs_local() -> MediaSyncResult:
    """Validate that all local media files exist in Anki (subset check)"""
    # Load configuration and connect to Anki
    config = load_config()
    anki_conn = AnkiConnection(config['apis']['anki']['url'])
    
    if not anki_conn.ensure_connection():
        logger.error(f"{ICONS['cross']} Cannot connect to Anki")
        # Return empty result if can't connect
        return MediaSyncResult(missing_images=[], missing_audio=[])
    
    # Get media files from both locations
    local_images, local_audio = get_local_media_files()
    anki_images, anki_audio = get_anki_media_files(anki_conn)
    
    # Check if all local images exist in Anki (subset check)
    missing_images = list(local_images - anki_images)
    
    # Check if all local audio exists in Anki (subset check)  
    missing_audio = list(local_audio - anki_audio)
    
    return MediaSyncResult(
        missing_images=missing_images,
        missing_audio=missing_audio
    )