#!/usr/bin/env python3
"""
Local Media Validator
Validates that local media files match vocabulary.json references
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from utils.logging_config import get_logger, ICONS

logger = get_logger('validation.local_media')

def load_vocabulary() -> dict:
    """Load vocabulary.json"""
    vocab_path = Path(__file__).parent.parent.parent / 'vocabulary.json'
    try:
        with open(vocab_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"{ICONS['cross']} Failed to load vocabulary.json: {e}")
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

def validate_local_vs_vocabulary() -> bool:
    """Validate local media files vs vocabulary.json references"""
    print("🔍 LOCAL MEDIA ↔ VOCABULARY.JSON VALIDATOR")
    print("=" * 48)
    
    # Load data
    vocab_data = load_vocabulary()
    local_images, local_audio = get_local_media_files()
    vocab_images, vocab_audio = get_vocabulary_media_references(vocab_data)
    
    print(f"📊 SUMMARY:")
    print(f"   Local media:      {len(local_images)} images, {len(local_audio)} audio")
    print(f"   Vocabulary refs:  {len(vocab_images)} images, {len(vocab_audio)} audio")
    print()
    
    print("🔍 Validating local media vs vocabulary.json references...\n")
    
    differences_found = False
    
    # Check images
    missing_local_images = vocab_images - local_images
    unused_local_images = local_images - vocab_images
    
    if missing_local_images:
        differences_found = True
        print("❌ IMAGES REFERENCED BUT MISSING LOCALLY:")
        for image in sorted(missing_local_images):
            print(f"   • {image}")
        print()
    
    if unused_local_images:
        differences_found = True
        print("⚠️  IMAGES EXIST LOCALLY BUT NOT REFERENCED:")
        for image in sorted(unused_local_images):
            print(f"   • {image}")
        print()
    
    # Check audio
    missing_local_audio = vocab_audio - local_audio
    unused_local_audio = local_audio - vocab_audio
    
    if missing_local_audio:
        differences_found = True
        print("❌ AUDIO REFERENCED BUT MISSING LOCALLY:")
        for audio in sorted(missing_local_audio):
            print(f"   • {audio}")
        print()
    
    if unused_local_audio:
        differences_found = True
        print("⚠️  AUDIO EXIST LOCALLY BUT NOT REFERENCED:")
        for audio in sorted(unused_local_audio):
            print(f"   • {audio}")
        print()
    
    # Final verdict
    if not differences_found:
        print("✅ VALIDATION PASSED")
        print("   Local media and vocabulary.json references are perfectly synchronized!")
        return True
    else:
        print("❌ VALIDATION FAILED")
        print("   Differences found between local media and vocabulary.json references")
        return False