#!/usr/bin/env python3
"""
Unit tests for media generation changes with provider support
"""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch, Mock, MagicMock
import pytest

from sync.media_generation import (
    run_media_generation,
    generate_images,
    estimate_cost,
    GenerationPlan
)


class TestMediaGenerationProviderSupport:
    """Test media generation with configurable providers"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_config = {
            "apis": {
                "base": {"user_agent": "Test/1.0", "timeout": 5, "max_retries": 1},
                "openai": {
                    "env_var": "OPENAI_API_KEY",
                    "model": "dall-e-3",
                    "base_url": "https://api.openai.com/v1",
                    "cost_per_image": 0.04
                },
                "runware": {
                    "env_var": "RUNWARE_API_KEY", 
                    "base_url": "https://api.runware.ai",
                    "cost_per_image": 0.01
                },
                "forvo": {
                    "env_var": "FORVO_API_KEY",
                    "base_url": "https://apifree.forvo.com",
                    "country_priorities": ["MX", "CO", "ES"],
                    "priority_groups": [["MX", "CO"], ["ES"]]
                },
                "anki": {
                    "url": "http://localhost:8765",
                    "deck_name": "Test",
                    "note_type": "Fluent Forever",
                    "launch_wait_time": 1
                }
            },
            "image_generation": {
                "primary_provider": "openai",
                "providers": {
                    "openai": {
                        "model": "dall-e-3",
                        "style": "test style",
                        "width": 1024,
                        "height": 1024,
                        "quality": "standard"
                    },
                    "runware": {
                        "model": "stable-diffusion-xl",
                        "style": "test style",
                        "width": 1024,
                        "height": 1024,
                        "steps": 25,
                        "guidance_scale": 7.0,
                        "sampler": "euler"
                    }
                }
            },
            "paths": {
                "media_folder": "media",
                "vocabulary_db": "vocabulary.json",
                "word_queue": "word_queue.txt",
                "downloads": "/tmp"
            },
            "media_generation": {
                "max_new_items": 10,
                "default_timeout": 60,
                "retry_attempts": 3
            },
            "validation": {
                "vocabulary_schema": {
                    "metadata": {"required_fields": ["created", "last_updated", "total_words", "total_cards", "source"]},
                    "word_entry": {"required_fields": ["word", "processed_date", "meanings", "cards_created"]},
                    "meaning_entry": {"required_fields": [
                        "CardID", "SpanishWord", "IPA", "MeaningContext", "MonolingualDef",
                        "ExampleSentence", "GappedSentence", "ImageFile", "WordAudio",
                        "WordAudioAlt", "UsageNote", "MeaningID", "prompt"
                    ]}
                },
                "field_patterns": {
                    "CardID": "^[a-z_0-9]+$",
                    "SpanishWord": "^[a-záéíóúñü]+$",
                    "IPA": "^\\[.*\\]$|^/.*/$",
                    "ImageFile": "^.*\\.png$",
                    "WordAudio": "^\\[sound:.*\\.mp3\\]$",
                    "MeaningID": "^[a-z_]+$"
                },
                "constraints": {
                    "max_cards_per_word": 10,
                    "min_definition_length": 1,
                    "min_example_length": 1
                }
            }
        }

        self.mock_vocabulary = {
            "metadata": {"created": "2025-01-01", "last_updated": "2025-01-01", "total_words": 1, "total_cards": 1, "source": "test"},
            "words": {
                "test": {
                    "word": "test",
                    "processed_date": "2025-01-01",
                    "cards_created": 1,
                    "meanings": [{
                        "CardID": "test_meaning",
                        "SpanishWord": "test",
                        "IPA": "[test]",
                        "MeaningContext": "test",
                        "MonolingualDef": "test definition",
                        "ExampleSentence": "test sentence",
                        "GappedSentence": "_____ sentence",
                        "ImageFile": "test_meaning.png",
                        "WordAudio": "[sound:test.mp3]",
                        "WordAudioAlt": "",
                        "UsageNote": "",
                        "MeaningID": "meaning1",
                        "prompt": "test image prompt"
                    }]
                }
            }
        }

    def create_test_project(self, tmp_path: Path, primary_provider: str = "openai"):
        """Create a test project with specified primary provider"""
        config = self.mock_config.copy()
        config["image_generation"]["primary_provider"] = primary_provider
        config["paths"]["media_folder"] = str(tmp_path / "media")
        config["paths"]["vocabulary_db"] = str(tmp_path / "vocabulary.json")
        
        (tmp_path / "config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2))
        (tmp_path / "vocabulary.json").write_text(json.dumps(self.mock_vocabulary, ensure_ascii=False, indent=2))
        (tmp_path / "media" / "images").mkdir(parents=True)
        (tmp_path / "media" / "audio").mkdir(parents=True)
        
        return config

    @patch('sync.media_generation.create_image_client')
    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch('sync.media_generation.validate_vocabulary')
    @patch('validation.internal.media_validator.validate_local_vs_vocabulary')
    def test_generate_images_uses_factory_openai(self, mock_validator, mock_validate_vocab, mock_load_config, mock_create_client, tmp_path):
        """Test that generate_images uses factory to create OpenAI client"""
        config = self.create_test_project(tmp_path, "openai")
        mock_load_config.return_value = config
        mock_validate_vocab.return_value = True
        
        # Mock no missing files
        mock_result = Mock()
        mock_result.missing_images = []
        mock_result.missing_audio = []
        mock_validator.return_value = mock_result
        
        # Mock client creation
        mock_client = Mock()
        mock_client.generate_image.return_value = Mock(success=True)
        mock_create_client.return_value = mock_client
        
        plan = GenerationPlan(
            card_ids=["test_meaning"],
            words_needed={"test"},
            images_needed={"test_meaning.png"},
            audio_needed={"test.mp3"},
            images_to_generate={"test_meaning.png"},
            audio_to_generate=set()
        )
        
        with patch('sync.media_generation.load_vocabulary', return_value=self.mock_vocabulary), \
             patch('sync.media_generation.load_provenance', return_value={}), \
             patch('sync.media_generation.save_provenance'):
            
            generated, skipped = generate_images(tmp_path, plan, dry_run=False)
            
            # Verify factory was called with correct provider
            mock_create_client.assert_called_once_with("openai")
            assert generated == 1
            assert skipped == 0

    @patch('sync.media_generation.create_image_client')
    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch('sync.media_generation.validate_vocabulary')
    @patch('validation.internal.media_validator.validate_local_vs_vocabulary')
    def test_generate_images_uses_factory_runware(self, mock_validator, mock_validate_vocab, mock_load_config, mock_create_client, tmp_path):
        """Test that generate_images uses factory to create Runware client"""
        config = self.create_test_project(tmp_path, "runware")
        mock_load_config.return_value = config
        mock_validate_vocab.return_value = True
        
        # Mock no missing files
        mock_result = Mock()
        mock_result.missing_images = []
        mock_result.missing_audio = []
        mock_validator.return_value = mock_result
        
        # Mock client creation
        mock_client = Mock()
        mock_client.generate_image.return_value = Mock(success=True)
        mock_create_client.return_value = mock_client
        
        plan = GenerationPlan(
            card_ids=["test_meaning"],
            words_needed={"test"},
            images_needed={"test_meaning.png"},
            audio_needed={"test.mp3"},
            images_to_generate={"test_meaning.png"},
            audio_to_generate=set()
        )
        
        with patch('sync.media_generation.load_vocabulary', return_value=self.mock_vocabulary), \
             patch('sync.media_generation.load_provenance', return_value={}), \
             patch('sync.media_generation.save_provenance'):
            
            generated, skipped = generate_images(tmp_path, plan, dry_run=False)
            
            # Verify factory was called with correct provider
            mock_create_client.assert_called_once_with("runware")
            assert generated == 1
            assert skipped == 0

    @patch('apis.base_client.BaseAPIClient.load_config')
    def test_estimate_cost_openai_provider(self, mock_load_config, tmp_path):
        """Test cost estimation with OpenAI provider"""
        config = self.create_test_project(tmp_path, "openai")
        mock_load_config.return_value = config
        
        plan = GenerationPlan(
            card_ids=["test_meaning"],
            words_needed={"test"},
            images_needed={"test_meaning.png"},
            audio_needed={"test.mp3"},
            images_to_generate={"test_meaning.png"},
            audio_to_generate=set()
        )
        
        cost = estimate_cost(plan, tmp_path)
        
        # Should use OpenAI cost (0.04 per image)
        assert cost == 0.04

    @patch('apis.base_client.BaseAPIClient.load_config')
    def test_estimate_cost_runware_provider(self, mock_load_config, tmp_path):
        """Test cost estimation with Runware provider"""
        config = self.create_test_project(tmp_path, "runware")
        mock_load_config.return_value = config
        
        plan = GenerationPlan(
            card_ids=["test_meaning"],
            words_needed={"test"},
            images_needed={"test_meaning.png"},
            audio_needed={"test.mp3"},
            images_to_generate={"test_meaning.png"},
            audio_to_generate=set()
        )
        
        cost = estimate_cost(plan, tmp_path)
        
        # Should use Runware cost (0.01 per image)
        assert cost == 0.01

    @patch('apis.base_client.BaseAPIClient.load_config')
    def test_estimate_cost_multiple_images(self, mock_load_config, tmp_path):
        """Test cost estimation with multiple images"""
        config = self.create_test_project(tmp_path, "runware")
        mock_load_config.return_value = config
        
        plan = GenerationPlan(
            card_ids=["test1", "test2", "test3"],
            words_needed={"test"},
            images_needed={"test1.png", "test2.png", "test3.png"},
            audio_needed=set(),
            images_to_generate={"test1.png", "test2.png", "test3.png"},
            audio_to_generate=set()
        )
        
        cost = estimate_cost(plan, tmp_path)
        
        # Should be 3 * 0.01 = 0.03
        assert cost == 0.03

    @patch('sync.media_generation.create_image_client')
    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch('sync.media_generation.validate_vocabulary')
    @patch('validation.internal.media_validator.validate_local_vs_vocabulary')
    def test_provenance_tracks_provider(self, mock_validator, mock_validate_vocab, mock_load_config, mock_create_client, tmp_path):
        """Test that provenance correctly tracks the provider used"""
        config = self.create_test_project(tmp_path, "runware")
        mock_load_config.return_value = config
        mock_validate_vocab.return_value = True
        
        # Mock no missing files
        mock_result = Mock()
        mock_result.missing_images = []
        mock_result.missing_audio = []
        mock_validator.return_value = mock_result
        
        # Mock client creation
        mock_client = Mock()
        mock_client.generate_image.return_value = Mock(success=True)
        mock_create_client.return_value = mock_client
        
        plan = GenerationPlan(
            card_ids=["test_meaning"],
            words_needed={"test"},
            images_needed={"test_meaning.png"},
            audio_needed={"test.mp3"},
            images_to_generate={"test_meaning.png"},
            audio_to_generate=set()
        )
        
        saved_provenance = {}
        
        def capture_provenance(path, provenance):
            saved_provenance.update(provenance)
        
        with patch('sync.media_generation.load_vocabulary', return_value=self.mock_vocabulary), \
             patch('sync.media_generation.load_provenance', return_value={}), \
             patch('sync.media_generation.save_provenance', side_effect=capture_provenance):
            
            generated, skipped = generate_images(tmp_path, plan, dry_run=False)
            
            # Verify provenance includes correct provider
            assert "test_meaning.png" in saved_provenance
            assert saved_provenance["test_meaning.png"]["provider"] == "runware"
            assert saved_provenance["test_meaning.png"]["word"] == "test"

    @patch('sync.media_generation.create_image_client')
    @patch('apis.base_client.BaseAPIClient.load_config')
    @patch('sync.media_generation.validate_vocabulary')
    @patch('validation.internal.media_validator.validate_local_vs_vocabulary')  
    def test_dry_run_does_not_create_client(self, mock_validator, mock_validate_vocab, mock_load_config, mock_create_client, tmp_path):
        """Test that dry run mode does not create image client"""
        config = self.create_test_project(tmp_path, "openai")
        mock_load_config.return_value = config
        mock_validate_vocab.return_value = True
        
        # Mock no missing files
        mock_result = Mock()
        mock_result.missing_images = []
        mock_result.missing_audio = []
        mock_validator.return_value = mock_result
        
        plan = GenerationPlan(
            card_ids=["test_meaning"],
            words_needed={"test"},
            images_needed={"test_meaning.png"},
            audio_needed={"test.mp3"},
            images_to_generate={"test_meaning.png"},
            audio_to_generate=set()
        )
        
        with patch('sync.media_generation.load_vocabulary', return_value=self.mock_vocabulary), \
             patch('sync.media_generation.load_provenance', return_value={}), \
             patch('sync.media_generation.save_provenance'):
            
            generated, skipped = generate_images(tmp_path, plan, dry_run=True)
            
            # Verify factory was NOT called in dry run mode
            mock_create_client.assert_not_called()

    @patch('sync.media_generation.create_image_client')  
    @patch('apis.base_client.BaseAPIClient.load_config')
    def test_factory_creation_error_handling(self, mock_load_config, mock_create_client, tmp_path):
        """Test handling of factory creation errors"""
        config = self.create_test_project(tmp_path, "invalid_provider")
        mock_load_config.return_value = config
        
        # Mock factory error
        mock_create_client.side_effect = ValueError("Unsupported provider")
        
        plan = GenerationPlan(
            card_ids=["test_meaning"],
            words_needed={"test"},
            images_needed={"test_meaning.png"}, 
            audio_needed={"test.mp3"},
            images_to_generate={"test_meaning.png"},
            audio_to_generate=set()
        )
        
        with patch('sync.media_generation.load_vocabulary', return_value=self.mock_vocabulary), \
             patch('sync.media_generation.load_provenance', return_value={}), \
             patch('sync.media_generation.save_provenance'), \
             pytest.raises(ValueError, match="Unsupported provider"):
            
            generate_images(tmp_path, plan, dry_run=False)