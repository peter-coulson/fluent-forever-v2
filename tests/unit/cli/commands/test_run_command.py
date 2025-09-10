"""Unit tests for run command."""

from pathlib import Path
from unittest.mock import Mock, patch

from src.cli.commands.run_command import RunCommand
from src.core.config import Config
from src.core.context import PipelineContext
from src.core.pipeline import Pipeline
from src.core.registry import PipelineRegistry
from src.core.stages import StageResult
from src.providers.registry import ProviderRegistry


class MockPipeline(Pipeline):
    """Mock pipeline for testing."""

    def __init__(self, name="test", validation_errors=None, execution_result=None):
        self._name = name
        self.validation_errors = validation_errors or []
        self.execution_result = execution_result or StageResult.success_result(
            "Success"
        )
        self.validate_called = False
        self.populate_called = False
        self.show_plan_called = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def display_name(self) -> str:
        return f"Mock {self._name.title()}"

    @property
    def stages(self) -> list:
        return ["prepare", "process", "finish"]

    def validate_cli_args(self, args) -> list[str]:
        self.validate_called = True
        return self.validation_errors

    def populate_context_from_cli(self, context, args) -> None:
        self.populate_called = True

    def show_cli_execution_plan(self, context, args) -> None:
        self.show_plan_called = True

    def execute_stage(self, stage_name: str, context: PipelineContext):
        return self.execution_result

    def get_stage(self, stage_name: str):
        return Mock()

    @property
    def data_file(self) -> str:
        return f"{self._name}.json"

    @property
    def anki_note_type(self) -> str:
        return f"Mock {self._name.title()}"


