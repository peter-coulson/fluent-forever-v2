"""
Configuration Validation

Validates configuration files and provides detailed error reporting.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ValidationResult:
    """Result of configuration validation"""

    is_valid: bool
    errors: list[str]
    warnings: list[str]


class ConfigValidator:
    """Validates configuration files and data structures"""

    def __init__(self):
        self.required_sections = {
            "system": ["log_level", "cache_enabled", "max_concurrent_requests"],
            "paths": [],  # Paths section is required but fields are flexible
            "pipelines": [],  # Must exist but content is flexible
            "providers": [],  # Must exist but content is flexible
        }

    def validate(self, config: dict[str, Any]) -> ValidationResult:
        """Validate a complete configuration"""
        errors = []
        warnings = []

        # Check required top-level sections
        for section, required_fields in self.required_sections.items():
            if section not in config:
                errors.append(f"Missing required section: {section}")
                continue

            # Check required fields in section
            section_config = config[section]
            if not isinstance(section_config, dict):
                errors.append(f"Section {section} must be a dictionary")
                continue

            for field in required_fields:
                if field not in section_config:
                    errors.append(
                        f"Missing required field {field} in section {section}"
                    )

        # Validate pipeline configurations
        if "pipelines" in config:
            pipeline_errors = self._validate_pipelines(config["pipelines"])
            errors.extend(pipeline_errors)

        # Validate provider configurations
        if "providers" in config:
            provider_errors = self._validate_providers(config["providers"])
            errors.extend(provider_errors)

        return ValidationResult(
            is_valid=len(errors) == 0, errors=errors, warnings=warnings
        )

    def _validate_pipelines(self, pipelines: dict[str, Any]) -> list[str]:
        """Validate pipeline configurations"""
        errors = []

        for pipeline_name, pipeline_config in pipelines.items():
            if not isinstance(pipeline_config, dict):
                errors.append(f"Pipeline {pipeline_name} must be a dictionary")
                continue

            # Check if there's a pipeline section within the config
            if "pipeline" in pipeline_config:
                # Validate the nested pipeline section
                nested_pipeline = pipeline_config["pipeline"]
                if "stages" not in nested_pipeline:
                    errors.append(
                        f"Pipeline {pipeline_name} pipeline section missing required field: stages"
                    )
                elif not isinstance(nested_pipeline["stages"], list):
                    errors.append(f"Pipeline {pipeline_name} stages must be a list")
            else:
                # Direct pipeline config format
                if "stages" not in pipeline_config:
                    errors.append(
                        f"Pipeline {pipeline_name} missing required field: stages"
                    )
                elif not isinstance(pipeline_config["stages"], list):
                    errors.append(f"Pipeline {pipeline_name} stages must be a list")

        return errors

    def _validate_providers(self, providers: dict[str, Any]) -> list[str]:
        """Validate provider configurations"""
        errors = []

        for provider_name, provider_config in providers.items():
            if not isinstance(provider_config, dict):
                errors.append(f"Provider {provider_name} must be a dictionary")

        return errors
