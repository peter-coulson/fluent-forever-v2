"""Unit tests for pipeline registry."""

import pytest
from src.core.exceptions import PipelineAlreadyRegisteredError, PipelineNotFoundError
from src.core.pipeline import Pipeline
from src.core.registry import PipelineRegistry
from src.core.stages import Stage, StageResult


class MockStage(Stage):
    """Mock stage for testing."""

    def __init__(self, name):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def display_name(self) -> str:
        return f"Mock {self._name.title()} Stage"

    def execute(self, context) -> StageResult:
        return StageResult.success_result(f"{self._name} completed")

    def validate_context(self, context) -> list:
        return []


class MockPipeline(Pipeline):
    """Mock pipeline for testing."""

    def __init__(self, name):
        self._name = name
        self._stages = {"test": MockStage("test")}

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


class TestPipelineRegistry:
    """Test cases for PipelineRegistry."""

    def test_registry_creation(self):
        """Test registry creation."""
        registry = PipelineRegistry()
        assert registry is not None

    def test_register_pipeline(self):
        """Test registering a pipeline."""
        registry = PipelineRegistry()
        pipeline = MockPipeline("test")

        registry.register(pipeline)
        retrieved = registry.get("test")

        assert retrieved is pipeline
        assert retrieved.name == "test"

    def test_register_duplicate_pipeline(self):
        """Test registering duplicate pipeline raises error."""
        registry = PipelineRegistry()
        pipeline1 = MockPipeline("test")
        pipeline2 = MockPipeline("test")

        registry.register(pipeline1)

        with pytest.raises(PipelineAlreadyRegisteredError):
            registry.register(pipeline2)

    def test_get_nonexistent_pipeline(self):
        """Test getting non-existent pipeline raises error."""
        registry = PipelineRegistry()

        with pytest.raises(PipelineNotFoundError):
            registry.get("nonexistent")

    def test_list_pipelines(self):
        """Test listing available pipelines."""
        registry = PipelineRegistry()
        pipeline1 = MockPipeline("test1")
        pipeline2 = MockPipeline("test2")

        registry.register(pipeline1)
        registry.register(pipeline2)

        pipelines = registry.list_pipelines()
        assert len(pipelines) == 2
        assert "test1" in pipelines
        assert "test2" in pipelines

    def test_has_pipeline(self):
        """Test checking if pipeline exists."""
        registry = PipelineRegistry()
        pipeline = MockPipeline("test")

        assert not registry.has_pipeline("test")

        registry.register(pipeline)

        assert registry.has_pipeline("test")
        assert not registry.has_pipeline("nonexistent")
