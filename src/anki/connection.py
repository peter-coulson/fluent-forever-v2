#!/usr/bin/env python3
"""
Anki connection and setup utilities
Handles AnkiConnect communication and Anki application launching
"""

import requests
import time
import os
import sys
from typing import Dict, List, Any, Optional
from utils.logging_config import get_logger, ICONS

logger = get_logger('anki.connection')

class AnkiConnection:
    """Manages connection to AnkiConnect"""
    
    def __init__(self, url: str = "http://localhost:8765"):
        self.url = url
        self.timeout = 10
    
    def is_available(self) -> bool:
        """Check if AnkiConnect is responding"""
        try:
            response = requests.post(self.url, json={
                "action": "version",
                "version": 6
            }, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                return not result.get("error")
        except:
            pass
        return False
    
    def launch_anki(self) -> bool:
        """Launch Anki application in background"""
        logger.info("🚀 Launching Anki in background...")
        
        # Launch Anki (macOS specific)
        os.system("open -a Anki --background")
        
        # Wait for startup
        logger.info("⏳ Waiting for Anki to start...")
        time.sleep(8)
        
        return self.is_available()
    
    def ensure_connection(self) -> bool:
        """Ensure AnkiConnect is available, launching Anki if needed"""
        logger.info(f"{ICONS['gear']} Checking AnkiConnect setup...")
        
        if self.is_available():
            logger.info(f"{ICONS['check']} AnkiConnect is running")
            return True
        
        # Try launching Anki
        if self.launch_anki():
            logger.info(f"{ICONS['check']} AnkiConnect is now running")
            return True
        
        # Failed to connect
        logger.error(f"{ICONS['cross']} CRITICAL: AnkiConnect unavailable!")
        logger.error("Please ensure:")
        logger.error("1. Anki is running")
        logger.error("2. AnkiConnect addon is installed")
        logger.error("3. AnkiConnect addon is enabled")
        return False
    
    def request(self, action: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a request to AnkiConnect"""
        if params is None:
            params = {}
        
        payload = {
            "action": action,
            "version": 6,
            "params": params
        }
        
        try:
            response = requests.post(self.url, json=payload, timeout=self.timeout)
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}")
            
            result = response.json()
            
            if result.get("error"):
                raise Exception(f"AnkiConnect error: {result['error']}")
            
            return result["result"]
            
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to AnkiConnect - make sure Anki is running")
        except requests.exceptions.Timeout:
            raise Exception("AnkiConnect request timed out")
    
    def get_notes(self, query: str) -> List[int]:
        """Get note IDs matching query"""
        return self.request("findNotes", {"query": query})
    
    def get_notes_info(self, note_ids: List[int]) -> List[Dict[str, Any]]:
        """Get detailed info for notes"""
        return self.request("notesInfo", {"notes": note_ids})
    
    def get_deck_cards(self, deck_name: str) -> Dict[str, Dict[str, Dict[str, str]]]:
        """Get all cards from a deck, organized by word/meaning"""
        note_ids = self.get_notes(f'deck:"{deck_name}"')
        notes_info = self.get_notes_info(note_ids)
        
        cards = {}
        for note in notes_info:
            fields = {k: v['value'] for k, v in note['fields'].items()}
            word = fields.get('SpanishWord', '')
            meaning_id = fields.get('MeaningID', '')
            
            if word and meaning_id:
                if word not in cards:
                    cards[word] = {}
                cards[word][meaning_id] = fields
        
        return cards