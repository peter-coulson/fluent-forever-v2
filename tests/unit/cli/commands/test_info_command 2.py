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

    def get_stage_info(self, stage_name: str):
        """Get stage info for testing."""
        return {"name": stage_name, "display_name": f"{stage_name.title()} Stage"}

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

    def test_execute_with_stages_flag(self, capsys):
        """Test info with --stages flag for detailed stage info."""
        registry = PipelineRegistry()
        config = Config()
        command = InfoCommand(registry, config)

        # Register test pipeline
        pipeline = MockPipeline("test", "Test Pipeline")
        registry.register(pipeline)

        args = Mock()
        args.pipeline = "test"
        args.stages = True

        result = command.execute(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "prepare" in captured.out
        assert "Prepare Stage" in captured.out

    def test_execute_with_stages_flag_no_detailed_info(self, capsys):
        """Test info with --stages flag when no detailed stage info available."""
        registry = PipelineRegistry()
        config = Config()
        command = InfoCommand(registry, config)

        # Create pipeline that returns None for stage info
        class MockPipelineNoStageInfo(MockPipeline):
            def get_stage_info(self, stage_name: str):
                return None

        pipeline = MockPipelineNoStageInfo("test", "Test Pipeline")
        registry.register(pipeline)

        args = Mock()
        args.pipeline = "test"
        args.stages = True

        result = command.execute(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "No detailed info available" in captured.out

    def test_execute_with_stages_flag_stage_info_error(self, capsys):
        """Test info with --stages flag when stage info raises exception."""
        registry = PipelineRegistry()
        config = Config()
        command = InfoCommand(registry, config)

        # Create pipeline that raises error for stage info
        class MockPipelineStageInfoError(MockPipeline):
            def get_stage_info(self, stage_name: str):
                raise Exception("Stage info error")

        pipeline = MockPipelineStageInfoError("test", "Test Pipeline")
        registry.register(pipeline)

        args = Mock()
        args.pipeline = "test"
        args.stages = True

        result = command.execute(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Error getting stage info" in captured.out

    def test_execute_pipeline_no_stages(self, capsys):
        """Test info for pipeline with no stages."""
        registry = PipelineRegistry()
        config = Config()
        command = InfoCommand(registry, config)

        # Create pipeline with no stages
        class MockPipelineNoStages(MockPipeline):
            @property
            def stages(self) -> list:
                return []

        pipeline = MockPipelineNoStages("test", "Test Pipeline")
        registry.register(pipeline)

        args = Mock()
        args.pipeline = "test"

        result = command.execute(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "No stages available" in captured.out

    def test_execute_registry_error(self, capsys):
        """Test info when registry raises exception getting pipeline info."""
        registry = PipelineRegistry()
        config = Config()
        command = InfoCommand(registry, config)

        # Mock registry to raise exception
        registry.get_pipeline_info = Mock(side_effect=Exception("Registry error"))

        args = Mock()
        args.pipeline = "test"

        result = command.execute(args)

        assert result == 1
        captured = capsys.readouterr()
        assert "not found" in captured.out
        assert "Registry error" in captured.out

    def test_execute_stage_info_with_dependencies(self, capsys):
        """Test stage info display with dependencies."""
        registry = PipelineRegistry()
        config = Config()
        command = InfoCommand(registry, config)

        # Create pipeline with stage dependencies
        class MockPipelineWithDeps(MockPipeline):
            def get_stage_info(self, stage_name: str):
                if stage_name == "prepare":
                    return {
                        "name": "prepare",
                        "display_name": "Prepare Stage",
                        "dependencies": ["stage1", "stage2"],
                    }
                return super().get_stage_info(stage_name)

        pipeline = MockPipelineWithDeps("test", "Test Pipeline")
        registry.register(pipeline)

        args = Mock()
        args.pipeline = "test"
        args.stages = True

        result = command.execute(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Dependencies" in captured.out
        assert "stage1, stage2" in captured.out

    def test_execute_args_without_stages_attr(self, capsys):
        """Test info when args doesn't have stages attribute."""
        registry = PipelineRegistry()
        config = Config()
        command = InfoCommand(registry, config)

        # Register test pipeline
        pipeline = MockPipeline("test", "Test Pipeline")
        registry.register(pipeline)

        # Create args without stages attribute
        args = Mock()
        args.pipeline = "test"
        del args.stages  # Remove stages attribute

        result = command.execute(args)

        assert result == 0
        # Should work normally without --stages flag behavior
