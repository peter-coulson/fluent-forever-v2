"""Preview command implementation."""

import webbrowser
from pathlib import Path
from core.registry import PipelineRegistry
from providers.registry import ProviderRegistry
from cli.config.cli_config import CLIConfig
from cli.utils.output import print_success, print_error, print_info
from cli.utils.validation import validate_port


class PreviewCommand:
    """Preview card functionality."""
    
    def __init__(self, pipeline_registry: PipelineRegistry, 
                 provider_registry: ProviderRegistry,
                 project_root: Path, config: CLIConfig):
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
        """Execute preview command.
        
        Args:
            args: Command arguments
            
        Returns:
            Exit code
        """
        # Validate port if provided
        if hasattr(args, 'port') and args.port:
            port_error = validate_port(args.port)
            if port_error:
                print_error(port_error)
                return 1
        
        # Determine action
        if getattr(args, 'start_server', False):
            return self._start_preview_server(args)
        elif getattr(args, 'card_id', None):
            return self._preview_card(args)
        else:
            print_error("Must specify --card-id or --start-server")
            return 1
    
    def _start_preview_server(self, args) -> int:
        """Start multi-card preview server.
        
        Args:
            args: Command arguments
            
        Returns:
            Exit code
        """
        port = getattr(args, 'port', None) or self.config.get_default_port()
        
        try:
            # Import and create the Flask app
            from cli.preview_server_multi import create_app
            
            app = create_app()
            print_success(f"Starting preview server on http://127.0.0.1:{port}")
            print_info("Use Ctrl+C to stop the server")
            
            # Start the server
            app.run(host='127.0.0.1', port=port, debug=False)
            return 0
            
        except ImportError as e:
            print_error(f"Preview server not available: {e}")
            return 1
        except Exception as e:
            print_error(f"Failed to start preview server: {e}")
            return 1
    
    def _preview_card(self, args) -> int:
        """Open specific card in browser.
        
        Args:
            args: Command arguments
            
        Returns:
            Exit code
        """
        card_id = args.card_id
        pipeline_name = args.pipeline
        port = getattr(args, 'port', None) or self.config.get_default_port()
        
        # Verify pipeline exists
        try:
            self.pipeline_registry.get(pipeline_name)
        except Exception as e:
            print_error(f"Pipeline '{pipeline_name}' not found: {e}")
            return 1
        
        # Construct URL
        url = f"http://127.0.0.1:{port}/preview?card_id={card_id}&card_type={pipeline_name}"
        
        try:
            # Open in browser
            webbrowser.open(url)
            print_success(f"Opening card preview: {url}")
            print_info("Make sure the preview server is running on the same port")
            return 0
            
        except Exception as e:
            print_error(f"Failed to open browser: {e}")
            print_info(f"You can manually open: {url}")
            return 1
    
    def _get_available_cards(self, pipeline_name: str) -> list:
        """Get available cards for a pipeline.
        
        Args:
            pipeline_name: Pipeline name
            
        Returns:
            List of available card IDs
        """
        try:
            # This would need to be implemented based on the pipeline's data provider
            data_provider = self.provider_registry.get_data_provider('default')
            if data_provider:
                pipeline = self.pipeline_registry.get(pipeline_name)
                data_file = pipeline.data_file
                
                # Load data and extract card IDs
                data = data_provider.load_data(data_file)
                if isinstance(data, dict) and 'words' in data:
                    # Extract card IDs from vocabulary structure
                    cards = []
                    for word_data in data['words']:
                        if isinstance(word_data, dict) and 'meanings' in word_data:
                            for meaning in word_data['meanings']:
                                if isinstance(meaning, dict) and 'CardID' in meaning:
                                    cards.append(meaning['CardID'])
                    return cards
        except Exception:
            pass
        
        return []