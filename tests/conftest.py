#!/usr/bin/env python3
"""
Shared test fixtures and mocks
"""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


@pytest.fixture(scope="session", autouse=True)
def suppress_cli_output():
    """Global fixture to suppress CLI output and logging."""
    import os
    import subprocess
    from unittest.mock import patch

    original_run = subprocess.run

    def patched_run(*args, **kwargs):
        # Check if this is a CLI command
        if (
            args
            and isinstance(args[0], list)
            and len(args[0]) >= 3
            and args[0][2] == "src.cli.pipeline_runner"
        ):
            # Add environment variables to suppress all logging
            env = kwargs.get("env", os.environ.copy())
            env["FLUENT_FOREVER_LOG_LEVEL"] = "CRITICAL"  # Even higher than ERROR
            env["FLUENT_FOREVER_LOG_TO_FILE"] = "false"  # Disable file logging
            kwargs["env"] = env

        return original_run(*args, **kwargs)

    # Mock CLI output functions to suppress print statements
    with patch("subprocess.run", patched_run), patch(
        "src.cli.utils.output.print_success"
    ), patch("src.cli.utils.output.print_error"), patch(
        "src.cli.utils.output.print_warning"
    ), patch("src.cli.utils.output.print_info"):
        yield


@pytest.fixture
def mock_config():
    """Mock config.json data"""
    return {
        "apis": {"anki": {"url": "http://localhost:8765"}},
        "validation": {
            "vocabulary_schema": {
                "metadata": {
                    "required_fields": [
                        "created",
                        "last_updated",
                        "total_words",
                        "total_cards",
                    ]
                },
                "word_entry": {"required_fields": ["word", "meanings"]},
                "meaning_entry": {"required_fields": ["CardID", "SpanishWord"]},
            },
            "field_patterns": {"SpanishWord": "^[a-záéíóúñü]+$"},
            "constraints": {
                "min_lengths": {"SpanishWord": 1},
                "max_cards_per_word": 10,
            },
        },
    }


@pytest.fixture
def mock_vocabulary():
    """Mock vocabulary.json data"""
    return {
        "metadata": {
            "created": "2024-01-01",
            "last_updated": "2024-01-02",
            "total_words": 2,
            "total_cards": 3,
        },
        "words": {
            "test": {
                "meanings": [
                    {
                        "CardID": "test_meaning1",
                        "SpanishWord": "test",
                        "ImageFile": "test_image.png",
                        "WordAudio": "[sound:test.mp3]",
                    }
                ]
            }
        },
    }


@pytest.fixture
def mock_anki_client():
    """Mock AnkiClient class"""
    mock = Mock()
    mock.test_connection.return_value = True
    mock.get_media_files.return_value = Mock(success=True, data=[])
    mock.get_deck_cards.return_value = Mock(success=True, data={})
    return mock


@pytest.fixture
def local_media_files():
    """Mock local media file sets"""
    return (
        {"test_image.png", "other_image.png"},  # images
        {"test.mp3", "other.mp3"},  # audio
    )


@pytest.fixture
def anki_media_files():
    """Mock Anki media file sets"""
    return (
        {"test_image.png", "anki_only_image.png"},  # images
        {"test.mp3", "anki_only.mp3"},  # audio
    )


@pytest.fixture
def mock_conjugations():
    """Mock conjugations.json data"""
    return {
        "conjugations": {
            "hablar_present_yo": {
                "CardID": "hablar_present_yo",
                "Front": "hablo",
                "Back": "hablar",
                "Add Reverse": "1",
                "Sentence": "Yo _____ español todos los días.",
                "Extra": "Present tense, first person singular",
                "Picture": "",
            },
            "comer_preterite_el": {
                "CardID": "comer_preterite_el",
                "Front": "comió",
                "Back": "comer",
                "Add Reverse": "1",
                "Sentence": "Él _____ una manzana ayer.",
                "Extra": "Preterite tense, third person singular",
                "Picture": "",
            },
        },
        "metadata": {
            "created": "2024-01-01T00:00:00Z",
            "description": "Spanish verb conjugation practice cards",
            "total_cards": 2,
        },
    }


