"""Unit tests for list command."""

from unittest.mock import Mock

from src.cli.commands.list_command import ListCommand
from src.core.config import Config
from src.core.pipeline import Pipeline
from src.core.registry import PipelineRegistry


class MockPipeline(Pipeline):
    """Mock pipeline for testing."""

    def __init__(self, name, display_name):
        self._name = name
        self._display_name = display_name

    @property
    def name(self) -> str:
        return self._name

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def stages(self) -> list:
        return ["stage1", "stage2"]

    def get_stage(self, stage_name: str):
        return Mock()

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


class TestListCommand:
    """Test cases for ListCommand."""

    def test_list_command_creation(self):
        """Test list command creation."""
        registry = PipelineRegistry()
        config = Config()

        command = ListCommand(registry, config)

        assert command.registry is registry
        assert command.config is config

    def test_execute_empty_registry(self, capsys):
        """Test listing when no pipelines are registered."""
        registry = PipelineRegistry()
        config = Config()
        command = ListCommand(registry, config)

        args = Mock()
        result = command.execute(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "No pipelines registered" in captured.out

    def test_execute_with_pipelines(self, capsys):
        """Test listing when pipelines are registered."""
        registry = PipelineRegistry()
        config = Config()
        command = ListCommand(registry, config)

        # Register test pipelines
        pipeline1 = MockPipeline("test1", "Test Pipeline 1")
        pipeline2 = MockPipeline("test2", "Test Pipeline 2")
        registry.register(pipeline1)
        registry.register(pipeline2)

        args = Mock()
        result = command.execute(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "test1" in captured.out
        assert "test2" in captured.out
        assert "Test Pipeline 1" in captured.out
        assert "Test Pipeline 2" in captured.out
