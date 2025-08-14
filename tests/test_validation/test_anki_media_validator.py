#!/usr/bin/env python3
"""
Tests for anki_media_validator.py - focused on specific failure cases
"""

import pytest
from unittest.mock import patch, Mock
from validation.anki_media_validator import validate_anki_vs_local, MediaSyncResult

class TestAnkiMediaValidator:
    
    def test_anki_connection_fails(self, mock_config):
        """FAILURE CASE: AnkiConnect is not available"""
        with patch('validation.anki_media_validator.load_config', return_value=mock_config), \
             patch('validation.anki_media_validator.AnkiConnection') as mock_anki_class:
            
            # Mock connection failure
            mock_conn = Mock()
            mock_conn.ensure_connection.return_value = False
            mock_anki_class.return_value = mock_conn
            
            result = validate_anki_vs_local()
            
            # Should return empty result when connection fails
            assert isinstance(result, MediaSyncResult)
            assert result.missing_images == []
            assert result.missing_audio == []
            assert not result.has_missing_files()

    def test_local_audio_missing_in_anki(self, mock_config, local_media_files, anki_media_files):
        """FAILURE CASE: Local audio files are missing from Anki"""
        with patch('validation.anki_media_validator.load_config', return_value=mock_config), \
             patch('validation.anki_media_validator.AnkiConnection') as mock_anki_class, \
             patch('validation.anki_media_validator.get_local_media_files', return_value=local_media_files), \
             patch('validation.anki_media_validator.get_anki_media_files', return_value=anki_media_files):
            
            # Mock successful connection
            mock_conn = Mock()
            mock_conn.ensure_connection.return_value = True
            mock_anki_class.return_value = mock_conn
            
            result = validate_anki_vs_local()
            
            # Should detect missing audio: "other.mp3" is local but not in Anki
            assert "other.mp3" in result.missing_audio
            assert result.has_missing_files()

    def test_anki_api_error(self, mock_config, local_media_files):
        """FAILURE CASE: Anki API throws error when getting media files"""
        with patch('validation.anki_media_validator.load_config', return_value=mock_config), \
             patch('validation.anki_media_validator.AnkiConnection') as mock_anki_class, \
             patch('validation.anki_media_validator.get_local_media_files', return_value=local_media_files):
            
            # Mock connection success but API error
            mock_conn = Mock()
            mock_conn.ensure_connection.return_value = True
            mock_conn.request.side_effect = Exception("API Error")
            mock_anki_class.return_value = mock_conn
            
            result = validate_anki_vs_local()
            
            # Should return empty Anki media and detect all local files as missing
            assert len(result.missing_images) == len(local_media_files[0])
            assert len(result.missing_audio) == len(local_media_files[1])
            assert result.has_missing_files()