#!/usr/bin/env python3
"""
Session 4 Validation Gate: Data Provider System

Tests the contract for data source abstraction.
These tests define how data providers should abstract
access to vocabulary, configuration, and other data sources.

CONTRACT BEING TESTED:
- Data providers abstract file system access
- Providers handle different data formats consistently
- Data validation and schema enforcement
- Caching and performance optimization
- Error handling for data access
"""

import pytest
from typing import Dict, Any, List, Optional
from pathlib import Path
from tests.e2e.conftest import MockProvider


class TestDataProviderContract:
    """Test data provider basic contracts"""
    
    def test_vocabulary_data_provider(self):
        """Contract: Vocabulary data provider loads and validates vocabulary data"""
        provider = MockVocabularyDataProvider()
        
        # Should load vocabulary data
        data = provider.load_vocabulary_data("/test/path/vocabulary.json")
        
        assert isinstance(data, dict)
        assert "metadata" in data
        assert "words" in data
        assert data["metadata"]["total_words"] > 0
        
        # Should validate data structure
        assert provider.validate_vocabulary_structure(data) is True
    
    def test_configuration_data_provider(self):
        """Contract: Configuration provider loads and validates configuration"""
        provider = MockConfigurationDataProvider()
        
        # Should load configuration
        config = provider.load_configuration("/test/path/config.json")
        
        assert isinstance(config, dict)
        assert "apis" in config
        assert "paths" in config
        
        # Should validate configuration
        assert provider.validate_configuration(config) is True
    
    def test_template_data_provider(self):
        """Contract: Template provider loads template data"""
        provider = MockTemplateDataProvider()
        
        # Should load template manifest
        manifest = provider.load_template_manifest("/test/templates/Fluent_Forever")
        
        assert isinstance(manifest, dict)
        assert "note_type" in manifest
        assert "fields" in manifest
        assert "templates" in manifest
        
        # Should load template files
        template_content = provider.load_template_file(
            "/test/templates/Fluent_Forever/templates/Front.html"
        )
        assert isinstance(template_content, str)
        assert len(template_content) > 0
    
    def test_staging_data_provider(self):
        """Contract: Staging provider manages staging files"""
        provider = MockStagingDataProvider()
        
        # Should create staging file
        staging_data = {
            "words": ["haber", "casa"],
            "meanings": [],
            "metadata": {"created": "2024-01-01T00:00:00Z"}
        }
        
        staging_path = provider.create_staging_file(staging_data)
        assert staging_path is not None
        
        # Should load staging file
        loaded_data = provider.load_staging_file(staging_path)
        assert loaded_data["words"] == staging_data["words"]
        
        # Should list staging files
        staging_files = provider.list_staging_files()
        assert len(staging_files) > 0
    
    def test_media_data_provider(self):
        """Contract: Media provider manages media file metadata"""
        provider = MockMediaDataProvider()
        
        # Should track media files
        media_info = provider.get_media_info("test_image.png")
        assert media_info is not None
        assert "file_path" in media_info
        assert "created" in media_info
        
        # Should list media files
        media_files = provider.list_media_files("images")
        assert isinstance(media_files, list)
        
        # Should validate media files exist
        assert provider.media_file_exists("test_image.png") is True
        assert provider.media_file_exists("nonexistent.png") is False


