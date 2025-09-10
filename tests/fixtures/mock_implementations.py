"""Mock implementations for testing the Fluent Forever framework"""

from pathlib import Path
from typing import Any

from src.core.context import PipelineContext
from src.core.pipeline import Pipeline
from src.core.stages import Stage, StageResult
from src.providers.base.data_provider import DataProvider
from src.providers.base.media_provider import MediaProvider, MediaRequest, MediaResult
from src.providers.base.sync_provider import SyncProvider, SyncResult


class MockDataProvider(DataProvider):
    """Mock data provider for testing"""

    def __init__(self):
        super().__init__()
        self.data_storage: dict[str, dict[str, Any]] = {}
        self.should_fail = False
        self.fail_on_save = False

    def _load_data_impl(self, identifier: str) -> dict[str, Any]:
        if self.should_fail:
            raise ValueError(f"Mock failure loading {identifier}")
        return self.data_storage.get(identifier, {})

    def _save_data_impl(self, identifier: str, data: dict[str, Any]) -> bool:
        if self.should_fail or self.fail_on_save:
            return False
        self.data_storage[identifier] = data
        return True

    def exists(self, identifier: str) -> bool:
        return identifier in self.data_storage

    def list_identifiers(self) -> list[str]:
        return list(self.data_storage.keys())

    def backup_data(self, identifier: str) -> str | None:
        if self.should_fail:
            return None
        if identifier in self.data_storage:
            backup_id = f"{identifier}_backup"
            self.data_storage[backup_id] = self.data_storage[identifier].copy()
            return backup_id
        return None


class MockMediaProvider(MediaProvider):
    """Mock media provider for testing"""

    def __init__(self, provider_type: str = "audio"):
        super().__init__()
        self.provider_type = provider_type
        self.should_fail = False
        self.generated_files: list[Path] = []

    @property
    def supported_types(self) -> list[str]:
        return [self.provider_type]

    def get_service_info(self) -> dict[str, Any]:
        return {
            "service": f"Mock{self.provider_type.title()}Provider",
            "type": f"{self.provider_type}_provider",
            "supported_languages": ["es", "en"],
        }

    def _generate_media_impl(self, request: MediaRequest) -> MediaResult:
        if self.should_fail:
            return MediaResult(
                success=False,
                file_path=None,
                metadata={},
                error="Mock provider failure",
            )

        if request.type not in self.supported_types:
            return MediaResult(
                success=False,
                file_path=None,
                metadata={},
                error=f"Unsupported media type: {request.type}",
            )

        # Create mock file path
        if request.output_path:
            file_path = request.output_path
        else:
            file_path = Path(f"mock_{request.type}_{request.content}.mp3")

        self.generated_files.append(file_path)

        return MediaResult(
            success=True,
            file_path=file_path,
            metadata={
                "content": request.content,
                "type": request.type,
                "provider": "mock",
            },
        )

    def estimate_cost(self, request: MediaRequest) -> float:
        return 0.0

    def get_cost_estimate(self, requests: list[MediaRequest]) -> dict[str, float]:
        supported_requests = [
            req for req in requests if req.type in self.supported_types
        ]
        return {
            "total_cost": 0.0,
            "per_request": 0.0,
            "requests_count": len(supported_requests),
        }


class MockSyncProvider(SyncProvider):
    """Mock sync provider for testing"""

    def __init__(self):
        super().__init__()
        self.should_fail = False
        self.synced_data: list[dict[str, Any]] = []
        self.synced_templates: list[dict[str, Any]] = []
        self.synced_media: list[Path] = []

    def _test_connection_impl(self) -> bool:
        return not self.should_fail

    def get_service_info(self) -> dict[str, Any]:
        return {
            "service": "MockSyncProvider",
            "type": "sync_provider",
            "supported_note_types": ["Basic", "Cloze"],
        }

    def sync_templates(self, note_type: str, templates: list[dict]) -> SyncResult:
        if self.should_fail:
            return SyncResult(
                success=False,
                processed_count=0,
                metadata={},
                error_message="Mock template sync failure",
            )

        self.synced_templates.extend(templates)
        return SyncResult(
            success=True,
            processed_count=len(templates),
            metadata={"note_type": note_type, "templates_synced": len(templates)},
        )

    def sync_media(self, media_files: list[Path]) -> SyncResult:
        if self.should_fail:
            return SyncResult(
                success=False,
                processed_count=0,
                metadata={},
                error_message="Mock media sync failure",
            )

        self.synced_media.extend(media_files)
        return SyncResult(
            success=True,
            processed_count=len(media_files),
            metadata={"media_synced": len(media_files)},
        )

    def _sync_cards_impl(self, cards: list[dict[str, Any]]) -> SyncResult:
        if self.should_fail:
            return SyncResult(
                success=False,
                processed_count=0,
                metadata={},
                error_message="Mock card sync failure",
            )

        self.synced_data.extend(cards)
        return SyncResult(
            success=True,
            processed_count=len(cards),
            metadata={"cards_synced": len(cards)},
        )

    def list_existing(self, note_type: str) -> list[dict]:
        if self.should_fail:
            return []

        # Return mock existing data
        return [
            {"id": "mock1", "note_type": note_type, "fields": {"word": "existing1"}},
            {"id": "mock2", "note_type": note_type, "fields": {"word": "existing2"}},
        ]


