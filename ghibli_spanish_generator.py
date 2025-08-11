#!/usr/bin/env python3
"""
Fluent Forever V3 - Ghibli Style Spanish Learning Card Generator
Batch processing system: 5 words at a time with user-provided prompts
"""

import json
import requests
import time
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GhibliCardGenerator:
    """Main class for generating Spanish learning cards with Ghibli-style images"""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the generator with configuration"""
        self.config = self.load_config(config_path)
        self.api_key = self.config["apis"]["openai"]["api_key"]
        self.style = self.config["image_generation"]["style"]
        self.media_folder = Path(self.config["paths"]["media_folder"])
        self.media_folder.mkdir(exist_ok=True)
        
        # Load vocabulary database
        self.vocab_db_path = Path(self.config["paths"]["vocabulary_db"])
        self.vocabulary = self.load_vocabulary()
        
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
        
        return {"words": {}, "last_batch": 0, "total_cards": 0}
    
    def save_vocabulary(self):
        """Save vocabulary database to file"""
        try:
            with open(self.vocab_db_path, 'w') as f:
                json.dump(self.vocabulary, f, indent=2, ensure_ascii=False)
            logger.info("Vocabulary database saved")
        except Exception as e:
            logger.error(f"Failed to save vocabulary: {e}")
    
    def collect_batch_prompts(self) -> List[Dict]:
        """Collect 5 Spanish words and their image prompts from user"""
        print("\\n🎨 Ghibli Spanish Learning - Batch Setup")
        print("=" * 50)
        print("Please provide 5 Spanish words and their image prompts.")
        print("I'll format them into consistent Ghibli-style prompts.\\n")
        
        batch = []
        for i in range(5):
            print(f"--- Word {i+1}/5 ---")
            
            spanish_word = input(f"Spanish word: ").strip()
            if not spanish_word:
                print("❌ Spanish word cannot be empty")
                return self.collect_batch_prompts()
            
            english_meaning = input(f"English meaning: ").strip()
            if not english_meaning:
                print("❌ English meaning cannot be empty")  
                return self.collect_batch_prompts()
            
            user_prompt = input(f"Image prompt (what should be shown): ").strip()
            if not user_prompt:
                print("❌ Image prompt cannot be empty")
                return self.collect_batch_prompts()
            
            example_sentence = input(f"Example sentence (optional): ").strip()
            if not example_sentence:
                example_sentence = f"Ejemplo con {spanish_word}"
            
            batch.append({
                "spanish_word": spanish_word,
                "english_meaning": english_meaning,
                "user_prompt": user_prompt,
                "example_sentence": example_sentence
            })
            
            print(f"✅ Added: {spanish_word} = {english_meaning}")
            print()
        
        return batch
    
    def format_ghibli_prompt(self, user_prompt: str) -> str:
        """Format user prompt into consistent Ghibli style"""
        # Clean and enhance the user prompt
        ghibli_prompt = f"{user_prompt}, {self.style}"
        
        # Ensure it's not too long for DALL-E 3
        if len(ghibli_prompt) > 400:
            ghibli_prompt = f"{user_prompt}, Studio Ghibli style anime illustration"
            
        return ghibli_prompt
    
    def generate_image(self, word_data: Dict) -> Optional[str]:
        """Generate a single Ghibli-style image"""
        ghibli_prompt = self.format_ghibli_prompt(word_data["user_prompt"])
        
        print(f"  🎨 Generating: {word_data['spanish_word']}")
        print(f"     Prompt: {ghibli_prompt[:60]}...")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "dall-e-3",
            "prompt": ghibli_prompt,
            "size": "1024x1024",
            "quality": "standard",
            "n": 1
        }
        
        try:
            print("     ⏳ Generating...")
            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                image_url = data["data"][0]["url"]
                
                # Download image
                print("     📥 Downloading...")
                img_response = requests.get(image_url, timeout=30)
                
                if img_response.status_code == 200:
                    # Create filename
                    timestamp = int(time.time())
                    filename = f"{word_data['spanish_word'].lower()}_{timestamp}.png"
                    filepath = self.media_folder / filename
                    
                    # Save image
                    with open(filepath, "wb") as f:
                        f.write(img_response.content)
                    
                    print(f"     ✅ Saved: {filename}")
                    return filename
                    
            print(f"     ❌ Failed: HTTP {response.status_code}")
            return None
            
        except Exception as e:
            print(f"     ❌ Error: {e}")
            return None
    
    def download_audio(self, spanish_word: str) -> Optional[str]:
        """Download audio from Forvo API"""
        # TODO: Implement Forvo API integration
        # For now, return placeholder
        print(f"     🔊 Audio: {spanish_word} (Forvo integration pending)")
        return None
    
    def create_anki_card(self, word_data: Dict, image_filename: str, audio_filename: Optional[str]) -> Dict:
        """Create Anki card data structure"""
        card_data = {
            "SpanishWord": word_data["spanish_word"],
            "IPA": f"[{word_data['spanish_word']}]",  # Placeholder
            "MeaningContext": word_data["english_meaning"],
            "MonolingualDef": f"Definición de {word_data['spanish_word']}",  # Placeholder
            "ExampleSentence": word_data["example_sentence"],
            "GappedSentence": word_data["example_sentence"].replace(word_data["spanish_word"], "___"),
            "ImageFile": f"<img src='{image_filename}'>",
            "WordAudio": f"[sound:{audio_filename}]" if audio_filename else "",
            "WordAudioAlt": "",
            "UsageNote": "",
            "PersonalMnemonic": f"Ghibli scene: {word_data['user_prompt']}",
            "MeaningID": word_data["spanish_word"].lower()
        }
        
        return card_data
    
    def process_batch(self, batch: List[Dict]) -> List[Dict]:
        """Process a complete batch of 5 words"""
        print(f"\\n🚀 Processing Batch of {len(batch)} Words")
        print("=" * 40)
        
        batch_results = []
        total_cost = 0.0
        
        for i, word_data in enumerate(batch, 1):
            print(f"\\n--- Processing {i}/{len(batch)}: {word_data['spanish_word']} ---")
            
            # Generate image
            image_filename = self.generate_image(word_data)
            if image_filename:
                total_cost += 0.04  # OpenAI cost per image
            
            # Download audio (placeholder for now)
            audio_filename = self.download_audio(word_data["spanish_word"])
            
            # Create card data
            if image_filename:
                card_data = self.create_anki_card(word_data, image_filename, audio_filename)
                batch_results.append(card_data)
                
                # Store in vocabulary database
                self.vocabulary["words"][word_data["spanish_word"]] = {
                    "english_meaning": word_data["english_meaning"],
                    "image_prompt": word_data["user_prompt"],
                    "image_filename": image_filename,
                    "audio_filename": audio_filename,
                    "example_sentence": word_data["example_sentence"],
                    "created_at": time.time()
                }
            
            # Brief pause between generations
            if i < len(batch):
                time.sleep(2)
        
        # Update batch statistics
        self.vocabulary["last_batch"] += 1
        self.vocabulary["total_cards"] += len(batch_results)
        self.save_vocabulary()
        
        print(f"\\n{'='*40}")
        print(f"🎉 Batch Complete!")
        print(f"✅ Generated: {len(batch_results)}/{len(batch)} cards")
        print(f"💰 Cost: ~${total_cost:.2f}")
        print(f"📊 Total cards created: {self.vocabulary['total_cards']}")
        
        return batch_results
    
    def export_to_anki(self, batch_results: List[Dict]):
        """Export batch results to Anki-compatible format"""
        # TODO: Implement AnkiConnect integration
        print(f"\\n📤 Anki Export (Placeholder)")
        print("Cards ready for manual import to Anki:")
        
        for card in batch_results:
            print(f"  📄 {card['SpanishWord']} - {card['MeaningContext']}")
    
    def run_batch_workflow(self):
        """Main workflow: collect prompts → generate images → create cards"""
        print("🎌 Fluent Forever V3 - Ghibli Style Spanish Learning")
        print("=" * 60)
        print("Batch processing: 5 words at a time with Ghibli-style images")
        
        # Collect user input
        batch = self.collect_batch_prompts()
        
        # Confirm batch before processing
        print(f"\\n📋 Batch Summary:")
        for i, word_data in enumerate(batch, 1):
            print(f"  {i}. {word_data['spanish_word']} = {word_data['english_meaning']}")
            print(f"     Scene: {word_data['user_prompt']}")
        
        confirm = input(f"\\n🤔 Process this batch? (~${len(batch) * 0.04:.2f}) [y/N]: ")
        if not confirm.lower().startswith('y'):
            print("❌ Batch cancelled")
            return
        
        # Process the batch
        results = self.process_batch(batch)
        
        if results:
            # Export to Anki
            self.export_to_anki(results)
            
            print(f"\\n✨ Success! Your Spanish learning cards are ready.")
            print(f"📁 Images saved in: {self.media_folder}")
            print(f"💾 Progress saved in: {self.vocab_db_path}")
        else:
            print(f"\\n❌ No cards were generated successfully")

def main():
    """Main entry point"""
    try:
        generator = GhibliCardGenerator()
        generator.run_batch_workflow()
    except KeyboardInterrupt:
        print(f"\\n\\n👋 Batch processing cancelled by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"❌ System error: {e}")

if __name__ == "__main__":
    main()
