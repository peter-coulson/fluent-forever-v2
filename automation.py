#!/usr/bin/env python3
"""
Fluent Forever V2 - Automation System
Simple, clear automation for Spanish vocabulary learning with personal imagery
"""

import json
import os
import sys
import requests
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Load configuration
def load_config() -> dict:
    """Load configuration from config.json"""
    config_path = Path(__file__).parent / 'config.json'
    with open(config_path, 'r') as f:
        return json.load(f)

# Load vocabulary database
def load_vocabulary() -> dict:
    """Load vocabulary database, create if doesn't exist"""
    vocab_path = Path(__file__).parent / 'vocabulary.json'
    if vocab_path.exists():
        with open(vocab_path, 'r') as f:
            return json.load(f)
    else:
        # Create new database structure
        return {
            "metadata": {
                "created": datetime.now().strftime("%Y-%m-%d"),
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "total_words": 0,
                "total_cards": 0
            },
            "words": []
        }

# Save vocabulary database
def save_vocabulary(vocab: dict) -> None:
    """Save vocabulary database with timestamp"""
    vocab['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d")
    vocab_path = Path(__file__).parent / 'vocabulary.json'
    with open(vocab_path, 'w', encoding='utf-8') as f:
        json.dump(vocab, f, indent=2, ensure_ascii=False)
    print("✅ Vocabulary database saved")

# Test Automatic1111 connection
def test_automatic1111(config: dict) -> bool:
    """Test if Automatic1111 WebUI is running"""
    try:
        url = f"{config['apis']['automatic1111']['url']}/sdapi/v1/options"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print("✅ Automatic1111 WebUI connected")
            return True
    except:
        pass
    print("❌ Automatic1111 WebUI not available - please start it first")
    return False

# Generate image from prompt
def generate_image(prompt: str, base_word: str, meaning_id: str, config: dict) -> Optional[str]:
    """
    Generate image using Automatic1111 API
    Returns path to saved image or None if failed
    """
    if not config['apis']['automatic1111']['enabled']:
        print("⚠️  Image generation disabled in config")
        return None
    
    # Build full prompt with style
    full_prompt = f"{prompt}, {config['image_generation']['style_prompt']}"
    
    # API payload
    payload = {
        "prompt": full_prompt,
        "negative_prompt": config['image_generation']['negative_prompt'],
        "steps": config['image_generation']['steps'],
        "cfg_scale": config['image_generation']['cfg_scale'],
        "width": config['image_generation']['width'],
        "height": config['image_generation']['height'],
        "sampler_name": config['image_generation']['sampler']
    }
    
    try:
        # Send generation request
        url = f"{config['apis']['automatic1111']['url']}/sdapi/v1/txt2img"
        response = requests.post(url, json=payload, timeout=config['apis']['automatic1111']['timeout'])
        
        if response.status_code == 200:
            # Save generated image
            result = response.json()
            image_data = result['images'][0]
            
            # Create media directory if needed
            media_dir = Path(__file__).parent / config['paths']['media_folder'] / 'images'
            media_dir.mkdir(parents=True, exist_ok=True)
            
            # Save image file
            filename = f"{base_word}_{meaning_id}.png"
            filepath = media_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(base64.b64decode(image_data))
            
            print(f"✅ Generated image: {filename}")
            return str(filepath)
        else:
            print(f"❌ Image generation failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Image generation error: {e}")
        return None

# Download audio from Forvo
def download_audio(word: str, config: dict) -> Optional[str]:
    """
    Download pronunciation from Forvo API
    Returns path to saved audio or None if failed
    """
    if not config['apis']['forvo']['enabled']:
        print("⚠️  Forvo disabled - please add API key to config.json")
        return use_tts_fallback(word, config)
    
    try:
        # Build Forvo API request
        api_key = config['apis']['forvo']['api_key']
        url = f"https://apifree.forvo.com/key/{api_key}/format/json/action/word-pronunciations/word/{word}/language/es"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Filter by preferred accents
            pronunciations = data.get('items', [])
            preferred_accents = config['apis']['forvo']['preferred_accents']
            
            # Sort by preference and rating
            for accent in preferred_accents:
                for item in pronunciations:
                    if accent.lower() in item.get('country', '').lower():
                        # Download the audio file
                        audio_url = item['pathmp3']
                        audio_response = requests.get(audio_url)
                        
                        # Save audio file
                        media_dir = Path(__file__).parent / config['paths']['media_folder'] / 'audio'
                        media_dir.mkdir(parents=True, exist_ok=True)
                        
                        filename = f"{word}.mp3"
                        filepath = media_dir / filename
                        
                        with open(filepath, 'wb') as f:
                            f.write(audio_response.content)
                        
                        print(f"✅ Downloaded audio: {filename} ({item['country']})")
                        return str(filepath)
            
            # If no preferred accent found, use first available
            if pronunciations:
                item = pronunciations[0]
                audio_url = item['pathmp3']
                audio_response = requests.get(audio_url)
                
                media_dir = Path(__file__).parent / config['paths']['media_folder'] / 'audio'
                media_dir.mkdir(parents=True, exist_ok=True)
                
                filename = f"{word}.mp3"
                filepath = media_dir / filename
                
                with open(filepath, 'wb') as f:
                    f.write(audio_response.content)
                
                print(f"✅ Downloaded audio: {filename} (fallback)")
                return str(filepath)
        
        print(f"⚠️  No Forvo pronunciation found for '{word}'")
        return use_tts_fallback(word, config)
        
    except Exception as e:
        print(f"❌ Forvo error: {e}")
        return use_tts_fallback(word, config)

# TTS fallback for audio
def use_tts_fallback(word: str, config: dict) -> Optional[str]:
    """
    Generate audio using TTS as fallback
    For now, returns None - implement ElevenLabs later
    """
    print(f"⚠️  TTS fallback not yet implemented for '{word}'")
    return None

# Process word with meanings
def process_word(word_data: dict, config: dict) -> bool:
    """
    Process a word entry with all its meanings
    Generates images and downloads audio
    """
    base_word = word_data['base_word']
    print(f"\n🚀 Processing: {base_word}")
    
    # Download audio once (shared across all meanings)
    audio_path = download_audio(base_word, config)
    if audio_path:
        word_data['audio_file'] = audio_path
    
    # Generate images for each meaning
    for meaning in word_data['meanings']:
        if 'prompt' in meaning and meaning['prompt']:
            image_path = generate_image(
                meaning['prompt'],
                base_word,
                meaning['id'],
                config
            )
            if image_path:
                meaning['image_file'] = image_path
        else:
            print(f"⚠️  No prompt provided for meaning: {meaning['id']}")
    
    return True

# Show system status
def show_status():
    """Display current system status"""
    print("\n" + "="*60)
    print("🎯 Fluent Forever V2 - System Status")
    print("="*60)
    
    config = load_config()
    vocab = load_vocabulary()
    
    # Check connections
    print("\n📡 Connections:")
    if test_automatic1111(config):
        print("  ✅ Automatic1111 WebUI: Connected")
    else:
        print("  ❌ Automatic1111 WebUI: Not running")
    
    if config['apis']['forvo']['enabled']:
        print("  ✅ Forvo API: Configured")
    else:
        print("  ⚠️  Forvo API: No API key")
    
    # Show statistics
    print(f"\n📊 Statistics:")
    print(f"  • Total words: {vocab['metadata']['total_words']}")
    print(f"  • Total cards: {vocab['metadata']['total_cards']}")
    print(f"  • Last updated: {vocab['metadata']['last_updated']}")
    
    # Check word queue
    queue_path = Path(__file__).parent / 'word_queue.txt'
    if queue_path.exists():
        with open(queue_path, 'r') as f:
            lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith('#')]
            print(f"\n📝 Word queue: {len(lines)} words pending")
            if lines:
                print(f"  • Next word: {lines[0]}")
    
    print("\n" + "="*60)

# Main entry point
if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            show_status()
        elif command == "test":
            config = load_config()
            test_automatic1111(config)
        else:
            print(f"Unknown command: {command}")
            print("Available commands: status, test")
    else:
        show_status()
