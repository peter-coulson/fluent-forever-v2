"""Integration tests for Pipeline-Provider integration."""

from pathlib import Path

import pytest
from src.core.context import PipelineContext
from src.core.registry import PipelineRegistry
from src.providers.registry import ProviderRegistry

from tests.fixtures.mock_implementations import (
    MockDataProvider,
    MockMediaProvider,
    MockPipeline,
    MockStage,
    MockSyncProvider,
)


class TestPipelineProviderIntegration:
    """Test pipeline context creation and provider access integration."""

    def test_pipeline_context_provider_access(self):
        """Test that context provides access to all registered providers."""
        # Create provider registry with mock providers
        provider_registry = ProviderRegistry()
        provider_registry.register_data_provider("default", MockDataProvider())
        provider_registry.register_audio_provider("default", MockMediaProvider("audio"))
        provider_registry.register_image_provider("default", MockMediaProvider("image"))
        provider_registry.register_sync_provider("default", MockSyncProvider())

        # Create pipeline context
        context = PipelineContext(
            pipeline_name="test_pipeline",
            project_root=Path("."),
            config={},
            args={"stage": "test"},
        )

        # Add providers to context (simulating how RunCommand does it)
        context.set(
            "providers",
            {
                "data": provider_registry.get_data_provider("default"),
                "audio": provider_registry.get_audio_provider("default"),
                "image": provider_registry.get_image_provider("default"),
                "sync": provider_registry.get_sync_provider("default"),
            },
        )

        # Verify providers are accessible
        providers = context.get("providers")
        assert providers is not None
        assert providers["data"] is not None
        assert providers["audio"] is not None
        assert providers["image"] is not None
        assert providers["sync"] is not None

        # Verify provider types
        assert isinstance(providers["data"], MockDataProvider)
        assert isinstance(providers["audio"], MockMediaProvider)
        assert isinstance(providers["image"], MockMediaProvider)
        assert isinstance(providers["sync"], MockSyncProvider)

    def test_pipeline_context_missing_provider(self):
        """Test that stages handle missing optional providers."""
        # Create context with minimal providers
        context = PipelineContext(
            pipeline_name="test_pipeline",
            project_root=Path("."),
            config={},
            args={"stage": "test"},
        )

        # Add only data provider
        context.set(
            "providers",
            {
                "data": MockDataProvider(),
                "audio": None,
                "image": None,
                "sync": MockSyncProvider(),
            },
        )

        # Create stage that requires optional provider
        stage = MockStage("test_stage", requires_provider="audio")

        # Execute stage - should fail gracefully
        result = stage.execute(context)
        assert not result.success
        assert "audio" in str(result.errors)
        assert "validation failed" in result.message.lower()

    def test_pipeline_context_data_flow(self):
        """Test that data flows correctly between stages via context."""
        # Create pipeline context
        context = PipelineContext(
            pipeline_name="test_pipeline",
            project_root=Path("."),
        )

        # Add minimal providers
        context.set(
            "providers",
            {
                "data": MockDataProvider(),
                "sync": MockSyncProvider(),
            },
        )

        # Create stages
        stage1 = MockStage("stage1")
        stage2 = MockStage("stage2", requires_provider="data")

        # Execute first stage
        result1 = stage1.execute(context)
        assert result1.success

        # Verify data was added to context
        assert context.get("stage1_executed") is True
        assert context.get("stage1_execution_count") == 1

        # Execute second stage
        result2 = stage2.execute(context)
        assert result2.success

        # Verify data from both stages persists
        assert context.get("stage1_executed") is True
        assert context.get("stage2_executed") is True
        assert context.get("stage1_execution_count") == 1
        assert context.get("stage2_execution_count") == 1

    def test_pipeline_execution_with_providers(self):
        """Test complete pipeline execution with provider integration."""
        # Create mock pipeline
        pipeline = MockPipeline(
            "test",
            stages=[
                MockStage("prepare"),
                MockStage("process", requires_provider="data"),
                MockStage("sync", requires_provider="sync"),
            ],
        )

        # Create context with providers
        context = PipelineContext(
            pipeline_name="test",
            project_root=Path("."),
        )

        context.set(
            "providers",
            {
                "data": MockDataProvider(),
                "sync": MockSyncProvider(),
            },
        )

        # Execute each stage
        for stage_name in pipeline.stages:
            result = pipeline.execute_stage(stage_name, context)
            assert result.success
            assert stage_name in context.completed_stages

        # Verify all stages completed
        assert len(context.completed_stages) == 3
        assert "prepare" in context.completed_stages
        assert "process" in context.completed_stages
        assert "sync" in context.completed_stages

    def test_pipeline_stage_failure_handling(self):
        """Test pipeline handling of stage failures."""
        # Create pipeline with failing stage
        failing_stage = MockStage("failing_stage", should_fail=True)
        pipeline = MockPipeline("test", stages=[failing_stage])

        # Create context
        context = PipelineContext(
            pipeline_name="test",
            project_root=Path("."),
        )

        # Execute failing stage
        result = pipeline.execute_stage("failing_stage", context)

        # Verify failure is handled properly
        assert not result.success
        assert "failed intentionally" in result.message
        assert len(result.errors) > 0

        # Verify stage not marked as complete
        assert "failing_stage" not in context.completed_stages

    def test_pipeline_context_validation(self):
        """Test that pipeline validates context before stage execution."""
        # Create stage that requires specific provider
        stage = MockStage("test_stage", requires_provider="missing_provider")
        pipeline = MockPipeline("test", stages=[stage])

        # Create context without required provider
        context = PipelineContext(
            pipeline_name="test",
            project_root=Path("."),
        )

        context.set("providers", {"data": MockDataProvider()})

        # Execute stage - should fail validation
        result = pipeline.execute_stage("test_stage", context)
        assert not result.success
        assert "validation failed" in result.message.lower()


