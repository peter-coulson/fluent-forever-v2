"""End-to-end tests using mock pipeline to validate framework functionality."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from src.core.context import PipelineContext
from src.core.registry import PipelineRegistry
from src.providers.registry import ProviderRegistry

from tests.fixtures.mock_implementations import (
    MockDataProvider,
    MockPipeline,
    MockStage,
    MockSyncProvider,
)


class TestMockPipelineEndToEnd:
    """Test complete pipeline execution using mock implementations."""

    @pytest.fixture
    def mock_registry_setup(self):
        """Set up mock registries with test data."""
        # Create registries
        pipeline_registry = PipelineRegistry()
        provider_registry = ProviderRegistry()

        # Create mock pipeline
        pipeline = MockPipeline(
            "test_pipeline",
            stages=[
                MockStage("initialize"),
                MockStage("process_data", requires_provider="data"),
                MockStage("sync_results", requires_provider="sync"),
            ],
        )

        # Register pipeline
        pipeline_registry.register(pipeline)

        # Register providers
        provider_registry.register_data_provider("default", MockDataProvider())
        provider_registry.register_sync_provider("default", MockSyncProvider())

        return pipeline_registry, provider_registry

    def test_e2e_mock_pipeline_success(self, mock_registry_setup):
        """Test complete pipeline executes successfully."""
        pipeline_registry, provider_registry = mock_registry_setup

        # Get pipeline
        pipeline = pipeline_registry.get("test_pipeline")

        # Create context
        context = PipelineContext(
            pipeline_name="test_pipeline",
            project_root=Path("."),
            config={"debug": True},
            args={"stage": "all"},
        )

        # Add providers to context
        context.set(
            "providers",
            {
                "data": provider_registry.get_data_provider("default"),
                "sync": provider_registry.get_sync_provider("default"),
            },
        )

        # Execute all stages
        for stage_name in pipeline.stages:
            result = pipeline.execute_stage(stage_name, context)
            assert result.success, f"Stage {stage_name} failed: {result.message}"
            assert stage_name in context.completed_stages

        # Verify final state
        assert len(context.completed_stages) == 3
        assert "initialize" in context.completed_stages
        assert "process_data" in context.completed_stages
        assert "sync_results" in context.completed_stages

        # Verify context data was populated by stages
        assert context.get("initialize_executed") is True
        assert context.get("process_data_executed") is True
        assert context.get("sync_results_executed") is True

    def test_e2e_mock_pipeline_stage_failure(self, mock_registry_setup):
        """Test pipeline handles stage failures appropriately."""
        pipeline_registry, provider_registry = mock_registry_setup

        # Create pipeline with failing stage
        failing_pipeline = MockPipeline(
            "failing_pipeline",
            stages=[
                MockStage("initialize"),
                MockStage("failing_stage", should_fail=True),
                MockStage("cleanup"),
            ],
        )

        pipeline_registry.register(failing_pipeline)

        # Get pipeline
        pipeline = pipeline_registry.get("failing_pipeline")

        # Create context
        context = PipelineContext(
            pipeline_name="failing_pipeline",
            project_root=Path("."),
        )

        # Add providers
        context.set(
            "providers",
            {
                "data": provider_registry.get_data_provider("default"),
                "sync": provider_registry.get_sync_provider("default"),
            },
        )

        # Execute stages until failure
        result1 = pipeline.execute_stage("initialize", context)
        assert result1.success
        assert "initialize" in context.completed_stages

        result2 = pipeline.execute_stage("failing_stage", context)
        assert not result2.success
        assert "failing_stage" not in context.completed_stages
        assert "failed intentionally" in result2.message

        # Cleanup stage should still be executable
        result3 = pipeline.execute_stage("cleanup", context)
        assert result3.success
        assert "cleanup" in context.completed_stages

    def test_e2e_mock_pipeline_dry_run_simulation(self, mock_registry_setup):
        """Test dry run mode works correctly."""
        pipeline_registry, provider_registry = mock_registry_setup

        pipeline = pipeline_registry.get("test_pipeline")

        # Create context for dry run
        context = PipelineContext(
            pipeline_name="test_pipeline",
            project_root=Path("."),
            args={"dry_run": True, "stage": "process_data"},
        )

        # Add providers
        context.set(
            "providers",
            {
                "data": provider_registry.get_data_provider("default"),
                "sync": provider_registry.get_sync_provider("default"),
            },
        )

        # Mock args for dry run
        mock_args = MagicMock()
        mock_args.stage = "process_data"
        mock_args.dry_run = True

        # Test CLI argument validation (should pass)
        errors = pipeline.validate_cli_args(mock_args)
        assert len(errors) == 0

        # Test context population
        pipeline.populate_context_from_cli(context, mock_args)
        assert context.get("cli_args") is not None

        # Test execution plan display (should not raise errors)
        try:
            pipeline.show_cli_execution_plan(context, mock_args)
            dry_run_successful = True
        except Exception:
            dry_run_successful = False

        assert dry_run_successful

    def test_e2e_mock_pipeline_provider_dependency_validation(
        self, mock_registry_setup
    ):
        """Test pipeline validates provider dependencies correctly."""
        pipeline_registry, provider_registry = mock_registry_setup

        # Create pipeline with stage requiring missing provider
        dependent_pipeline = MockPipeline(
            "dependent_pipeline",
            stages=[
                MockStage("needs_audio", requires_provider="audio"),
            ],
        )

        pipeline_registry.register(dependent_pipeline)
        pipeline = pipeline_registry.get("dependent_pipeline")

        # Create context without audio provider
        context = PipelineContext(
            pipeline_name="dependent_pipeline",
            project_root=Path("."),
        )

        context.set(
            "providers",
            {
                "data": provider_registry.get_data_provider("default"),
                # No audio provider
            },
        )

        # Execute stage - should fail due to missing provider
        result = pipeline.execute_stage("needs_audio", context)

        assert not result.success
        assert "validation failed" in result.message.lower()
        assert "needs_audio" not in context.completed_stages

    def test_e2e_mock_pipeline_context_isolation(self, mock_registry_setup):
        """Test that different pipeline contexts are properly isolated."""
        pipeline_registry, provider_registry = mock_registry_setup

        pipeline = pipeline_registry.get("test_pipeline")

        # Create two separate contexts
        context1 = PipelineContext(
            pipeline_name="test_pipeline",
            project_root=Path("."),
            args={"context_id": "first"},
        )

        context2 = PipelineContext(
            pipeline_name="test_pipeline",
            project_root=Path("."),
            args={"context_id": "second"},
        )

        # Add providers to both
        providers = {
            "data": provider_registry.get_data_provider("default"),
            "sync": provider_registry.get_sync_provider("default"),
        }

        context1.set("providers", providers)
        context2.set("providers", providers)

        # Execute first stage in each context
        result1 = pipeline.execute_stage("initialize", context1)
        result2 = pipeline.execute_stage("initialize", context2)

        assert result1.success
        assert result2.success

        # Contexts should be isolated
        assert context1.args["context_id"] == "first"
        assert context2.args["context_id"] == "second"

        # Both should have the stage marked complete independently
        assert "initialize" in context1.completed_stages
        assert "initialize" in context2.completed_stages

    def test_e2e_mock_pipeline_error_accumulation(self, mock_registry_setup):
        """Test that errors are properly accumulated in context."""
        pipeline_registry, provider_registry = mock_registry_setup

        # Create context
        context = PipelineContext(
            pipeline_name="test_pipeline",
            project_root=Path("."),
        )

        # Add some errors manually
        context.add_error("Initial error")

        # Add providers
        context.set(
            "providers",
            {
                "data": provider_registry.get_data_provider("default"),
                "sync": provider_registry.get_sync_provider("default"),
            },
        )

        # Execute successful stage
        pipeline = pipeline_registry.get("test_pipeline")
        result = pipeline.execute_stage("initialize", context)

        assert result.success

        # Previous errors should still be in context
        assert context.has_errors()
        assert "Initial error" in context.errors

    def test_e2e_mock_pipeline_stage_info_retrieval(self, mock_registry_setup):
        """Test that pipeline can provide information about its stages."""
        pipeline_registry, provider_registry = mock_registry_setup

        pipeline = pipeline_registry.get("test_pipeline")

        # Test stage info retrieval
        for stage_name in pipeline.stages:
            stage_info = pipeline.get_stage_info(stage_name)

            assert "name" in stage_info
            assert "display_name" in stage_info
            assert "dependencies" in stage_info

            assert stage_info["name"] == stage_name
            assert isinstance(stage_info["display_name"], str)
            assert isinstance(stage_info["dependencies"], list)

    def test_e2e_mock_pipeline_complete_workflow_simulation(self, mock_registry_setup):
        """Test complete workflow from registry setup to execution."""
        pipeline_registry, provider_registry = mock_registry_setup

        # Simulate complete workflow

        # 1. Pipeline discovery
        available_pipelines = pipeline_registry.list_pipelines()
        assert "test_pipeline" in available_pipelines

        # 2. Pipeline info retrieval
        pipeline_info = pipeline_registry.get_pipeline_info("test_pipeline")
        assert pipeline_info["name"] == "test_pipeline"
        assert len(pipeline_info["stages"]) == 3

        # 3. Pipeline execution setup
        pipeline = pipeline_registry.get("test_pipeline")
        context = PipelineContext(
            pipeline_name="test_pipeline",
            project_root=Path("."),
            args={"full_workflow": True},
        )

        # 4. Provider setup
        context.set(
            "providers",
            {
                "data": provider_registry.get_data_provider("default"),
                "sync": provider_registry.get_sync_provider("default"),
            },
        )

        # 5. Mock CLI args validation
        mock_args = MagicMock()
        errors = pipeline.validate_cli_args(mock_args)
        assert len(errors) == 0

        # 6. Context population from CLI
        pipeline.populate_context_from_cli(context, mock_args)

        # 7. Execute all stages
        execution_results = []
        for stage_name in pipeline.stages:
            result = pipeline.execute_stage(stage_name, context)
            execution_results.append(result)
            if not result.success:
                break

        # 8. Verify complete success
        assert all(result.success for result in execution_results)
        assert len(context.completed_stages) == len(pipeline.stages)
        assert not context.has_errors()

        # 9. Verify final state
        final_data_keys = list(context.data.keys())
        expected_keys = [
            "providers",
            "cli_args",
            "pipeline_name",
            "initialize_executed",
            "process_data_executed",
            "sync_results_executed",
        ]
        for key in expected_keys:
            assert key in final_data_keys
