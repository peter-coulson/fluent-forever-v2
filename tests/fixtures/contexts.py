"""Context and data fixtures for E2E testing."""

from pathlib import Path
from typing import Any

from src.core.context import PipelineContext


def create_test_context(
    pipeline_name: str = "test_pipeline",
    project_root: Path | None = None,
    data: dict[str, Any] | None = None,
    config: dict[str, Any] | None = None,
    args: dict[str, Any] | None = None,
) -> PipelineContext:
    """Create a test pipeline context with default values."""
    if project_root is None:
        project_root = Path.cwd()

    context = PipelineContext(
        pipeline_name=pipeline_name,
        project_root=project_root,
        data=data or {},
        config=config or {},
        args=args or {},
    )
    return context


def create_context_with_providers(providers: dict[str, Any]) -> PipelineContext:
    """Create context with providers for testing provider-dependent stages."""
    context = create_test_context()
    context.set("providers", providers)
    return context


def create_context_with_dependencies() -> PipelineContext:
    """Create context with completed dependencies for testing dependency validation."""
    context = create_test_context()
    context.mark_stage_complete("test_stage")
    context.set("required_data", "test_value")
    return context


def create_context_with_errors() -> PipelineContext:
    """Create context with existing errors for testing error handling."""
    context = create_test_context()
    context.add_error("Previous stage failed")
    context.add_error("Missing required data")
    return context


def create_context_with_cli_args(args: dict[str, Any]) -> PipelineContext:
    """Create context with CLI arguments for testing CLI integration."""
    context = create_test_context(args=args)
    return context


def create_vocabulary_context() -> PipelineContext:
    """Create context for vocabulary pipeline testing."""
    context = create_test_context("vocabulary")
    context.set("words", ["casa", "perro", "gato"])
    context.set("target_language", "spanish")
    context.set("source_language", "english")
    return context


def create_conjugation_context() -> PipelineContext:
    """Create context for conjugation pipeline testing."""
    context = create_test_context("conjugation")
    context.set("verbs", ["hablar", "comer", "vivir"])
    context.set("tenses", ["present", "preterite", "imperfect"])
    return context


def create_context_with_data_providers() -> PipelineContext:
    """Create context with mock data providers."""
    from tests.fixtures.providers import MockDataProvider

    providers = {
        "data": {
            "test_data": MockDataProvider(Path("."), read_only=False),
            "readonly_data": MockDataProvider(Path("."), read_only=True),
        },
        "audio": {},
        "image": {},
        "sync": {},
    }
    return create_context_with_providers(providers)


def create_context_with_all_providers() -> PipelineContext:
    """Create context with all types of mock providers."""
    from tests.fixtures.providers import (
        MockAudioProvider,
        MockDataProvider,
        MockImageProvider,
        MockSyncProvider,
    )

    providers = {
        "data": {
            "main_data": MockDataProvider(Path("."), read_only=False),
        },
        "audio": {
            "forvo": MockAudioProvider({"api_key": "test_key"}),
        },
        "image": {
            "openai": MockImageProvider({"api_key": "test_key"}),
        },
        "sync": {
            "anki": MockSyncProvider({"anki_connect_url": "http://localhost:8765"}),
        },
    }
    return create_context_with_providers(providers)


def create_performance_test_context() -> PipelineContext:
    """Create context with data for performance testing."""
    context = create_test_context("performance_test")

    # Add large dataset for performance testing
    large_words = [f"word_{i}" for i in range(1000)]
    context.set("words", large_words)
    context.set("batch_size", 50)
    context.set("performance_monitoring", True)

    return context


def create_context_with_partial_completion() -> PipelineContext:
    """Create context with some stages completed for testing resumption."""
    context = create_test_context()
    context.mark_stage_complete("prepare")
    context.mark_stage_complete("validate")
    context.set("preparation_data", {"status": "completed"})
    context.set("validation_results", {"errors": 0, "warnings": 2})
    return context


def create_context_with_configuration() -> PipelineContext:
    """Create context with realistic configuration data."""
    config = {
        "providers": {
            "data": {
                "main": {"type": "json", "base_path": "data"},
            },
            "audio": {
                "forvo": {"type": "forvo", "api_key": "test_key"},
            },
        },
        "system": {
            "log_level": "DEBUG",
            "max_retries": 3,
        },
    }
    return create_test_context(config=config)


def create_execution_contexts() -> dict[str, PipelineContext]:
    """Create various contexts for different execution scenarios."""
    return {
        "basic": create_test_context(),
        "with_providers": create_context_with_all_providers(),
        "with_dependencies": create_context_with_dependencies(),
        "with_errors": create_context_with_errors(),
        "vocabulary": create_vocabulary_context(),
        "conjugation": create_conjugation_context(),
        "performance": create_performance_test_context(),
        "partial": create_context_with_partial_completion(),
        "configured": create_context_with_configuration(),
    }


class ContextBuilder:
    """Builder pattern for creating test contexts with specific configurations."""

    def __init__(self, pipeline_name: str = "test_pipeline"):
        self.pipeline_name = pipeline_name
        self.project_root = Path.cwd()
        self.data: dict[str, Any] = {}
        self.config: dict[str, Any] = {}
        self.args: dict[str, Any] = {}
        self.completed_stages: list[str] = []
        self.errors: list[str] = []

    def with_data(self, key: str, value: Any) -> "ContextBuilder":
        """Add data to context."""
        self.data[key] = value
        return self

    def with_config(self, config: dict[str, Any]) -> "ContextBuilder":
        """Set configuration."""
        self.config = config
        return self

    def with_args(self, args: dict[str, Any]) -> "ContextBuilder":
        """Set CLI arguments."""
        self.args = args
        return self

    def with_completed_stage(self, stage_name: str) -> "ContextBuilder":
        """Mark stage as completed."""
        self.completed_stages.append(stage_name)
        return self

    def with_error(self, error: str) -> "ContextBuilder":
        """Add error to context."""
        self.errors.append(error)
        return self

    def with_providers(self, providers: dict[str, Any]) -> "ContextBuilder":
        """Add providers to context."""
        self.data["providers"] = providers
        return self

    def build(self) -> PipelineContext:
        """Build the context."""
        context = PipelineContext(
            pipeline_name=self.pipeline_name,
            project_root=self.project_root,
            data=self.data,
            config=self.config,
            args=self.args,
        )

        # Apply completed stages
        for stage in self.completed_stages:
            context.mark_stage_complete(stage)

        # Apply errors
        for error in self.errors:
            context.add_error(error)

        return context
