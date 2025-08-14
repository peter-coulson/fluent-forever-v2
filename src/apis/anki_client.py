#!/usr/bin/env python3
"""
AnkiConnect API Client
Handles all interactions with Anki via the AnkiConnect addon
"""

import os
import time
import base64
from pathlib import Path
from typing import Dict, Any, Optional, List
from apis.base_client import BaseAPIClient, APIResponse, APIError
from utils.logging_config import get_logger, ICONS

logger = get_logger('apis.anki')

class AnkiClient(BaseAPIClient):
    """AnkiConnect API client for Anki operations"""
    
    def __init__(self):
        super().__init__("AnkiConnect")
        self.api_config = self.config["apis"]["anki"]
        self.base_url = self.api_config["url"]
        self.deck_name = self.api_config["deck_name"]
        self.note_type = self.api_config["note_type"]
        
    def test_connection(self) -> bool:
        """Test AnkiConnect connection and try to launch Anki if needed"""
        # First try to connect
        if self._check_connection():
            return True
            
        # Try to launch Anki and wait
        self.logger.info(f"{ICONS['gear']} AnkiConnect not responding, launching Anki...")
        if self._launch_anki():
            return self._check_connection()
            
        return False
    
    def _check_connection(self) -> bool:
        """Check if AnkiConnect is responding"""
        try:
            response = self._make_request(
                "POST", 
                self.base_url,
                json={"action": "version", "version": 6},
                max_retries=1  # Quick check, don't retry
            )
            
            if response.success:
                version = response.data
                self.logger.info(f"{ICONS['check']} AnkiConnect is running (version: {version})")
                return True
            else:
                self.logger.debug(f"AnkiConnect not responding: {response.error_message}")
                return False
                
        except Exception as e:
            self.logger.debug(f"AnkiConnect connection check failed: {e}")
            return False
    
    def _launch_anki(self) -> bool:
        """Launch Anki application in background (macOS specific)"""
        try:
            self.logger.info(f"{ICONS['gear']} Launching Anki in background...")
            os.system("open -a Anki --background")
            
            # Wait for Anki to start
            wait_time = self.api_config["launch_wait_time"]
            self.logger.info(f"{ICONS['gear']} Waiting {wait_time}s for Anki to start...")
            time.sleep(wait_time)
            
            return True
            
        except Exception as e:
            self.logger.error(f"{ICONS['cross']} Failed to launch Anki: {e}")
            return False
    
    def get_service_info(self) -> Dict[str, Any]:
        """Deprecated: service info not used by new flow"""
        return {
            "service": "AnkiConnect",
            "deck_name": self.deck_name,
            "note_type": self.note_type,
            "url": self.base_url
        }
    
    def create_card(self, card_data: Dict[str, Any]) -> APIResponse:
        """
        Create Anki card with media files
        
        Args:
            card_data: Dictionary with card field data and media info
            
        Returns:
            APIResponse with success status and note ID if created
        """
        try:
            self.logger.info(f"{ICONS['gear']} Creating Anki card: {card_data.get('CardID', 'unknown')}")
            
            # First, store media files
            media_stored = self._store_media_files(card_data)
            if not media_stored:
                return APIResponse(success=False, error_message="Failed to store media files")
            
            # Create the note
            note_data = {
                "action": "addNote",
                "version": 6,
                "params": {
                    "note": {
                        "deckName": self.deck_name,
                        "modelName": self.note_type,
                        "fields": self._prepare_card_fields(card_data),
                        "tags": ["fluent-forever", "auto-generated"]
                    }
                }
            }
            
            response = self._make_request("POST", self.base_url, json=note_data)
            
            if response.success:
                note_id = response.data
                self.logger.info(f"{ICONS['check']} Card created successfully (ID: {note_id})")
                return APIResponse(success=True, data={"note_id": note_id})
            else:
                return response
                
        except Exception as e:
            error_msg = f"Failed to create card: {e}"
            self.logger.error(f"{ICONS['cross']} {error_msg}")
            return APIResponse(success=False, error_message=error_msg)
    
    def _unwrap_result(self, response: APIResponse) -> APIResponse:
        """Unwrap AnkiConnect's {result, error} envelope into plain data.
        If error is present, convert to unsuccessful APIResponse.
        """
        try:
            if not response.success:
                return response
            data = response.data
            if isinstance(data, dict) and 'result' in data and 'error' in data:
                if data.get('error'):
                    return APIResponse(success=False, error_message=str(data['error']))
                return APIResponse(success=True, data=data.get('result'))
            return response
        except Exception as e:
            self.logger.error(f"{ICONS['cross']} Failed to unwrap AnkiConnect response: {e}")
            return APIResponse(success=False, error_message=str(e))

    def get_model_field_names(self, model_name: Optional[str] = None) -> APIResponse:
        """Get field names for the specified note type (model)"""
        try:
            if model_name is None:
                model_name = self.note_type
            request_data = {
                "action": "modelFieldNames",
                "version": 6,
                "params": {"modelName": model_name}
            }
            response = self._make_request("POST", self.base_url, json=request_data)
            return self._unwrap_result(response)
        except Exception as e:
            error_msg = f"Failed to get model field names: {e}"
            self.logger.error(f"{ICONS['cross']} {error_msg}")
            return APIResponse(success=False, error_message=error_msg)

    def get_model_templates(self, model_name: Optional[str] = None) -> APIResponse:
        """Get templates (front/back HTML per card) for the note type"""
        try:
            if model_name is None:
                model_name = self.note_type
            request_data = {
                "action": "modelTemplates",
                "version": 6,
                "params": {"modelName": model_name}
            }
            response = self._make_request("POST", self.base_url, json=request_data)
            return self._unwrap_result(response)
        except Exception as e:
            error_msg = f"Failed to get model templates: {e}"
            self.logger.error(f"{ICONS['cross']} {error_msg}")
            return APIResponse(success=False, error_message=error_msg)

    def get_model_styling(self, model_name: Optional[str] = None) -> APIResponse:
        """Get CSS styling for the note type"""
        try:
            if model_name is None:
                model_name = self.note_type
            request_data = {
                "action": "modelStyling",
                "version": 6,
                "params": {"modelName": model_name}
            }
            response = self._make_request("POST", self.base_url, json=request_data)
            return self._unwrap_result(response)
        except Exception as e:
            error_msg = f"Failed to get model styling: {e}"
            self.logger.error(f"{ICONS['cross']} {error_msg}")
            return APIResponse(success=False, error_message=error_msg)

    def _store_media_files(self, card_data: Dict[str, Any]) -> bool:
        """Store media files in Anki"""
        try:
            media_folder = Path(self.config["paths"]["media_folder"])
            
            # Store image file
            if "ImageFile" in card_data:
                image_filename = card_data["ImageFile"]
                if image_filename and not image_filename.startswith("<img"):  # Not HTML format
                    image_path = media_folder / "images" / image_filename
                    if image_path.exists():
                        if not self._store_media_file(image_path, image_filename):
                            return False
            
            # Store audio file  
            if "WordAudio" in card_data:
                audio_field = card_data["WordAudio"]
                if audio_field and audio_field.startswith("[sound:"):
                    # Extract filename from [sound:filename.mp3]
                    audio_filename = audio_field[7:-1]  # Remove [sound: and ]
                    audio_path = media_folder / "audio" / audio_filename
                    if audio_path.exists():
                        if not self._store_media_file(audio_path, audio_filename):
                            return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"{ICONS['cross']} Error storing media files: {e}")
            return False
    
    def _store_media_file(self, file_path: Path, filename: str) -> bool:
        """Store individual media file in Anki"""
        try:
            # Read and encode file
            with open(file_path, 'rb') as f:
                file_data = base64.b64encode(f.read()).decode()
            
            # Store in Anki
            store_request = {
                "action": "storeMediaFile",
                "version": 6,
                "params": {
                    "filename": filename,
                    "data": file_data
                }
            }
            
            response = self._make_request("POST", self.base_url, json=store_request)
            
            if response.success:
                self.logger.debug(f"Stored media file: {filename}")
                return True
            else:
                self.logger.error(f"{ICONS['cross']} Failed to store {filename}: {response.error_message}")
                return False
                
        except Exception as e:
            self.logger.error(f"{ICONS['cross']} Error storing {filename}: {e}")
            return False

    def store_media_file(self, file_path: Path, filename: str) -> APIResponse:
        """Public wrapper to store a media file in Anki."""
        try:
            ok = self._store_media_file(file_path, filename)
            if ok:
                return APIResponse(success=True, data={"filename": filename})
            return APIResponse(success=False, error_message=f"Failed to store {filename}")
        except Exception as e:
            error_msg = f"Failed to store {filename}: {e}"
            self.logger.error(f"{ICONS['cross']} {error_msg}")
            return APIResponse(success=False, error_message=error_msg)
    
    def _prepare_card_fields(self, card_data: Dict[str, Any]) -> Dict[str, str]:
        """Prepare card fields for Anki note creation"""
        # Define the expected field structure
        anki_fields = {
            "CardID": "",
            "SpanishWord": "",
            "IPA": "",
            "MeaningContext": "",
            "MonolingualDef": "",
            "ExampleSentence": "",
            "GappedSentence": "",
            "ImageFile": "",
            "WordAudio": "",
            "WordAudioAlt": "",
            "UsageNote": "",
            "MeaningID": ""
        }
        
        # Populate fields from card_data
        for field in anki_fields:
            if field in card_data:
                anki_fields[field] = str(card_data[field])
        
        return anki_fields

    def normalize_card_fields(self, card_data: Dict[str, Any]) -> Dict[str, str]:
        """Public wrapper to normalize an arbitrary card dict to Anki fields only."""
        return self._prepare_card_fields(card_data)
    
    def get_deck_cards(self, deck_name: Optional[str] = None) -> APIResponse:
        """Get all cards from a deck"""
        try:
            if deck_name is None:
                deck_name = self.deck_name
                
            # Get note IDs from deck
            find_request = {
                "action": "findNotes",
                "version": 6,
                "params": {
                    "query": f'deck:"{deck_name}"'
                }
            }
            
            response = self._make_request("POST", self.base_url, json=find_request)
            response = self._unwrap_result(response)

            if not response.success:
                return response
                
            note_ids = response.data
            
            if not note_ids:
                return APIResponse(success=True, data={})
            
            # Get detailed info for notes
            info_request = {
                "action": "notesInfo",
                "version": 6,
                "params": {
                    "notes": note_ids
                }
            }
            response = self._make_request("POST", self.base_url, json=info_request)
            response = self._unwrap_result(response)

            if response.success:
                # Organize cards by word/meaning
                cards = {}
                for note in response.data:
                    fields = {k: v['value'] for k, v in note['fields'].items()}
                    word = fields.get('SpanishWord', '')
                    meaning_id = fields.get('MeaningID', '')
                    
                    if word and meaning_id:
                        if word not in cards:
                            cards[word] = {}
                        cards[word][meaning_id] = fields
                
                return APIResponse(success=True, data=cards)
            else:
                return response
                
        except Exception as e:
            error_msg = f"Failed to get deck cards: {e}"
            self.logger.error(f"{ICONS['cross']} {error_msg}")
            return APIResponse(success=False, error_message=error_msg)
    
    def get_media_files(self, pattern: str = "*") -> APIResponse:
        """Get media files from Anki collection"""
        try:
            request_data = {
                "action": "getMediaFilesNames",
                "version": 6,
                "params": {
                    "pattern": pattern
                }
            }
            
            response = self._make_request("POST", self.base_url, json=request_data)
            response = self._unwrap_result(response)

            if response.success:
                files = response.data if response.data else []
                return APIResponse(success=True, data=files)
            else:
                return response
                
        except Exception as e:
            error_msg = f"Failed to get media files: {e}"
            self.logger.error(f"{ICONS['cross']} {error_msg}")
            return APIResponse(success=False, error_message=error_msg)

    def find_notes(self, query: str) -> APIResponse:
        """Find notes by search query"""
        try:
            request_data = {
                "action": "findNotes",
                "version": 6,
                "params": {"query": query}
            }
            response = self._make_request("POST", self.base_url, json=request_data)
            return self._unwrap_result(response)
        except Exception as e:
            error_msg = f"Failed to find notes: {e}"
            self.logger.error(f"{ICONS['cross']} {error_msg}")
            return APIResponse(success=False, error_message=error_msg)

    def notes_info(self, note_ids: list[int]) -> APIResponse:
        """Get notesInfo for given note IDs"""
        try:
            request_data = {
                "action": "notesInfo",
                "version": 6,
                "params": {"notes": note_ids}
            }
            response = self._make_request("POST", self.base_url, json=request_data)
            return self._unwrap_result(response)
        except Exception as e:
            error_msg = f"Failed to get notes info: {e}"
            self.logger.error(f"{ICONS['cross']} {error_msg}")
            return APIResponse(success=False, error_message=error_msg)

    def update_note_fields(self, note_id: int, fields: Dict[str, str]) -> APIResponse:
        """Update fields for a single note"""
        try:
            request_data = {
                "action": "updateNoteFields",
                "version": 6,
                "params": {
                    "note": {
                        "id": note_id,
                        "fields": fields
                    }
                }
            }
            response = self._make_request("POST", self.base_url, json=request_data)
            return self._unwrap_result(response)
        except Exception as e:
            error_msg = f"Failed to update note fields: {e}"
            self.logger.error(f"{ICONS['cross']} {error_msg}")
            return APIResponse(success=False, error_message=error_msg)

    def delete_notes(self, note_ids: list[int]) -> APIResponse:
        """Delete notes by ID"""
        try:
            request_data = {
                "action": "deleteNotes",
                "version": 6,
                "params": {"notes": note_ids}
            }
            response = self._make_request("POST", self.base_url, json=request_data)
            return self._unwrap_result(response)
        except Exception as e:
            error_msg = f"Failed to delete notes: {e}"
            self.logger.error(f"{ICONS['cross']} {error_msg}")
            return APIResponse(success=False, error_message=error_msg)

    def update_model_templates(self, templates: list[Dict[str, str]] | Dict[str, Dict[str, str]], model_name: Optional[str] = None) -> APIResponse:
        """Push updated templates to the model"""
        try:
            if model_name is None:
                model_name = self.note_type
            # AnkiConnect expects a mapping of template name -> {Front, Back}
            if isinstance(templates, list):
                templates_map: Dict[str, Dict[str, str]] = {}
                for t in templates:
                    name = t.get('Name') or t.get('name')
                    if not name:
                        continue
                    templates_map[name] = {
                        'Front': t.get('Front', ''),
                        'Back': t.get('Back', '')
                    }
            else:
                templates_map = templates
            payload = {
                "action": "updateModelTemplates",
                "version": 6,
                "params": {
                    "model": {
                        "name": model_name,
                        "templates": templates_map
                    }
                }
            }
            response = self._make_request("POST", self.base_url, json=payload)
            return self._unwrap_result(response)
        except Exception as e:
            error_msg = f"Failed to update model templates: {e}"
            self.logger.error(f"{ICONS['cross']} {error_msg}")
            return APIResponse(success=False, error_message=error_msg)

    def update_model_styling(self, css: str, model_name: Optional[str] = None) -> APIResponse:
        """Push CSS styling to the model"""
        try:
            if model_name is None:
                model_name = self.note_type
            payload = {
                "action": "updateModelStyling",
                "version": 6,
                "params": {
                    "model": {
                        "name": model_name,
                        "css": css
                    }
                }
            }
            response = self._make_request("POST", self.base_url, json=payload)
            return self._unwrap_result(response)
        except Exception as e:
            error_msg = f"Failed to update model styling: {e}"
            self.logger.error(f"{ICONS['cross']} {error_msg}")
            return APIResponse(success=False, error_message=error_msg)

    def remove_model_field(self, field_name: str, model_name: Optional[str] = None) -> APIResponse:
        """Remove a field from the note type (model)"""
        try:
            if model_name is None:
                model_name = self.note_type
            payload = {
                "action": "removeModelField",
                "version": 6,
                "params": {
                    "model": model_name,
                    "field": field_name
                }
            }
            response = self._make_request("POST", self.base_url, json=payload)
            return self._unwrap_result(response)
        except Exception as e:
            error_msg = f"Failed to remove model field '{field_name}': {e}"
            self.logger.error(f"{ICONS['cross']} {error_msg}")
            return APIResponse(success=False, error_message=error_msg)