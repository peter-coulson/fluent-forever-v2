#!/usr/bin/env python3
"""
Fluent Forever V2 - End-to-End Spanish Learning Card Generator
Complete pipeline: word_queue.txt → meaning analysis → user prompts → Anki cards
"""

import json
import requests
import time
import os
import base64
from pathlib import Path
from typing import Dict, List, Optional
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FluentForeverAutomation:
    """End-to-end automation for Fluent Forever Spanish learning"""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the automation system"""
        # Load environment variables from .env if present
        load_dotenv()
        self.config = self.load_config(config_path)
        self.media_folder = Path(self.config["paths"]["media_folder"])
        self.media_folder.mkdir(exist_ok=True)
        (self.media_folder / "images").mkdir(exist_ok=True)
        (self.media_folder / "audio").mkdir(exist_ok=True)
        
        # Load databases
        self.vocab_db_path = Path(self.config["paths"]["vocabulary_db"])
        self.vocabulary = self.load_vocabulary()
        
        self.word_queue_path = Path(self.config["paths"]["word_queue"])
        
    def load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
    
    def load_vocabulary(self) -> Dict:
        """Load existing vocabulary database or create new one"""
        if self.vocab_db_path.exists():
            try:
                with open(self.vocab_db_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load vocabulary database: {e}")
        
        return {
            "metadata": {
                "total_words": 0,
                "total_cards": 0,
                "last_updated": None
            },
            "words": {}
        }
    
    def save_vocabulary(self):
        """Save vocabulary database to file"""
        try:
            from datetime import datetime
            self.vocabulary["metadata"]["last_updated"] = datetime.now().isoformat()
            
            with open(self.vocab_db_path, 'w') as f:
                json.dump(self.vocabulary, f, indent=2, ensure_ascii=False)
            logger.info("Vocabulary database saved")
        except Exception as e:
            logger.error(f"Failed to save vocabulary: {e}")
    
    def get_next_words_from_queue(self, max_meanings: int = 5) -> List[str]:
        """Get next words from queue that will create ≤5 meanings total"""
        if not self.word_queue_path.exists():
            logger.error("Word queue file not found")
            return []
        
        with open(self.word_queue_path, 'r') as f:
            lines = f.readlines()
        
        available_words = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                if line not in self.vocabulary.get("words", {}):
                    available_words.append(line)
        
        if not available_words:
            print("🎉 All words in queue have been processed!")
            return []
        
        # For now, return first word (Claude will analyze meanings and decide batch size)
        return available_words[:1]  # Start with one word for meaning analysis
    
    def download_audio_forvo(self, word: str) -> Optional[str]:
        """Download pronunciation from Forvo API"""
        if not self.config["apis"]["forvo"]["enabled"]:
            logger.info("Forvo API disabled")
            return None
        
        # Check if audio already exists to prevent API waste
        audio_filename = f"{word}.mp3"
        audio_path = self.media_folder / "audio" / audio_filename
        
        if audio_path.exists():
            logger.info(f"Audio already exists, skipping download: {audio_filename}")
            return str(audio_path)
            
        try:
            # Prefer environment variable, fallback to config for backwards compatibility
            api_key = os.getenv("FORVO_API_KEY") or self.config["apis"]["forvo"].get("api_key")
            if not api_key:
                logger.error("FORVO_API_KEY not set. Set the environment variable or provide it in config.")
                return None
            url = f"https://apifree.forvo.com/key/{api_key}/format/json/action/word-pronunciations/word/{word}/language/es"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                pronunciations = data.get('items', [])
                
                if not pronunciations:
                    logger.warning(f"No pronunciations found for '{word}'")
                    return None
                
                # Filter by preferred accents
                preferred_accents = self.config["apis"]["forvo"]["preferred_accents"]
                selected_pronunciation = None
                
                for accent in preferred_accents:
                    for item in pronunciations:
                        if accent.lower() in item.get('country', '').lower():
                            selected_pronunciation = item
                            break
                    if selected_pronunciation:
                        break
                
                # Use first available if no preferred accent found
                if not selected_pronunciation:
                    selected_pronunciation = pronunciations[0]
                
                # Download audio file
                audio_url = selected_pronunciation['pathmp3']
                audio_response = requests.get(audio_url)
                
                audio_filename = f"{word}.mp3"
                audio_path = self.media_folder / "audio" / audio_filename
                
                with open(audio_path, 'wb') as f:
                    f.write(audio_response.content)
                
                logger.info(f"Downloaded audio: {audio_filename} ({selected_pronunciation.get('country', 'Unknown')})")
                return str(audio_path)
                
        except Exception as e:
            logger.error(f"Forvo API error for '{word}': {e}")
        
        return None
    
    def generate_image_openai(self, prompt: str, word: str, meaning_id: str) -> Optional[str]:
        """Generate image using OpenAI DALL-E 3"""
        if not self.config["apis"]["openai"]["enabled"]:
            logger.error("OpenAI API disabled")
            return None
        
        # Check if image already exists to prevent API waste
        image_filename = f"{word}_{meaning_id}.png"
        image_path = self.media_folder / "images" / image_filename
        
        if image_path.exists():
            logger.info(f"Image already exists, skipping generation: {image_filename}")
            return str(image_path)
        
        try:
            # Build full prompt with Ghibli style
            full_prompt = f"{prompt}, {self.config['image_generation']['style']}"
            
            # OpenAI API call
            api_key = os.getenv("OPENAI_API_KEY") or self.config["apis"]["openai"].get("api_key")
            if not api_key:
                logger.error("OPENAI_API_KEY not set. Set the environment variable or provide it in config.")
                return None

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.config["apis"]["openai"]["model"],
                "prompt": full_prompt,
                "n": 1,
                "size": f"{self.config['image_generation']['width']}x{self.config['image_generation']['height']}"
            }
            
            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers=headers,
                json=payload,
                timeout=self.config["apis"]["openai"]["timeout"]
            )
            
            if response.status_code == 200:
                result = response.json()
                image_url = result["data"][0]["url"]
                
                # Download the image
                image_response = requests.get(image_url)
                
                with open(image_path, 'wb') as f:
                    f.write(image_response.content)
                
                logger.info(f"Generated image: {image_filename}")
                return str(image_path)
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Image generation error: {e}")
        
        return None
    
    def validate_anki_setup(self) -> bool:
        """Validate AnkiConnect connection and V4 note type"""
        try:
            # Test connection
            response = requests.post(self.config["apis"]["anki"]["url"], json={
                "action": "version",
                "version": 6
            })
            if response.status_code != 200:
                logger.error("AnkiConnect not responding")
                return False
            
            # Verify V4 note type exists
            response = requests.post(self.config["apis"]["anki"]["url"], json={
                "action": "modelNames", 
                "version": 6
            })
            if response.status_code == 200:
                note_types = response.json()["result"]
                if self.config["apis"]["anki"]["note_type"] not in note_types:
                    logger.error(f"Note type '{self.config['apis']['anki']['note_type']}' not found")
                    logger.info(f"Available note types: {note_types}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"AnkiConnect validation error: {e}")
            return False
    
    def create_anki_card(self, card_data: Dict) -> bool:
        """Create Anki card using AnkiConnect API with V4 format"""
        if not self.config["apis"]["anki"]["url"]:
            logger.error("AnkiConnect not configured")
            return False
        
        # Validate setup before creating cards
        if not self.validate_anki_setup():
            logger.error("Anki setup validation failed")
            return False
        
        try:
            # Prepare media files for Anki
            media_files = []
            
            # Add image to Anki media
            if card_data.get("image_path"):
                image_filename = Path(card_data["image_path"]).name
                with open(card_data["image_path"], "rb") as f:
                    image_data = base64.b64encode(f.read()).decode()
                
                media_files.append({
                    "filename": image_filename,
                    "data": image_data
                })
                card_data["image_field"] = f"<img src='{image_filename}'>"
            
            # Add audio to Anki media
            if card_data.get("audio_path"):
                audio_filename = Path(card_data["audio_path"]).name
                with open(card_data["audio_path"], "rb") as f:
                    audio_data = base64.b64encode(f.read()).decode()
                
                media_files.append({
                    "filename": audio_filename,
                    "data": audio_data
                })
                card_data["audio_field"] = f"[sound:{audio_filename}]"
            
            # Store media files first with enhanced error checking
            for media_file in media_files:
                store_request = {
                    "action": "storeMediaFile",
                    "version": 6,
                    "params": {
                        "filename": media_file["filename"],
                        "data": media_file["data"]
                    }
                }
                
                response = requests.post(self.config["apis"]["anki"]["url"], json=store_request)
                if response.status_code != 200:
                    logger.error(f"HTTP error storing media file {media_file['filename']}: {response.status_code}")
                    return False
                
                # Check if AnkiConnect returned an error
                result = response.json()
                if result.get("error"):
                    logger.error(f"AnkiConnect error storing {media_file['filename']}: {result['error']}")
                    return False
                
                # Verify file was actually stored
                verify_request = {
                    "action": "getMediaFilesNames",
                    "version": 6,
                    "params": {
                        "pattern": media_file["filename"]
                    }
                }
                verify_response = requests.post(self.config["apis"]["anki"]["url"], json=verify_request)
                if verify_response.status_code == 200:
                    files = verify_response.json().get("result", [])
                    if media_file["filename"] not in files:
                        logger.error(f"Media file {media_file['filename']} not found after storage")
                        return False
                    else:
                        logger.info(f"Successfully stored and verified: {media_file['filename']}")
                else:
                    logger.warning(f"Could not verify storage of {media_file['filename']}")
            
            # Create the note with V4 format
            note_request = {
                "action": "addNote",
                "version": 6,
                "params": {
                    "note": {
                        "deckName": self.config["apis"]["anki"]["deck_name"],
                        "modelName": self.config["apis"]["anki"]["note_type"],
                        "fields": {
                            "CardID": f"{card_data['spanish_word']}_{card_data['meaning_id']}",
                            "SpanishWord": card_data["spanish_word"],
                            "IPA": card_data.get("ipa", ""),
                            "MeaningContext": card_data["meaning_context"],
                            "MonolingualDef": card_data["monolingual_def"],
                            "ExampleSentence": card_data["example_sentence"],
                            "GappedSentence": card_data["gapped_sentence"],
                            "ImageFile": card_data.get("image_field", ""),
                            "WordAudio": card_data.get("audio_field", ""),
                            "WordAudioAlt": "",
                            "UsageNote": card_data.get("usage_note", ""),
                            "PersonalMnemonic": card_data.get("personal_mnemonic", ""),
                            "MeaningID": card_data["meaning_id"]
                        },
                        "tags": ["fluent-forever-v2", "auto-generated"]
                    }
                }
            }
            
            response = requests.post(self.config["apis"]["anki"]["url"], json=note_request)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("error"):
                    # Handle duplicate cards by updating instead of failing
                    if "duplicate" in result["error"].lower():
                        logger.warning(f"Duplicate card detected for {card_data['spanish_word']} ({card_data['meaning_id']}), attempting to update existing card")
                        # Try to find and update the existing card
                        return self.update_existing_card(card_data)
                    else:
                        logger.error(f"AnkiConnect error: {result['error']}")
                        return False
                else:
                    logger.info(f"Created Anki card: {card_data['spanish_word']} ({card_data['meaning_id']})")
                    return True
            else:
                logger.error(f"AnkiConnect request failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Anki card creation error: {e}")
            return False
    
    def update_existing_card(self, card_data: Dict) -> bool:
        """Update existing card with new media and data"""
        try:
            # Find existing notes by CardID field content
            find_request = {
                "action": "findNotes",
                "version": 6,
                "params": {
                    "query": f'CardID:"{card_data["spanish_word"]}_{card_data["meaning_id"]}"'
                }
            }
            
            response = requests.post(self.config["apis"]["anki"]["url"], json=find_request)
            if response.status_code != 200:
                logger.error("Failed to find existing note for update")
                return False
                
            notes = response.json().get("result", [])
            if not notes:
                logger.error("No existing note found to update")
                return False
            
            # Update the first matching note
            note_id = notes[0]
            update_request = {
                "action": "updateNoteFields",
                "version": 6,
                "params": {
                    "note": {
                        "id": note_id,
                        "fields": {
                            "CardID": f"{card_data['spanish_word']}_{card_data['meaning_id']}",
                            "SpanishWord": card_data["spanish_word"],
                            "IPA": card_data.get("ipa", ""),
                            "MeaningContext": card_data["meaning_context"],
                            "MonolingualDef": card_data["monolingual_def"],
                            "ExampleSentence": card_data["example_sentence"],
                            "GappedSentence": card_data["gapped_sentence"],
                            "ImageFile": card_data.get("image_field", ""),
                            "WordAudio": card_data.get("audio_field", ""),
                            "WordAudioAlt": "",
                            "UsageNote": card_data.get("usage_note", ""),
                            "PersonalMnemonic": card_data.get("personal_mnemonic", ""),
                            "MeaningID": card_data["meaning_id"]
                        }
                    }
                }
            }
            
            response = requests.post(self.config["apis"]["anki"]["url"], json=update_request)
            if response.status_code == 200:
                result = response.json()
                if result.get("error"):
                    logger.error(f"Error updating card: {result['error']}")
                    return False
                else:
                    logger.info(f"Updated existing card: {card_data['spanish_word']} ({card_data['meaning_id']})")
                    return True
            else:
                logger.error(f"Failed to update card: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Card update error: {e}")
            return False
    
    def generate_contextual_sentences(self, word: str, meaning_context: str, user_prompt: str) -> Dict[str, str]:
        """Generate example and gapped sentences that match the user's image prompt"""
        # This function creates sentences that align with the visual scene described by the user
        
        # Basic sentence templates based on the word and meaning context
        sentence_templates = {
            'ser': {
                'identity': {
                    'doctor': ('Soy médico en el hospital.', '_____ médico en el hospital.'),
                    'professional': ('Es profesional de la medicina.', '_____ profesional de la medicina.'),
                    'default': ('Soy médico.', '_____ médico.')
                },
                'qualities': {
                    'intelligent': ('Ella es muy inteligente.', 'Ella _____ muy inteligente.'),
                    'strong': ('Él es fuerte y capaz.', 'Él _____ fuerte y capaz.'),
                    'skilled': ('Es una persona muy hábil.', '_____ una persona muy hábil.'),
                    'default': ('Es inteligente.', '_____ inteligente.')
                },
                'time': {
                    'clock': ('Son las tres de la tarde.', '_____ las tres de la tarde.'),
                    'day': ('Hoy es lunes.', 'Hoy _____ lunes.'),
                    'calendar': ('Es el primer día del mes.', '_____ el primer día del mes.'),
                    'default': ('Son las tres.', '_____ las tres.')
                },
                'origin': {
                    'wales': ('Es de Gales.', '_____ de Gales.'),
                    'welsh': ('Es de origen galés.', '_____ de origen galés.'),
                    'map': ('Es de ese país.', '_____ de ese país.'),
                    'flag': ('Es de la región galesa.', '_____ de la región galesa.'),
                    'default': ('Es de allí.', '_____ de allí.')
                }
            }
        }
        
        # Analyze the user prompt to select appropriate sentence
        prompt_lower = user_prompt.lower()
        
        if word in sentence_templates:
            meaning_templates = sentence_templates[word].get(meaning_context, {})
            
            # Match prompt keywords to sentence templates
            for keyword, (example, gapped) in meaning_templates.items():
                if keyword in prompt_lower and keyword != 'default':
                    return {'example': example, 'gapped': gapped}
            
            # Use default if no specific match
            default_template = meaning_templates.get('default', ('Es ejemplo.', '_____ ejemplo.'))
            return {'example': default_template[0], 'gapped': default_template[1]}
        
        # Fallback for unknown words
        return {
            'example': f'Es un ejemplo de {word}.',
            'gapped': f'_____ un ejemplo de {word}.'
        }
    
    def create_card_with_prompt_context(self, word: str, meaning_data: Dict, user_prompt: str, 
                                       image_path: str, audio_path: str) -> bool:
        """Create a card with sentences that match the user's visual prompt"""
        
        # Generate contextual sentences based on the prompt
        sentences = self.generate_contextual_sentences(
            word, 
            meaning_data['context_key'], 
            user_prompt
        )
        
        # Create comprehensive card data
        card_data = {
            'spanish_word': word,
            'meaning_id': meaning_data['id'],
            'meaning_context': meaning_data['context'],
            'monolingual_def': meaning_data['definition'],
            'example_sentence': sentences['example'],
            'gapped_sentence': sentences['gapped'],
            'ipa': f'[{word}]',
            'usage_note': meaning_data.get('usage_note', ''),
            'personal_mnemonic': f"Imagen: {user_prompt}",
            'image_path': image_path,
            'audio_path': audio_path
        }
        
        return self.create_anki_card(card_data)
    
    def process_batch(self):
        """Main processing function - to be called by Claude"""
        print("🚀 Fluent Forever V2 - Starting batch processing")
        print("=" * 60)
        
        # Get next words from queue
        next_words = self.get_next_words_from_queue(5)
        if not next_words:
            return
        
        print(f"📝 Next word to analyze: {next_words[0]}")
        print("\n🤖 Claude will now analyze meanings and prepare batch...")
        print("(This system is designed to work with Claude for intelligent analysis)")
        print("\nTo continue, Claude should:")
        print("1. Analyze the word meanings")
        print("2. Create batch with ≤5 cards") 
        print("3. Collect user prompts")
        print("4. Generate media and cards")

if __name__ == "__main__":
    automation = FluentForeverAutomation()
    automation.process_batch()