"""Unit tests for pipeline registry basic functionality."""

import pytest
from src.core.exceptions import PipelineAlreadyRegisteredError, PipelineNotFoundError
from src.core.registry import PipelineRegistry, get_pipeline_registry

from tests.fixtures.pipelines import InvalidPipeline, MockPipeline


class TestPipelineRegistry:
    """Test pipeline registry basic functionality."""

    @pytest.fixture
    def clean_registry(self):
        """Provide a clean registry instance for each test."""
        registry = PipelineRegistry()
        # Clear any existing pipelines to ensure isolation
        registry._pipelines.clear()
        return registry

    @pytest.fixture
    def sample_pipeline(self):
        """Provide a sample pipeline for testing."""
        return MockPipeline("test_pipeline", ["stage1", "stage2"])

    @pytest.fixture
    def another_pipeline(self):
        """Provide another sample pipeline for testing."""
        return MockPipeline("another_pipeline", ["stage3", "stage4"])

    def test_singleton_access(self):
        """Test singleton access through get_pipeline_registry."""
        registry1 = get_pipeline_registry()
        registry2 = get_pipeline_registry()

        # Should return the same instance
        assert registry1 is registry2

    def test_register_pipeline(self, clean_registry, sample_pipeline):
        """Test successful pipeline registration."""
        clean_registry.register(sample_pipeline)

        assert sample_pipeline.name in clean_registry._pipelines
        assert clean_registry._pipelines[sample_pipeline.name] is sample_pipeline

    def test_register_duplicate_pipeline_error(self, clean_registry, sample_pipeline):
        """Test error when registering duplicate pipeline."""
        # Register pipeline first time
        clean_registry.register(sample_pipeline)

        # Try to register same pipeline again
        duplicate_pipeline = MockPipeline("test_pipeline", ["different_stage"])
        with pytest.raises(PipelineAlreadyRegisteredError) as exc_info:
            clean_registry.register(duplicate_pipeline)

        assert "Pipeline 'test_pipeline' already registered" in str(exc_info.value)

    def test_list_pipelines(self, clean_registry, sample_pipeline, another_pipeline):
        """Test listing all registered pipelines."""
        # Initially empty
        assert clean_registry.list_pipelines() == []

        # Add pipelines
        clean_registry.register(sample_pipeline)
        pipeline_names = clean_registry.list_pipelines()
        assert pipeline_names == ["test_pipeline"]

        clean_registry.register(another_pipeline)
        pipeline_names = clean_registry.list_pipelines()
        assert set(pipeline_names) == {"test_pipeline", "another_pipeline"}

    def test_get_pipeline_existing(self, clean_registry, sample_pipeline):
        """Test getting an existing pipeline."""
        clean_registry.register(sample_pipeline)

        retrieved_pipeline = clean_registry.get("test_pipeline")
        assert retrieved_pipeline is sample_pipeline

    def test_get_pipeline_nonexistent(self, clean_registry):
        """Test getting a nonexistent pipeline raises error."""
        with pytest.raises(PipelineNotFoundError) as exc_info:
            clean_registry.get("nonexistent_pipeline")

        assert "Pipeline 'nonexistent_pipeline' not found" in str(exc_info.value)

    def test_has_pipeline_existing(self, clean_registry, sample_pipeline):
        """Test has_pipeline returns True for existing pipeline."""
        clean_registry.register(sample_pipeline)

        assert clean_registry.has_pipeline("test_pipeline") is True

    def test_has_pipeline_nonexistent(self, clean_registry):
        """Test has_pipeline returns False for nonexistent pipeline."""
        assert clean_registry.has_pipeline("nonexistent_pipeline") is False

    def test_get_pipeline_info_existing(self, clean_registry, sample_pipeline):
        """Test getting pipeline info for existing pipeline."""
        clean_registry.register(sample_pipeline)

        info = clean_registry.get_pipeline_info("test_pipeline")

        expected_info = {
            "name": "test_pipeline",
            "display_name": "Test Pipeline (test_pipeline)",
            "description": "Test Pipeline (test_pipeline) pipeline for test_data.json",
            "stages": ["stage1", "stage2"],
            "data_file": "test_data.json",
            "anki_note_type": "Test Note Type",
        }

        assert info == expected_info

    def test_get_pipeline_info_nonexistent(self, clean_registry):
        """Test getting pipeline info for nonexistent pipeline raises error."""
        with pytest.raises(PipelineNotFoundError) as exc_info:
            clean_registry.get_pipeline_info("nonexistent_pipeline")

        assert "Pipeline 'nonexistent_pipeline' not found" in str(exc_info.value)

    def test_get_all_pipeline_info(
        self, clean_registry, sample_pipeline, another_pipeline
    ):
        """Test getting info for all registered pipelines."""
        clean_registry.register(sample_pipeline)
        clean_registry.register(another_pipeline)

        all_info = clean_registry.get_all_pipeline_info()

        assert len(all_info) == 2
        assert "test_pipeline" in all_info
        assert "another_pipeline" in all_info

        # Verify structure of returned info
        test_info = all_info["test_pipeline"]
        assert test_info["name"] == "test_pipeline"
        assert test_info["display_name"] == "Test Pipeline (test_pipeline)"
        assert test_info["stages"] == ["stage1", "stage2"]

        another_info = all_info["another_pipeline"]
        assert another_info["name"] == "another_pipeline"
        assert another_info["display_name"] == "Test Pipeline (another_pipeline)"
        assert another_info["stages"] == ["stage3", "stage4"]

    def test_registry_isolation_between_tests(self, clean_registry, sample_pipeline):
        """Test that registry state is properly isolated between tests."""
        # This test verifies the clean_registry fixture works correctly
        initial_pipelines = clean_registry.list_pipelines()
        assert initial_pipelines == []

        # Register a pipeline
        clean_registry.register(sample_pipeline)
        assert clean_registry.list_pipelines() == ["test_pipeline"]

        # This test should not affect other tests due to fixture isolation

    def test_invalid_pipeline_registration(self, clean_registry):
        """Test registering invalid pipeline still works at registry level."""
        invalid_pipeline = InvalidPipeline()
        clean_registry.register(invalid_pipeline)

        assert clean_registry.has_pipeline("invalid_pipeline") is True
        retrieved = clean_registry.get("invalid_pipeline")
        assert retrieved is invalid_pipeline

    def test_pipeline_info_with_invalid_pipeline(self, clean_registry):
        """Test getting pipeline info works even with invalid pipeline."""
        invalid_pipeline = InvalidPipeline()
        clean_registry.register(invalid_pipeline)

        info = clean_registry.get_pipeline_info("invalid_pipeline")

        expected_info = {
            "name": "invalid_pipeline",
            "display_name": "Invalid Test Pipeline",
            "description": "Invalid Test Pipeline pipeline for invalid.json",
            "stages": ["invalid_stage"],
            "data_file": "invalid.json",
            "anki_note_type": "Invalid Type",
        }

        assert info == expected_info
