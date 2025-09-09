#!/usr/bin/env python3
"""
Anki Sync Provider
Handles all interactions with Anki via the AnkiConnect addon
Migrated from src/apis/anki_client.py to new provider structure
"""

import base64
import time
from pathlib import Path
from typing import Any

from providers.base.api_client import BaseAPIClient
from providers.base.sync_provider import SyncProvider, SyncRequest, SyncResult
from utils.logging_config import ICONS, get_logger

logger = get_logger("providers.sync.anki")


class AnkiProvider(SyncProvider, BaseAPIClient):
    """Anki sync provider for card and template synchronization"""

    def __init__(self):
        BaseAPIClient.__init__(self, "AnkiConnect")

        # Handle both old and new config structure during migration
        if "apis" in self.config and "anki" in self.config["apis"]:
            self.api_config = self.config["apis"]["anki"]
        elif (
            "providers" in self.config
            and "sync" in self.config["providers"]
            and "anki" in self.config["providers"]["sync"]
        ):
            self.api_config = self.config["providers"]["sync"]["anki"]
        else:
            # Fallback config
            self.api_config = {
                "url": "http://127.0.0.1:8765",
                "deck_name": "FluentForever",
                "note_type": "FluentForever",
            }

        self.base_url = self.api_config["url"]
        self.deck_name = self.api_config["deck_name"]
        self.note_type = self.api_config["note_type"]

    @property
    def supported_targets(self) -> list[str]:
        """Sync targets supported by Anki provider"""
        return ["anki"]

    def test_connection(self) -> bool:
        """Test AnkiConnect connection and try to launch Anki if needed"""
        # First try to connect
        if self._check_connection():
            return True

        # Try to launch Anki and wait
        self.logger.info(
            f"{ICONS['gear']} AnkiConnect not responding, launching Anki..."
        )
        if self._launch_anki():
            return self._check_connection()

        return False

    def get_service_info(self) -> dict[str, Any]:
        """Get AnkiConnect service information"""
        try:
            response = self._make_request(
                "POST", self.base_url, json={"action": "version", "version": 6}
            )

            if response.success:
                return {
                    "service": "AnkiConnect",
                    "type": "sync_provider",
                    "version": response.data,
                    "supported_targets": self.supported_targets,
                }
        except Exception as e:
            logger.warning(f"Could not get service info: {e}")

        return {
            "service": "AnkiConnect",
            "type": "sync_provider",
            "status": "unavailable",
        }

    def sync_data(self, request: SyncRequest) -> SyncResult:
        """
        Sync data to Anki

        Args:
            request: SyncRequest with target='anki', data=cards/notes, params with operation type

        Returns:
            SyncResult with success status and processed count
        """
        if request.target != "anki":
            return SyncResult(
                success=False,
                processed_count=0,
                metadata={},
                error_message=f"Unsupported sync target: {request.target}. Anki provider only supports 'anki'.",
            )

        operation = request.params.get("operation", "sync_cards")

        try:
            if operation == "sync_cards":
                return self._sync_cards(request.data, request.params)
            elif operation == "sync_templates":
                return self._sync_templates(request.data, request.params)
            elif operation == "sync_media":
                return self._sync_media(request.data, request.params)
            else:
                return SyncResult(
                    success=False,
                    processed_count=0,
                    metadata={},
                    error_message=f"Unsupported operation: {operation}",
                )

        except Exception as e:
            logger.error(f"{ICONS['cross']} Error syncing to Anki: {e}")
            return SyncResult(
                success=False,
                processed_count=0,
                metadata={"operation": operation},
                error_message=str(e),
            )

    def sync_templates(self, note_type: str, templates: list[dict]) -> SyncResult:
        """Sync card templates to Anki (abstract method implementation)"""
        template_data = {"model_name": note_type, "templates": templates}
        return self._sync_templates(template_data, {})

    def sync_media(self, media_files: list[Path]) -> SyncResult:
        """Sync media files to Anki (abstract method implementation)"""
        # Convert Path objects to the format expected by _sync_media
        media_data = []
        for file_path in media_files:
            media_data.append({"filename": file_path.name, "path": str(file_path)})
        return self._sync_media(media_data, {})

    def sync_cards(self, cards: list[dict]) -> SyncResult:
        """Sync card data to Anki (abstract method implementation)"""
        return self._sync_cards(cards, {})

    def list_existing(self, note_type: str) -> list[dict]:
        """List existing items of specified note type (abstract method implementation)"""
        try:
            # Find all notes of the specified note type
            response = self._make_request(
                "POST",
                self.base_url,
                json={
                    "action": "findNotes",
                    "version": 6,
                    "params": {"query": f'note:"{note_type}"'},
                },
            )

            if response.success and response.data:
                note_ids = response.data

                # Get note info for these IDs
                info_response = self._make_request(
                    "POST",
                    self.base_url,
                    json={
                        "action": "notesInfo",
                        "version": 6,
                        "params": {"notes": note_ids},
                    },
                )

                if info_response.success:
                    return info_response.data

            return []

        except Exception as e:
            logger.error(f"{ICONS['cross']} Error listing existing notes: {e}")
            return []

    # Keep existing sync_request-based methods for backward compatibility
    def sync_templates_request(self, request: SyncRequest) -> SyncResult:
        """Sync card templates to Anki (request-based)"""
        return self._sync_templates(request.data, request.params)

    def sync_media_request(self, request: SyncRequest) -> SyncResult:
        """Sync media files to Anki (request-based)"""
        return self._sync_media(request.data, request.params)

    def list_existing_decks(self) -> list[str]:
        """List existing deck names in Anki"""
        try:
            response = self._make_request(
                "POST", self.base_url, json={"action": "deckNames", "version": 6}
            )

            if response.success and response.data:
                # Extract the 'result' field from Anki Connect response
                if isinstance(response.data, dict) and "result" in response.data:
                    return response.data["result"] if response.data["result"] else []
                # If response.data is already a list (shouldn't happen with AnkiConnect)
                elif isinstance(response.data, list):
                    return response.data

        except Exception as e:
            logger.error(f"{ICONS['cross']} Error listing decks: {e}")

        return []

    def _check_connection(self) -> bool:
        """Check if AnkiConnect is responding"""
        try:
            response = self._make_request(
                "POST",
                self.base_url,
                json={"action": "version", "version": 6},
                max_retries=1,  # Quick check, don't retry
            )

            if response.success and response.data:
                # Extract version from Anki Connect response structure
                if isinstance(response.data, dict) and "result" in response.data:
                    version = response.data["result"]
                else:
                    version = response.data

                if version and version >= 6:
                    self.logger.debug(
                        f"{ICONS['check']} AnkiConnect version {version} available"
                    )
                    return True
                else:
                    self.logger.warning(
                        f"{ICONS['warning']} AnkiConnect version too old: {version}"
                    )

        except Exception as e:
            self.logger.debug(f"AnkiConnect not available: {e}")

        return False

    def _launch_anki(self) -> bool:
        """Try to launch Anki application"""
        try:
            import subprocess
            import sys

            if sys.platform == "darwin":  # macOS
                subprocess.Popen(
                    ["open", "-a", "Anki"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            elif sys.platform == "win32":  # Windows
                subprocess.Popen(
                    ["anki"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            else:  # Linux
                subprocess.Popen(
                    ["anki"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )

            # Wait for Anki to start
            self.logger.info("Waiting for Anki to launch...")
            time.sleep(5)
            return True

        except Exception as e:
            self.logger.error(f"{ICONS['cross']} Failed to launch Anki: {e}")
            return False

    def _sync_cards(
        self, cards: list[dict[str, Any]], params: dict[str, Any]
    ) -> SyncResult:
        """Sync cards/notes to Anki"""
        if not cards:
            return SyncResult(
                success=True,
                processed_count=0,
                metadata={"operation": "sync_cards"},
                error_message="No cards to sync",
            )

        deck_name = params.get("deck", self.deck_name)
        note_type = params.get("note_type", self.note_type)

        # Prepare notes for Anki
        anki_notes = []
        for card in cards:
            note = {
                "deckName": deck_name,
                "modelName": note_type,
                "fields": {
                    "Front": card.get("front", ""),
                    "Back": card.get("back", ""),
                    "Audio": card.get("audio", ""),
                    "Image": card.get("image", ""),
                    "IPA": card.get("ipa", ""),
                    "Tags": card.get("tags", ""),
                },
                "tags": card.get("tag_list", []),
            }
            anki_notes.append(note)

        # Add notes to Anki
        response = self._make_request(
            "POST",
            self.base_url,
            json={"action": "addNotes", "version": 6, "params": {"notes": anki_notes}},
        )

        if not response.success:
            return SyncResult(
                success=False,
                processed_count=0,
                metadata={"operation": "sync_cards", "deck": deck_name},
                error_message=response.error_message,
            )

        # Check for Anki-level errors in the response data
        if response.data and isinstance(response.data, dict):
            if response.data.get("error"):
                return SyncResult(
                    success=False,
                    processed_count=0,
                    metadata={"operation": "sync_cards", "deck": deck_name},
                    error_message=response.data["error"],
                )
            note_ids = response.data.get("result")
        else:
            note_ids = response.data
        if not note_ids:
            return SyncResult(
                success=False,
                processed_count=0,
                metadata={"operation": "sync_cards", "deck": deck_name},
                error_message="Anki returned no note IDs - check note type and deck exist",
            )

        # Count successful additions (non-null IDs)
        successful_count = sum(1 for note_id in note_ids if note_id is not None)

        return SyncResult(
            success=True,
            processed_count=successful_count,
            metadata={
                "operation": "sync_cards",
                "deck": deck_name,
                "note_type": note_type,
            },
            created_ids=[nid for nid in note_ids if nid is not None],
        )

    def _sync_templates(
        self, template_data: dict[str, Any], params: dict[str, Any]
    ) -> SyncResult:
        """Sync card templates to Anki"""
        model_name = template_data.get("model_name", self.note_type)

        # Update model/note type in Anki
        response = self._make_request(
            "POST",
            self.base_url,
            json={
                "action": "updateModelTemplates",
                "version": 6,
                "params": {
                    "model": {
                        "name": model_name,
                        "templates": template_data.get("templates", []),
                    }
                },
            },
        )

        if response.success:
            return SyncResult(
                success=True,
                processed_count=len(template_data.get("templates", [])),
                metadata={"operation": "sync_templates", "model": model_name},
            )
        else:
            return SyncResult(
                success=False,
                processed_count=0,
                metadata={"operation": "sync_templates", "model": model_name},
                error_message=response.error_message,
            )

    def _sync_media(
        self, media_files: list[dict[str, Any]], params: dict[str, Any]
    ) -> SyncResult:
        """Sync media files to Anki"""
        if not media_files:
            return SyncResult(
                success=True,
                processed_count=0,
                metadata={"operation": "sync_media"},
                error_message="No media files to sync",
            )

        successful_count = 0

        for media_file in media_files:
            filename = media_file.get("filename")
            file_path = media_file.get("path")

            if not filename or not file_path:
                continue

            try:
                # Read file and encode as base64
                with open(file_path, "rb") as f:
                    file_data = base64.b64encode(f.read()).decode("utf-8")

                # Store media file in Anki
                response = self._make_request(
                    "POST",
                    self.base_url,
                    json={
                        "action": "storeMediaFile",
                        "version": 6,
                        "params": {"filename": filename, "data": file_data},
                    },
                )

                if response.success:
                    successful_count += 1
                    logger.debug(f"{ICONS['check']} Stored media file: {filename}")
                else:
                    logger.warning(
                        f"{ICONS['warning']} Failed to store media file {filename}: {response.error_message}"
                    )

            except Exception as e:
                logger.error(
                    f"{ICONS['cross']} Error processing media file {filename}: {e}"
                )

        return SyncResult(
            success=successful_count > 0,
            processed_count=successful_count,
            metadata={"operation": "sync_media", "total_files": len(media_files)},
        )