class MockStage(Stage):
    """Mock stage for testing pipeline execution"""

    def __init__(
        self, name: str, should_fail: bool = False, requires_provider: str | None = None
    ):
        super().__init__()
        self._name = name
        self.should_fail = should_fail
        self.requires_provider = requires_provider
        self.execution_count = 0

    @property
    def name(self) -> str:
        return self._name

    @property
    def display_name(self) -> str:
        return f"Mock {self._name.title()} Stage"

    def _execute_impl(self, context: PipelineContext) -> StageResult:
        self.execution_count += 1

        if self.should_fail:
            return StageResult.failure(
                f"Mock stage {self.name} failed intentionally",
                [f"Mock error in {self.name}"],
            )

        # Add some data to context
        context.set(f"{self.name}_executed", True)
        context.set(f"{self.name}_execution_count", self.execution_count)

        return StageResult.success_result(
            f"Mock stage {self.name} completed successfully",
            {
                "stage_name": self.name,
                "execution_count": self.execution_count,
                "context_keys": list(context.data.keys()),
            },
        )

    def validate_context(self, context: PipelineContext) -> list[str]:
        errors = []
        if self.requires_provider:
            provider = context.get("providers", {}).get(self.requires_provider)
            if not provider:
                errors.append(
                    f"Required provider {self.requires_provider} not available"
                )
        return errors


class MockPipeline(Pipeline):
    """Mock pipeline for testing framework functionality"""

    def __init__(self, name: str = "mock", stages: list[Stage] | None = None):
        self._name = name
        self._stages = stages or [
            MockStage("prepare"),
            MockStage("process", requires_provider="data"),
            MockStage("finalize"),
        ]
        self._stage_map = {stage.name: stage for stage in self._stages}

    @property
    def name(self) -> str:
        return self._name

    @property
    def display_name(self) -> str:
        # Replace underscores with spaces and title case properly
        display_name = self._name.replace("_", " ")
        # Avoid double "Pipeline" if name already ends with "pipeline"
        if display_name.lower().endswith("pipeline"):
            return f"Mock {display_name.title()}"
        else:
            return f"Mock {display_name.title()} Pipeline"

    @property
    def stages(self) -> list[str]:
        return [stage.name for stage in self._stages]

    @property
    def data_file(self) -> str:
        return f"{self._name}.json"

    @property
    def anki_note_type(self) -> str:
        # Replace underscores with empty for anki note type
        clean_name = self._name.replace("_", "")
        return f"Mock{clean_name.title()}"

    def get_stage(self, stage_name: str) -> Stage:
        if stage_name not in self._stage_map:
            from src.core.exceptions import StageNotFoundError

            raise StageNotFoundError(
                f"Stage '{stage_name}' not found in pipeline '{self.name}'"
            )
        return self._stage_map[stage_name]

    def validate_cli_args(self, args: Any) -> list[str]:
        errors = []
        if hasattr(args, "required_arg") and not args.required_arg:
            errors.append("Mock pipeline requires --required-arg")
        return errors

    def populate_context_from_cli(self, context: PipelineContext, args: Any) -> None:
        context.set("cli_args", vars(args))
        context.set("pipeline_name", self.name)

    def show_cli_execution_plan(self, context: PipelineContext, args: Any) -> None:
        print(f"Mock execution plan for {self.name}:")
        if hasattr(args, "stage"):
            print(f"  - Would execute stage: {args.stage}")
        print(f"  - Context keys: {list(context.data.keys())}")
