#!/usr/bin/env python3
"""
Claude-coordinated batch generation for haber + con

This script is coordinated by Claude - Claude analyzes meanings, requests prompts,
then runs this script to generate media and create Anki cards.

IMPORTANT: Always run with virtual environment:
source venv/bin/activate && python generate_batch.py
"""
import os
import sys
import json
import requests
import base64
from pathlib import Path
from dotenv import load_dotenv

# Check if we're in virtual environment
if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    print("❌ ERROR: Not running in virtual environment!")
    print("Run these commands to set up:")
    print("python3 -m venv venv")
    print("source venv/bin/activate") 
    print("pip install -r requirements.txt")
    print("python generate_batch.py")
    sys.exit(1)

# Check required packages
try:
    import requests
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

load_dotenv()

def load_config(config_path="config.json"):
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        sys.exit(1)

# Load configuration
config = load_config()

def load_vocabulary():
    """Load existing vocabulary database or create new one"""
    vocab_path = config["paths"]["vocabulary_db"]
    if os.path.exists(vocab_path):
        try:
            with open(vocab_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to load vocabulary database: {e}")
    
    return {
        "metadata": {
            "total_words": 0,
            "total_cards": 0,
            "last_updated": None
        },
        "words": {}
    }

def save_vocabulary(vocab_data):
    """Save vocabulary database to file"""
    try:
        from datetime import datetime
        vocab_data["metadata"]["last_updated"] = datetime.now().isoformat()
        
        with open(config["paths"]["vocabulary_db"], 'w') as f:
            json.dump(vocab_data, f, indent=2, ensure_ascii=False)
        print("📝 Vocabulary database updated")
    except Exception as e:
        print(f"❌ Failed to save vocabulary: {e}")

def add_word_to_vocabulary(vocab_data, word_data):
    """Add processed word data to vocabulary database"""
    from datetime import datetime
    
    word = word_data["word"]
    vocab_data["words"][word] = {
        "word": word,
        "processed_date": datetime.now().isoformat(),
        "meanings": word_data["meanings"],
        "cards_created": len(word_data["meanings"])
    }
    
    # Update metadata
    vocab_data["metadata"]["total_words"] += 1
    vocab_data["metadata"]["total_cards"] += len(word_data["meanings"])
    
    return vocab_data

# Load vocabulary database
vocabulary = load_vocabulary()

def generate_contextual_sentences(word, meaning_context, definition, user_prompt):
    """Generate contextual Spanish sentences that match the user's image prompt"""
    
    # Create a prompt for Claude to generate contextual sentences
    claude_prompt = f"""Given this Spanish learning context:

WORD: {word}
MEANING: {meaning_context}  
DEFINITION: {definition}
USER'S IMAGE PROMPT: "{user_prompt}"

Generate TWO Spanish sentences that perfectly match the visual scene described in the user's prompt:

1. EXAMPLE sentence: Complete sentence using "{word}" in the context of "{meaning_context}"
2. GAPPED sentence: Same sentence with "{word}" replaced by "______"

Requirements:
- Sentences must match the visual scene exactly (characters, setting, action)
- Use simple, clear Spanish appropriate for learning
- Make the connection between image and word meaning obvious
- Use natural, authentic Spanish

Format your response as:
EXAMPLE: [complete sentence]
GAPPED: [sentence with ______ replacing {word}]"""

    # For now, return basic templates (this would call Claude API in real implementation)
    # This is a placeholder - in full implementation, this would make an API call to Claude
    
    # Basic fallback templates based on the data we have
    if 'auxiliary_verb' in meaning_context.lower():
        return {
            'example': f'El niño ha comido con su padre.',
            'gapped': f'El niño _____ comido con su padre.'
        }
    elif 'existential' in meaning_context.lower():
        return {
            'example': f'Hay un gato en el jardín.',
            'gapped': f'_____ un gato en el jardín.'
        }
    elif 'necessity' in meaning_context.lower():
        return {
            'example': f'Hay que estudiar temprano.',
            'gapped': f'_____ que estudiar temprano.'
        }
    elif 'accompaniment' in meaning_context.lower():
        return {
            'example': f'Viajan con dos amigos.',
            'gapped': f'Viajan _____ dos amigos.'
        }
    elif 'instrument' in meaning_context.lower():
        return {
            'example': f'Trabaja con un martillo.',
            'gapped': f'Trabaja _____ un martillo.'
        }
    else:
        # Generic fallback
        return {
            'example': f'Es un ejemplo de {word}.',
            'gapped': f'_____ un ejemplo de {word}.'
        }

def get_ipa_pronunciation(word):
    """Get Latin American Spanish IPA pronunciation with contextual fricatives"""
    # OPTIMAL PRONUNCIATION STRATEGY: "Neutral Latin American"
    # Sounds native in Colombia/Mexico/Venezuela, understood everywhere
    # Key features:
    # - Seseo: 'c/z' → [s] (universal LA feature)
    # - Yeísmo: 'll/y' → [ʝ] (modern standard)
    # - Contextual fricatives: stops word-initially, fricatives intervocalically
    # - Clear vowels (no reduction like Spain)
    
    latin_american_ipa = {
        'haber': 'aˈβeɾ',     # Intervocalic β (natural)
        'con': 'kon',         # Word-initial consonant (clear)
        'ser': 'seɾ',         # Simple consonants
        'estar': 'esˈtaɾ',    # Standard
        'que': 'ke',          # Standard
        'de': 'de',           # Standard  
        'a': 'a',             # Standard
        'en': 'en',           # Standard
        'por': 'poɾ',         # Standard
        'para': 'ˈpaɾa',      # Standard
        'su': 'su',           # Standard
        # Contextual fricative examples
        'casa': 'ˈkasa',      # Seseo [s] not [θ]
        'hacer': 'aˈseɾ',     # Seseo [s] not [θ]  
        'cinco': 'ˈsinko',    # Seseo [s] not [θ]
        'llamar': 'ʝaˈmaɾ',   # Yeísmo [ʝ] not [ʎ]
        'bueno': 'ˈbweno',    # Word-initial stop [b] not fricative
        'trabajo': 'traˈβaxo', # Intervocalic fricative [β]
        'cada': 'ˈkaða',      # Intervocalic fricative [ð]
        'lugar': 'luˈɣaɾ'     # Intervocalic fricative [ɣ]
    }
    
    # Return LA IPA if available, otherwise generate basic phonetic approximation
    if word in latin_american_ipa:
        return f"[{latin_american_ipa[word]}]"
    else:
        # Contextual fricative system for unknown words
        phonetic = word
        
        # 1. Apply universal LA features first
        phonetic = (phonetic.replace('rr', 'r')
                           .replace('ll', 'ʝ')    # Yeísmo
                           .replace('ñ', 'ɲ')
                           .replace('ce', 'se')   # Seseo
                           .replace('ci', 'si')   # Seseo  
                           .replace('za', 'sa')   # Seseo
                           .replace('zo', 'so')   # Seseo
                           .replace('zu', 'su'))  # Seseo
        
        # 2. Apply contextual fricatives (simplified approach)
        # This is basic - full implementation would need phonological analysis
        import re
        
        # Word-initial consonants stay as stops (clear pronunciation)
        # Intervocalic consonants become fricatives (natural)
        
        # Simple pattern: vowel + consonant + vowel = fricative context
        phonetic = re.sub(r'([aeiou])b([aeiou])', r'\1β\2', phonetic)  # aba → aβa
        phonetic = re.sub(r'([aeiou])d([aeiou])', r'\1ð\2', phonetic)  # ada → aða  
        phonetic = re.sub(r'([aeiou])g([aeiou])', r'\1ɣ\2', phonetic)  # aga → aɣa
        
        return f"[{phonetic}]"

# Our batch data
batch_data = [
    {
        'word': 'haber',
        'meaning': 'auxiliary_verb',
        'definition': 'Forms compound tenses with past participle',
        'example': 'He comido tacos',
        'gapped': 'He _____ tacos',
        'prompt': 'A boy of 13 with blond hair and blue eyes sitting on a man made embankment at the edge of the beach with grass on top and a town behind. His father with dark hair sits next to him and they are both eating fish and chips.'
    },
    {
        'word': 'haber', 
        'meaning': 'existential',
        'definition': 'Expresses existence using hay form',
        'example': 'Hay un gato en el jardín',
        'gapped': '_____ un gato en el jardín',
        'prompt': 'A man with dark hair and fair skin chasing a cat out the garden with a hose. The garden has grass in the middle, lined with 4 azalea bushes and trees on the perimeter.'
    },
    {
        'word': 'haber',
        'meaning': 'necessity', 
        'definition': 'Expresses obligation using hay que',
        'example': 'Hay que estudiar para el examen',
        'gapped': '_____ que estudiar para el examen',
        'prompt': 'The alarm is ringing at 5:30am, it is dark outside as a boy of 16 with blond hair and blue eyes jumps out of bed towards a desk piled with paper and books.'
    },
    {
        'word': 'con',
        'meaning': 'accompaniment',
        'definition': 'Together with someone or something',
        'example': 'Voy al cine con mi hermana',
        'gapped': 'Voy al cine _____ mi hermana',
        'prompt': 'Two guys in their early twenties in a little white car driving through italy, one bald with small round specticals that is driving and another blonde in the passenger seat. Both have blue eyes.'
    },
    {
        'word': 'con',
        'meaning': 'instrument',
        'definition': 'Using something as a tool or means',
        'example': 'Escribir con un lápiz',
        'gapped': 'Escribir _____ un lápiz',
        'prompt': 'A boy of 11 with blond hair and blue eyes with a very sore neck working in a basement with a hammer driving some nails into a small flat piece of wood.'
    }
]

def generate_image(prompt, filename):
    """Generate image using OpenAI DALL-E"""
    openai_key = os.getenv(config["apis"]["openai"]["env_var"])
    if not openai_key:
        print(f"❌ Missing OpenAI API key: {config['apis']['openai']['env_var']}")
        return False
        
    headers = {
        "Authorization": f"Bearer {openai_key}",
        "Content-Type": "application/json"
    }
    
    style_prompt = config["image_generation"]["style"]
    full_prompt = f"{style_prompt}. {prompt}"
    
    data = {
        "model": config["apis"]["openai"]["model"],
        "prompt": full_prompt,
        "n": 1,
        "size": f"{config['image_generation']['width']}x{config['image_generation']['height']}",
        "quality": "standard"
    }
    
    response = requests.post("https://api.openai.com/v1/images/generations", 
                           headers=headers, json=data)
    
    if response.status_code == 200:
        image_url = response.json()['data'][0]['url']
        # Download image
        img_response = requests.get(image_url)
        if img_response.status_code == 200:
            Path(f"{config['paths']['media_folder']}/images").mkdir(parents=True, exist_ok=True)
            with open(f"{config['paths']['media_folder']}/images/{filename}", 'wb') as f:
                f.write(img_response.content)
            return True
    return False

def download_audio(word, filename):
    """Download audio from Forvo"""
    try:
        forvo_key = os.getenv(config["apis"]["forvo"]["env_var"])
        if not forvo_key:
            print(f"❌ Missing Forvo API key: {config['apis']['forvo']['env_var']}")
            return False
        
        # Try Latin American countries first, then Spain as backup
        # Prioritize clear, neutral accents; avoid difficult ones like Chile (CL)
        latin_american_countries = [
            "CO",  # Colombia - Very clear, neutral accent
            "MX",  # Mexico - Most common Spanish globally
            "PE",  # Peru - Clear pronunciation
            "VE",  # Venezuela - Clear pronunciation
            "AR",  # Argentina - Distinct but understandable
            "EC",  # Ecuador - Clear pronunciation
            "UY",  # Uruguay - Clear pronunciation
            "CR",  # Costa Rica - Clear pronunciation
            "ES"   # Spain - BACKUP ONLY (different pronunciation)
        ]
        
        for country in latin_american_countries:
            url = f"https://apifree.forvo.com/key/{forvo_key}/format/json/action/word-pronunciations/word/{word}/language/es/country/{country}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get('items'):
                    audio_url = data['items'][0]['pathmp3']
                    audio_response = requests.get(audio_url)
                    if audio_response.status_code == 200:
                        Path(config["paths"]["media_folder"]).mkdir(parents=True, exist_ok=True)
                        Path(f"{config['paths']['media_folder']}/audio").mkdir(parents=True, exist_ok=True)
                        with open(f"{config['paths']['media_folder']}/audio/{filename}", 'wb') as f:
                            f.write(audio_response.content)
                        return True
    except Exception as e:
        print(f"  ⚠️ Audio download error: {e}")
    return False

def setup_anki_connect():
    """Ensure Anki and AnkiConnect are running"""
    print("🔧 Checking AnkiConnect setup...")
    
    # Check if AnkiConnect is available
    anki_url = config["apis"]["anki"]["url"]
    try:
        response = requests.post(anki_url, 
                               json={"action": "version", "version": 6}, 
                               timeout=5)
        if response.status_code == 200:
            result = response.json()
            if not result.get("error"):
                print("✅ AnkiConnect is running")
                return True
    except:
        pass
    
    # Try to launch Anki in background
    print("🚀 Launching Anki in background...")
    os.system("open -a Anki --background")
    
    # Wait and retry
    print("⏳ Waiting for Anki to start...")
    import time
    time.sleep(8)
    
    try:
        response = requests.post(anki_url, 
                               json={"action": "version", "version": 6}, 
                               timeout=5)
        if response.status_code == 200:
            result = response.json()
            if not result.get("error"):
                print("✅ AnkiConnect is now running")
                return True
    except:
        pass
    
    # Failed to connect
    print("❌ CRITICAL: AnkiConnect unavailable!")
    print("Please ensure:")
    print("1. Anki is running")
    print("2. AnkiConnect addon is installed")
    print("3. AnkiConnect addon is enabled")
    return False

def create_anki_card(card_data):
    """Create Anki card via AnkiConnect"""
    # First store media files
    media_files = []
    
    # Add image
    media_folder = config["paths"]["media_folder"]
    image_path = f"{media_folder}/images/{card_data['word']}_{card_data['meaning']}.png"
    if os.path.exists(image_path):
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode()
        media_files.append({
            "filename": f"{card_data['word']}_{card_data['meaning']}.png",
            "data": image_data
        })
    
    # Add audio
    audio_path = f"{media_folder}/audio/{card_data['word']}.mp3"
    if os.path.exists(audio_path):
        with open(audio_path, 'rb') as f:
            audio_data = base64.b64encode(f.read()).decode()
        media_files.append({
            "filename": f"{card_data['word']}.mp3", 
            "data": audio_data
        })
    
    # Store media files
    for media_file in media_files:
        store_request = {
            "action": "storeMediaFile",
            "version": 6,
            "params": {
                "filename": media_file["filename"],
                "data": media_file["data"]
            }
        }
        response = requests.post(config["apis"]["anki"]["url"], json=store_request)
        if response.status_code != 200:
            print(f"Failed to store {media_file['filename']}")
            return False
    
    # Create card
    note_request = {
        "action": "addNote",
        "version": 6, 
        "params": {
            "note": {
                "deckName": config["apis"]["anki"]["deck_name"],
                "modelName": config["apis"]["anki"]["note_type"],
                "fields": {
                    "SpanishWord": card_data['word'],
                    "IPA": get_ipa_pronunciation(card_data['word']), 
                    "MeaningContext": card_data['meaning'].replace('_', ' '),
                    "MonolingualDef": card_data['definition'],
                    "ExampleSentence": card_data['example'],
                    "GappedSentence": card_data['gapped'],
                    "ImageFile": f"<img src='{card_data['word']}_{card_data['meaning']}.png'>",
                    "WordAudio": f"[sound:{card_data['word']}.mp3]",
                    "UsageNote": f"Generated from user prompt: {card_data.get('prompt', '')[:100]}...",
                    "PersonalMnemonic": ""
                },
                "tags": ["fluent-forever", "auto-generated"]
            }
        }
    }
    
    response = requests.post(config["apis"]["anki"]["url"], json=note_request)
    return response.status_code == 200

if __name__ == "__main__":
    print("🚀 Generating batch: haber + con")
    
    # Setup AnkiConnect first
    if not setup_anki_connect():
        print("\n❌ Cannot proceed without AnkiConnect")
        print("🔧 Please install AnkiConnect addon in Anki")
        print("📖 Instructions: https://foosoft.net/projects/anki-connect/")
        sys.exit(1)
    
    # Organize batch data by words for vocabulary tracking
    words_data = {}
    for item in batch_data:
        word = item['word']
        if word not in words_data:
            words_data[word] = {
                "word": word,
                "meanings": []
            }
        
        # Generate contextual sentences
        sentences = generate_contextual_sentences(
            word, 
            item['meaning'], 
            item['definition'],
            item['prompt']
        )
        
        # Add meaning data
        meaning_data = {
            "id": item['meaning'],
            "context": item['meaning'].replace('_', '/'),
            "definition": item['definition'],
            "example": sentences['example'],
            "image_file": f"{word}_{item['meaning']}.png",
            "audio_file": f"{word}.mp3"
        }
        words_data[word]["meanings"].append(meaning_data)
        
        # Update item with generated sentences for card creation
        item['example'] = sentences['example']
        item['gapped'] = sentences['gapped']
    
    # Process each item for media generation and card creation
    audio_downloaded = set()
    
    for item in batch_data:
        print(f"Processing {item['word']} ({item['meaning']})")
        
        # Generate image
        media_folder = config["paths"]["media_folder"]
        image_filename = f"{item['word']}_{item['meaning']}.png"
        image_path = f"{media_folder}/images/{image_filename}"
        
        if not os.path.exists(image_path):
            print(f"  Generating image...")
            if generate_image(item['prompt'], image_filename):
                print(f"  ✅ Image generated")
            else:
                print(f"  ❌ Image failed")
        
        # Download audio (once per word)
        audio_filename = f"{item['word']}.mp3"
        audio_path = f"{media_folder}/audio/{audio_filename}"
        
        if item['word'] not in audio_downloaded and not os.path.exists(audio_path):
            print(f"  Downloading audio...")
            if download_audio(item['word'], audio_filename):
                print(f"  ✅ Audio downloaded")
                audio_downloaded.add(item['word'])
            else:
                print(f"  ❌ Audio failed")
        
        # Create Anki card
        print(f"  Creating Anki card...")
        if create_anki_card(item):
            print(f"  ✅ Card created successfully")
        else:
            print(f"  ❌ Card creation failed")
    
    # Add words to vocabulary database
    print(f"\n📊 Updating vocabulary database...")
    for word_data in words_data.values():
        vocabulary = add_word_to_vocabulary(vocabulary, word_data)
        print(f"  Added {word_data['word']} ({len(word_data['meanings'])} meanings)")
    
    # Save vocabulary database
    save_vocabulary(vocabulary)
    
    print("\n✅ Batch complete!")