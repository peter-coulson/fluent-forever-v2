#!/usr/bin/env python3
"""
Universal Pipeline Runner

Provides consistent CLI interface for all pipeline operations.
Replaces all hardcoded CLI scripts with unified command structure.
"""

import argparse
from pathlib import Path
from typing import Any

# Import command classes
from src.cli.commands import InfoCommand, ListCommand, PreviewCommand, RunCommand
from src.cli.config.cli_config import CLIConfig
from src.cli.utils.validation import validate_arguments
from src.core.context import PipelineContext
from src.core.exceptions import PipelineError
from src.core.registry import get_pipeline_registry
from src.providers.registry import get_provider_registry
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

  # Preview
  %(prog)s preview vocabulary --card-id lo_neuter_article
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

    # Common run arguments (extract from existing scripts)
    run_parser.add_argument("--words", help="Comma-separated word list")
    run_parser.add_argument(
        "--verbs", help="Comma-separated verb list (for conjugation pipeline)"
    )
    run_parser.add_argument("--cards", help="Comma-separated card IDs")
    run_parser.add_argument("--file", help="Input file path")
    run_parser.add_argument("--execute", action="store_true", help="Execute changes")
    run_parser.add_argument(
        "--no-images", action="store_true", help="Skip image generation"
    )
    run_parser.add_argument(
        "--no-audio", action="store_true", help="Skip audio generation"
    )
    run_parser.add_argument(
        "--force-regenerate", action="store_true", help="Force regeneration"
    )
    run_parser.add_argument("--max", type=int, help="Maximum items to process")
    run_parser.add_argument(
        "--delete-extras", action="store_true", help="Delete extra items"
    )
    run_parser.add_argument(
        "--tenses", help="Comma-separated tense list (for conjugation pipeline)"
    )
    run_parser.add_argument(
        "--persons", help="Comma-separated person list (for conjugation pipeline)"
    )

    # Preview command
    preview_parser = subparsers.add_parser("preview", help="Preview cards")
    preview_parser.add_argument("pipeline", help="Pipeline name")
    preview_parser.add_argument("--card-id", help="Card ID to preview")
    preview_parser.add_argument(
        "--port", type=int, default=8000, help="Preview server port"
    )
    preview_parser.add_argument(
        "--start-server", action="store_true", help="Start preview server"
    )

    return parser


class PipelineRunner:
    """Pipeline runner class for programmatic access."""

    def __init__(self, config: CLIConfig | None = None):
        """Initialize pipeline runner.

        Args:
            config: Optional CLI configuration
        """
        self.config = config or CLIConfig.load()
        self.pipeline_registry = get_pipeline_registry()
        self.provider_registry = get_provider_registry()
        self.project_root = Path(__file__).parents[2]

        # Initialize providers from configuration
        self.config.initialize_providers(self.provider_registry)

        # Register pipelines
        self._register_pipelines()

    def _register_pipelines(self) -> None:
        """Register available pipelines."""
        # Use the centralized pipeline registration

    def list_pipelines(self) -> list[str]:
        """List available pipelines.

        Returns:
            List of pipeline names
        """
        return self.pipeline_registry.list_pipelines()

    def get_pipeline_info(self, pipeline_name: str) -> dict[str, Any]:
        """Get pipeline information.

        Args:
            pipeline_name: Name of pipeline

        Returns:
            Pipeline information dictionary
        """
        return self.pipeline_registry.get_pipeline_info(pipeline_name)

    def execute_stage(
        self, pipeline_name: str, stage_name: str, context_data: dict[str, Any]
    ) -> Any:
        """Execute a pipeline stage.

        Args:
            pipeline_name: Name of pipeline
            stage_name: Name of stage
            context_data: Context data

        Returns:
            Stage execution result
        """
        pipeline = self.pipeline_registry.get(pipeline_name)

        context = PipelineContext(
            pipeline_name=pipeline_name,
            project_root=self.project_root,
            config=self.config.to_dict(),
            data=context_data,
        )

        # Add providers to context
        context.set(
            "providers",
            {
                "data": self.provider_registry.get_data_provider("default"),
                "media": self.provider_registry.get_media_provider("default"),
                "sync": self.provider_registry.get_sync_provider("default"),
            },
        )

        return pipeline.execute_stage(stage_name, context)


def main() -> int:
    """Main CLI entry point."""
    setup_logging()
    logger = setup_logging().getChild("cli.pipeline_runner")

    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Load configuration
    config = CLIConfig.load(getattr(args, "config", None))

    # Setup registries
    pipeline_registry = get_pipeline_registry()
    provider_registry = get_provider_registry()

    # Initialize providers from config
    config.initialize_providers(provider_registry)

    # Register pipelines using centralized system

    project_root = Path(__file__).parents[2]

    try:
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
            command = InfoCommand(pipeline_registry, config)
            return command.execute(args)
        elif args.command == "run":
            command = RunCommand(
                pipeline_registry, provider_registry, project_root, config
            )
            return command.execute(args)
        elif args.command == "preview":
            command = PreviewCommand(
                pipeline_registry, provider_registry, project_root, config
            )
            return command.execute(args)
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
