#!/usr/bin/env python3
"""
Universal Pipeline Runner

Provides consistent CLI interface for all pipeline operations.
Replaces all hardcoded CLI scripts with unified command structure.
"""

import argparse
import logging
import os
from pathlib import Path

# Import command classes
from src.cli.commands import InfoCommand, ListCommand, RunCommand
from src.cli.utils.validation import validate_arguments
from src.core.config import Config
from src.core.exceptions import PipelineError
from src.core.registry import get_pipeline_registry
from src.providers.registry import ProviderRegistry
from src.utils.logging_config import ICONS, get_logger, setup_logging


def create_parser() -> argparse.ArgumentParser:
    """Create comprehensive argument parser."""
    parser = argparse.ArgumentParser(
        description="Universal pipeline runner for card creation workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Discovery
  %(prog)s list
  %(prog)s info vocabulary

  # Single stage execution
  %(prog)s run vocabulary --stage prepare --words por,para
  %(prog)s run vocabulary --stage sync --execute

  # Phase execution (multiple stages)
  %(prog)s run vocabulary --phase preparation
  %(prog)s run vocabulary --phase full --dry-run

        """,
    )

    # Global options
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    list_parser = subparsers.add_parser("list", help="List available pipelines")
    list_parser.add_argument(
        "--detailed", action="store_true", help="Show detailed info"
    )

    # Info command
    info_parser = subparsers.add_parser("info", help="Show pipeline information")
    info_parser.add_argument("pipeline", help="Pipeline name")
    info_parser.add_argument(
        "--stages", action="store_true", help="Show available stages"
    )

    # Run command
    run_parser = subparsers.add_parser("run", help="Run pipeline stage or phase")
    run_parser.add_argument("pipeline", help="Pipeline name")

    # Create mutually exclusive group for stage vs phase
    execution_group = run_parser.add_mutually_exclusive_group(required=True)
    execution_group.add_argument("--stage", help="Single stage to execute")
    execution_group.add_argument("--phase", help="Phase (group of stages) to execute")

    run_parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done"
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point."""

    parser = create_parser()
    args = parser.parse_args(argv)

    # Setup logging with verbose mode
    if getattr(args, "verbose", False) or os.getenv("FLUENT_FOREVER_DEBUG"):
        # Only enable file logging in verbose mode if not in test environment
        # or if explicitly requested via environment variable
        enable_file_logging = (
            os.getenv("FLUENT_FOREVER_LOG_TO_FILE", "false").lower() == "true"
        )
        setup_logging(level=logging.DEBUG, log_to_file=enable_file_logging)
    else:
        setup_logging()

    logger = get_logger("cli.runner")
    logger.info(f"{ICONS['gear']} Starting Fluent Forever v2 Pipeline Runner")

    logger.info(f"{ICONS['info']} Command: {args.command or 'none'}")
    logger.debug(f"Full arguments: {vars(args)}")

    if not args.command:
        parser.print_help()
        return 1

    try:
        # Load configuration
        logger.info(f"{ICONS['gear']} Loading configuration...")
        config = Config.load(getattr(args, "config", None))
        logger.info(f"{ICONS['check']} Configuration loaded successfully")

        # Setup registries
        logger.info(f"{ICONS['gear']} Initializing registries...")
        pipeline_registry = get_pipeline_registry()
        provider_registry = ProviderRegistry.from_config(config)
        logger.info(f"{ICONS['check']} Registries initialized")

        # Register pipelines using centralized system

        project_root = Path(__file__).parents[2]
        # Validate command arguments
        validation_errors = validate_arguments(args.command, args)
        if validation_errors:
            for error in validation_errors:
                logger.error(f"{ICONS['cross']} {error}")
            return 1

        # Execute command
        logger.info(f"{ICONS['gear']} Executing {args.command} command...")
        if args.command == "list":
            command = ListCommand(pipeline_registry, config)
            result = command.execute(args)
        elif args.command == "info":
            info_command = InfoCommand(pipeline_registry, config)
            result = info_command.execute(args)
        elif args.command == "run":
            run_command = RunCommand(
                pipeline_registry, provider_registry, project_root, config
            )
            result = run_command.execute(args)
        else:
            logger.error(f"Unknown command: {args.command}")
            return 1

        if result == 0:
            logger.info(f"{ICONS['check']} Command completed successfully")
        return result

    except PipelineError as e:
        logger.error(f"{ICONS['cross']} Pipeline error: {e}")
        return 1
    except Exception as e:
        logger.error(f"{ICONS['cross']} Unexpected error: {e}")
        logger.debug("Full error details:", exc_info=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
