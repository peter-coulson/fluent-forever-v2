"""Unit tests for CLI validation utilities."""

from unittest.mock import Mock, patch

from src.cli.utils.validation import (
    parse_and_validate_config,
    validate_arguments,
    validate_card_list,
    validate_file_path,
    validate_port,
    validate_word_list,
)


class TestValidateArguments:
    """Test argument validation."""

    def test_validate_info_command_valid(self):
        """Test info command with valid arguments."""
        args = Mock()
        args.pipeline = "test_pipeline"

        errors = validate_arguments("info", args)

        assert errors == []

    def test_validate_info_command_missing_pipeline(self):
        """Test info command missing pipeline name."""
        args = Mock()
        args.pipeline = None

        errors = validate_arguments("info", args)

        assert len(errors) == 1
        assert "Pipeline name is required for info command" in errors[0]

    def test_validate_run_command_valid(self):
        """Test run command with valid arguments."""
        args = Mock()
        args.pipeline = "test_pipeline"
        args.stage = "prepare"
        args.dry_run = True  # Dry run skips stage-specific validation

        errors = validate_arguments("run", args)

        assert errors == []

    def test_validate_run_command_missing_pipeline(self):
        """Test run command missing pipeline name."""
        args = Mock()
        args.pipeline = None
        args.stage = "prepare"

        errors = validate_arguments("run", args)

        assert "Pipeline name is required for run command" in errors

    def test_validate_run_command_missing_stage(self):
        """Test run command missing stage name."""
        args = Mock()
        args.pipeline = "test_pipeline"
        args.stage = None

        errors = validate_arguments("run", args)

        assert "Stage name is required for run command" in errors

    def test_validate_run_command_prepare_stage_missing_words(self):
        """Test run command prepare stage missing words."""
        args = Mock()
        args.pipeline = "test_pipeline"
        args.stage = "prepare"
        args.dry_run = False
        args.words = None

        errors = validate_arguments("run", args)

        assert "--words is required for prepare stage" in errors

    def test_validate_run_command_media_stage_missing_cards(self):
        """Test run command media stage missing cards."""
        args = Mock()
        args.pipeline = "test_pipeline"
        args.stage = "media"
        args.dry_run = False
        args.cards = None

        errors = validate_arguments("run", args)

        assert "--cards is required for media stage" in errors

    def test_validate_run_command_dry_run_skips_stage_validation(self):
        """Test dry run skips stage-specific validation."""
        args = Mock()
        args.pipeline = "test_pipeline"
        args.stage = "prepare"
        args.dry_run = True
        args.words = None  # Would normally cause error

        errors = validate_arguments("run", args)

        assert errors == []

    def test_validate_unknown_command(self):
        """Test validation of unknown command."""
        args = Mock()

        errors = validate_arguments("unknown_command", args)

        assert errors == []  # Unknown commands don't have specific validation

    def test_validate_list_command(self):
        """Test list command validation."""
        args = Mock()

        errors = validate_arguments("list", args)

        assert errors == []  # List command has no required arguments


class TestValidateFilePath:
    """Test file path validation."""

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_file")
    def test_validate_file_path_valid(self, mock_is_file, mock_exists):
        """Test validation of valid file path."""
        mock_exists.return_value = True
        mock_is_file.return_value = True

        result = validate_file_path("/path/to/file.txt")

        assert result is None

    @patch("pathlib.Path.exists")
    def test_validate_file_path_not_exists(self, mock_exists):
        """Test validation of non-existent file path."""
        mock_exists.return_value = False

        result = validate_file_path("/path/to/nonexistent.txt")

        assert "File does not exist" in result

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_file")
    def test_validate_file_path_not_file(self, mock_is_file, mock_exists):
        """Test validation of path that exists but is not a file."""
        mock_exists.return_value = True
        mock_is_file.return_value = False

        result = validate_file_path("/path/to/directory")

        assert "Path is not a file" in result


