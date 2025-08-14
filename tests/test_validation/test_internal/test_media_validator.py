#!/usr/bin/env python3
"""
Tests for internal media_validator.py - focused on specific failure cases
"""

import pytest
from unittest.mock import patch, Mock
from validation.internal.media_validator import validate_local_vs_vocabulary
from validation.media_sync_result import MediaSyncResult

class TestInternalMediaValidator:
    
    def test_vocabulary_file_missing(self):
        """FAILURE CASE: vocabulary.json file doesn't exist"""
        with patch('validation.internal.media_validator.load_vocabulary') as mock_load:
            mock_load.side_effect = FileNotFoundError("vocabulary.json not found")
            
            with pytest.raises(FileNotFoundError):
                validate_local_vs_vocabulary()

    def test_local_image_referenced_but_missing(self, mock_vocabulary):
        """FAILURE CASE: Image referenced in vocabulary.json but missing locally"""
        # Mock vocabulary that references an image
        vocab_with_missing_ref = {
            **mock_vocabulary,
            "words": {
                "test": {
                    "meanings": [
                        {
                            "ImageFile": "missing_image.png",
                            "WordAudio": "[sound:test.mp3]"
                        }
                    ]
                }
            }
        }
        
        # Mock local files that don't include the referenced image
        local_files = ({"other_image.png"}, {"test.mp3"})
        
        with patch('validation.internal.media_validator.load_vocabulary', return_value=vocab_with_missing_ref), \
             patch('validation.internal.media_validator.get_local_media_files', return_value=local_files):
            
            result = validate_local_vs_vocabulary()
            
            # Should detect missing referenced image in MediaSyncResult
            assert isinstance(result, MediaSyncResult)
            assert "missing_image.png" in result.missing_images
            
    def test_local_audio_referenced_but_missing(self, mock_vocabulary):
        """FAILURE CASE: Audio referenced in vocabulary.json but missing locally"""
        # Mock vocabulary that references an audio file
        vocab_with_missing_audio = {
            **mock_vocabulary,
            "words": {
                "test": {
                    "meanings": [
                        {
                            "ImageFile": "test_image.png", 
                            "WordAudio": "[sound:missing_audio.mp3]"
                        }
                    ]
                }
            }
        }
        
        # Mock local files that don't include the referenced audio
        local_files = ({"test_image.png"}, {"other.mp3"})
        
        with patch('validation.internal.media_validator.load_vocabulary', return_value=vocab_with_missing_audio), \
             patch('validation.internal.media_validator.get_local_media_files', return_value=local_files):
            
            result = validate_local_vs_vocabulary()
            
            # Should detect missing referenced audio in MediaSyncResult
            assert isinstance(result, MediaSyncResult)
            assert "missing_audio.mp3" in result.missing_audio