class TestDataProviderValidation:
    """Test data validation contracts"""
    
    def test_vocabulary_schema_validation(self):
        """Contract: Vocabulary data is validated against schema"""
        provider = MockVocabularyDataProvider()
        
        # Valid vocabulary structure should pass
        valid_vocab = {
            "metadata": {"total_words": 1, "total_cards": 1},
            "words": {
                "casa": {
                    "word": "casa",
                    "meanings": [
                        {
                            "CardID": "casa_house",
                            "SpanishWord": "la casa",
                            "IPA": "[ˈka.sa]"
                        }
                    ]
                }
            }
        }
        
        assert provider.validate_vocabulary_structure(valid_vocab) is True
        
        # Invalid structure should fail
        invalid_vocab = {
            "words": {}  # Missing metadata
        }
        
        assert provider.validate_vocabulary_structure(invalid_vocab) is False
    
    def test_configuration_validation(self):
        """Contract: Configuration is validated for completeness"""
        provider = MockConfigurationDataProvider()
        
        # Valid configuration should pass
        valid_config = {
            "apis": {"openai": {"api_key": "test", "enabled": True}},
            "paths": {"vocabulary_db": "vocabulary.json"},
            "validation": {"vocabulary_schema": {}}
        }
        
        assert provider.validate_configuration(valid_config) is True
        
        # Missing required sections should fail
        invalid_config = {"paths": {}}  # Missing apis
        
        assert provider.validate_configuration(invalid_config) is False
    
    def test_field_validation(self):
        """Contract: Individual fields are validated"""
        provider = MockVocabularyDataProvider()
        
        # Valid card fields
        valid_meaning = {
            "CardID": "casa_house",
            "SpanishWord": "la casa",
            "IPA": "[ˈka.sa]",
            "MeaningContext": "dwelling",
            "MonolingualDef": "Edificio para habitar"
        }
        
        validation_result = provider.validate_meaning_fields(valid_meaning)
        assert validation_result["valid"] is True
        assert len(validation_result["errors"]) == 0
        
        # Invalid fields should be caught
        invalid_meaning = {
            "CardID": "",  # Empty CardID
            "SpanishWord": "casa",  # Missing article
            "IPA": "ka.sa"  # Missing brackets
        }
        
        validation_result = provider.validate_meaning_fields(invalid_meaning)
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0
    
    def test_data_integrity_checks(self):
        """Contract: Data integrity is checked across relationships"""
        provider = MockVocabularyDataProvider()
        
        vocab_data = {
            "metadata": {"total_words": 2, "total_cards": 3},
            "words": {
                "casa": {
                    "word": "casa",
                    "cards_created": 1,
                    "meanings": [{"CardID": "casa_house"}]
                },
                "haber": {
                    "word": "haber", 
                    "cards_created": 2,
                    "meanings": [{"CardID": "haber_aux"}, {"CardID": "haber_exist"}]
                }
            }
        }
        
        integrity_result = provider.check_data_integrity(vocab_data)
        assert integrity_result["valid"] is True
        
        # Test integrity violation
        vocab_data["metadata"]["total_cards"] = 5  # Incorrect count
        
        integrity_result = provider.check_data_integrity(vocab_data)
        assert integrity_result["valid"] is False
        assert "card count mismatch" in integrity_result["errors"][0].lower()


class TestDataProviderPerformance:
    """Test data provider performance contracts"""
    
    def test_data_caching(self):
        """Contract: Frequently accessed data is cached"""
        provider = MockVocabularyDataProvider()
        
        # First load should read from source
        data1 = provider.load_vocabulary_data("/test/vocabulary.json")
        assert provider.cache_hits == 0
        assert provider.cache_misses == 1
        
        # Second load should use cache
        data2 = provider.load_vocabulary_data("/test/vocabulary.json")
        assert data1 == data2  # Same data
        assert provider.cache_hits == 1
        assert provider.cache_misses == 1
    
    def test_cache_invalidation(self):
        """Contract: Cache is invalidated when data changes"""
        provider = MockVocabularyDataProvider()
        
        # Load data
        provider.load_vocabulary_data("/test/vocabulary.json")
        
        # Invalidate cache
        provider.invalidate_cache("/test/vocabulary.json")
        
        # Next load should miss cache
        provider.load_vocabulary_data("/test/vocabulary.json")
        assert provider.cache_misses == 2
    
    def test_lazy_loading(self):
        """Contract: Large data sets support lazy loading"""
        provider = MockVocabularyDataProvider()
        
        # Should support loading specific words only
        word_data = provider.load_word_data("casa")
        assert word_data["word"] == "casa"
        assert "meanings" in word_data
        
        # Should support pagination
        word_batch = provider.load_words_batch(offset=0, limit=10)
        assert len(word_batch) <= 10


