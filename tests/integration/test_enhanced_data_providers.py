"""Integration tests for enhanced data provider functionality."""

import json

import pytest
from src.core.config import Config
from src.providers.registry import ProviderRegistry


class TestEnhancedDataProviderIntegration:
    """Test enhanced data provider integration functionality."""

    def test_from_config_read_only_providers(self, tmp_path):
        """Test loading read-only providers from configuration."""
        config_content = {
            "providers": {
                "data": {
                    "source_data": {
                        "type": "json",
                        "base_path": str(tmp_path / "sources"),
                        "files": ["dictionary", "conjugations"],
                        "read_only": True,
                        "pipelines": ["vocabulary"],
                    }
                },
                "sync": {"anki": {"type": "anki", "pipelines": ["*"]}},
            }
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_content))

        config = Config.load(str(config_path))
        registry = ProviderRegistry.from_config(config)

        # Verify provider was created
        provider = registry.get_data_provider("source_data")
        assert provider is not None
        assert provider.is_read_only is True
        assert provider.managed_files == ["dictionary", "conjugations"]

        # Verify read-only behavior
        with pytest.raises(PermissionError, match="provider is read-only"):
            provider.save_data("dictionary", {"word": "test"})

    def test_from_config_multiple_named_providers_with_files(self, tmp_path):
        """Test loading multiple named providers with file assignments."""
        config_content = {
            "providers": {
                "data": {
                    "sources": {
                        "type": "json",
                        "base_path": str(tmp_path / "sources"),
                        "files": ["spanish_dict", "verb_patterns"],
                        "read_only": True,
                        "pipelines": ["vocabulary"],
                    },
                    "working": {
                        "type": "json",
                        "base_path": str(tmp_path / "work"),
                        "files": ["word_queue", "progress"],
                        "read_only": False,
                        "pipelines": ["vocabulary"],
                    },
                    "output": {
                        "type": "json",
                        "base_path": str(tmp_path / "output"),
                        "files": ["vocabulary", "anki_cards"],
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

        # Verify all providers were created
        sources = registry.get_data_provider("sources")
        working = registry.get_data_provider("working")
        output = registry.get_data_provider("output")

        assert sources is not None
        assert working is not None
        assert output is not None

        # Verify configurations
        assert sources.is_read_only is True
        assert sources.managed_files == ["spanish_dict", "verb_patterns"]

        assert working.is_read_only is False
        assert working.managed_files == ["word_queue", "progress"]

        assert output.is_read_only is False
        assert output.managed_files == ["vocabulary", "anki_cards"]

    def test_from_config_file_conflict_validation(self, tmp_path):
        """Test that file conflicts are detected during configuration loading."""
        config_content = {
            "providers": {
                "data": {
                    "provider1": {
                        "type": "json",
                        "base_path": str(tmp_path),
                        "files": ["shared_file", "file1"],
                        "read_only": True,
                        "pipelines": ["*"],
                    },
                    "provider2": {
                        "type": "json",
                        "base_path": str(tmp_path),
                        "files": ["shared_file", "file2"],  # shared_file conflicts
                        "read_only": False,
                        "pipelines": ["*"],
                    },
                },
                "sync": {"anki": {"type": "anki", "pipelines": ["*"]}},
            }
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_content))

        config = Config.load(str(config_path))

        # Should raise ValueError due to file conflicts
        with pytest.raises(
            ValueError,
            match="File conflicts detected.*shared_file.*provider1.*provider2",
        ):
            ProviderRegistry.from_config(config)

    def test_pipeline_filtering_with_multiple_named_providers(self, tmp_path):
        """Test that pipeline filtering works with multiple named data providers."""
        config_content = {
            "providers": {
                "data": {
                    "vocab_data": {
                        "type": "json",
                        "base_path": str(tmp_path),
                        "files": ["vocabulary", "word_lists"],
                        "read_only": False,
                        "pipelines": ["vocabulary"],
                    },
                    "conjugation_data": {
                        "type": "json",
                        "base_path": str(tmp_path),
                        "files": ["conjugations", "verb_forms"],
                        "read_only": False,
                        "pipelines": ["conjugation"],
                    },
                    "shared_data": {
                        "type": "json",
                        "base_path": str(tmp_path),
                        "files": ["common_words"],
                        "read_only": True,
                        "pipelines": ["*"],
                    },
                },
                "sync": {"anki": {"type": "anki", "pipelines": ["*"]}},
            }
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_content))

        config = Config.load(str(config_path))
        registry = ProviderRegistry.from_config(config)

        # Test vocabulary pipeline filtering
        vocab_providers = registry.get_providers_for_pipeline("vocabulary")
        vocab_data_providers = vocab_providers["data"]

        assert "vocab_data" in vocab_data_providers
        assert "shared_data" in vocab_data_providers  # Wildcard access
        assert "conjugation_data" not in vocab_data_providers

        # Test conjugation pipeline filtering
        conj_providers = registry.get_providers_for_pipeline("conjugation")
        conj_data_providers = conj_providers["data"]

        assert "conjugation_data" in conj_data_providers
        assert "shared_data" in conj_data_providers  # Wildcard access
        assert "vocab_data" not in conj_data_providers

    def test_read_only_provider_write_operations(self, tmp_path):
        """Test read-only provider behavior in realistic scenario."""
        # Create source data directory and files
        source_dir = tmp_path / "sources"
        source_dir.mkdir()

        dict_file = source_dir / "spanish_dict.json"
        dict_file.write_text('{"hola": "hello", "mundo": "world"}')

        config_content = {
            "providers": {
                "data": {
                    "source_dict": {
                        "type": "json",
                        "base_path": str(source_dir),
                        "files": ["spanish_dict"],
                        "read_only": True,
                        "pipelines": ["*"],
                    }
                },
                "sync": {"anki": {"type": "anki", "pipelines": ["*"]}},
            }
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_content))

        config = Config.load(str(config_path))
        registry = ProviderRegistry.from_config(config)

        provider = registry.get_data_provider("source_dict")

        # Should be able to read existing data
        data = provider.load_data("spanish_dict")
        assert data == {"hola": "hello", "mundo": "world"}

        # Should NOT be able to write to read-only provider
        with pytest.raises(PermissionError, match="provider is read-only"):
            provider.save_data("spanish_dict", {"nuevo": "new"})

    def test_file_specific_access_control(self, tmp_path):
        """Test that file-specific access control works correctly."""
        config_content = {
            "providers": {
                "data": {
                    "vocab_files": {
                        "type": "json",
                        "base_path": str(tmp_path),
                        "files": ["vocabulary", "word_progress"],
                        "read_only": False,
                        "pipelines": ["*"],
                    },
                    "config_files": {
                        "type": "json",
                        "base_path": str(tmp_path),
                        "files": ["user_config", "app_settings"],
                        "read_only": False,
                        "pipelines": ["*"],
                    },
                },
                "sync": {"anki": {"type": "anki", "pipelines": ["*"]}},
            }
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_content))

        config = Config.load(str(config_path))
        registry = ProviderRegistry.from_config(config)

        vocab_provider = registry.get_data_provider("vocab_files")
        config_provider = registry.get_data_provider("config_files")

        # Vocab provider should only handle vocab files
        vocab_provider.save_data("vocabulary", {"word": "casa"})
        vocab_provider.save_data("word_progress", {"learned": 50})

        with pytest.raises(ValueError, match="not managed by this provider"):
            vocab_provider.save_data("user_config", {"theme": "dark"})

        # Config provider should only handle config files
        config_provider.save_data("user_config", {"theme": "dark"})
        config_provider.save_data("app_settings", {"language": "es"})

        with pytest.raises(ValueError, match="not managed by this provider"):
            config_provider.save_data("vocabulary", {"word": "casa"})

    def test_backwards_compatibility_with_phase1_config(self, tmp_path):
        """Test that Phase 1 configurations still work without Phase 2 fields."""
        config_content = {
            "providers": {
                "data": {
                    "default": {
                        "type": "json",
                        "base_path": str(tmp_path),
                        "pipelines": ["*"],
                        # No "files" or "read_only" fields - should use defaults
                    }
                },
                "sync": {"anki": {"type": "anki", "pipelines": ["*"]}},
            }
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_content))

        config = Config.load(str(config_path))
        registry = ProviderRegistry.from_config(config)

        provider = registry.get_data_provider("default")
        assert provider is not None

        # Should have default values
        assert provider.is_read_only is False
        assert provider.managed_files == []

        # Should work with any file (no restrictions)
        test_data = {"key": "value"}
        assert provider.save_data("any_file", test_data) is True
        assert provider.load_data("any_file") == test_data

    def test_config_validation_missing_pipelines_field(self, tmp_path):
        """Test that configurations missing pipelines field are rejected."""
        config_content = {
            "providers": {
                "data": {
                    "invalid_provider": {
                        "type": "json",
                        "base_path": str(tmp_path),
                        "files": ["some_file"],
                        "read_only": False,
                        # Missing required "pipelines" field
                    }
                },
                "sync": {"anki": {"type": "anki", "pipelines": ["*"]}},
            }
        }

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(config_content))

        config = Config.load(str(config_path))

        with pytest.raises(
            ValueError,
            match="Provider 'invalid_provider'.*missing required 'pipelines' field",
        ):
            ProviderRegistry.from_config(config)
