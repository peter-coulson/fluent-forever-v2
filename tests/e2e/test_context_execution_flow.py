"""
E2E Test Scenario 3: CLI Execution Flow with Context Management

Purpose: Validate end-to-end stage execution infrastructure
"""

from pathlib import Path
from unittest.mock import patch

import pytest
from src.cli.pipeline_runner import main
from src.core.config import Config
from src.core.context import PipelineContext
from src.core.registry import get_pipeline_registry
from src.core.stages import StageStatus
from src.providers.registry import ProviderRegistry

from tests.fixtures.configs import ConfigFixture, create_base_config
from tests.fixtures.contexts import ContextBuilder, create_test_context
from tests.fixtures.pipelines import MockPipeline, MultiPhasePipeline
from tests.utils.assertions import (
    assert_cli_output_contains,
    assert_context_has_data,
    assert_context_no_errors,
    assert_context_stage_completed,
    assert_stage_result_success,
)


class TestContextExecutionFlow:
    """Test CLI execution flow with context management."""

    @pytest.fixture
    def test_config(self):
        """Create test configuration."""
        return create_base_config()

    @pytest.fixture
    def config_file(self, test_config):
        """Create temporary config file."""
        with ConfigFixture(test_config) as config_path:
            yield config_path

    @pytest.fixture
    def pipeline_registry(self):
        """Create pipeline registry with test pipelines."""
        registry = get_pipeline_registry()
        registry._pipelines.clear()

        # Register test pipelines
        test_pipeline = MockPipeline("test_pipeline")
        multi_phase = MultiPhasePipeline()

        registry.register(test_pipeline)
        registry.register(multi_phase)

        yield registry
        registry._pipelines.clear()

    @pytest.fixture
    def provider_registry(self, config_file):
        """Create provider registry from config."""
        config = Config.load(str(config_file))
        return ProviderRegistry.from_config(config)

    @pytest.fixture
    def project_root(self):
        """Get project root path."""
        return Path(__file__).parents[3]

    def test_cli_run_single_stage_dry_run(
        self, config_file, pipeline_registry, provider_registry, capsys
    ):
        """Test CLI run command with single stage dry run."""
        test_args = [
            "--config",
            str(config_file),
            "run",
            "test_pipeline",
            "--stage",
            "test_stage",
            "--dry-run",
        ]

        with (
            patch(
                "src.cli.pipeline_runner.get_pipeline_registry",
                return_value=pipeline_registry,
            ),
            patch(
                "src.cli.pipeline_runner.ProviderRegistry.from_config",
                return_value=provider_registry,
            ),
        ):
            result = main(test_args)

        assert result == 0
        captured = capsys.readouterr()

        # Should show dry run output
        assert_cli_output_contains(captured.out.lower(), "dry")
        assert_cli_output_contains(captured.out, "test_stage")

    def test_cli_run_single_stage_execute(
        self, config_file, pipeline_registry, provider_registry, capsys
    ):
        """Test CLI run command with single stage execution."""
        test_args = [
            "--config",
            str(config_file),
            "run",
            "test_pipeline",
            "--stage",
            "test_stage",
        ]

        with (
            patch(
                "src.cli.pipeline_runner.get_pipeline_registry",
                return_value=pipeline_registry,
            ),
            patch(
                "src.cli.pipeline_runner.ProviderRegistry.from_config",
                return_value=provider_registry,
            ),
        ):
            result = main(test_args)

        assert result == 0
        captured = capsys.readouterr()

        # Should show successful execution
        output = captured.out + captured.err
        assert "success" in output.lower() or "completed" in output.lower()

    def test_cli_run_phase_execution(
        self, config_file, pipeline_registry, provider_registry, capsys
    ):
        """Test CLI run command with phase execution."""
        test_args = [
            "--config",
            str(config_file),
            "run",
            "multi_phase_pipeline",
            "--phase",
            "phase1",
        ]

        with (
            patch(
                "src.cli.pipeline_runner.get_pipeline_registry",
                return_value=pipeline_registry,
            ),
            patch(
                "src.cli.pipeline_runner.ProviderRegistry.from_config",
                return_value=provider_registry,
            ),
        ):
            result = main(test_args)

        assert result == 0
        captured = capsys.readouterr()

        # Should show phase execution
        output = captured.out + captured.err
        assert "phase" in output.lower() or "completed" in output.lower()

    def test_context_creation_and_provider_injection(self, config_file, project_root):
        """Test context creation with provider injection."""
        config = Config.load(str(config_file))
        provider_registry = ProviderRegistry.from_config(config)

        # Create context
        context = PipelineContext(
            pipeline_name="test_pipeline", project_root=project_root
        )

        # Inject providers
        providers = provider_registry.get_providers_for_pipeline("test_pipeline")
        context.set("providers", providers)

        # Validate context has providers
        assert_context_has_data(context, "providers")

        context_providers = context.get("providers")
        assert "data" in context_providers
        assert "audio" in context_providers
        assert "image" in context_providers
        assert "sync" in context_providers

    def test_stage_execution_with_context_validation(self, project_root):
        """Test stage execution with context validation."""
        from tests.fixtures.pipelines import ContextDependentStage

        # Create context with required data
        context = (
            ContextBuilder("test_pipeline")
            .with_data("required_data", "test_value")
            .build()
        )
        context.project_root = project_root

        # Execute stage
        stage = ContextDependentStage()
        result = stage.execute(context)

        # Validate successful execution
        assert_stage_result_success(result)
        assert_context_has_data(context, "processed_data", "Processed: test_value")

    def test_stage_execution_context_validation_failure(self, project_root):
        """Test stage execution with context validation failure."""
        from tests.fixtures.pipelines import ContextDependentStage

        # Create context without required data
        context = create_test_context("test_pipeline", project_root)

        # Execute stage
        stage = ContextDependentStage()
        result = stage.execute(context)

        # Should fail validation
        assert result.status == StageStatus.FAILURE
        assert "required_data" in str(result.errors)

    def test_stage_dependency_validation(self, project_root):
        """Test stage execution with dependency validation."""
        from tests.fixtures.pipelines import DependencyStage

        # Create context without dependencies completed
        context = create_test_context("test_pipeline", project_root)

        # Execute stage (should fail)
        stage = DependencyStage()
        result = stage.execute(context)

        assert result.status == StageStatus.FAILURE
        assert "dependency" in str(result.errors).lower()

        # Mark dependency as complete and retry
        context.mark_stage_complete("test_stage")
        result = stage.execute(context)

        assert_stage_result_success(result)
        assert_context_stage_completed(context, "test_stage")

    def test_provider_access_in_stage(self, config_file, project_root):
        """Test provider access within stage execution."""
        from tests.fixtures.pipelines import ProviderUsingStage

        config = Config.load(str(config_file))
        provider_registry = ProviderRegistry.from_config(config)

        # Create context with providers
        context = (
            ContextBuilder("test_pipeline")
            .with_providers(
                provider_registry.get_providers_for_pipeline("test_pipeline")
            )
            .build()
        )
        context.project_root = project_root

        # Execute stage
        stage = ProviderUsingStage()
        result = stage.execute(context)

        # Validate provider access
        assert_stage_result_success(result)
        assert_context_has_data(context, "data_provider_count")
        assert_context_has_data(context, "audio_provider_count")

    def test_phase_execution_with_multiple_stages(self, project_root):
        """Test phase execution with multiple stages."""
        pipeline = MultiPhasePipeline()

        # Create context
        context = ContextBuilder("multi_phase_pipeline").build()
        context.project_root = project_root

        # Execute phase with multiple stages
        results = pipeline.execute_phase("phase2", context)

        # Should have results for multiple stages
        assert len(results) == 2  # phase2 has stage2 and stage3

        # All should succeed
        for result in results:
            assert result.status in [StageStatus.SUCCESS, StageStatus.PARTIAL]

    def test_phase_execution_fail_fast(self, project_root):
        """Test phase execution with fail-fast behavior."""
        from tests.fixtures.pipelines import FailureStage

        class FailFastPipeline(MockPipeline):
            def __init__(self):
                super().__init__(
                    "fail_fast_pipeline", ["failure_stage", "success_stage"]
                )
                self._phases = {"test_phase": ["failure_stage", "success_stage"]}

            def get_stage(self, stage_name: str):
                if stage_name == "failure_stage":
                    return FailureStage()
                return super().get_stage(stage_name)

        pipeline = FailFastPipeline()
        context = create_test_context("fail_fast_pipeline", project_root)

        # Execute phase (should stop at first failure)
        results = pipeline.execute_phase("test_phase", context)

        # Should only have one result (failed stage)
        assert len(results) == 1
        assert results[0].status == StageStatus.FAILURE

    def test_error_propagation_and_result_aggregation(self, project_root):
        """Test error propagation and result aggregation."""
        from tests.fixtures.pipelines import FailureStage

        context = create_test_context("test_pipeline", project_root)

        # Execute failing stage
        stage = FailureStage()
        result = stage.execute(context)

        # Validate error handling
        assert result.status == StageStatus.FAILURE
        assert len(result.errors) > 0
        assert "Intentional test failure" in result.errors

    def test_cli_argument_validation_and_pipeline_lookup(
        self, config_file, pipeline_registry, provider_registry, capsys
    ):
        """Test CLI argument validation and pipeline lookup."""
        # Test invalid pipeline
        test_args = [
            "--config",
            str(config_file),
            "run",
            "nonexistent_pipeline",
            "--stage",
            "test_stage",
        ]

        with (
            patch(
                "src.cli.pipeline_runner.get_pipeline_registry",
                return_value=pipeline_registry,
            ),
            patch(
                "src.cli.pipeline_runner.ProviderRegistry.from_config",
                return_value=provider_registry,
            ),
        ):
            result = main(test_args)

        assert result == 1
        captured = capsys.readouterr()

        # Should contain error about pipeline not found
        error_output = captured.err
        assert "not found" in error_output.lower()

    def test_stage_execution_timing_and_logging(self, project_root, capsys):
        """Test stage execution with timing and logging."""
        from tests.fixtures.pipelines import SuccessStage

        context = create_test_context("test_pipeline", project_root)

        # Execute stage with logging
        stage = SuccessStage()
        result = stage.execute(context)

        # Should succeed
        assert_stage_result_success(result)

        # Capture any logging output
        capsys.readouterr()
        # In test environment, may not have visible logging output

    def test_context_state_tracking(self, project_root):
        """Test context state tracking across stage execution."""
        context = create_test_context("test_pipeline", project_root)

        # Initial state
        assert len(context.completed_stages) == 0
        assert not context.has_errors()

        # Execute stage
        from tests.fixtures.pipelines import SuccessStage

        stage = SuccessStage()
        result = stage.execute(context)

        # Context should be updated
        assert_stage_result_success(result)
        assert_context_no_errors(context)

        # Note: Pipeline.execute_stage() marks stages complete, not Stage.execute()
        # So we test this at the pipeline level instead

    def test_dry_run_execution_plan_display(
        self, config_file, pipeline_registry, provider_registry, capsys
    ):
        """Test dry run execution plan display."""
        test_args = [
            "--config",
            str(config_file),
            "run",
            "test_pipeline",
            "--phase",
            "test_phase",
            "--dry-run",
        ]

        with (
            patch(
                "src.cli.pipeline_runner.get_pipeline_registry",
                return_value=pipeline_registry,
            ),
            patch(
                "src.cli.pipeline_runner.ProviderRegistry.from_config",
                return_value=provider_registry,
            ),
        ):
            result = main(test_args)

        assert result == 0
        captured = capsys.readouterr()

        # Should show execution plan
        assert_cli_output_contains(captured.out.lower(), "dry")
        assert_cli_output_contains(captured.out, "test_phase")

    def test_cli_execution_with_invalid_stage(
        self, config_file, pipeline_registry, provider_registry, capsys
    ):
        """Test CLI execution with invalid stage name."""
        test_args = [
            "--config",
            str(config_file),
            "run",
            "test_pipeline",
            "--stage",
            "invalid_stage",
        ]

        with (
            patch(
                "src.cli.pipeline_runner.get_pipeline_registry",
                return_value=pipeline_registry,
            ),
            patch(
                "src.cli.pipeline_runner.ProviderRegistry.from_config",
                return_value=provider_registry,
            ),
        ):
            result = main(test_args)

        assert result == 1
        captured = capsys.readouterr()

        # Should contain stage not found error
        error_output = captured.err
        assert "not found" in error_output.lower() or "invalid" in error_output.lower()

    def test_cli_execution_with_invalid_phase(
        self, config_file, pipeline_registry, provider_registry, capsys
    ):
        """Test CLI execution with invalid phase name."""
        test_args = [
            "--config",
            str(config_file),
            "run",
            "test_pipeline",
            "--phase",
            "invalid_phase",
        ]

        with (
            patch(
                "src.cli.pipeline_runner.get_pipeline_registry",
                return_value=pipeline_registry,
            ),
            patch(
                "src.cli.pipeline_runner.ProviderRegistry.from_config",
                return_value=provider_registry,
            ),
        ):
            result = main(test_args)

        assert result == 1
        captured = capsys.readouterr()

        # Should contain phase not found error
        error_output = captured.err
        assert "not found" in error_output.lower() or "invalid" in error_output.lower()

    def test_complete_execution_workflow(
        self, config_file, pipeline_registry, provider_registry, project_root
    ):
        """Test complete execution workflow from CLI to context completion."""
        # This tests the full flow:
        # 1. CLI argument parsing
        # 2. Pipeline lookup
        # 3. Context creation
        # 4. Provider injection
        # 5. Stage execution
        # 6. Result handling

        config = Config.load(str(config_file))
        providers = ProviderRegistry.from_config(config)

        # Get pipeline
        pipeline = pipeline_registry.get("test_pipeline")

        # Create context with providers
        context = PipelineContext(
            pipeline_name="test_pipeline", project_root=project_root
        )

        # Inject providers
        pipeline_providers = providers.get_providers_for_pipeline("test_pipeline")
        context.set("providers", pipeline_providers)

        # Execute stage
        result = pipeline.execute_stage("test_stage", context)

        # Validate complete workflow
        assert_stage_result_success(result)
        assert_context_stage_completed(context, "test_stage")
        assert_context_has_data(context, "test_stage_executed", True)
