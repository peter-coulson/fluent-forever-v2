"""Info command implementation."""

from core.registry import PipelineRegistry
from cli.config.cli_config import CLIConfig
from cli.utils.output import print_error, format_key_value_pairs, format_list


class InfoCommand:
    """Show pipeline information."""
    
    def __init__(self, registry: PipelineRegistry, config: CLIConfig):
        """Initialize command.
        
        Args:
            registry: Pipeline registry
            config: CLI configuration
        """
        self.registry = registry
        self.config = config
    
    def execute(self, args) -> int:
        """Execute info command.
        
        Args:
            args: Command arguments
            
        Returns:
            Exit code
        """
        try:
            info = self.registry.get_pipeline_info(args.pipeline)
            
            # Basic pipeline information
            pairs = [
                ("Pipeline", info['name']),
                ("Display Name", info['display_name']),
                ("Description", info['description']),
                ("Data File", info['data_file']),
                ("Anki Note Type", info['anki_note_type'])
            ]
            
            print(format_key_value_pairs(pairs))
            
            # Stage information
            stages = info.get('stages', [])
            if stages:
                print(f"\nAvailable Stages ({len(stages)}):")
                if getattr(args, 'stages', False):
                    # Detailed stage info
                    for stage_name in stages:
                        try:
                            pipeline = self.registry.get(args.pipeline)
                            stage_info = pipeline.get_stage_info(stage_name)
                            if stage_info:
                                print(f"\n  {stage_name}:")
                                stage_pairs = [
                                    ("    Name", stage_info.get('name', 'N/A')),
                                    ("    Display Name", stage_info.get('display_name', 'N/A')),
                                ]
                                if stage_info.get('dependencies'):
                                    stage_pairs.append(("    Dependencies", ", ".join(stage_info['dependencies'])))
                                print(format_key_value_pairs(stage_pairs, indent=""))
                            else:
                                print(f"  {stage_name}: No detailed info available")
                        except Exception as e:
                            print(f"  {stage_name}: Error getting stage info - {e}")
                else:
                    # Simple stage list
                    print(format_list(stages))
            else:
                print("\nNo stages available")
            
            return 0
            
        except Exception as e:
            print_error(f"Pipeline '{args.pipeline}' not found: {e}")
            return 1