class TestDataProviderErrorHandling:
    """Test error handling in data providers"""
    
    def test_file_not_found_handling(self):
        """Contract: Missing files are handled gracefully"""
        provider = MockVocabularyDataProvider()
        
        with pytest.raises(FileNotFoundError):
            provider.load_vocabulary_data("/nonexistent/file.json")
    
    def test_invalid_json_handling(self):
        """Contract: Invalid JSON is handled gracefully"""
        provider = MockVocabularyDataProvider()
        
        with pytest.raises(ValueError, match="Invalid JSON"):
            provider.load_vocabulary_data("/test/invalid.json")
    
    def test_permission_error_handling(self):
        """Contract: Permission errors are handled gracefully"""
        provider = MockVocabularyDataProvider()
        
        with pytest.raises(PermissionError):
            provider.load_vocabulary_data("/restricted/file.json")
    
    def test_corrupted_data_handling(self):
        """Contract: Corrupted data is detected and reported"""
        provider = MockVocabularyDataProvider()
        
        with pytest.raises(DataCorruptionError):
            provider.load_vocabulary_data("/test/corrupted.json")


# Mock Data Provider Implementations
class MockVocabularyDataProvider(MockProvider):
    """Mock vocabulary data provider"""
    
    def __init__(self):
        super().__init__("vocabulary_provider")
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Mock vocabulary data
        self._mock_data = {
            "metadata": {"total_words": 2, "total_cards": 3, "created": "2024-01-01"},
            "words": {
                "casa": {
                    "word": "casa",
                    "cards_created": 1,
                    "meanings": [
                        {
                            "CardID": "casa_house",
                            "SpanishWord": "la casa",
                            "IPA": "[ˈka.sa]",
                            "MeaningContext": "dwelling",
                            "MonolingualDef": "Edificio para habitar"
                        }
                    ]
                },
                "haber": {
                    "word": "haber",
                    "cards_created": 2,
                    "meanings": [
                        {
                            "CardID": "haber_aux",
                            "SpanishWord": "haber",
                            "IPA": "[a.βeɾ]",
                            "MeaningContext": "auxiliary",
                            "MonolingualDef": "Verbo auxiliar"
                        },
                        {
                            "CardID": "haber_exist",
                            "SpanishWord": "haber",
                            "IPA": "[a.βeɾ]",
                            "MeaningContext": "existence",
                            "MonolingualDef": "Expresar existencia"
                        }
                    ]
                }
            }
        }
    
    def load_vocabulary_data(self, file_path: str) -> Dict[str, Any]:
        """Load vocabulary data with caching"""
        if "nonexistent" in file_path:
            raise FileNotFoundError(f"File not found: {file_path}")
        if "invalid.json" in file_path:
            raise ValueError("Invalid JSON format")
        if "restricted" in file_path:
            raise PermissionError("Permission denied")
        if "corrupted.json" in file_path:
            raise DataCorruptionError("Data corruption detected")
        
        if file_path in self.cache:
            self.cache_hits += 1
            return self.cache[file_path]
        
        self.cache_misses += 1
        data = self._mock_data.copy()
        self.cache[file_path] = data
        return data
    
    def validate_vocabulary_structure(self, data: Dict[str, Any]) -> bool:
        """Validate vocabulary data structure"""
        if "metadata" not in data or "words" not in data:
            return False
        return True
    
    def validate_meaning_fields(self, meaning: Dict[str, Any]) -> Dict[str, Any]:
        """Validate individual meaning fields"""
        errors = []
        
        if not meaning.get("CardID"):
            errors.append("CardID cannot be empty")
        
        spanish_word = meaning.get("SpanishWord", "")
        if "casa" in spanish_word and not spanish_word.startswith("la "):
            errors.append("Casa should include article 'la'")
        
        ipa = meaning.get("IPA", "")
        if ipa and not (ipa.startswith("[") and ipa.endswith("]")):
            errors.append("IPA should be in brackets")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def check_data_integrity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check data integrity across relationships"""
        errors = []
        
        # Check card count consistency
        expected_cards = data["metadata"]["total_cards"]
        actual_cards = sum(len(word_data["meanings"]) for word_data in data["words"].values())
        
        if expected_cards != actual_cards:
            errors.append(f"Card count mismatch: expected {expected_cards}, found {actual_cards}")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def invalidate_cache(self, file_path: str):
        """Invalidate cache for specific file"""
        if file_path in self.cache:
            del self.cache[file_path]
    
    def load_word_data(self, word: str) -> Dict[str, Any]:
        """Load data for specific word"""
        return self._mock_data["words"].get(word, {})
    
    def load_words_batch(self, offset: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Load batch of words with pagination"""
        words = list(self._mock_data["words"].values())
        return words[offset:offset + limit]


