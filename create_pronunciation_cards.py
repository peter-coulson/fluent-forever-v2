#!/usr/bin/env python3
"""
Create pronunciation cards for Latin Spanish deck
Creates both basic (sound -> IPA) and reversed (IPA -> sound) cards
"""

import sys
import os
import base64
from pathlib import Path

# Add src to path for imports
sys.path.append('src')

from apis.anki_client import AnkiClient
from apis.base_client import APIResponse

def get_ipa_from_filename(filename):
    """Extract IPA symbol from filename (everything before .mp3)"""
    return filename.replace('.mp3', '')

def create_pronunciation_cards():
    """Create pronunciation cards for all sound files in references folder"""
    
    # Initialize Anki client
    client = AnkiClient()
    
    # Test connection
    if not client.test_connection():
        print("Failed to connect to Anki. Make sure Anki is running with AnkiConnect addon.")
        return False
    
    # Get all MP3 files from references folder
    references_path = Path('references')
    if not references_path.exists():
        print("References folder not found!")
        return False
    
    mp3_files = list(references_path.glob('*.mp3'))
    if not mp3_files:
        print("No MP3 files found in references folder!")
        return False
    
    print(f"Found {len(mp3_files)} sound files")
    
    deck_name = "Latin Spanish::5. Pronunciation Rulse"
    
    success_count = 0
    error_count = 0
    
    for mp3_file in mp3_files:
        ipa_symbol = get_ipa_from_filename(mp3_file.name)
        print(f"Processing: {mp3_file.name} -> {ipa_symbol}")
        
        # Store the audio file in Anki first
        store_response = client.store_media_file(mp3_file, mp3_file.name)
        if not store_response.success:
            print(f"  Failed to store audio file: {store_response.error_message}")
            error_count += 1
            continue
        
        # Create basic card: Sound -> IPA
        basic_card_data = {
            "action": "addNote",
            "version": 6,
            "params": {
                "note": {
                    "deckName": deck_name,
                    "modelName": "Basic (and reversed card)",
                    "fields": {
                        "Front": f"[sound:{mp3_file.name}]",
                        "Back": ipa_symbol
                    },
                    "tags": ["pronunciation", "ipa", "sound-to-ipa"]
                }
            }
        }
        
        # Create reversed card: IPA -> Sound  
        reversed_card_data = {
            "action": "addNote",
            "version": 6,
            "params": {
                "note": {
                    "deckName": deck_name,
                    "modelName": "Basic (and reversed card)",
                    "fields": {
                        "Front": ipa_symbol,
                        "Back": f"[sound:{mp3_file.name}]"
                    },
                    "tags": ["pronunciation", "ipa", "ipa-to-sound"]
                }
            }
        }
        
        # Create basic card
        basic_response = client._make_request("POST", client.base_url, json=basic_card_data)
        basic_response = client._unwrap_result(basic_response)
        if basic_response.success:
            print(f"  ✓ Created basic card (sound -> IPA)")
            success_count += 1
        else:
            print(f"  ✗ Failed to create basic card: {basic_response.error_message}")
            error_count += 1
        
        # Create reversed card
        reversed_response = client._make_request("POST", client.base_url, json=reversed_card_data)
        reversed_response = client._unwrap_result(reversed_response)
        if reversed_response.success:
            print(f"  ✓ Created reversed card (IPA -> sound)")
            success_count += 1
        else:
            print(f"  ✗ Failed to create reversed card: {reversed_response.error_message}")
            error_count += 1
    
    print(f"\nCompleted: {success_count} cards created, {error_count} errors")
    return error_count == 0

if __name__ == "__main__":
    success = create_pronunciation_cards()
    sys.exit(0 if success else 1)