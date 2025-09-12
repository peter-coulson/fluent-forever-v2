"""End-to-end tests for Phase 2 enhanced data provider workflows."""

import json
from unittest.mock import patch

import pytest
from src.core.config import Config
from src.core.context import PipelineContext
from src.providers.registry import ProviderRegistry


class TestPhase2Workflows:
    """End-to-end workflow tests for Phase 2 functionality."""

    def test_vocabulary_pipeline_with_multiple_data_providers(self, tmp_path):
        """Test complete vocabulary workflow with multiple data providers."""
        # Setup directory structure
        sources_dir = tmp_path / "sources"
        working_dir = tmp_path / "working"
        output_dir = tmp_path / "output"

        sources_dir.mkdir()
        working_dir.mkdir()
        output_dir.mkdir()

        # Create source dictionary (read-only)
        source_dict = sources_dir / "spanish_dictionary.json"
        source_dict.write_text(
            json.dumps(
                {
                    "casa": {"translation": "house", "gender": "f"},
                    "perro": {"translation": "dog", "gender": "m"},
                    "agua": {"translation": "water", "gender": "f"},
                }
            )
        )

        # Configuration with multiple data providers
        config_content = {
            "providers": {
                "data": {
                    "source_data": {
                        "type": "json",
                        "base_path": str(sources_dir),
                        "files": ["spanish_dictionary"],
                        "read_only": True,
                        "pipelines": ["vocabulary"],
                    },
                    "working_data": {
                        "type": "json",
                        "base_path": str(working_dir),
                        "files": ["word_queue", "learning_progress"],
                        "read_only": False,
                        "pipelines": ["vocabulary"],
                    },
                    "output_data": {
                        "type": "json",
                        "base_path": str(output_dir),
                        "files": ["vocabulary_cards", "final_output"],
                        "read_only": False,
                        "pipelines": ["vocabulary"],
                    },
                },
                "sync": {"anki": {"type": "anki", "pipelines": ["*"]}},
            }
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_content))

        # Load configuration and create registry
        config = Config.load(str(config_path))
        registry = ProviderRegistry.from_config(config)

        # Create context for vocabulary pipeline
        context = PipelineContext("vocabulary", tmp_path)
        context.config = config._config_data  # Set config data

        # Add filtered providers to context
        filtered_providers = registry.get_providers_for_pipeline("vocabulary")
        context.set("providers", filtered_providers)

        # Simulate workflow stages

        # Stage 1: Load source data (read-only provider)
        source_provider = filtered_providers["data"]["source_data"]
        dictionary_data = source_provider.load_data("spanish_dictionary")
        assert len(dictionary_data) == 3
        assert "casa" in dictionary_data

        # Stage 2: Process words and save to working data
        working_provider = filtered_providers["data"]["working_data"]

        # Create word queue from source
        word_queue = []
        for word, info in dictionary_data.items():
            word_queue.append(
                {"word": word, "translation": info["translation"], "status": "pending"}
            )

        # Save to working provider
        working_provider.save_data("word_queue", {"words": word_queue})

        # Save learning progress
        working_provider.save_data(
            "learning_progress",
            {
                "total_words": len(word_queue),
                "learned": 0,
                "session_date": "2024-01-01",
            },
        )

        # Stage 3: Generate final vocabulary cards
        output_provider = filtered_providers["data"]["output_data"]

        # Process words into cards
        vocabulary_cards = []
        for word_info in word_queue:
            vocabulary_cards.append(
                {
                    "front": word_info["word"],
                    "back": word_info["translation"],
                    "tags": ["spanish", "vocabulary"],
                    "card_type": "basic",
                }
            )

        # Save final output
        output_provider.save_data("vocabulary_cards", {"cards": vocabulary_cards})
        output_provider.save_data(
            "final_output",
            {
                "generated_cards": len(vocabulary_cards),
                "source_file": "spanish_dictionary",
                "timestamp": "2024-01-01T10:00:00Z",
            },
        )

        # Verify workflow completed successfully
        assert (working_dir / "word_queue.json").exists()
        assert (working_dir / "learning_progress.json").exists()
        assert (output_dir / "vocabulary_cards.json").exists()
        assert (output_dir / "final_output.json").exists()

        # Verify source data remains untouched and read-only
        with pytest.raises(PermissionError, match="provider is read-only"):
            source_provider.save_data("spanish_dictionary", {"modified": "data"})

    def test_read_only_source_data_protection(self, tmp_path):
        """Test that read-only source data is protected throughout workflow."""
        # Setup source data
        sources_dir = tmp_path / "sources"
        sources_dir.mkdir()

        reference_data = sources_dir / "reference_conjugations.json"
        reference_data.write_text(
            json.dumps(
                {
                    "hablar": {"type": "ar", "meaning": "to speak"},
                    "comer": {"type": "er", "meaning": "to eat"},
                    "vivir": {"type": "ir", "meaning": "to live"},
                }
            )
        )

        config_content = {
            "providers": {
                "data": {
                    "reference_data": {
                        "type": "json",
                        "base_path": str(sources_dir),
                        "files": ["reference_conjugations"],
                        "read_only": True,
                        "pipelines": ["conjugation"],
                    },
                    "temp_data": {
                        "type": "json",
                        "base_path": str(tmp_path / "temp"),
                        "files": ["temp_conjugations"],
                        "read_only": False,
                        "pipelines": ["conjugation"],
                    },
                },
                "sync": {"anki": {"type": "anki", "pipelines": ["*"]}},
            }
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_content))

        config = Config.load(str(config_path))
        registry = ProviderRegistry.from_config(config)

        providers = registry.get_providers_for_pipeline("conjugation")
        reference_provider = providers["data"]["reference_data"]
        temp_provider = providers["data"]["temp_data"]

        # Can read from reference data
        ref_data = reference_provider.load_data("reference_conjugations")
        assert len(ref_data) == 3

        # Cannot write to reference data at any point in workflow
        with pytest.raises(PermissionError):
            reference_provider.save_data(
                "reference_conjugations", {"corrupted": "data"}
            )

        # Can work with temporary data
        temp_provider.save_data("temp_conjugations", {"processed": ref_data})
        processed = temp_provider.load_data("temp_conjugations")
        assert "processed" in processed

    def test_file_segregation_workflow(self, tmp_path):
        """Test workflow with strict file segregation between providers."""
        # Setup multiple data directories
        user_data_dir = tmp_path / "user_data"
        system_data_dir = tmp_path / "system_data"
        cache_dir = tmp_path / "cache"

        user_data_dir.mkdir()
        system_data_dir.mkdir()
        cache_dir.mkdir()

        # Create initial user vocabulary
        user_vocab = user_data_dir / "my_vocabulary.json"
        user_vocab.write_text(
            json.dumps({"words": ["casa", "perro", "gato"], "difficulty": "beginner"})
        )

        # Create system configuration
        system_config = system_data_dir / "system_defaults.json"
        system_config.write_text(
            json.dumps(
                {"default_note_type": "Spanish::Vocabulary", "audio_enabled": True}
            )
        )

        config_content = {
            "providers": {
                "data": {
                    "user_files": {
                        "type": "json",
                        "base_path": str(user_data_dir),
                        "files": ["my_vocabulary", "user_progress"],
                        "read_only": False,
                        "pipelines": ["vocabulary"],
                    },
                    "system_files": {
                        "type": "json",
                        "base_path": str(system_data_dir),
                        "files": ["system_defaults", "templates"],
                        "read_only": True,
                        "pipelines": ["vocabulary"],
                    },
                    "cache_files": {
                        "type": "json",
                        "base_path": str(cache_dir),
                        "files": ["word_cache", "audio_cache"],
                        "read_only": False,
                        "pipelines": ["vocabulary"],
                    },
                },
                "sync": {"anki": {"type": "anki", "pipelines": ["*"]}},
            }
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_content))

        config = Config.load(str(config_path))
        registry = ProviderRegistry.from_config(config)

        providers = registry.get_providers_for_pipeline("vocabulary")
        user_provider = providers["data"]["user_files"]
        system_provider = providers["data"]["system_files"]
        cache_provider = providers["data"]["cache_files"]

        # Workflow: Process user vocabulary with system defaults
        user_vocab_data = user_provider.load_data("my_vocabulary")
        system_defaults = system_provider.load_data("system_defaults")

        # Process and cache results
        processed_words = []
        for word in user_vocab_data["words"]:
            processed_words.append(
                {
                    "word": word,
                    "note_type": system_defaults["default_note_type"],
                    "audio_enabled": system_defaults["audio_enabled"],
                }
            )

        # Save to cache (allowed)
        cache_provider.save_data("word_cache", {"processed_words": processed_words})

        # Save user progress (allowed)
        user_provider.save_data("user_progress", {"processed": len(processed_words)})

        # Verify file segregation is enforced

        # User provider cannot access system files
        with pytest.raises(ValueError, match="not managed by this provider"):
            user_provider.load_data("system_defaults")

        # System provider cannot access user files
        with pytest.raises(ValueError, match="not managed by this provider"):
            system_provider.load_data("my_vocabulary")

        # Cache provider cannot access either user or system files
        with pytest.raises(ValueError, match="not managed by this provider"):
            cache_provider.load_data("my_vocabulary")

        with pytest.raises(ValueError, match="not managed by this provider"):
            cache_provider.load_data("system_defaults")

        # System provider cannot be written to (read-only)
        with pytest.raises(PermissionError, match="provider is read-only"):
            system_provider.save_data("system_defaults", {"modified": "config"})

    def test_config_migration_from_phase1(self, tmp_path):
        """Test that Phase 1 configurations work seamlessly in Phase 2."""
        # Create Phase 1 style configuration (no files/read_only fields)
        config_content = {
            "providers": {
                "data": {
                    "default": {
                        "type": "json",
                        "base_path": str(tmp_path),
                        "pipelines": ["vocabulary"],
                    }
                },
                "audio": {"forvo": {"type": "forvo", "pipelines": ["vocabulary"]}},
                "sync": {"anki": {"type": "anki", "pipelines": ["*"]}},
            }
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_content))

        # Should load without errors
        config = Config.load(str(config_path))

        with patch("src.providers.audio.forvo_provider.ForvoProvider"):
            registry = ProviderRegistry.from_config(config)

        # Verify provider works with default Phase 2 settings
        data_provider = registry.get_data_provider("default")
        assert data_provider is not None
        assert data_provider.is_read_only is False  # Default value
        assert data_provider.managed_files == []  # Default value (no restrictions)

        # Should work with any file (backward compatibility)
        test_data = {"phase1": "compatibility"}
        assert data_provider.save_data("any_file", test_data) is True
        assert data_provider.load_data("any_file") == test_data

        # Pipeline filtering should still work
        vocab_providers = registry.get_providers_for_pipeline("vocabulary")
        assert "default" in vocab_providers["data"]

        # Other pipeline should not have access
        other_providers = registry.get_providers_for_pipeline("conjugation")
        assert "default" not in other_providers["data"]
