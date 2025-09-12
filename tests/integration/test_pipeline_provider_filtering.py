"""Integration tests for pipeline-specific provider filtering."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from src.cli.commands.run_command import RunCommand
from src.core.config import Config
from src.core.context import PipelineContext
from src.core.pipeline import Pipeline
from src.core.registry import PipelineRegistry
from src.core.stages import StageResult
from src.providers.registry import ProviderRegistry


class MockFilteringPipeline(Pipeline):
    """Mock pipeline that tracks provider access for filtering tests."""

    def __init__(self, name="filtering_test"):
        self._name = name
        self.accessed_providers = []
        self.context_received = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def display_name(self) -> str:
        return f"Mock Filtering {self._name.title()}"

    @property
    def stages(self) -> list:
        return ["prepare", "process", "finish"]

    def validate_cli_args(self, args) -> list[str]:
        return []

    def populate_context_from_cli(self, context, args) -> None:
        self.context_received = context
        providers = context.get("providers", {})

        # Track which providers are available
        for provider_type, provider_dict in providers.items():
            for provider_name in provider_dict:
                self.accessed_providers.append(f"{provider_type}:{provider_name}")

    def show_cli_execution_plan(self, context, args) -> None:
        pass

    def execute_stage(self, stage_name: str, context: PipelineContext):
        return StageResult.success_result("Stage completed successfully")

    def get_stage(self, stage_name: str):
        return Mock()

    @property
    def data_file(self) -> str:
        return f"{self._name}.json"

    @property
    def anki_note_type(self) -> str:
        return f"Mock {self._name.title()}"


class TestPipelineProviderFiltering:
    """Integration tests for pipeline-specific provider filtering."""

    def test_end_to_end_pipeline_execution_with_filtering(self):
        """Test complete pipeline execution respects provider filtering."""
        # Create config with pipeline-specific provider assignments
        config_data = {
            "providers": {
                "data": {
                    "vocab_data": {
                        "type": "json",
                        "base_path": ".",
                        "pipelines": ["vocabulary"],
                    },
                    "conjugation_data": {
                        "type": "json",
                        "base_path": ".",
                        "pipelines": ["conjugation"],
                    },
                },
                "audio": {"forvo": {"type": "forvo", "pipelines": ["vocabulary"]}},
                "image": {
                    "runware": {
                        "type": "runware",
                        "pipelines": ["*"],  # Available to all pipelines
                    }
                },
                "sync": {
                    "anki": {"type": "anki", "pipelines": ["vocabulary", "conjugation"]}
                },
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            config = Config(config_path)

            # Mock the providers to avoid requiring actual API keys/Anki
            with (
                patch("src.providers.audio.forvo_provider.ForvoProvider"),
                patch("src.providers.image.runware_provider.RunwareProvider"),
                patch("src.providers.sync.anki_provider.AnkiProvider"),
            ):
                # Create provider registry and pipeline registry
                provider_registry = ProviderRegistry.from_config(config)
                pipeline_registry = PipelineRegistry()

                # Create mock pipelines for vocabulary and conjugation
                vocab_pipeline = MockFilteringPipeline("vocabulary")
                conjugation_pipeline = MockFilteringPipeline("conjugation")

                pipeline_registry.register(vocab_pipeline)
                pipeline_registry.register(conjugation_pipeline)

                # Create run command
                run_command = RunCommand(
                    pipeline_registry, provider_registry, Path("."), config
                )

                # Execute vocabulary pipeline
                vocab_args = Mock()
                vocab_args.pipeline = "vocabulary"
                vocab_args.stage = "prepare"
                vocab_args.dry_run = False

                vocab_result = run_command.execute(vocab_args)

                # Verify vocabulary pipeline execution succeeded
                assert vocab_result == 0

                # Verify vocabulary pipeline received only assigned providers
                vocab_providers = vocab_pipeline.accessed_providers
                assert "data:vocab_data" in vocab_providers
                assert "data:conjugation_data" not in vocab_providers
                assert "audio:forvo" in vocab_providers
                assert "image:runware" in vocab_providers  # Wildcard
                assert "sync:anki" in vocab_providers

                # Execute conjugation pipeline
                conjugation_args = Mock()
                conjugation_args.pipeline = "conjugation"
                conjugation_args.stage = "prepare"
                conjugation_args.dry_run = False

                conjugation_result = run_command.execute(conjugation_args)

                # Verify conjugation pipeline execution succeeded
                assert conjugation_result == 0

                # Verify conjugation pipeline received only assigned providers
                conjugation_providers = conjugation_pipeline.accessed_providers
                assert "data:vocab_data" not in conjugation_providers
                assert "data:conjugation_data" in conjugation_providers
                assert "audio:forvo" not in conjugation_providers
                assert "image:runware" in conjugation_providers  # Wildcard
                assert "sync:anki" in conjugation_providers

        finally:
            Path(config_path).unlink()

    def test_provider_access_validation(self):
        """Test that pipelines cannot access unauthorized providers."""
        # Create config with restricted provider access
        config_data = {
            "providers": {
                "data": {
                    "restricted_data": {
                        "type": "json",
                        "base_path": ".",
                        "pipelines": ["authorized_pipeline"],
                    }
                },
                "sync": {
                    "anki": {
                        "type": "anki",
                        "pipelines": ["*"],  # Universal access
                    }
                },
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            config = Config(config_path)

            with patch("src.providers.sync.anki_provider.AnkiProvider"):
                provider_registry = ProviderRegistry.from_config(config)
                pipeline_registry = PipelineRegistry()

                # Create pipeline that should NOT have access to restricted_data
                unauthorized_pipeline = MockFilteringPipeline("unauthorized_pipeline")
                pipeline_registry.register(unauthorized_pipeline)

                run_command = RunCommand(
                    pipeline_registry, provider_registry, Path("."), config
                )

                # Execute unauthorized pipeline
                args = Mock()
                args.pipeline = "unauthorized_pipeline"
                args.stage = "prepare"
                args.dry_run = False

                result = run_command.execute(args)

                # Pipeline should still execute successfully
                assert result == 0

                # But it should NOT have access to restricted data provider
                accessed_providers = unauthorized_pipeline.accessed_providers
                assert "data:restricted_data" not in accessed_providers
                assert "sync:anki" in accessed_providers  # Should have universal access

        finally:
            Path(config_path).unlink()

    def test_configuration_loading_new_format(self):
        """Test configuration loading handles new format correctly."""
        # Test config with new provider assignment format
        config_data = {
            "providers": {
                "data": {
                    "primary": {
                        "type": "json",
                        "base_path": ".",
                        "pipelines": ["pipeline1", "pipeline2"],
                    },
                    "secondary": {
                        "type": "json",
                        "base_path": ".",
                        "pipelines": ["pipeline3"],
                    },
                },
                "audio": {
                    "service1": {"type": "forvo", "pipelines": ["pipeline1"]},
                    "service2": {"type": "forvo", "pipelines": ["*"]},
                },
                "sync": {
                    "anki": {
                        "type": "anki",
                        "pipelines": ["pipeline1", "pipeline2", "pipeline3"],
                    }
                },
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            config = Config(config_path)

            with (
                patch("src.providers.audio.forvo_provider.ForvoProvider"),
                patch("src.providers.sync.anki_provider.AnkiProvider"),
            ):
                registry = ProviderRegistry.from_config(config)

                # Verify providers were created with correct names
                assert registry.get_data_provider("primary") is not None
                assert registry.get_data_provider("secondary") is not None
                assert registry.get_audio_provider("service1") is not None
                assert registry.get_audio_provider("service2") is not None
                assert registry.get_sync_provider("anki") is not None

                # Verify pipeline assignments were stored correctly
                assert registry.get_pipeline_assignments("data", "primary") == [
                    "pipeline1",
                    "pipeline2",
                ]
                assert registry.get_pipeline_assignments("data", "secondary") == [
                    "pipeline3"
                ]
                assert registry.get_pipeline_assignments("audio", "service1") == [
                    "pipeline1"
                ]
                assert registry.get_pipeline_assignments("audio", "service2") == ["*"]
                assert registry.get_pipeline_assignments("sync", "anki") == [
                    "pipeline1",
                    "pipeline2",
                    "pipeline3",
                ]

                # Test provider filtering for each pipeline
                pipeline1_providers = registry.get_providers_for_pipeline("pipeline1")
                assert "primary" in pipeline1_providers["data"]
                assert "secondary" not in pipeline1_providers["data"]
                assert "service1" in pipeline1_providers["audio"]
                assert "service2" in pipeline1_providers["audio"]  # Wildcard
                assert "anki" in pipeline1_providers["sync"]

                pipeline2_providers = registry.get_providers_for_pipeline("pipeline2")
                assert "primary" in pipeline2_providers["data"]
                assert "secondary" not in pipeline2_providers["data"]
                assert "service1" not in pipeline2_providers["audio"]
                assert "service2" in pipeline2_providers["audio"]  # Wildcard
                assert "anki" in pipeline2_providers["sync"]

                pipeline3_providers = registry.get_providers_for_pipeline("pipeline3")
                assert "primary" not in pipeline3_providers["data"]
                assert "secondary" in pipeline3_providers["data"]
                assert "service1" not in pipeline3_providers["audio"]
                assert "service2" in pipeline3_providers["audio"]  # Wildcard
                assert "anki" in pipeline3_providers["sync"]

        finally:
            Path(config_path).unlink()

    def test_old_config_format_fails_integration(self):
        """Test that old configuration format fails with clear error message."""
        # Test with old config format (should fail)
        config_data = {
            "providers": {
                "data": {"type": "json", "base_path": "."},
                "audio": {"type": "forvo"},
                "sync": {"type": "anki"},
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            config = Config(config_path)

            # Should fail when trying to create provider registry
            with pytest.raises(
                ValueError, match="Configuration uses old format.*named provider"
            ):
                ProviderRegistry.from_config(config)

        finally:
            Path(config_path).unlink()