@pytest.fixture
def setup_test_templates(tmp_path):
    """Setup test template directories for multiple card types"""
    # Fluent Forever templates
    ff_dir = tmp_path / "templates" / "anki" / "Fluent_Forever"
    ff_templates_dir = ff_dir / "templates"
    ff_templates_dir.mkdir(parents=True)

    # Create manifest
    ff_manifest = {
        "note_type": "Fluent Forever",
        "templates": [
            {
                "name": "Test Template",
                "front": "templates/Test_Front.html",
                "back": "templates/Test_Back.html",
            }
        ],
        "css": "styling.css",
        "fields": ["CardID", "SpanishWord", "ExampleSentence"],
    }
    (ff_dir / "manifest.json").write_text(json.dumps(ff_manifest))
    (ff_dir / "styling.css").write_text(".card { color: white; }")
    (ff_templates_dir / "Test_Front.html").write_text("<div>{{SpanishWord}}</div>")
    (ff_templates_dir / "Test_Back.html").write_text("<div>{{ExampleSentence}}</div>")

    # Conjugation templates
    conj_dir = tmp_path / "templates" / "anki" / "Conjugation"
    conj_templates_dir = conj_dir / "templates"
    conj_templates_dir.mkdir(parents=True)

    # Create manifest
    conj_manifest = {
        "note_type": "Conjugation",
        "templates": [
            {
                "name": "Card 1",
                "front": "templates/Card1_Front.html",
                "back": "templates/Card1_Back.html",
            }
        ],
        "css": "styling.css",
        "fields": ["Front", "Back", "Sentence"],
    }
    (conj_dir / "manifest.json").write_text(json.dumps(conj_manifest))
    (conj_dir / "styling.css").write_text(".card { color: white; }")
    (conj_templates_dir / "Card1_Front.html").write_text("<div>{{Front}}</div>")
    (conj_templates_dir / "Card1_Back.html").write_text("<div>{{Back}}</div>")

    return tmp_path


# Validation Gate Fixtures


@pytest.fixture
def mock_external_apis():
    """Mock external APIs for validation gates"""
    with patch("apis.openai_client.OpenAIClient") as mock_openai, patch(
        "apis.runware_client.RunwareClient"
    ) as mock_runware, patch("apis.forvo_client.ForvoClient") as mock_forvo, patch(
        "apis.anki_client.AnkiClient"
    ) as mock_anki:
        # Configure OpenAI mock
        mock_openai.return_value.generate_image.return_value = {
            "success": True,
            "image_url": "https://example.com/image.png",
        }

        # Configure Runware mock
        mock_runware.return_value.generate_image.return_value = {
            "success": True,
            "image_url": "https://example.com/image.png",
        }

        # Configure Forvo mock
        mock_forvo.return_value.get_pronunciations.return_value = {
            "success": True,
            "pronunciations": [{"url": "https://example.com/audio.mp3"}],
        }

        # Configure Anki mock
        mock_anki.return_value.test_connection.return_value = True
        mock_anki.return_value.get_deck_cards.return_value = Mock(success=True, data={})

        yield {
            "openai": mock_openai.return_value,
            "runware": mock_runware.return_value,
            "forvo": mock_forvo.return_value,
            "anki": mock_anki.return_value,
        }


@pytest.fixture
def temp_workspace():
    """Create temporary workspace for testing"""
    import shutil
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create required directories
        (temp_path / "src").mkdir()
        (temp_path / "staging").mkdir()
        (temp_path / "media").mkdir()
        (temp_path / "media" / "images").mkdir()
        (temp_path / "media" / "audio").mkdir()

        # Copy source code if needed for integration tests
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"
        if src_dir.exists():
            shutil.copytree(src_dir, temp_path / "src", dirs_exist_ok=True)

        # Create minimal test files
        create_test_config(temp_path)
        create_test_vocabulary(temp_path)

        yield temp_path


