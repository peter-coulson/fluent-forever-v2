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

    def test_execute_detailed_listing(self, capsys):
        """Test detailed pipeline listing."""
        registry = PipelineRegistry()
        config = Config()
        command = ListCommand(registry, config)

        # Register test pipelines
        pipeline1 = MockPipeline("test1", "Test Pipeline 1")
        pipeline2 = MockPipeline("test2", "Test Pipeline 2")
        registry.register(pipeline1)
        registry.register(pipeline2)

        args = Mock()
        args.detailed = True

        result = command.execute(args)

        assert result == 0
        captured = capsys.readouterr()
        # Should show table with headers
        assert "Name" in captured.out
        assert "Display Name" in captured.out
        assert "Stages" in captured.out
        assert "Anki Note Type" in captured.out
        assert "Data File" in captured.out
        # Should show pipeline data
        assert "test1" in captured.out
        assert "Test Pipeline 1" in captured.out

    def test_execute_detailed_with_registry_error(self, capsys):
        """Test detailed listing when registry throws error for a pipeline."""
        registry = PipelineRegistry()
        config = Config()
        command = ListCommand(registry, config)

        # Register one good pipeline
        pipeline1 = MockPipeline("test1", "Test Pipeline 1")
        registry.register(pipeline1)

        # Mock list_pipelines to return pipeline that causes error
        registry.list_pipelines = Mock(return_value=["test1", "error_pipeline"])

        # Mock get_pipeline_info to throw error for error_pipeline
        def mock_get_info(name):
            if name == "error_pipeline":
                raise Exception("Pipeline info error")
            return (
                pipeline1.to_dict()
                if hasattr(pipeline1, "to_dict")
                else {
                    "name": name,
                    "display_name": "Test Pipeline 1",
                    "stages": ["stage1", "stage2"],
                    "anki_note_type": "Mock Test1",
                    "data_file": "test1.json",
                }
            )

        registry.get_pipeline_info = Mock(side_effect=mock_get_info)

        args = Mock()
        args.detailed = True

        result = command.execute(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "test1" in captured.out
        assert "error_pipeline" in captured.out
        assert "Error:" in captured.out

    def test_execute_simple_with_registry_error(self, capsys):
        """Test simple listing when registry throws error for a pipeline."""
        registry = PipelineRegistry()
        config = Config()
        command = ListCommand(registry, config)

        # Mock list_pipelines to return pipeline that causes error
        registry.list_pipelines = Mock(return_value=["test1", "error_pipeline"])

        # Mock get_pipeline_info to throw error for error_pipeline
        def mock_get_info(name):
            if name == "error_pipeline":
                raise Exception("Pipeline info error")
            return {
                "name": name,
                "display_name": "Test Pipeline 1",
                "description": "Test description",
                "stages": ["stage1", "stage2"],
                "anki_note_type": "Mock Test1",
                "data_file": "test1.json",
            }

        registry.get_pipeline_info = Mock(side_effect=mock_get_info)

        args = Mock()
        args.detailed = False  # Explicitly set to False for simple path

        result = command.execute(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "test1" in captured.out
        assert "error_pipeline" in captured.out
        assert "Error getting info - Pipeline info error" in captured.out

    def test_execute_args_without_detailed_attr(self, capsys):
        """Test execute when args doesn't have detailed attribute."""
        registry = PipelineRegistry()
        config = Config()
        command = ListCommand(registry, config)

        # Register test pipeline
        pipeline = MockPipeline("test", "Test Pipeline")
        registry.register(pipeline)

        # Create args without detailed attribute
        args = Mock()
        del args.detailed  # Remove detailed attribute

        result = command.execute(args)

        assert result == 0
        captured = capsys.readouterr()
        # Should default to simple listing
        assert "test" in captured.out

    def test_list_simple_sorted_output(self, capsys):
        """Test that simple listing outputs pipelines in sorted order."""
        registry = PipelineRegistry()
        config = Config()
        command = ListCommand(registry, config)

        # Register pipelines in non-alphabetical order
        pipeline_z = MockPipeline("z_pipeline", "Z Pipeline")
        pipeline_a = MockPipeline("a_pipeline", "A Pipeline")
        pipeline_m = MockPipeline("m_pipeline", "M Pipeline")

        registry.register(pipeline_z)
        registry.register(pipeline_a)
        registry.register(pipeline_m)

        args = Mock()

        result = command.execute(args)

        assert result == 0
        captured = capsys.readouterr()
        output_lines = captured.out.split("\n")

        # Find lines with pipeline names
        pipeline_lines = [line for line in output_lines if "pipeline" in line]

        # Should be sorted: a_pipeline, m_pipeline, z_pipeline
        a_index = next(
            (i for i, line in enumerate(pipeline_lines) if "a_pipeline" in line), -1
        )
        m_index = next(
            (i for i, line in enumerate(pipeline_lines) if "m_pipeline" in line), -1
        )
        z_index = next(
            (i for i, line in enumerate(pipeline_lines) if "z_pipeline" in line), -1
        )

        assert a_index < m_index < z_index

    def test_list_detailed_sorted_output(self, capsys):
        """Test that detailed listing outputs pipelines in sorted order."""
        registry = PipelineRegistry()
        config = Config()
        command = ListCommand(registry, config)

        # Register pipelines in non-alphabetical order
        pipeline_z = MockPipeline("z_pipeline", "Z Pipeline")
        pipeline_a = MockPipeline("a_pipeline", "A Pipeline")

        registry.register(pipeline_z)
        registry.register(pipeline_a)

        args = Mock()
        args.detailed = True

        result = command.execute(args)

        assert result == 0
        captured = capsys.readouterr()

        # Find positions of pipeline names in output
        a_index = captured.out.find("a_pipeline")
        z_index = captured.out.find("z_pipeline")

        # a_pipeline should appear before z_pipeline
        assert 0 <= a_index < z_index

    def test_list_simple_no_description_fallback(self, capsys):
        """Test simple listing with pipeline that has no description."""
        registry = PipelineRegistry()
        config = Config()
        command = ListCommand(registry, config)

        # Mock pipeline with no description
        registry.list_pipelines = Mock(return_value=["test"])
        registry.get_pipeline_info = Mock(
            return_value={"name": "test"}
        )  # Missing description

        args = Mock()
        args.detailed = False  # Explicitly set to False for simple path

        result = command.execute(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "test" in captured.out
        assert "No description" in captured.out
