"""Info command implementation."""

from typing import Any

from src.cli.utils.output import format_key_value_pairs, format_list, print_error
from src.core.config import Config
from src.core.registry import PipelineRegistry
from src.utils.logging_config import ICONS, get_logger


class InfoCommand:
    """Show pipeline information."""

    def __init__(self, registry: PipelineRegistry, config: Config):
        """Initialize command.

        Args:
            registry: Pipeline registry
            config: CLI configuration
        """
        self.registry = registry
        self.config = config
        self.logger = get_logger("cli.commands.info")

    def execute(self, args: Any) -> int:
        """Execute info command.

        Args:
            args: Command arguments

        Returns:
            Exit code
        """
        self.logger.info(
            f"{ICONS['search']} Getting info for pipeline '{args.pipeline}'"
        )

        try:
            info = self.registry.get_pipeline_info(args.pipeline)
            self.logger.debug(f"Retrieved pipeline info: {info}")

            # Basic pipeline information
            pairs = [
                ("Pipeline", info["name"]),
                ("Display Name", info["display_name"]),
                ("Description", info["description"]),
                ("Data File", info["data_file"]),
                ("Anki Note Type", info["anki_note_type"]),
            ]

            print(format_key_value_pairs(pairs))

            # Stage information
            stages = info.get("stages", [])
            if stages:
                print(f"\nAvailable Stages ({len(stages)}):")
                if getattr(args, "stages", False):
                    # Detailed stage info
                    for stage_name in stages:
                        try:
                            pipeline = self.registry.get(args.pipeline)
                            stage_info = pipeline.get_stage_info(stage_name)
                            if stage_info:
                                print(f"\n  {stage_name}:")
                                stage_pairs = [
                                    ("    Name", stage_info.get("name", "N/A")),
                                    (
                                        "    Display Name",
                                        stage_info.get("display_name", "N/A"),
                                    ),
                                ]
                                if stage_info.get("dependencies"):
                                    stage_pairs.append(
                                        (
                                            "    Dependencies",
                                            ", ".join(stage_info["dependencies"]),
                                        )
                                    )
                                print(format_key_value_pairs(stage_pairs, indent=""))
                            else:
                                self.logger.warning(
                                    f"{ICONS['warning']} No detailed info available for stage '{stage_name}'"
                                )
                                print(f"  {stage_name}: No detailed info available")
                        except Exception as e:
                            self.logger.error(
                                f"{ICONS['cross']} Error getting stage info for '{stage_name}': {e}"
                            )
                            print(f"  {stage_name}: Error getting stage info - {e}")
                else:
                    # Simple stage list
                    print(format_list(stages))
            else:
                print("\nNo stages available")

            return 0

        except Exception as e:
            self.logger.error(
                f"{ICONS['cross']} Pipeline '{args.pipeline}' not found: {e}"
            )
            print_error(f"Pipeline '{args.pipeline}' not found: {e}")
            return 1
