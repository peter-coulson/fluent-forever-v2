#!/usr/bin/env python3
"""
Generate como batch with user-provided prompts
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

config = load_config()

# Como batch data
como_batch = {
    "word": "como",
    "meanings": [
        {
            "id": "comparison",
            "context": "comparison/similarity", 
            "definition": "expressing similarity or comparison like/as",
            "user_prompt": "A guy with brown skin and dark hair running across a footbridge in japan doing the naruto run.",
            "sentence_attachment": "Like naruto"
        },
        {
            "id": "manner",
            "context": "manner/way",
            "definition": "indicating how something is done", 
            "user_prompt": "At a pool party, a guy with light brown hair flipping into a pool with everyone watching.",
            "sentence_attachment": "How did you do that?"
        },
        {
            "id": "interrogative",
            "context": "interrogative how",
            "definition": "asking about manner or condition",
            "user_prompt": "A woman of 60 with dark hair upset whilst a bald guy with small rounded glasses tries to comfort her.",
            "sentence_attachment": ""
        },
        {
            "id": "since",
            "context": "since/given that", 
            "definition": "expressing cause or reason",
            "user_prompt": "It's getting dark and dangerous, a bald guy with small round glasses is running home.",
            "sentence_attachment": "It's getting dark so I need to go home"
        }
    ]
}

def check_anki_connect():
    """Check if AnkiConnect is available"""
    try:
        response = requests.post(config["apis"]["anki"]["url"], json={
            "action": "version",
            "version": 6
        }, timeout=5)
        if response.status_code == 200:
            print("✅ AnkiConnect is running")
            return True
    except:
        print("❌ AnkiConnect not available - make sure Anki is open")
        return False

def generate_image(prompt, filename):
    """Generate image using OpenAI DALL-E"""
    api_key = os.getenv(config["apis"]["openai"]["env_var"])
    if not api_key:
        print(f"❌ Missing {config['apis']['openai']['env_var']}")
        return False
    
    full_prompt = f"{prompt}, {config['image_generation']['style']}"
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": config["apis"]["openai"]["model"],
                "prompt": full_prompt,
                "size": f"{config['image_generation']['width']}x{config['image_generation']['height']}",
                "quality": "standard",
                "n": 1
            },
            timeout=60
        )
        
        if response.status_code == 200:
            image_url = response.json()["data"][0]["url"]
            
            # Download image
            img_response = requests.get(image_url)
            if img_response.status_code == 200:
                os.makedirs("media/images", exist_ok=True)
                with open(f"media/images/{filename}", "wb") as f:
                    f.write(img_response.content)
                print(f"  ✅ Image generated: {filename}")
                return True
        else:
            print(f"  ❌ Image generation failed: {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Image generation error: {e}")
        return False

def get_audio(word, filename):
    """Get audio from Forvo"""
    api_key = os.getenv(config["apis"]["forvo"]["env_var"])
    if not api_key:
        print(f"❌ Missing {config['apis']['forvo']['env_var']}")
        return False
    
    try:
        # Try to get pronunciation from preferred countries
        for country in ["CO", "MX", "PE", "VE", "AR"]:
            url = f"https://apifree.forvo.com/key/{api_key}/format/json/action/word-pronunciations/word/{word}/country/{country}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("items"):
                    # Get the first pronunciation
                    pronunciation = data["items"][0]
                    audio_url = pronunciation["pathmp3"]
                    
                    # Download audio
                    audio_response = requests.get(audio_url)
                    if audio_response.status_code == 200:
                        os.makedirs("media/audio", exist_ok=True)
                        with open(f"media/audio/{filename}", "wb") as f:
                            f.write(audio_response.content)
                        print(f"  ✅ Audio downloaded: {filename} ({country})")
                        return True
        
        print(f"  ⚠️ No audio found for {word}")
        return False
    except Exception as e:
        print(f"  ❌ Audio error: {e}")
        return False

def create_sentence(word, meaning, prompt, attachment):
    """Generate contextual sentence for the meaning"""
    sentences = {
        "comparison": f"Corre como Naruto por el puente" if attachment == "Like naruto" else f"Corre como un ninja",
        "manner": f"¿Cómo hiciste eso?" if attachment == "How did you do that?" else f"¿Cómo lo haces?",
        "interrogative": f"¿Cómo te sientes?",
        "since": f"Como está oscuro, corro a casa" if attachment == "It's getting dark so I need to go home" else f"Como llueve, me quedo"
    }
    
    sentence = sentences.get(meaning["id"], f"Como ejemplo de {word}")
    gapped = sentence.replace("como", "_____").replace("Como", "_____")
    
    return sentence, gapped

def create_anki_card(word, meaning, sentence, gapped_sentence, image_file, audio_file):
    """Create Anki card"""
    try:
        response = requests.post(config["apis"]["anki"]["url"], json={
            "action": "addNote",
            "version": 6,
            "params": {
                "note": {
                    "deckName": config["apis"]["anki"]["deck_name"],
                    "modelName": config["apis"]["anki"]["note_type"],
                    "fields": {
                        "SpanishWord": word,
                        "IPA": "/ˈkomo/",
                        "MeaningContext": meaning["context"],
                        "MonolingualDef": meaning["definition"],
                        "ExampleSentence": sentence,
                        "GappedSentence": gapped_sentence,
                        "ImageFile": f"<img src='{image_file}'>",
                        "WordAudio": f"[sound:{audio_file}]"
                    },
                    "tags": ["claude-generated", "fluent-forever", word]
                }
            }
        }, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("error"):
                print(f"  ❌ Anki error: {result['error']}")
                return False
            else:
                print(f"  ✅ Card created successfully")
                return True
        else:
            print(f"  ❌ Anki request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Card creation error: {e}")
        return False

def update_vocabulary_db(word, meanings):
    """Update vocabulary.json"""
    try:
        # Load existing vocabulary
        vocab_path = "vocabulary.json"
        if os.path.exists(vocab_path):
            with open(vocab_path, 'r') as f:
                vocab_data = json.load(f)
        else:
            vocab_data = {"metadata": {}, "words": {}}
        
        # Add word data
        vocab_data["words"][word] = {
            "word": word,
            "processed_date": "2025-08-13T15:40:00.000000",
            "meanings": meanings,
            "cards_created": len(meanings)
        }
        
        # Update metadata
        vocab_data["metadata"]["last_updated"] = "2025-08-13T15:40:00.000000"
        vocab_data["metadata"]["total_words"] = len(vocab_data["words"])
        vocab_data["metadata"]["total_cards"] = sum(w.get("cards_created", 0) for w in vocab_data["words"].values())
        
        # Save
        with open(vocab_path, 'w') as f:
            json.dump(vocab_data, f, indent=2)
        
        print("📝 Vocabulary database updated")
        return True
    except Exception as e:
        print(f"❌ Vocabulary update error: {e}")
        return False

def update_word_queue(word):
    """Move word from pending to completed in word_queue.txt"""
    try:
        with open("word_queue.txt", 'r') as f:
            lines = f.readlines()
        
        # Remove word from pending section
        new_lines = []
        in_pending = False
        in_completed = False
        
        for line in lines:
            if "## PENDING WORDS" in line:
                in_pending = True
                in_completed = False
            elif "## SKIPPED WORDS" in line or "## COMPLETED WORDS" in line:
                in_pending = False
                if "## COMPLETED WORDS" in line:
                    in_completed = True
            
            if in_pending and line.strip() == word:
                continue  # Skip this line (remove from pending)
            
            new_lines.append(line)
            
            # Add to completed section
            if in_completed and line.startswith("# Format:"):
                new_lines.append(f"{word} - comparison/manner/interrogative/since (4 cards) - 2025-08-13\n")
        
        with open("word_queue.txt", 'w') as f:
            f.writelines(new_lines)
        
        print("📝 Word queue updated")
        return True
    except Exception as e:
        print(f"❌ Word queue update error: {e}")
        return False

def main():
    print("🚀 Generating como batch")
    
    # Check AnkiConnect
    print("🔧 Checking AnkiConnect setup...")
    if not check_anki_connect():
        sys.exit(1)
    
    word = como_batch["word"]
    meanings = como_batch["meanings"]
    
    # Process each meaning
    vocab_meanings = []
    cards_created = 0
    
    for meaning in meanings:
        print(f"Processing {word} ({meaning['id']})")
        
        # Generate media files
        image_file = f"{word}_{meaning['id']}.png"
        audio_file = f"{word}.mp3"
        
        # Skip if files exist (API cost protection)
        image_path = f"media/images/{image_file}"
        audio_path = f"media/audio/{audio_file}"
        
        if not os.path.exists(image_path):
            if not generate_image(meaning["user_prompt"], image_file):
                print(f"  ⚠️ Continuing without image")
        else:
            print(f"  ✅ Image exists: {image_file}")
        
        if not os.path.exists(audio_path):
            if not get_audio(word, audio_file):
                print(f"  ⚠️ Continuing without audio")
        else:
            print(f"  ✅ Audio exists: {audio_file}")
        
        # Generate sentences
        sentence, gapped = create_sentence(word, meaning, meaning["user_prompt"], meaning["sentence_attachment"])
        
        # Create Anki card
        if create_anki_card(word, meaning, sentence, gapped, image_file, audio_file):
            cards_created += 1
        
        # Add to vocabulary data
        vocab_meanings.append({
            "id": meaning["id"],
            "context": meaning["context"],
            "definition": meaning["definition"],
            "example": sentence,
            "image_file": image_file,
            "audio_file": audio_file
        })
    
    # Update databases
    print("📊 Updating vocabulary database...")
    update_vocabulary_db(word, vocab_meanings)
    
    print("📝 Updating word queue...")
    update_word_queue(word)
    
    print(f"✅ Batch complete! Created {cards_created} cards")

if __name__ == "__main__":
    main()