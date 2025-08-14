#!/usr/bin/env python3
"""
Internal Media Validator
Validates that local media files match vocabulary.json references
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from utils.logging_config import get_logger, ICONS
from validation.media_sync_result import MediaSyncResult

logger = get_logger('validation.internal.media')

def load_vocabulary() -> dict:
    """Load vocabulary.json"""
    vocab_path = Path(__file__).parent.parent.parent.parent / 'vocabulary.json'
    try:
        with open(vocab_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"{ICONS['cross']} Failed to load vocabulary.json: {e}")
        raise

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

def get_vocabulary_media_references(vocab_data: dict) -> Tuple[Set[str], Set[str]]:
    """Extract media file references from vocabulary.json"""
    vocab_images = set()
    vocab_audio = set()
    
    for word_data in vocab_data.get('words', {}).values():
        for meaning in word_data.get('meanings', []):
            # Extract image file reference
            image_file = meaning.get('ImageFile', '')
            if image_file:
                vocab_images.add(image_file)
            
            # Extract audio file reference
            audio_field = meaning.get('WordAudio', '')
            if audio_field and audio_field.startswith('[sound:') and audio_field.endswith(']'):
                # Extract filename from [sound:filename.mp3]
                audio_file = audio_field[7:-1]  # Remove [sound: and ]
                vocab_audio.add(audio_file)
    
    return vocab_images, vocab_audio

def validate_local_vs_vocabulary() -> MediaSyncResult:
    """Validate local media files vs vocabulary.json references"""
    logger.info(f"{ICONS['search']} Validating local media vs vocabulary.json references...")
    
    # Load data
    vocab_data = load_vocabulary()
    local_images, local_audio = get_local_media_files()
    vocab_images, vocab_audio = get_vocabulary_media_references(vocab_data)
    
    logger.info(f"{ICONS['chart']} Local media: {len(local_images)} images, {len(local_audio)} audio")
    logger.info(f"{ICONS['chart']} Vocabulary refs: {len(vocab_images)} images, {len(vocab_audio)} audio")
    
    # Check for missing files (vocabulary references but not local)
    missing_images = list(vocab_images - local_images)
    missing_audio = list(vocab_audio - local_audio)
    
    # Log unused files (local but not referenced) as warnings
    unused_images = local_images - vocab_images  
    unused_audio = local_audio - vocab_audio
    
    if unused_images:
        logger.warning(f"{ICONS['warning']} Unused local images: {sorted(unused_images)}")
    
    if unused_audio:
        logger.warning(f"{ICONS['warning']} Unused local audio: {sorted(unused_audio)}")
    
    return MediaSyncResult(
        missing_images=missing_images,
        missing_audio=missing_audio
    )