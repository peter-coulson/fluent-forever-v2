#!/usr/bin/env python3
"""
Anki Media Validator
Validates that Anki media collection matches local media files
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple
from apis.anki_client import AnkiClient
from utils.logging_config import get_logger, ICONS
from validation.media_sync_result import MediaSyncResult

logger = get_logger('validation.anki.media')

# Config loading now handled by BaseAPIClient

def get_local_media_files() -> Tuple[Set[str], Set[str]]:
    """Get sets of local image and audio files"""
    project_root = Path(__file__).parent.parent.parent.parent
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

def get_anki_media_files(anki_client: AnkiClient) -> Tuple[Set[str], Set[str]]:
    """Get sets of Anki media files"""
    try:
        # Get image files from Anki
        image_response = anki_client.get_media_files("*.png")
        anki_images = set(image_response.data) if image_response.success else set()
        
        # Get audio files from Anki
        audio_response = anki_client.get_media_files("*.mp3")
        anki_audio = set(audio_response.data) if audio_response.success else set()
        
        return anki_images, anki_audio
        
    except Exception as e:
        logger.error(f"{ICONS['cross']} Failed to get Anki media files: {e}")
        return set(), set()

def validate_anki_vs_local() -> MediaSyncResult:
    """Validate that all local media files exist in Anki (subset check)"""
    # Connect to Anki (config loaded automatically)
    anki_client = AnkiClient()
    
    if not anki_client.test_connection():
        logger.error(f"{ICONS['cross']} Cannot connect to Anki")
        # Return empty result if can't connect
        return MediaSyncResult(missing_images=[], missing_audio=[])
    
    # Get media files from both locations
    local_images, local_audio = get_local_media_files()
    anki_images, anki_audio = get_anki_media_files(anki_client)
    
    # Check if all local images exist in Anki (subset check)
    missing_images = list(local_images - anki_images)
    
    # Check if all local audio exists in Anki (subset check)  
    missing_audio = list(local_audio - anki_audio)
    
    return MediaSyncResult(
        missing_images=missing_images,
        missing_audio=missing_audio
    )