class TestValidateWordList:
    """Test word list validation."""

    def test_validate_word_list_valid(self):
        """Test validation of valid word list."""
        errors = validate_word_list("word1,word2,word3")

        assert errors == []

    def test_validate_word_list_empty_string(self):
        """Test validation of empty word list string."""
        errors = validate_word_list("")

        assert "Word list cannot be empty" in errors

    def test_validate_word_list_none(self):
        """Test validation of None word list."""
        errors = validate_word_list(None)

        assert "Word list cannot be empty" in errors

    def test_validate_word_list_only_commas(self):
        """Test validation of word list with only commas."""
        errors = validate_word_list(",,,")

        assert "No valid words found in word list" in errors

    def test_validate_word_list_with_spaces(self):
        """Test validation of word list with spaces."""
        errors = validate_word_list("word1, word2 , word3")

        assert errors == []  # Spaces should be stripped

    def test_validate_word_list_mixed_empty(self):
        """Test validation of word list with some empty entries."""
        errors = validate_word_list("word1,,word2,")

        assert errors == []  # Empty entries should be filtered out


class TestValidateCardList:
    """Test card list validation."""

    def test_validate_card_list_valid(self):
        """Test validation of valid card list."""
        errors = validate_card_list("card1,card2,card3")

        assert errors == []

    def test_validate_card_list_empty_string(self):
        """Test validation of empty card list string."""
        errors = validate_card_list("")

        assert "Card list cannot be empty" in errors

    def test_validate_card_list_none(self):
        """Test validation of None card list."""
        errors = validate_card_list(None)

        assert "Card list cannot be empty" in errors

    def test_validate_card_list_only_commas(self):
        """Test validation of card list with only commas."""
        errors = validate_card_list(",,,")

        assert "No valid card IDs found in card list" in errors

    def test_validate_card_list_with_spaces(self):
        """Test validation of card list with spaces."""
        errors = validate_card_list("card1, card2 , card3")

        assert errors == []  # Spaces should be stripped

    def test_validate_card_list_mixed_empty(self):
        """Test validation of card list with some empty entries."""
        errors = validate_card_list("card1,,card2,")

        assert errors == []  # Empty entries should be filtered out


class TestValidatePort:
    """Test port validation."""

    def test_validate_port_valid(self):
        """Test validation of valid port numbers."""
        assert validate_port(8000) is None
        assert validate_port(80) is None
        assert validate_port(1) is None
        assert validate_port(65535) is None

    def test_validate_port_too_low(self):
        """Test validation of port number too low."""
        result = validate_port(0)

        assert "Port must be between 1 and 65535" in result

    def test_validate_port_negative(self):
        """Test validation of negative port number."""
        result = validate_port(-1)

        assert "Port must be between 1 and 65535" in result

    def test_validate_port_too_high(self):
        """Test validation of port number too high."""
        result = validate_port(65536)

        assert "Port must be between 1 and 65535" in result


class TestParseAndValidateConfig:
    """Test configuration validation."""

    def test_parse_and_validate_config_valid(self):
        """Test validation of valid configuration."""
        config_dict = {
            "providers": {
                "data": {"type": "json"},
                "media": {"type": "openai"},
                "sync": {"type": "anki"},
            },
            "output": {"format": "table", "verbose": False},
        }

        errors = parse_and_validate_config(config_dict)

        assert errors == []

    def test_parse_and_validate_config_providers_not_dict(self):
        """Test validation of config with providers not being a dict."""
        config_dict = {"providers": "not_a_dict"}

        errors = parse_and_validate_config(config_dict)

        assert "'providers' must be a dictionary" in errors

    def test_parse_and_validate_config_output_not_dict(self):
        """Test validation of config with output not being a dict."""
        config_dict = {"output": "not_a_dict"}

        errors = parse_and_validate_config(config_dict)

        assert "'output' must be a dictionary" in errors

    def test_parse_and_validate_config_empty(self):
        """Test validation of empty configuration."""
        config_dict = {}

        errors = parse_and_validate_config(config_dict)

        assert errors == []

    def test_parse_and_validate_config_multiple_errors(self):
        """Test validation with multiple errors."""
        config_dict = {"providers": "not_a_dict", "output": "also_not_a_dict"}

        errors = parse_and_validate_config(config_dict)

        assert len(errors) == 2
        assert any("'providers' must be a dictionary" in error for error in errors)
        assert any("'output' must be a dictionary" in error for error in errors)

    def test_parse_and_validate_config_nested_structure(self):
        """Test validation of complex nested configuration."""
        config_dict = {
            "providers": {"data": {"type": "json", "config": {"nested": "value"}}},
            "output": {"format": "json", "colors": True},
            "custom_section": {"custom_key": "custom_value"},
        }

        errors = parse_and_validate_config(config_dict)

        assert errors == []
