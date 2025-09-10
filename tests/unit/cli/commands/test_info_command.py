"""Unit tests for info command."""

from unittest.mock import Mock

from src.cli.commands.info_command import InfoCommand
from src.core.config import Config
from src.core.pipeline import Pipeline
from src.core.registry import PipelineRegistry


class MockStage:
    """Mock stage for testing."""

    def __init__(self, name, display_name):
        self.name = name
        self.display_name = display_name


class MockPipeline(Pipeline):
    """Mock pipeline for testing."""

    def __init__(self, name, display_name):
        self._name = name
        self._display_name = display_name
        self._stages = ["prepare", "process", "finish"]

    @property
    def name(self) -> str:
        return self._name

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def stages(self) -> list:
        return self._stages

    def get_stage(self, stage_name: str):
        return MockStage(stage_name, f"{stage_name.title()} Stage")

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


class TestInfoCommand:
    """Test cases for InfoCommand."""

    def test_info_command_creation(self):
        """Test info command creation."""
        registry = PipelineRegistry()
        config = Config()

        command = InfoCommand(registry, config)

        assert command.registry is registry
        assert command.config is config

    def test_execute_nonexistent_pipeline(self, capsys):
        """Test info for non-existent pipeline."""
        registry = PipelineRegistry()
        config = Config()
        command = InfoCommand(registry, config)

        args = Mock()
        args.pipeline = "nonexistent"

        result = command.execute(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "not found" in captured.out

    def test_execute_existing_pipeline(self, capsys):
        """Test info for existing pipeline."""
        registry = PipelineRegistry()
        config = Config()
        command = InfoCommand(registry, config)

        # Register test pipeline
        pipeline = MockPipeline("test", "Test Pipeline")
        registry.register(pipeline)

        args = Mock()
        args.pipeline = "test"

        result = command.execute(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Test Pipeline" in captured.out
        assert "prepare" in captured.out
        assert "process" in captured.out
        assert "finish" in captured.out
