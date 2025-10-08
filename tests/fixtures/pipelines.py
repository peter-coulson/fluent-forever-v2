"""Test pipeline and stage implementations for E2E testing."""

from typing import Any

from src.core.context import PipelineContext
from src.core.pipeline import Pipeline
from src.core.stages import Stage, StageResult


class MockPipeline(Pipeline):
    """Minimal pipeline implementation for infrastructure testing."""

    def __init__(self, name: str = "test_pipeline", stages: list[str] | None = None):
        self._name = name
        self._stages = stages or ["test_stage", "dependency_stage", "provider_stage"]
        self._phases = {
            "test_phase": ["test_stage"],
            "full": ["test_stage", "dependency_stage"],
            "provider_test": ["provider_stage"],
        }

    @property
    def name(self) -> str:
        return self._name

    @property
    def display_name(self) -> str:
        return f"Test Pipeline ({self._name})"

    @property
    def stages(self) -> list[str]:
        return self._stages

    @property
    def phases(self) -> dict[str, list[str]]:
        return self._phases

    def get_stage(self, stage_name: str) -> Stage:
        """Get stage instance by name."""
        if stage_name == "test_stage":
            return SuccessStage()
        elif stage_name == "dependency_stage":
            return DependencyStage()
        elif stage_name == "provider_stage":
            return ProviderUsingStage()
        elif stage_name == "failure_stage":
            return FailureStage()
        elif stage_name == "context_dependent_stage":
            return ContextDependentStage()
        else:
            from src.core.exceptions import StageNotFoundError

            raise StageNotFoundError(f"Stage '{stage_name}' not found")

    @property
    def data_file(self) -> str:
        return "test_data.json"

    @property
    def anki_note_type(self) -> str:
        return "Test Note Type"

    def validate_cli_args(self, args: Any) -> list[str]:
        """Validate CLI arguments for this pipeline."""
        errors = []
        if hasattr(args, "invalid_arg") and args.invalid_arg:
            errors.append("Invalid argument provided")
        return errors

    def populate_context_from_cli(self, context: PipelineContext, args: Any) -> None:
        """Populate context from CLI arguments."""
        context.set("cli_populated", True)
        if hasattr(args, "test_data"):
            context.set("test_data", args.test_data)

    def show_cli_execution_plan(self, context: PipelineContext, args: Any) -> None:
        """Show execution plan for dry run."""
        print(f"Dry run for pipeline '{self.name}'")
        if hasattr(args, "stage"):
            print(f"Would execute stage: {args.stage}")
        elif hasattr(args, "phase"):
            stage_names = self.phases.get(args.phase, [])
            print(f"Would execute phase '{args.phase}' with stages: {stage_names}")


class SuccessStage(Stage):
    """Test stage that always succeeds."""

    @property
    def name(self) -> str:
        return "test_stage"

    @property
    def display_name(self) -> str:
        return "Test Success Stage"

    def _execute_impl(self, context: PipelineContext) -> StageResult:
        context.set("test_stage_executed", True)
        return StageResult.success_result("Test stage completed successfully")


class FailureStage(Stage):
    """Test stage that always fails."""

    @property
    def name(self) -> str:
        return "failure_stage"

    @property
    def display_name(self) -> str:
        return "Test Failure Stage"

    def _execute_impl(self, context: PipelineContext) -> StageResult:
        return StageResult.failure("Test failure", ["Intentional test failure"])


class DependencyStage(Stage):
    """Test stage with dependencies."""

    @property
    def name(self) -> str:
        return "dependency_stage"

    @property
    def display_name(self) -> str:
        return "Test Dependency Stage"

    @property
    def dependencies(self) -> list[str]:
        return ["test_stage"]

    def _execute_impl(self, context: PipelineContext) -> StageResult:
        context.set("dependency_stage_executed", True)
        return StageResult.success_result("Dependency stage completed")

    def validate_context(self, context: PipelineContext) -> list[str]:
        """Validate that dependencies are completed."""
        errors = []
        if "test_stage" not in context.completed_stages:
            errors.append("Required dependency 'test_stage' not completed")
        return errors


class ContextDependentStage(Stage):
    """Test stage that validates context data."""

    @property
    def name(self) -> str:
        return "context_dependent_stage"

    @property
    def display_name(self) -> str:
        return "Context Dependent Stage"

    def validate_context(self, context: PipelineContext) -> list[str]:
        """Validate required context data."""
        errors = []
        if not context.get("required_data"):
            errors.append("Missing required_data in context")
        return errors

    def _execute_impl(self, context: PipelineContext) -> StageResult:
        required_data = context.get("required_data")
        context.set("processed_data", f"Processed: {required_data}")
        return StageResult.success_result("Context processing completed")


class ProviderUsingStage(Stage):
    """Test stage that uses providers from context."""

    @property
    def name(self) -> str:
        return "provider_stage"

    @property
    def display_name(self) -> str:
        return "Provider Using Stage"

    def validate_context(self, context: PipelineContext) -> list[str]:
        """Validate that providers are available."""
        errors = []
        if not context.get("providers"):
            errors.append("No providers available in context")
        return errors

    def _execute_impl(self, context: PipelineContext) -> StageResult:
        providers = context.get("providers", {})
        data_providers = providers.get("data", {})
        audio_providers = providers.get("audio", {})

        context.set("data_provider_count", len(data_providers))
        context.set("audio_provider_count", len(audio_providers))

        return StageResult.success_result(
            f"Provider stage completed with {len(data_providers)} data providers"
        )


class MultiPhasePipeline(MockPipeline):
    """Pipeline with multiple phases for testing phase execution."""

    def __init__(self):
        super().__init__("multi_phase_pipeline", ["stage1", "stage2", "stage3"])
        self._phases = {
            "phase1": ["stage1"],
            "phase2": ["stage2", "stage3"],
            "full": ["stage1", "stage2", "stage3"],
        }

    def get_stage(self, stage_name: str) -> Stage:
        """Return simple success stages for all stages."""
        return SuccessStage()


class InvalidPipeline(Pipeline):
    """Pipeline that raises errors for testing error handling."""

    @property
    def name(self) -> str:
        return "invalid_pipeline"

    @property
    def display_name(self) -> str:
        return "Invalid Test Pipeline"

    @property
    def stages(self) -> list[str]:
        return ["invalid_stage"]

    def get_stage(self, stage_name: str) -> Stage:
        raise RuntimeError("Invalid stage access")

    @property
    def data_file(self) -> str:
        return "invalid.json"

    @property
    def anki_note_type(self) -> str:
        return "Invalid Type"

    def validate_cli_args(self, args: Any) -> list[str]:
        return ["Invalid pipeline"]

    def populate_context_from_cli(self, context: PipelineContext, args: Any) -> None:
        raise RuntimeError("Invalid context population")

    def show_cli_execution_plan(self, context: PipelineContext, args: Any) -> None:
        raise RuntimeError("Invalid execution plan")
