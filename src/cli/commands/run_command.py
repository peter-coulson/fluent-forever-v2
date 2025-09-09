"""Run command implementation."""

from pathlib import Path

from src.cli.config.cli_config import CLIConfig
from src.cli.utils.output import print_error, print_success, print_warning
from src.cli.utils.validation import (
    validate_arguments,
    validate_card_list,
    validate_word_list,
)
from src.core.context import PipelineContext
from src.core.registry import PipelineRegistry
from src.providers.registry import ProviderRegistry


class RunCommand:
    """Execute pipeline stages."""

    def __init__(
        self,
        pipeline_registry: PipelineRegistry,
        provider_registry: ProviderRegistry,
        project_root: Path,
        config: CLIConfig,
    ):
        """Initialize command.

        Args:
            pipeline_registry: Pipeline registry
            provider_registry: Provider registry
            project_root: Project root directory
            config: CLI configuration
        """
        self.pipeline_registry = pipeline_registry
        self.provider_registry = provider_registry
        self.project_root = project_root
        self.config = config

    def execute(self, args) -> int:
        """Execute run command.

        Args:
            args: Command arguments

        Returns:
            Exit code
        """
        # Validate arguments
        validation_errors = validate_arguments("run", args)
        if validation_errors:
            for error in validation_errors:
                print_error(error)
            return 1

        # Additional stage-specific validation (skip for dry-run)
        if not getattr(args, "dry_run", False):
            stage_errors = self._validate_stage_args(args)
            if stage_errors:
                for error in stage_errors:
                    print_error(error)
                return 1

        try:
            pipeline = self.pipeline_registry.get(args.pipeline)
        except Exception as e:
            print_error(f"Pipeline '{args.pipeline}' not found: {e}")
            return 1

        # Create execution context
        context = PipelineContext(
            pipeline_name=args.pipeline,
            project_root=self.project_root,
            config=self.config.to_dict(),
            args=vars(args),
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

        # Parse command arguments into context
        self._populate_context(context, args)

        # Handle dry-run
        if getattr(args, "dry_run", False):
            print_warning(
                f"DRY RUN: Would execute stage '{args.stage}' on pipeline '{args.pipeline}'"
            )
            self._show_execution_plan(context, args)
            return 0

        # Execute stage
        try:
            result = pipeline.execute_stage(args.stage, context)

            if result.status.value == "success":
                print_success(result.message)
                return 0
            elif result.status.value == "partial":
                print_warning(f"Partial success: {result.message}")
                if result.errors:
                    print("Errors encountered:")
                    for error in result.errors:
                        print(f"  - {error}")
                return 0
            else:
                print_error(result.message)
                if result.errors:
                    print("Errors:")
                    for error in result.errors:
                        print(f"  - {error}")
                return 1

        except Exception as e:
            print_error(f"Error executing stage '{args.stage}': {e}")
            return 1

    def _validate_stage_args(self, args) -> list:
        """Validate stage-specific arguments.

        Args:
            args: Command arguments

        Returns:
            List of validation errors
        """
        errors = []

        if args.stage == "prepare":
            if args.words:
                errors.extend(validate_word_list(args.words))
        elif args.stage == "media":
            if args.cards:
                errors.extend(validate_card_list(args.cards))

        return errors

    def _populate_context(self, context: PipelineContext, args) -> None:
        """Populate context from command arguments.

        Args:
            context: Pipeline context
            args: Command arguments
        """
        # Vocabulary-specific arguments
        if getattr(args, "words", None):
            context.set(
                "words", [w.strip() for w in args.words.split(",") if w.strip()]
            )

        # Conjugation-specific arguments
        if getattr(args, "verbs", None):
            context.set(
                "verbs", [v.strip() for v in args.verbs.split(",") if v.strip()]
            )
        if getattr(args, "tenses", None):
            context.set(
                "tenses", [t.strip() for t in args.tenses.split(",") if t.strip()]
            )
        if getattr(args, "persons", None):
            context.set(
                "persons", [p.strip() for p in args.persons.split(",") if p.strip()]
            )

        # Common arguments
        if getattr(args, "cards", None):
            context.set(
                "cards", [c.strip() for c in args.cards.split(",") if c.strip()]
            )
        if getattr(args, "file", None):
            context.set("input_file", Path(args.file))

        # Set execution flags
        context.set("execute", getattr(args, "execute", False))
        context.set("skip_images", getattr(args, "no_images", False))
        context.set("skip_audio", getattr(args, "no_audio", False))
        context.set("dry_run", getattr(args, "dry_run", False))
        context.set("force_regenerate", getattr(args, "force_regenerate", False))
        context.set("max_new", getattr(args, "max", None))
        context.set("delete_extras", getattr(args, "delete_extras", False))

    def _show_execution_plan(self, context: PipelineContext, args) -> None:
        """Show execution plan for dry run.

        Args:
            context: Pipeline context
            args: Command arguments
        """
        print("\nExecution Plan:")
        print(f"  Pipeline: {args.pipeline}")
        print(f"  Stage: {args.stage}")

        if context.get("words"):
            print(f"  Words: {', '.join(context.get('words'))}")
        if context.get("verbs"):
            print(f"  Verbs: {', '.join(context.get('verbs'))}")
        if context.get("tenses"):
            print(f"  Tenses: {', '.join(context.get('tenses'))}")
        if context.get("persons"):
            print(f"  Persons: {', '.join(context.get('persons'))}")
        if context.get("cards"):
            print(f"  Cards: {', '.join(context.get('cards'))}")
        if context.get("input_file"):
            print(f"  Input file: {context.get('input_file')}")

        # Show relevant flags
        flags = []
        if context.get("execute"):
            flags.append("execute")
        if context.get("skip_images"):
            flags.append("skip-images")
        if context.get("skip_audio"):
            flags.append("skip-audio")
        if context.get("force_regenerate"):
            flags.append("force-regenerate")
        if context.get("delete_extras"):
            flags.append("delete-extras")

        if flags:
            print(f"  Flags: {', '.join(flags)}")

        print()  # Empty line for readability
