"""Unit tests for CLI commands."""

from pathlib import Path
from unittest.mock import Mock, patch

from cli.commands.info_command import InfoCommand
from cli.commands.list_command import ListCommand
from cli.commands.preview_command import PreviewCommand
from cli.commands.run_command import RunCommand
from cli.config.cli_config import CLIConfig


class TestListCommand:
    """Test ListCommand."""

    def test_execute_simple(self, capsys):
        """Test simple list execution."""
        # Setup
        registry = Mock()
        registry.list_pipelines.return_value = ["vocabulary", "conjugation"]
        registry.get_pipeline_info.side_effect = [
            {"description": "Vocab pipeline"},
            {"description": "Conjugation pipeline"},
        ]

        config = CLIConfig({})
        command = ListCommand(registry, config)
        args = Mock(detailed=False)

        # Execute
        result = command.execute(args)

        # Verify
        assert result == 0
        captured = capsys.readouterr()
        assert "vocabulary" in captured.out
        assert "conjugation" in captured.out

    def test_execute_detailed(self, capsys):
        """Test detailed list execution."""
        # Setup
        registry = Mock()
        registry.list_pipelines.return_value = ["vocabulary"]
        registry.get_pipeline_info.return_value = {
            "display_name": "Vocabulary Pipeline",
            "stages": ["prepare", "media"],
            "anki_note_type": "Fluent Forever",
            "data_file": "vocabulary.json",
        }

        config = CLIConfig({})
        command = ListCommand(registry, config)
        args = Mock(detailed=True)

        # Execute
        result = command.execute(args)

        # Verify
        assert result == 0
        captured = capsys.readouterr()
        assert "vocabulary" in captured.out
        assert "Vocabulary Pipeline" in captured.out

    def test_execute_no_pipelines(self, capsys):
        """Test execution with no pipelines."""
        # Setup
        registry = Mock()
        registry.list_pipelines.return_value = []
        config = CLIConfig({})
        command = ListCommand(registry, config)
        args = Mock(detailed=False)

        # Execute
        result = command.execute(args)

        # Verify
        assert result == 0
        captured = capsys.readouterr()
        assert "No pipelines registered" in captured.out


class TestInfoCommand:
    """Test InfoCommand."""

    def test_execute_basic_info(self, capsys):
        """Test basic info execution."""
        # Setup
        registry = Mock()
        registry.get_pipeline_info.return_value = {
            "name": "vocabulary",
            "display_name": "Vocabulary Pipeline",
            "description": "Test pipeline",
            "data_file": "vocabulary.json",
            "anki_note_type": "Fluent Forever",
            "stages": ["prepare", "media"],
        }

        config = CLIConfig({})
        command = InfoCommand(registry, config)
        args = Mock(pipeline="vocabulary", stages=False)

        # Execute
        result = command.execute(args)

        # Verify
        assert result == 0
        captured = capsys.readouterr()
        assert "vocabulary" in captured.out
        assert "Vocabulary Pipeline" in captured.out
        assert "prepare" in captured.out

    def test_execute_pipeline_not_found(self, capsys):
        """Test info execution with missing pipeline."""
        # Setup
        registry = Mock()
        registry.get_pipeline_info.side_effect = Exception("Pipeline not found")

        config = CLIConfig({})
        command = InfoCommand(registry, config)
        args = Mock(pipeline="nonexistent")

        # Execute
        result = command.execute(args)

        # Verify
        assert result == 1
        captured = capsys.readouterr()
        assert "not found" in captured.out