@pytest.fixture(autouse=True)
def isolate_media_downloads(tmp_path, monkeypatch):
    """Global fixture to isolate all media downloads to temp directories"""
    # Create temp media directories
    temp_media = tmp_path / "test_media"
    temp_images = temp_media / "images"
    temp_audio = temp_media / "audio"

    temp_media.mkdir()
    temp_images.mkdir()
    temp_audio.mkdir()

    # Patch all media provider download methods to use temp directories
    def mock_download_image_openai(self, url, output_path=None):
        if output_path is None:
            import re

            safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", str(hash(url))[:8])
            output_path = temp_images / f"openai_{safe_name}.jpg"
        else:
            # Redirect to temp directory while preserving filename
            output_path = temp_images / output_path.name

        # Create mock file with sufficient size for validation
        output_path.touch()
        output_path.write_bytes(b"mock_image_data" * 1000)  # 15KB mock file
        return output_path

    def mock_download_image_runware(self, url, output_path=None):
        if output_path is None:
            import hashlib

            prompt_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            output_path = temp_images / f"runware_{prompt_hash}.png"
        else:
            # Redirect to temp directory while preserving filename
            output_path = temp_images / output_path.name

        # Create mock file with sufficient size for validation
        output_path.touch()
        output_path.write_bytes(b"mock_image_data" * 1000)  # 15KB mock file
        return output_path

    # Mock validation to always pass for downloaded files
    def mock_validate_file(self, file_path):
        return file_path.exists() and file_path.stat().st_size > 100

    # Apply patches for both import patterns (src. and direct imports)
    with patch(
        "src.providers.image.openai_provider.OpenAIProvider._download_image",
        mock_download_image_openai,
    ), patch(
        "src.providers.image.runware_provider.RunwareProvider._download_image",
        mock_download_image_runware,
    ), patch(
        "providers.image.openai_provider.OpenAIProvider._download_image",
        mock_download_image_openai,
    ), patch(
        "providers.image.runware_provider.RunwareProvider._download_image",
        mock_download_image_runware,
    ), patch(
        "src.providers.image.runware_provider.RunwareProvider._validate_downloaded_file",
        mock_validate_file,
    ), patch(
        "providers.image.runware_provider.RunwareProvider._validate_downloaded_file",
        mock_validate_file,
    ):
        yield temp_media


def create_test_config(temp_path: Path):
    """Create minimal test config.json"""
    config = {
        "apis": {
            "base": {"user_agent": "test", "timeout": 30, "max_retries": 3},
            "anki": {
                "url": "http://localhost:8765",
                "deck_name": "Test",
                "note_type": "Fluent Forever",
            },
        },
        "validation": {
            "vocabulary_schema": {
                "metadata": {
                    "required_fields": [
                        "created",
                        "last_updated",
                        "total_words",
                        "total_cards",
                        "source",
                    ]
                },
                "word_entry": {
                    "required_fields": [
                        "word",
                        "processed_date",
                        "meanings",
                        "cards_created",
                    ]
                },
                "meaning_entry": {
                    "required_fields": [
                        "CardID",
                        "SpanishWord",
                        "IPA",
                        "MeaningContext",
                        "MonolingualDef",
                        "ExampleSentence",
                        "GappedSentence",
                        "ImageFile",
                        "WordAudio",
                        "WordAudioAlt",
                        "UsageNote",
                        "MeaningID",
                        "prompt",
                    ]
                },
            },
            "field_patterns": {
                "CardID": "^[a-záéíóúñü_0-9]+$",
                "SpanishWord": "^[a-záéíóúñü]+$",
                "IPA": "^\\[.*\\]$|^/.*/$",
            },
        },
        "paths": {"media_folder": "media", "vocabulary_db": "vocabulary.json"},
        "media_generation": {"max_new_items": 5},
    }

    with open(temp_path / "config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def create_test_vocabulary(temp_path: Path):
    """Create minimal test vocabulary.json"""
    vocabulary = {
        "metadata": {
            "created": "2025-01-01",
            "last_updated": "2025-01-01T00:00:00.000000",
            "total_words": 0,
            "total_cards": 0,
            "source": "test",
        },
        "skipped_words": [],
        "words": {},
    }

    with open(temp_path / "vocabulary.json", "w", encoding="utf-8") as f:
        json.dump(vocabulary, f, ensure_ascii=False, indent=2)
