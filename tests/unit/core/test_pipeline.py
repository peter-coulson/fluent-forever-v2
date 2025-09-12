"""Unit tests for pipeline base class."""

from pathlib import Path

import pytest
from src.core.context import PipelineContext
from src.core.exceptions import StageNotFoundError
from src.core.pipeline import Pipeline
from src.core.stages import Stage, StageResult, StageStatus


class MockStage(Stage):
    """Mock stage for testing."""

    def __init__(self, name, success=True, validation_errors=None):
        super().__init__()
        self._name = name
        self._success = success
        self._validation_errors = validation_errors or []

    @property
    def name(self) -> str:
        return self._name

    @property
    def display_name(self) -> str:
        return f"Mock {self._name.title()} Stage"

    def _execute_impl(self, context: PipelineContext) -> StageResult:
        if self._success:
            return StageResult.success_result(
                f"{self._name} completed", {self._name: True}
            )
        else:
            return StageResult.failure(f"{self._name} failed", ["Test error"])

    def validate_context(self, context: PipelineContext) -> list:
        return self._validation_errors


class MockPipeline(Pipeline):
    """Mock pipeline for testing."""

    def __init__(self, name="mock"):
        self._name = name
        self._stages = {
            "prepare": MockStage("prepare"),
            "process": MockStage("process"),
            "finish": MockStage("finish"),
        }

    @property
    def name(self) -> str:
        return self._name

    @property
    def display_name(self) -> str:
        return f"Mock {self._name.title()} Pipeline"

    @property
    def stages(self) -> list:
        return list(self._stages.keys())

    def get_stage(self, stage_name: str) -> Stage:
        if stage_name not in self._stages:
            raise StageNotFoundError(f"Stage '{stage_name}' not found")
        return self._stages[stage_name]

    @property
    def data_file(self) -> str:
        return f"{self._name}.json"

    @property
    def anki_note_type(self) -> str:
        return f"Mock {self._name.title()}"

    def validate_cli_args(self, args) -> list[str]:
        return []

    def populate_context_from_cli(self, context, args) -> None:
        pass

    def show_cli_execution_plan(self, context, args) -> None:
        pass

    @property
    def phases(self) -> dict[str, list[str]]:
        """Mock phases for testing."""
        return {
            "preparation": ["prepare", "process"],
            "completion": ["finish"],
            "full": ["prepare", "process", "finish"],
        }


class TestPipeline:
    """Test cases for Pipeline base class."""

    def test_pipeline_properties(self):
        """Test pipeline property access."""
        pipeline = MockPipeline("test")

        assert pipeline.name == "test"
        assert pipeline.display_name == "Mock Test Pipeline"
        assert pipeline.stages == ["prepare", "process", "finish"]

    def test_get_stage(self):
        """Test getting stage by name."""
        pipeline = MockPipeline()

        stage = pipeline.get_stage("prepare")
        assert stage.name == "prepare"

        with pytest.raises(StageNotFoundError):
            pipeline.get_stage("nonexistent")

    def test_execute_stage_success(self):
        """Test successful stage execution."""
        pipeline = MockPipeline()
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        result = pipeline.execute_stage("prepare", context)

        assert result.status == StageStatus.SUCCESS
        assert "prepare completed" in result.message
        assert "prepare" in context.completed_stages

    def test_execute_stage_failure(self):
        """Test failed stage execution."""
        pipeline = MockPipeline()
        pipeline._stages["prepare"] = MockStage("prepare", success=False)

        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        result = pipeline.execute_stage("prepare", context)

        assert result.status == StageStatus.FAILURE
        assert "prepare" not in context.completed_stages

    def test_execute_stage_validation_failure(self):
        """Test stage execution with validation failure."""
        pipeline = MockPipeline()
        pipeline._stages["prepare"] = MockStage(
            "prepare", validation_errors=["Missing required field"]
        )

        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        result = pipeline.execute_stage("prepare", context)

        assert result.status == StageStatus.FAILURE
        assert "Context validation failed" in result.message
        assert "Missing required field" in result.errors

    def test_execute_nonexistent_stage(self):
        """Test executing non-existent stage."""
        pipeline = MockPipeline()
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        result = pipeline.execute_stage("nonexistent", context)

        assert result.status == StageStatus.FAILURE
        assert "not found" in result.message

    def test_pipeline_stage_execution_exception_handling(self):
        """Test pipeline handling of unhandled exceptions in stage.execute()."""

        class ExceptionStage(MockStage):
            def __init__(self, name, exception_type=Exception):
                super().__init__(name)
                self.exception_type = exception_type

            def execute(self, context):
                raise self.exception_type("Simulated stage exception")

        pipeline = MockPipeline()
        pipeline._stages["exception_stage"] = ExceptionStage("exception_stage")

        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        # Test that pipeline catches and handles the exception
        result = pipeline.execute_stage("exception_stage", context)

        assert result.status == StageStatus.FAILURE
        assert (
            "Simulated stage exception" in result.message
            or "exception" in result.message.lower()
        )
        assert "exception_stage" not in context.completed_stages

        # Test with different exception types
        pipeline._stages["runtime_error"] = ExceptionStage(
            "runtime_error", RuntimeError
        )
        result2 = pipeline.execute_stage("runtime_error", context)

        assert result2.status == StageStatus.FAILURE
        assert "runtime_error" not in context.completed_stages

    def test_execute_phase_success(self):
        """Test successful phase execution with multiple stages."""
        pipeline = MockPipeline()
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        results = pipeline.execute_phase("preparation", context)

        assert len(results) == 2
        assert all(result.status == StageStatus.SUCCESS for result in results)
        assert "prepare" in context.completed_stages
        assert "process" in context.completed_stages

    def test_execute_phase_invalid_phase(self):
        """Test executing non-existent phase raises ValueError."""
        pipeline = MockPipeline()
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        with pytest.raises(ValueError) as exc_info:
            pipeline.execute_phase("nonexistent", context)

        assert "Phase 'nonexistent' not found" in str(exc_info.value)
        assert "Available phases: " in str(exc_info.value)

    def test_execute_phase_failure_stops_execution(self):
        """Test phase execution stops on stage failure."""
        pipeline = MockPipeline()
        # Make the first stage in preparation phase fail
        pipeline._stages["prepare"] = MockStage("prepare", success=False)
        context = PipelineContext(pipeline_name="test", project_root=Path("/test"))

        results = pipeline.execute_phase("preparation", context)

        # Should only have one result (the failed stage)
        assert len(results) == 1
        assert results[0].status == StageStatus.FAILURE
        assert "prepare" not in context.completed_stages
        assert "process" not in context.completed_stages

    def test_get_phase_info(self):
        """Test getting phase information."""
        pipeline = MockPipeline()

        phase_info = pipeline.get_phase_info("preparation")

        assert phase_info["name"] == "preparation"
        assert phase_info["display_name"] == "Preparation"
        assert phase_info["stages"] == ["prepare", "process"]
        assert phase_info["stage_count"] == 2

        # Test invalid phase
        invalid_info = pipeline.get_phase_info("nonexistent")
        assert invalid_info == {}