class TestRunCommand:
    """Test RunCommand."""

    def test_execute_success(self, capsys):
        """Test successful run execution."""
        # Setup
        pipeline_registry = Mock()
        provider_registry = Mock()
        config = CLIConfig({})
        project_root = Path("/test")

        # Mock pipeline
        pipeline = Mock()
        stage_result = Mock()
        stage_result.status.value = "success"
        stage_result.message = "Stage completed successfully"
        stage_result.data = {"result": "test"}
        stage_result.errors = []
        pipeline.execute_stage.return_value = stage_result
        pipeline_registry.get.return_value = pipeline

        command = RunCommand(pipeline_registry, provider_registry, project_root, config)
        args = Mock(
            pipeline="vocabulary",
            stage="prepare",
            words="test1,test2",
            verbs=None,
            tenses=None,
            persons=None,
            dry_run=False,
            execute=False,
            cards=None,
            file=None,
            no_images=False,
            no_audio=False,
            force_regenerate=False,
            max=None,
            delete_extras=False,
        )

        # Execute
        result = command.execute(args)

        # Verify
        assert result == 0
        captured = capsys.readouterr()
        assert "Stage completed successfully" in captured.out
        pipeline_registry.get.assert_called_once_with("vocabulary")
        pipeline.execute_stage.assert_called_once()

    def test_execute_dry_run(self, capsys):
        """Test dry-run execution."""
        # Setup
        pipeline_registry = Mock()
        provider_registry = Mock()
        config = CLIConfig({})
        project_root = Path("/test")

        command = RunCommand(pipeline_registry, provider_registry, project_root, config)
        args = Mock(
            pipeline="vocabulary",
            stage="prepare",
            dry_run=True,
            words="test1",
            verbs=None,
            tenses=None,
            persons=None,
            cards=None,
            file=None,
            execute=False,
            no_images=False,
            no_audio=False,
            force_regenerate=False,
            max=None,
            delete_extras=False,
        )

        # Execute
        result = command.execute(args)

        # Verify
        assert result == 0
        captured = capsys.readouterr()
        assert "DRY RUN" in captured.out
        assert "vocabulary" in captured.out
        assert "prepare" in captured.out

    def test_execute_pipeline_not_found(self, capsys):
        """Test execution with missing pipeline."""
        # Setup
        pipeline_registry = Mock()
        pipeline_registry.get.side_effect = Exception("Pipeline not found")
        provider_registry = Mock()
        config = CLIConfig({})
        project_root = Path("/test")

        command = RunCommand(pipeline_registry, provider_registry, project_root, config)
        args = Mock(
            pipeline="nonexistent",
            stage="prepare",
            dry_run=False,
            words="test1",
            cards=None,
            file=None,
        )

        # Execute
        result = command.execute(args)

        # Verify
        assert result == 1
        captured = capsys.readouterr()
        assert "not found" in captured.out


class TestPreviewCommand:
    """Test PreviewCommand."""

    def test_execute_card_preview(self):
        """Test card preview execution."""
        # Setup
        pipeline_registry = Mock()
        pipeline_registry.get.return_value = Mock()  # Pipeline exists
        provider_registry = Mock()
        config = CLIConfig({})
        project_root = Path("/test")

        command = PreviewCommand(
            pipeline_registry, provider_registry, project_root, config
        )
        args = Mock(pipeline="vocabulary", card_id="test_card", start_server=False)
        args.port = 8000

        with patch("webbrowser.open") as mock_browser:
            result = command.execute(args)

        # Verify
        assert result == 0
        mock_browser.assert_called_once()
        expected_url = (
            "http://127.0.0.1:8000/preview?card_id=test_card&card_type=vocabulary"
        )
        mock_browser.assert_called_with(expected_url)

    def test_execute_missing_args(self, capsys):
        """Test preview with missing arguments."""
        # Setup
        pipeline_registry = Mock()
        provider_registry = Mock()
        config = CLIConfig({})
        project_root = Path("/test")

        command = PreviewCommand(
            pipeline_registry, provider_registry, project_root, config
        )
        args = Mock(pipeline="vocabulary", card_id=None, start_server=False)
        args.port = 8000

        # Execute
        result = command.execute(args)

        # Verify
        assert result == 1
        captured = capsys.readouterr()
        assert "Must specify" in captured.out

    def test_execute_start_server_not_supported(self, capsys):
        """Test that preview server functionality is no longer supported."""
        # Setup
        pipeline_registry = Mock()
        provider_registry = Mock()
        config = CLIConfig({})
        project_root = Path("/test")

        command = PreviewCommand(
            pipeline_registry, provider_registry, project_root, config
        )
        args = Mock(pipeline="vocabulary", start_server=True, card_id=None)
        args.port = 8001

        # Execute - should indicate preview functionality is stripped
        result = command.execute(args)

        # Verify - command should fail or indicate functionality not available
        # The exact behavior will depend on the PreviewCommand implementation after stripping
        assert result in [1, 2]  # Some error code indicating unsupported functionality

    def test_execute_pipeline_not_found(self, capsys):
        """Test preview with missing pipeline."""
        # Setup
        pipeline_registry = Mock()
        pipeline_registry.get.side_effect = Exception("Pipeline not found")
        provider_registry = Mock()
        config = CLIConfig({})
        project_root = Path("/test")

        command = PreviewCommand(
            pipeline_registry, provider_registry, project_root, config
        )
        args = Mock(pipeline="nonexistent", card_id="test_card", start_server=False)
        args.port = 8000

        # Execute
        result = command.execute(args)

        # Verify
        assert result == 1
        captured = capsys.readouterr()
        assert "not found" in captured.out
