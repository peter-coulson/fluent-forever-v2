"""List command implementation."""

from src.cli.config.cli_config import CLIConfig
from src.cli.utils.output import format_table, print_info
from src.core.registry import PipelineRegistry


class ListCommand:
    """List available pipelines."""

    def __init__(self, registry: PipelineRegistry, config: CLIConfig):
        """Initialize command.

        Args:
            registry: Pipeline registry
            config: CLI configuration
        """
        self.registry = registry
        self.config = config

    def execute(self, args) -> int:
        """Execute list command.

        Args:
            args: Command arguments

        Returns:
            Exit code
        """
        pipelines = self.registry.list_pipelines()

        if not pipelines:
            print_info("No pipelines registered")
            return 0

        if getattr(args, "detailed", False):
            return self._list_detailed(pipelines)
        else:
            return self._list_simple(pipelines)

    def _list_simple(self, pipelines: list[str]) -> int:
        """Simple pipeline listing.

        Args:
            pipelines: List of pipeline names

        Returns:
            Exit code
        """
        print("Available pipelines:")
        for pipeline in sorted(pipelines):
            try:
                info = self.registry.get_pipeline_info(pipeline)
                print(f"  - {pipeline}: {info.get('description', 'No description')}")
            except Exception as e:
                print(f"  - {pipeline}: Error getting info - {e}")
        return 0

    def _list_detailed(self, pipelines: list[str]) -> int:
        """Detailed pipeline listing.

        Args:
            pipelines: List of pipeline names

        Returns:
            Exit code
        """
        rows = []
        for pipeline_name in sorted(pipelines):
            try:
                info = self.registry.get_pipeline_info(pipeline_name)
                rows.append(
                    [
                        pipeline_name,
                        info.get("display_name", "N/A"),
                        len(info.get("stages", [])),
                        info.get("anki_note_type", "N/A"),
                        info.get("data_file", "N/A"),
                    ]
                )
            except Exception as e:
                rows.append([pipeline_name, f"Error: {e}", "N/A", "N/A", "N/A"])

        headers = ["Name", "Display Name", "Stages", "Anki Note Type", "Data File"]
        print(format_table(headers, rows))
        return 0