class TestRunCommand:
    """Test cases for RunCommand."""

    def setup_method(self):
        """Setup test fixtures."""
        self.pipeline_registry = PipelineRegistry()
        self.provider_registry = ProviderRegistry()
        self.project_root = Path("/test")
        self.config = Config()

        # Add mock providers
        mock_data_provider = Mock()
        mock_audio_provider = Mock()
        mock_image_provider = Mock()
        mock_sync_provider = Mock()

        self.provider_registry.register_data_provider("default", mock_data_provider)
        self.provider_registry.register_audio_provider("default", mock_audio_provider)
        self.provider_registry.register_image_provider("default", mock_image_provider)
        self.provider_registry.register_sync_provider("default", mock_sync_provider)

    def test_run_command_creation(self):
        """Test run command creation."""
        command = RunCommand(
            self.pipeline_registry,
            self.provider_registry,
            self.project_root,
            self.config,
        )

        assert command.pipeline_registry is self.pipeline_registry
        assert command.provider_registry is self.provider_registry
        assert command.project_root is self.project_root
        assert command.config is self.config

    def test_execute_nonexistent_pipeline(self, capsys):
        """Test run with non-existent pipeline."""
        command = RunCommand(
            self.pipeline_registry,
            self.provider_registry,
            self.project_root,
            self.config,
        )

        args = Mock()
        args.pipeline = "nonexistent"
        args.stage = "prepare"

        result = command.execute(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "not found" in captured.out

    def test_execute_validation_errors(self, capsys):
        """Test run with CLI validation errors."""
        command = RunCommand(
            self.pipeline_registry,
            self.provider_registry,
            self.project_root,
            self.config,
        )

        # Mock validation to return errors
        with patch("src.cli.commands.run_command.validate_arguments") as mock_validate:
            mock_validate.return_value = ["Validation error"]

            args = Mock()
            args.pipeline = "test"
            args.stage = "prepare"

            result = command.execute(args)

            assert result == 1
            captured = capsys.readouterr()
            assert "Validation error" in captured.out

    def test_execute_pipeline_validation_errors(self, capsys):
        """Test run with pipeline-specific validation errors."""
        pipeline = MockPipeline(validation_errors=["Pipeline validation error"])
        self.pipeline_registry.register(pipeline)

        command = RunCommand(
            self.pipeline_registry,
            self.provider_registry,
            self.project_root,
            self.config,
        )

        args = Mock()
        args.pipeline = "test"
        args.stage = "prepare"
        args.dry_run = False

        result = command.execute(args)

        assert result == 1
        assert pipeline.validate_called
        captured = capsys.readouterr()
        assert "Pipeline validation error" in captured.out

    def test_execute_dry_run(self, capsys):
        """Test dry run execution."""
        pipeline = MockPipeline()
        self.pipeline_registry.register(pipeline)

        command = RunCommand(
            self.pipeline_registry,
            self.provider_registry,
            self.project_root,
            self.config,
        )

        args = Mock()
        args.pipeline = "test"
        args.stage = "prepare"
        args.dry_run = True

        result = command.execute(args)

        assert result == 0
        assert not pipeline.validate_called  # Should skip validation for dry run
        assert pipeline.show_plan_called
        captured = capsys.readouterr()
        assert "DRY RUN" in captured.out

    def test_execute_success(self, capsys):
        """Test successful pipeline execution."""
        success_result = StageResult.success_result("Pipeline completed successfully")
        pipeline = MockPipeline(execution_result=success_result)
        self.pipeline_registry.register(pipeline)

        command = RunCommand(
            self.pipeline_registry,
            self.provider_registry,
            self.project_root,
            self.config,
        )

        args = Mock()
        args.pipeline = "test"
        args.stage = "prepare"
        args.dry_run = False

        result = command.execute(args)

        assert result == 0
        assert pipeline.validate_called
        assert pipeline.populate_called
        captured = capsys.readouterr()
        assert "Pipeline completed successfully" in captured.out

    def test_execute_partial_success(self, capsys):
        """Test partial success pipeline execution."""
        partial_result = StageResult.partial(
            "Pipeline completed with warnings", errors=["Warning 1", "Warning 2"]
        )
        pipeline = MockPipeline(execution_result=partial_result)
        self.pipeline_registry.register(pipeline)

        command = RunCommand(
            self.pipeline_registry,
            self.provider_registry,
            self.project_root,
            self.config,
        )

        args = Mock()
        args.pipeline = "test"
        args.stage = "prepare"
        args.dry_run = False

        result = command.execute(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Partial success" in captured.out
        assert "Warning 1" in captured.out
        assert "Warning 2" in captured.out

    def test_execute_failure(self, capsys):
        """Test failed pipeline execution."""
        failure_result = StageResult.failure(
            "Pipeline execution failed", errors=["Error 1", "Error 2"]
        )
        pipeline = MockPipeline(execution_result=failure_result)
        self.pipeline_registry.register(pipeline)

        command = RunCommand(
            self.pipeline_registry,
            self.provider_registry,
            self.project_root,
            self.config,
        )

        args = Mock()
        args.pipeline = "test"
        args.stage = "prepare"
        args.dry_run = False

        result = command.execute(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Pipeline execution failed" in captured.out
        assert "Error 1" in captured.out
        assert "Error 2" in captured.out

    def test_execute_stage_exception(self, capsys):
        """Test exception during stage execution."""
        pipeline = MockPipeline()
        pipeline.execute_stage = Mock(side_effect=Exception("Stage execution error"))
        self.pipeline_registry.register(pipeline)

        command = RunCommand(
            self.pipeline_registry,
            self.provider_registry,
            self.project_root,
            self.config,
        )

        args = Mock()
        args.pipeline = "test"
        args.stage = "prepare"
        args.dry_run = False

        result = command.execute(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "Error executing stage" in captured.out
        assert "Stage execution error" in captured.out

    def test_create_context(self):
        """Test context creation."""
        command = RunCommand(
            self.pipeline_registry,
            self.provider_registry,
            self.project_root,
            self.config,
        )

        args = Mock()
        args.pipeline = "test"
        args.stage = "prepare"
        # Add some attributes to args that would be converted to dict
        args.verbose = True
        args.dry_run = False

        context = command._create_context(args)

        assert isinstance(context, PipelineContext)
        assert context.pipeline_name == "test"
        assert context.project_root == self.project_root

        # Check providers are in context
        providers = context.get("providers")
        assert "data" in providers
        assert "audio" in providers
        assert "image" in providers
        assert "sync" in providers

    def test_execute_pipeline_stage_success(self):
        """Test _execute_pipeline_stage method with success."""
        success_result = StageResult.success_result("Stage completed")
        pipeline = MockPipeline(execution_result=success_result)
        context = PipelineContext("test", self.project_root)

        command = RunCommand(
            self.pipeline_registry,
            self.provider_registry,
            self.project_root,
            self.config,
        )

        result = command._execute_pipeline_stage(pipeline, "prepare", context)
        assert result == 0

    def test_execute_pipeline_stage_failure(self):
        """Test _execute_pipeline_stage method with failure."""
        failure_result = StageResult.failure("Stage failed")
        pipeline = MockPipeline(execution_result=failure_result)
        context = PipelineContext("test", self.project_root)

        command = RunCommand(
            self.pipeline_registry,
            self.provider_registry,
            self.project_root,
            self.config,
        )

        result = command._execute_pipeline_stage(pipeline, "prepare", context)
        assert result == 1

    def test_execute_missing_args_attributes(self):
        """Test execute with args missing expected attributes."""
        pipeline = MockPipeline()
        self.pipeline_registry.register(pipeline)

        command = RunCommand(
            self.pipeline_registry,
            self.provider_registry,
            self.project_root,
            self.config,
        )

        # Create args with minimal attributes that would normally cause getattr to be used
        args = Mock()
        args.pipeline = "test"
        args.stage = "process"  # Use a stage that doesn't require additional args
        # dry_run will be handled by getattr() with False default

        result = command.execute(args)

        assert result == 0
