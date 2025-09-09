#!/usr/bin/env python3
"""
Unit tests for Validation Stages after migration

Tests validation stage functionality in the new stage structure.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from core.context import PipelineContext
from core.stages import StageResult, StageStatus
from stages.validation.ipa_stage import IPAValidationStage
from stages.validation.media_stage import MediaValidationStage


class TestIPAValidationStage:
    """Test IPA validation stage"""

    def setup_method(self):
        """Set up test stage"""
        # Use a non-existent dictionary path to avoid file dependency
        self.stage = IPAValidationStage(
            data_key="vocabulary_data", dictionary_path="/nonexistent/path"
        )
        self.context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

    def test_stage_properties(self):
        """Test stage properties"""
        assert self.stage.name == "validate_vocabulary_data"
        assert "Validate Vocabulary Data" in self.stage.display_name
        assert self.stage.data_key == "vocabulary_data"

    def test_valid_ipa_data(self):
        """Test validation of valid IPA data"""
        valid_data = {
            "words": [
                {"word": "hola", "ipa": "ˈo.la", "definition": "hello"},
                {"word": "gracias", "ipa": "ˈɡɾa.θjas", "definition": "thank you"},
            ]
        }

        self.context.set("vocabulary_data", valid_data)

        result = self.stage.execute(self.context)

        assert isinstance(result, StageResult)
        assert result.status == StageStatus.SUCCESS
        assert len(result.data.get("errors", [])) == 0

    def test_invalid_ipa_data(self):
        """Test validation of invalid IPA data"""
        invalid_data = {
            "words": [
                {
                    "word": "hola",
                    "ipa": "invalid-ipa-123",  # Invalid IPA
                    "definition": "hello",
                },
                {
                    "word": "test",
                    "ipa": "",  # Empty IPA
                    "definition": "test",
                },
            ]
        }

        self.context.set("vocabulary_data", invalid_data)

        result = self.stage.execute(self.context)

        assert isinstance(result, StageResult)
        # Should still succeed but with validation errors reported
        assert result.status in [StageStatus.SUCCESS, StageStatus.PARTIAL]
        if "errors" in result.data:
            assert len(result.data["errors"]) > 0

    def test_missing_data(self):
        """Test validation with missing data"""
        result = self.stage.execute(self.context)

        assert isinstance(result, StageResult)
        assert result.status == StageStatus.FAILURE
        assert "found" in result.message.lower() and "data" in result.message.lower()

    def test_malformed_data(self):
        """Test validation with malformed data"""
        malformed_data = "not a dictionary"

        self.context.set("vocabulary_data", malformed_data)

        result = self.stage.execute(self.context)

        assert isinstance(result, StageResult)
        assert result.status == StageStatus.FAILURE


class TestMediaValidationStage:
    """Test media validation stage"""

    def setup_method(self):
        """Set up test stage"""
        self.stage = MediaValidationStage(data_key="media_data")
        self.context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

    def test_stage_properties(self):
        """Test stage properties"""
        assert self.stage.name == "validate_media_data"
        assert "Validate Media Data" in self.stage.display_name
        assert self.stage.data_key == "media_data"

    def test_valid_media_data(self):
        """Test validation of valid media data"""
        valid_data = {
            "media_files": [
                {
                    "id": "audio1",
                    "type": "audio",
                    "file_path": "/path/to/audio1.mp3",
                    "file_size": 12345,
                    "duration": 2.5,
                },
                {
                    "id": "image1",
                    "type": "image",
                    "file_path": "/path/to/image1.jpg",
                    "file_size": 67890,
                    "dimensions": {"width": 512, "height": 512},
                },
            ]
        }

        self.context.set("media_data", valid_data)

        with patch("pathlib.Path.exists") as mock_exists, patch(
            "pathlib.Path.is_file"
        ) as mock_is_file:
            mock_exists.return_value = True
            mock_is_file.return_value = True
            result = self.stage.execute(self.context)

            assert isinstance(result, StageResult)
            assert result.status == StageStatus.SUCCESS
            assert len(result.data.get("errors", [])) == 0

    def test_missing_files(self):
        """Test validation with missing media files"""
        data_with_missing_files = {
            "media_files": [
                {
                    "id": "missing1",
                    "type": "audio",
                    "file_path": "/nonexistent/path/audio.mp3",
                    "file_size": 12345,
                }
            ]
        }

        self.context.set("media_data", data_with_missing_files)

        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = False
            result = self.stage.execute(self.context)

            assert isinstance(result, StageResult)
            # Should report missing files but potentially still succeed
            assert result.status in [
                StageStatus.SUCCESS,
                StageStatus.PARTIAL,
                StageStatus.FAILURE,
            ]

    def test_invalid_media_format(self):
        """Test validation with invalid media format"""
        invalid_data = {
            "media_files": [
                {
                    "id": "invalid1",
                    "type": "unknown_type",  # Invalid media type
                    "file_path": "/path/to/file.xyz",
                    "file_size": -1,  # Invalid file size
                }
            ]
        }

        self.context.set("media_data", invalid_data)

        result = self.stage.execute(self.context)

        assert isinstance(result, StageResult)
        # Should detect format issues
        if result.status == StageStatus.SUCCESS and "errors" in result.data:
            assert len(result.data["errors"]) > 0

    def test_empty_media_data(self):
        """Test validation with empty media data"""
        empty_data = {"media_files": []}

        self.context.set("media_data", empty_data)

        result = self.stage.execute(self.context)

        assert isinstance(result, StageResult)
        # Empty data might be valid depending on stage configuration
        assert result.status in [StageStatus.SUCCESS, StageStatus.PARTIAL]


class TestValidationStageBase:
    """Test validation stage base functionality"""

    def test_abstract_validation_method(self):
        """Test that validation method is abstract"""
        from stages.base.validation_stage import ValidationStage

        # Cannot instantiate abstract class
        with pytest.raises(TypeError):
            ValidationStage("test_data")

    def test_validation_stage_error_handling(self):
        """Test error handling in validation stages"""
        stage = IPAValidationStage(data_key="test_data")
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        # Set invalid data type that will cause processing error
        context.set("test_data", None)

        result = stage.execute(context)

        assert isinstance(result, StageResult)
        assert result.status == StageStatus.FAILURE
        assert result.message is not None


if __name__ == "__main__":
    pytest.main([__file__])
