"""Argument validation utilities for CLI commands."""

from pathlib import Path
from typing import Any


def validate_arguments(command: str, args: Any) -> list[str]:
    """Validate command arguments.

    Args:
        command: Command name
        args: Parsed arguments

    Returns:
        List of validation errors
    """
    errors = []

    if command == "info":
        if not args.pipeline:
            errors.append("Pipeline name is required for info command")

    elif command == "run":
        if not args.pipeline:
            errors.append("Pipeline name is required for run command")
        if not args.stage:
            errors.append("Stage name is required for run command")

        # Validate stage-specific arguments (skip for dry-run)
        if not getattr(args, "dry_run", False):
            if args.stage == "prepare" and not args.words:
                errors.append("--words is required for prepare stage")
            elif args.stage == "media" and not args.cards:
                errors.append("--cards is required for media stage")

    elif command == "preview":
        if not args.pipeline:
            errors.append("Pipeline name is required for preview command")
        if not args.start_server and not args.card_id:
            errors.append(
                "Either --start-server or --card-id must be specified for preview"
            )

    return errors


def validate_file_path(file_path: str) -> str | None:
    """Validate file path exists.

    Args:
        file_path: Path to validate

    Returns:
        Error message if invalid, None if valid
    """
    path = Path(file_path)
    if not path.exists():
        return f"File does not exist: {file_path}"
    if not path.is_file():
        return f"Path is not a file: {file_path}"
    return None


def validate_word_list(words: str) -> list[str]:
    """Validate word list format.

    Args:
        words: Comma-separated word list

    Returns:
        List of validation errors
    """
    errors = []
    if not words:
        errors.append("Word list cannot be empty")
        return errors

    word_list = [w.strip() for w in words.split(",") if w.strip()]
    if not word_list:
        errors.append("No valid words found in word list")

    return errors


def validate_card_list(cards: str) -> list[str]:
    """Validate card ID list format.

    Args:
        cards: Comma-separated card ID list

    Returns:
        List of validation errors
    """
    errors = []
    if not cards:
        errors.append("Card list cannot be empty")
        return errors

    card_list = [c.strip() for c in cards.split(",") if c.strip()]
    if not card_list:
        errors.append("No valid card IDs found in card list")

    return errors


def validate_port(port: int) -> str | None:
    """Validate port number.

    Args:
        port: Port number

    Returns:
        Error message if invalid, None if valid
    """
    if port < 1 or port > 65535:
        return f"Port must be between 1 and 65535, got {port}"
    return None


def parse_and_validate_config(config_dict: dict[str, Any]) -> list[str]:
    """Parse and validate configuration dictionary.

    Args:
        config_dict: Configuration to validate

    Returns:
        List of validation errors
    """
    errors = []

    # Add specific validation rules for CLI configuration
    if "providers" in config_dict:
        providers = config_dict["providers"]
        if not isinstance(providers, dict):
            errors.append("'providers' must be a dictionary")

    if "output" in config_dict:
        output = config_dict["output"]
        if not isinstance(output, dict):
            errors.append("'output' must be a dictionary")

    return errors
