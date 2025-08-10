#!/usr/bin/env python3
"""
Fluent Forever V2 - Automation System
Simple, clear automation for Spanish vocabulary learning with personal imagery
Supports batch processing and bulletproof Anki integration
"""

import json
import os
import sys
import requests
import base64
import time
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ============= Configuration Functions =============

def load_config() -> dict:
    """Load configuration from config.json"""
    config_path = Path(__file__).parent / 'config.json'
    with open(config_path, 'r') as f:
        return json.load(f)

def load_vocabulary() -> dict:
    """Load vocabulary database, create if doesn't exist"""
    vocab_path = Path(__file__).parent / 'vocabulary.json'
    if vocab_path.exists():
        with open(vocab_path, 'r') as f:
            return json.load(f)
    else:
        return {
            "metadata": {
                "created": datetime.now().strftime("%Y-%m-%d"),
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "total_words": 0,
                "total_cards": 0
            },
            "words": []
        }

def save_vocabulary(vocab: dict) -> None:
    """Save vocabulary database with timestamp"""
    vocab['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d")
    vocab_path = Path(__file__).parent / 'vocabulary.json'
    with open(vocab_path, 'w', encoding='utf-8') as f:
        json.dump(vocab, f, indent=2, ensure_ascii=False)
    print("✅ Vocabulary database saved")

# ============= Anki Integration Functions =============

def test_anki_connection() -> bool:
    """Test if AnkiConnect is available"""
    try:
        result = invoke_anki("version")
        if result and not result.get('error'):
            print("✅ AnkiConnect connected")
            return True
    except:
        pass
    print("❌ AnkiConnect not available - is Anki running?")
    return False

def invoke_anki(action: str, params: dict = None) -> Optional[dict]:
    """Call AnkiConnect API"""
    request_data = {
        "action": action,
        "version": 6,
        "params": params or {}
    }
    
    try:
        json_data = json.dumps(request_data).encode('utf-8')
        request = urllib.request.Request(
            "http://localhost:8765",
            data=json_data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"❌ Anki error: {e}")
        return None

def upload_media_to_anki(filepath: Path, filename: str) -> bool:
    """Upload media file to Anki with validation"""
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        return False
    
    with open(filepath, 'rb') as f:
        data = base64.b64encode(f.read()).decode('utf-8')
    
    result = invoke_anki("storeMediaFile", {
        "filename": filename,
        "data": data
    })
    
    if result and not result.get('error'):
        print(f"✅ Uploaded to Anki: {filename}")
        return True
    else:
        print(f"❌ Failed to upload: {filename}")
        return False

def validate_card_fields(fields: dict) -> dict:
    """Ensure all fields are properly formatted for Anki"""
    required = ['SpanishWord', 'IPA', 'MonolingualDef', 'ExampleSentence']
    
    for field in required:
        if not fields.get(field) or str(fields[field]).strip() == '':
            raise ValueError(f"Required field {field} is empty")
    
    # Ensure audio format
    if fields.get('WordAudio') and not fields['WordAudio'].startswith('[sound:'):
        fields['WordAudio'] = f"[sound:{fields['WordAudio']}]"
    
    if fields.get('WordAudioAlt') and not fields['WordAudioAlt'].startswith('[sound:'):
        fields['WordAudioAlt'] = f"[sound:{fields['WordAudioAlt']}]"
    
    # Ensure image format
    if fields.get('ImageFile') and not fields['ImageFile'].startswith('<img'):
        fields['ImageFile'] = f"<img src='{fields['ImageFile']}'>"
    
    return fields

def create_anki_card(word_data: dict, meaning: dict) -> bool:
    """Create a single Anki card with bulletproof validation"""
    # First upload media files
    if meaning.get('image_file'):
        image_path = Path(meaning['image_file'])
        image_name = image_path.name
        if not upload_media_to_anki(image_path, image_name):
            return False
    
    if word_data.get('audio_file'):
        audio_path = Path(word_data['audio_file'])
        audio_name = audio_path.name
        upload_media_to_anki(audio_path, audio_name)
    
    # Handle alternative audio for gendered words
    if word_data.get('audio_file_alt'):
        audio_alt_path = Path(word_data['audio_file_alt'])
        audio_alt_name = audio_alt_path.name
        upload_media_to_anki(audio_alt_path, audio_alt_name)
    
    # Build and validate fields
    fields = {
        'SpanishWord': word_data['base_word'],
        'IPA': word_data.get('ipa', ''),
        'MeaningContext': meaning.get('context', ''),
        'MonolingualDef': meaning.get('definition', ''),
        'ExampleSentence': meaning.get('example', ''),
        'GappedSentence': meaning.get('gapped', ''),
        'ImageFile': Path(meaning['image_file']).name if meaning.get('image_file') else '',
        'WordAudio': Path(word_data['audio_file']).name if word_data.get('audio_file') else '',
        'WordAudioAlt': Path(word_data['audio_file_alt']).name if word_data.get('audio_file_alt') else '',
        'UsageNote': meaning.get('usage_note', ''),
        'MeaningID': meaning.get('id', '')
    }
    
    try:
        fields = validate_card_fields(fields)
    except ValueError as e:
        print(f"❌ Field validation failed: {e}")
        return False
    
    # Create the note
    note_data = {
        "deckName": "Spanish::Fluent Forever V2",
        "modelName": "Fluent Forever Spanish V2",
        "fields": fields,
        "tags": ["fluent-forever-v2", f"meaning:{meaning.get('id', 'default')}"]
    }
    
    result = invoke_anki("addNote", {"note": note_data})
    
    if result and not result.get('error'):
        print(f"✅ Created card: {word_data['base_word']} ({meaning['id']})")
        return True
    else:
        error = result.get('error') if result else 'Unknown error'
        print(f"❌ Failed to create card: {error}")
        return False

# ============= Media Generation Functions =============

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

def generate_image(prompt: str, base_word: str, meaning_id: str, config: dict) -> Optional[str]:
    """Generate image using Automatic1111 API"""
    if not config['apis']['automatic1111']['enabled']:
        print("⚠️  Image generation disabled in config")
        return None
    
    # Build full prompt with style
    full_prompt = f"{prompt}, {config['image_generation']['style_prompt']}"
    
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
        url = f"{config['apis']['automatic1111']['url']}/sdapi/v1/txt2img"
        response = requests.post(url, json=payload, timeout=config['apis']['automatic1111']['timeout'])
        
        if response.status_code == 200:
            result = response.json()
            image_data = result['images'][0]
            
            # Create media directory
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

def download_audio(word: str, config: dict) -> Optional[str]:
    """Download pronunciation from Forvo API"""
    if not config['apis']['forvo']['enabled']:
        print("⚠️  Forvo disabled - please add API key to config.json")
        return use_tts_fallback(word, config)
    
    try:
        api_key = config['apis']['forvo']['api_key']
        url = f"https://apifree.forvo.com/key/{api_key}/format/json/action/word-pronunciations/word/{word}/language/es"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            pronunciations = data.get('items', [])
            preferred_accents = config['apis']['forvo']['preferred_accents']
            
            # Sort by preference
            for accent in preferred_accents:
                for item in pronunciations:
                    if accent.lower() in item.get('country', '').lower():
                        audio_url = item['pathmp3']
                        audio_response = requests.get(audio_url)
                        
                        media_dir = Path(__file__).parent / config['paths']['media_folder'] / 'audio'
                        media_dir.mkdir(parents=True, exist_ok=True)
                        
                        filename = f"{word}.mp3"
                        filepath = media_dir / filename
                        
                        with open(filepath, 'wb') as f:
                            f.write(audio_response.content)
                        
                        print(f"✅ Downloaded audio: {filename} ({item['country']})")
                        return str(filepath)
            
            # Fallback to first available
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

def use_tts_fallback(word: str, config: dict) -> Optional[str]:
    """Generate audio using TTS as fallback"""
    print(f"⚠️  TTS fallback not yet implemented for '{word}'")
    return None

# ============= Batch Processing Functions =============

def process_batch(batch_data: dict, config: dict) -> dict:
    """Process a batch of words (typically 5)"""
    print(f"\n🚀 Processing batch of {len(batch_data['words'])} words")
    
    results = {
        'images_generated': 0,
        'audio_downloaded': 0,
        'cards_created': 0,
        'errors': []
    }
    
    for word_entry in batch_data['words']:
        base_word = word_entry['base_word']
        
        # Download audio once per word
        audio_path = download_audio(base_word, config)
        if audio_path:
            word_entry['audio_file'] = audio_path
            results['audio_downloaded'] += 1
        
        # Download alternative audio for gendered words
        if word_entry.get('has_feminine_form'):
            fem_audio = download_audio(word_entry['feminine_form'], config)
            if fem_audio:
                word_entry['audio_file_alt'] = fem_audio
        
        # Generate images for each meaning
        for meaning in word_entry.get('meanings', []):
            if meaning.get('prompt'):
                image_path = generate_image(
                    meaning['prompt'],
                    base_word,
                    meaning['id'],
                    config
                )
                if image_path:
                    meaning['image_file'] = image_path
                    results['images_generated'] += 1
                    
                    # Create Anki card
                    if test_anki_connection() and create_anki_card(word_entry, meaning):
                        results['cards_created'] += 1
                    else:
                        results['errors'].append(f"Card failed: {base_word}_{meaning['id']}")
                else:
                    results['errors'].append(f"Image failed: {base_word}_{meaning['id']}")
    
    # Update batch status
    batch_data['status'] = 'completed'
    batch_data['processed_at'] = datetime.now().isoformat()
    batch_data['results'] = results
    
    # Save batch results
    save_batch(batch_data)
    
    # Update vocabulary database
    vocab = load_vocabulary()
    vocab['metadata']['total_words'] += len(batch_data['words'])
    vocab['metadata']['total_cards'] += results['cards_created']
    vocab['words'].extend(batch_data['words'])
    save_vocabulary(vocab)
    
    print(f"\n📊 Batch Results:")
    print(f"  • Images generated: {results['images_generated']}")
    print(f"  • Audio downloaded: {results['audio_downloaded']}")
    print(f"  • Cards created: {results['cards_created']}")
    if results['errors']:
        print(f"  • Errors: {len(results['errors'])}")
        for error in results['errors']:
            print(f"    - {error}")
    
    return batch_data

def load_current_batch() -> Optional[dict]:
    """Load current batch from file"""
    batch_file = Path(__file__).parent / 'current_batch.json'
    if batch_file.exists():
        with open(batch_file, 'r') as f:
            return json.load(f)
    return None

def save_batch(batch_data: dict) -> None:
    """Save batch to file"""
    batch_file = Path(__file__).parent / 'current_batch.json'
    with open(batch_file, 'w', encoding='utf-8') as f:
        json.dump(batch_data, f, indent=2, ensure_ascii=False)
    print("✅ Batch saved")

def create_new_batch(size: int = 5) -> dict:
    """Create new batch from queue"""
    queue_path = Path(__file__).parent / 'word_queue.txt'
    if not queue_path.exists():
        print("❌ No word queue found")
        return None
    
    with open(queue_path, 'r') as f:
        lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith('#')]
    
    if not lines:
        print("✅ Word queue is empty!")
        return None
    
    # Take first N words
    batch_words = lines[:min(size, len(lines))]
    
    batch = {
        'batch_id': datetime.now().strftime("%Y%m%d_%H%M%S"),
        'created_at': datetime.now().isoformat(),
        'status': 'pending',
        'words': [{'base_word': word, 'meanings': []} for word in batch_words]
    }
    
    save_batch(batch)
    print(f"✅ Created batch with {len(batch_words)} words")
    return batch

