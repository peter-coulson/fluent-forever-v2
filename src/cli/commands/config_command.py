"""
Configuration Management CLI Commands

Provides commands for viewing, validating, and managing configuration.
"""

import json

from core.config import get_config_manager
from core.config_validator import ConfigValidator


class ConfigCommand:
    """Configuration management commands"""

    def __init__(self):
        self.config_manager = get_config_manager()
        self.validator = ConfigValidator()

    def execute(self, args) -> int:
        """Execute config command"""
        if args.action == "show":
            return self._show_config(args)
        elif args.action == "validate":
            return self._validate_config(args)
        elif args.action == "init":
            return self._init_config(args)
        elif args.action == "test":
            return self._test_config(args)
        else:
            print(f"Unknown config action: {args.action}")
            return 1

    def _show_config(self, args) -> int:
        """Show current configuration"""
        try:
            if args.type and args.name:
                config = self.config_manager.load_config(args.type, args.name)
                print(f"Configuration for {args.type}:{args.name}")
                print(json.dumps(config, indent=2))
            elif args.type:
                config = self.config_manager.load_config(args.type)
                print(f"Configuration for {args.type}")
                print(json.dumps(config, indent=2))
            else:
                # Show system configuration
                config = self.config_manager.load_config("system")
                print("System Configuration:")
                print(json.dumps(config, indent=2))
            return 0
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return 1

    def _validate_config(self, args) -> int:
        """Validate configuration"""
        try:
            # Validate system configuration
            is_valid = self.config_manager.validate_config()

            if is_valid:
                print("✅ Configuration is valid")

                # Also validate with detailed validator
                system_config = self.config_manager.load_config("system")
                result = self.validator.validate(system_config)

                if result.is_valid:
                    print("✅ Detailed validation passed")
                    return 0
                else:
                    print("❌ Detailed validation failed:")
                    for error in result.errors:
                        print(f"  - {error}")
                    return 1
            else:
                print("❌ Configuration validation failed")
                return 1
        except Exception as e:
            print(f"Error validating configuration: {e}")
            return 1

    def _init_config(self, args) -> int:
        """Initialize configuration files"""
        try:
            # Check if config files already exist
            config_dir = self.config_manager.base_path / "config"
            if config_dir.exists() and any(config_dir.glob("*.json")):
                print("Configuration files already exist")
                return 0

            print("Configuration files already initialized")
            print(f"Configuration directory: {config_dir}")
            return 0
        except Exception as e:
            print(f"Error initializing configuration: {e}")
            return 1

    def _test_config(self, args) -> int:
        """Test configuration loading and provider initialization"""
        try:
            # Test configuration loading
            print("Testing configuration loading...")

            system_config = self.config_manager.load_config("system")
            print(f"✅ System config loaded ({len(system_config)} sections)")

            vocab_config = self.config_manager.get_pipeline_config("vocabulary")
            print("✅ Vocabulary pipeline config loaded")

            openai_config = self.config_manager.get_provider_config("openai")
            print("✅ OpenAI provider config loaded")

            # Test validation
            print("\nTesting validation...")
            is_valid = self.config_manager.validate_config()
            if is_valid:
                print("✅ Configuration validation passed")
            else:
                print("❌ Configuration validation failed")
                return 1

            # Test environment overrides
            print("\nTesting environment overrides...")
            import os

            original_env = os.environ.get("FF_SYSTEM_LOG_LEVEL")
            os.environ["FF_SYSTEM_LOG_LEVEL"] = "ERROR"
            self.config_manager.clear_cache()

            test_config = self.config_manager.load_config("system")
            log_level = test_config.get("system", {}).get("log_level")
            print(f"Environment override test - log level: {log_level}")

            # Restore environment
            if original_env:
                os.environ["FF_SYSTEM_LOG_LEVEL"] = original_env
            else:
                os.environ.pop("FF_SYSTEM_LOG_LEVEL", None)
            self.config_manager.clear_cache()

            print("✅ All configuration tests passed")
            return 0

        except Exception as e:
            print(f"Configuration test failed: {e}")
            return 1


def add_config_arguments(parser):
    """Add configuration command arguments to parser"""
    config_parser = parser.add_parser("config", help="Configuration management")
    config_parser.add_argument(
        "action",
        choices=["show", "validate", "init", "test"],
        help="Configuration action to perform",
    )
    config_parser.add_argument(
        "--type",
        choices=["system", "pipeline", "provider", "cli"],
        help="Configuration type",
    )
    config_parser.add_argument(
        "--name", help="Configuration name (for pipeline/provider types)"
    )
    return config_parser