class TestPipelineRegistry:
    """Test pipeline registry functionality."""

    def test_pipeline_registry_registration(self):
        """Test pipeline registration and retrieval."""
        registry = PipelineRegistry()
        mock_pipeline = MockPipeline("test_pipeline")

        # Register pipeline
        registry.register(mock_pipeline)

        # Verify registration
        retrieved = registry.get("test_pipeline")
        assert retrieved is mock_pipeline

        # Verify listing
        pipelines = registry.list_pipelines()
        assert "test_pipeline" in pipelines

    def test_pipeline_registry_duplicate_registration(self):
        """Test that duplicate pipeline registration raises error."""
        from src.core.exceptions import PipelineAlreadyRegisteredError

        registry = PipelineRegistry()
        mock_pipeline = MockPipeline("test_pipeline")

        # Register pipeline
        registry.register(mock_pipeline)

        # Attempt to register again
        with pytest.raises(PipelineAlreadyRegisteredError):
            registry.register(mock_pipeline)

    def test_pipeline_registry_not_found(self):
        """Test that getting non-existent pipeline raises error."""
        from src.core.exceptions import PipelineNotFoundError

        registry = PipelineRegistry()

        # Attempt to get non-existent pipeline
        with pytest.raises(PipelineNotFoundError):
            registry.get("non_existent_pipeline")

    def test_pipeline_registry_info(self):
        """Test pipeline registry information retrieval."""
        registry = PipelineRegistry()
        mock_pipeline = MockPipeline("test_pipeline")

        # Register pipeline
        registry.register(mock_pipeline)

        # Get pipeline info
        info = registry.get_pipeline_info("test_pipeline")

        # Verify info structure
        assert info["name"] == "test_pipeline"
        assert info["display_name"] == "Mock Test Pipeline"
        assert isinstance(info["stages"], list)
        assert info["data_file"] == "test_pipeline.json"
        assert info["anki_note_type"] == "MockTestpipeline"

    def test_pipeline_registry_has_pipeline(self):
        """Test pipeline existence checking."""
        registry = PipelineRegistry()
        mock_pipeline = MockPipeline("test_pipeline")

        # Check non-existent pipeline
        assert not registry.has_pipeline("test_pipeline")

        # Register pipeline
        registry.register(mock_pipeline)

        # Check existing pipeline
        assert registry.has_pipeline("test_pipeline")