# ============= Main Functions =============

def show_status():
    """Display current system status"""
    print("\n" + "="*60)
    print("🎯 Fluent Forever V2 - System Status")
    print("="*60)
    
    config = load_config()
    vocab = load_vocabulary()
    
    # Check connections
    print("\n📡 Connections:")
    test_automatic1111(config)
    test_anki_connection()
    
    if config['apis']['forvo']['enabled']:
        print("  ✅ Forvo API: Configured")
    else:
        print("  ⚠️  Forvo API: No API key")
    
    # Show statistics
    print(f"\n📊 Statistics:")
    print(f"  • Total words: {vocab['metadata']['total_words']}")
    print(f"  • Total cards: {vocab['metadata']['total_cards']}")
    print(f"  • Last updated: {vocab['metadata']['last_updated']}")
    
    # Check current batch
    batch = load_current_batch()
    if batch:
        print(f"\n📦 Current batch:")
        print(f"  • Batch ID: {batch['batch_id']}")
        print(f"  • Status: {batch['status']}")
        print(f"  • Words: {', '.join([w['base_word'] for w in batch['words']])}")
    
    # Check word queue
    queue_path = Path(__file__).parent / 'word_queue.txt'
    if queue_path.exists():
        with open(queue_path, 'r') as f:
            lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith('#')]
            print(f"\n📝 Word queue: {len(lines)} words pending")
            if lines and not batch:
                print(f"  • Next words: {', '.join(lines[:5])}")
    
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
            test_anki_connection()
        elif command == "batch":
            # Create or load batch
            batch = load_current_batch()
            if not batch:
                batch = create_new_batch()
            if batch:
                print(f"Batch ready: {batch['batch_id']}")
        elif command == "process":
            # Process current batch
            batch = load_current_batch()
            if batch:
                config = load_config()
                process_batch(batch, config)
            else:
                print("❌ No batch to process. Run 'batch' first.")
        else:
            print(f"Unknown command: {command}")
            print("Available commands: status, test, batch, process")
    else:
        show_status()