class MockConfigurationDataProvider(MockProvider):
    """Mock configuration data provider"""
    
    def load_configuration(self, file_path: str) -> Dict[str, Any]:
        """Load configuration data"""
        return {
            "apis": {
                "openai": {"api_key": "test", "enabled": True},
                "anki": {"url": "http://localhost:8765"}
            },
            "paths": {
                "vocabulary_db": "vocabulary.json",
                "media_folder": "media"
            },
            "validation": {
                "vocabulary_schema": {}
            }
        }
    
    def validate_configuration(self, config: Dict[str, Any]) -> bool:
        """Validate configuration completeness"""
        required_sections = ["apis", "paths"]
        return all(section in config for section in required_sections)


class MockTemplateDataProvider(MockProvider):
    """Mock template data provider"""
    
    def load_template_manifest(self, template_dir: str) -> Dict[str, Any]:
        """Load template manifest"""
        return {
            "note_type": "Fluent Forever",
            "fields": ["SpanishWord", "MonolingualDef", "ExampleSentence"],
            "templates": [
                {"name": "Card", "front": "Front.html", "back": "Back.html"}
            ]
        }
    
    def load_template_file(self, template_path: str) -> str:
        """Load template file content"""
        if "Front.html" in template_path:
            return "{{SpanishWord}}"
        elif "Back.html" in template_path:
            return "{{FrontSide}}<hr>{{MonolingualDef}}"
        return ""


class MockStagingDataProvider(MockProvider):
    """Mock staging data provider"""
    
    def __init__(self):
        super().__init__("staging_provider")
        self._staging_files = {}
    
    def create_staging_file(self, data: Dict[str, Any]) -> str:
        """Create staging file and return path"""
        staging_path = f"/staging/claude_batch_test.json"
        self._staging_files[staging_path] = data
        return staging_path
    
    def load_staging_file(self, file_path: str) -> Dict[str, Any]:
        """Load staging file"""
        return self._staging_files.get(file_path, {})
    
    def list_staging_files(self) -> List[str]:
        """List all staging files"""
        return list(self._staging_files.keys())


class MockMediaDataProvider(MockProvider):
    """Mock media data provider"""
    
    def __init__(self):
        super().__init__("media_provider")
        self._media_files = {
            "test_image.png": {
                "file_path": "/media/images/test_image.png",
                "created": "2024-01-01T00:00:00Z",
                "size": 1024
            }
        }
    
    def get_media_info(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get media file information"""
        return self._media_files.get(filename)
    
    def list_media_files(self, media_type: str) -> List[str]:
        """List media files by type"""
        return list(self._media_files.keys())
    
    def media_file_exists(self, filename: str) -> bool:
        """Check if media file exists"""
        return filename in self._media_files


# Custom Exception for Testing
class DataCorruptionError(Exception):
    """Data corruption detected"""
    pass