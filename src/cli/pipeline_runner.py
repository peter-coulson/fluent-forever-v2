#!/usr/bin/env python3
"""
Universal Pipeline Runner

Provides consistent CLI interface for all pipeline operations.
Replaces all hardcoded CLI scripts with unified command structure.
"""

import argparse
from pathlib import Path

# Import command classes
from src.cli.commands import InfoCommand, ListCommand, RunCommand
from src.cli.utils.validation import validate_arguments
from src.core.config import Config
from src.core.exceptions import PipelineError
from src.core.registry import get_pipeline_registry
from src.providers.registry import ProviderRegistry
from src.utils.logging_config import ICONS, setup_logging


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

  # Execution
  %(prog)s run vocabulary --stage prepare --words por,para
  %(prog)s run vocabulary --stage sync --execute

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
    run_parser = subparsers.add_parser("run", help="Run pipeline stage")
    run_parser.add_argument("pipeline", help="Pipeline name")
    run_parser.add_argument("--stage", required=True, help="Stage to execute")
    run_parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done"
    )

    return parser


def main() -> int:
    """Main CLI entry point."""
    setup_logging()
    logger = setup_logging().getChild("cli.pipeline_runner")

    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        # Load configuration
        config = Config.load(getattr(args, "config", None))

        # Setup registries
        pipeline_registry = get_pipeline_registry()
        provider_registry = ProviderRegistry.from_config(config)

        # Register pipelines using centralized system

        project_root = Path(__file__).parents[2]
        # Validate command arguments
        validation_errors = validate_arguments(args.command, args)
        if validation_errors:
            for error in validation_errors:
                logger.error(f"{ICONS['cross']} {error}")
            return 1

        # Execute command
        if args.command == "list":
            command = ListCommand(pipeline_registry, config)
            return command.execute(args)
        elif args.command == "info":
            info_command = InfoCommand(pipeline_registry, config)
            return info_command.execute(args)
        elif args.command == "run":
            run_command = RunCommand(
                pipeline_registry, provider_registry, project_root, config
            )
            return run_command.execute(args)
        else:
            logger.error(f"Unknown command: {args.command}")
            return 1

    except PipelineError as e:
        logger.error(f"{ICONS['cross']} {e}")
        return 1
    except Exception as e:
        logger.error(f"{ICONS['cross']} Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
