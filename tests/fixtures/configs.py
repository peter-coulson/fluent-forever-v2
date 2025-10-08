"""Configuration fixtures for E2E testing."""

import json
import tempfile
from pathlib import Path
from typing import Any


def create_base_config() -> dict[str, Any]:
    """Create minimal valid configuration."""
    return {
        "providers": {
            "data": {
                "test_data": {
                    "type": "json",
                    "pipelines": ["test_pipeline"],
                    "base_path": ".",
                    "read_only": False,
                }
            },
            "audio": {
                "test_audio": {
                    "type": "forvo",
                    "pipelines": ["test_pipeline"],
                    "api_key": "${FORVO_API_KEY:test_key}",
                    "country_priorities": ["ES", "MX", "AR"],
                }
            },
            "image": {
                "test_image": {
                    "type": "openai",
                    "pipelines": ["test_pipeline"],
                    "api_key": "${OPENAI_API_KEY:test_key}",
                    "model": "dall-e-3",
                }
            },
            "sync": {
                "test_sync": {
                    "type": "anki",
                    "pipelines": ["test_pipeline"],
                    "anki_connect_url": "http://localhost:8765",
                }
            },
        },
        "system": {"log_level": "INFO", "max_retries": 3},
    }


def create_complex_config() -> dict[str, Any]:
    """Create complex multi-provider, multi-pipeline configuration."""
    return {
        "providers": {
            "data": {
                "vocabulary_data": {
                    "type": "json",
                    "pipelines": ["vocabulary"],
                    "base_path": "data",
                    "files": ["vocabulary.json"],
                    "read_only": False,
                },
                "conjugation_data": {
                    "type": "json",
                    "pipelines": ["conjugation"],
                    "base_path": "data",
                    "files": ["conjugations.json"],
                    "read_only": True,
                },
                "shared_data": {
                    "type": "json",
                    "pipelines": ["*"],
                    "base_path": "shared",
                    "read_only": False,
                },
            },
            "audio": {
                "primary_audio": {
                    "type": "forvo",
                    "pipelines": ["vocabulary", "conjugation"],
                    "api_key": "${FORVO_API_KEY:test_key}",
                    "language": "spanish",
                    "country_priorities": ["ES", "MX", "AR"],
                },
                "backup_audio": {
                    "type": "forvo",
                    "pipelines": ["vocabulary"],
                    "api_key": "${BACKUP_FORVO_KEY:backup_key}",
                    "language": "spanish",
                    "country_priorities": ["ES", "MX", "AR"],
                },
            },
            "image": {
                "openai_images": {
                    "type": "openai",
                    "pipelines": ["vocabulary"],
                    "api_key": "${OPENAI_API_KEY:test_key}",
                    "model": "dall-e-3",
                },
                "runware_images": {
                    "type": "runware",
                    "pipelines": ["vocabulary"],
                    "api_key": "${RUNWARE_API_KEY:test_key}",
                },
            },
            "sync": {
                "main_anki": {
                    "type": "anki",
                    "pipelines": ["*"],
                    "anki_connect_url": "http://localhost:8765",
                    "deck_name": "Spanish Learning",
                }
            },
        },
        "system": {
            "log_level": "DEBUG",
            "max_retries": 5,
            "timeout": 30,
            "cache_enabled": True,
        },
    }


def create_env_var_config() -> dict[str, Any]:
    """Create configuration with environment variables for testing substitution."""
    return {
        "providers": {
            "data": {
                "test_data": {
                    "type": "json",
                    "pipelines": ["test_pipeline"],
                    "base_path": "${DATA_PATH:./data}",
                    "read_only": "${READ_ONLY:false}",
                }
            },
            "audio": {
                "forvo_provider": {
                    "type": "forvo",
                    "pipelines": ["${PIPELINE_NAME:test_pipeline}"],
                    "api_key": "${FORVO_API_KEY}",
                    "language": "${LANGUAGE:spanish}",
                    "country_priorities": ["ES", "MX", "AR"],
                    "fallback_url": "${FALLBACK_URL:http://fallback.com}",
                }
            },
        },
        "system": {
            "log_level": "${LOG_LEVEL:INFO}",
            "debug_mode": "${DEBUG:false}",
            "api_timeout": "${API_TIMEOUT:30}",
        },
    }


def create_invalid_config() -> dict[str, Any]:
    """Create configuration with various errors for testing validation."""
    return {
        "providers": {
            "data": {
                "missing_pipelines": {
                    "type": "json",
                    "base_path": ".",
                    # Missing required 'pipelines' field
                }
            },
            "audio": {
                "unsupported_type": {
                    "type": "unsupported_audio_provider",
                    "pipelines": ["test_pipeline"],
                }
            },
            "image": {
                "invalid_image": {
                    "type": "invalid_image_provider",
                    "pipelines": ["test_pipeline"],
                }
            },
        }
    }


def create_file_conflict_config() -> dict[str, Any]:
    """Create configuration with file conflicts for testing validation."""
    return {
        "providers": {
            "data": {
                "provider1": {
                    "type": "json",
                    "pipelines": ["pipeline1"],
                    "files": ["shared_file.json", "provider1_file.json"],
                    "base_path": ".",
                },
                "provider2": {
                    "type": "json",
                    "pipelines": ["pipeline2"],
                    "files": ["shared_file.json", "provider2_file.json"],  # Conflict!
                    "base_path": ".",
                },
            }
        }
    }


def create_old_format_config() -> dict[str, Any]:
    """Create configuration in old format for testing migration errors."""
    return {
        "providers": {
            "audio": {
                "type": "forvo",  # Old format - should be under a named provider
                "pipelines": ["test_pipeline"],
            }
        }
    }


def create_config_file(config_data: dict[str, Any]) -> Path:
    """Create a temporary configuration file with given data."""
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump(config_data, temp_file, indent=2)
    temp_file.close()
    return Path(temp_file.name)


def create_invalid_json_file() -> Path:
    """Create a file with invalid JSON for testing error handling."""
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    temp_file.write('{"invalid": json syntax}')  # Missing quotes around 'json'
    temp_file.close()
    return Path(temp_file.name)


class ConfigFixture:
    """Helper class for managing test configuration files."""

    def __init__(self, config_data: dict[str, Any]):
        self.config_data = config_data
        self.config_file: Path | None = None

    def __enter__(self) -> Path:
        """Create temporary config file."""
        self.config_file = create_config_file(self.config_data)
        return self.config_file

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Clean up temporary config file."""
        if self.config_file and self.config_file.exists():
            self.config_file.unlink()


def get_test_config_variants() -> dict[str, dict[str, Any]]:
    """Get all test configuration variants."""
    return {
        "base": create_base_config(),
        "complex": create_complex_config(),
        "env_vars": create_env_var_config(),
        "invalid": create_invalid_config(),
        "file_conflicts": create_file_conflict_config(),
        "old_format": create_old_format_config(),
    }


def create_minimal_working_config() -> dict[str, Any]:
    """Create the most minimal configuration that should work."""
    return {
        "providers": {
            "data": {"test_data": {"type": "json", "pipelines": ["test_pipeline"]}}
        }
    }


def create_empty_config() -> dict[str, Any]:
    """Create empty configuration for testing defaults."""
    return {}


def create_no_providers_config() -> dict[str, Any]:
    """Create configuration without providers section."""
    return {"system": {"log_level": "INFO"}}
