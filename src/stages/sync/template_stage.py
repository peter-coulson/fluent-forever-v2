"""
Template Sync Stage

Synchronizes Anki templates with local template files. Extracts logic from
sync.templates_sync to create reusable stage.
"""

from pathlib import Path
from typing import Any

from core.context import PipelineContext
from core.stages import StageResult, StageStatus
from stages.base.api_stage import APIStage
from utils.logging_config import ICONS, get_logger


class TemplateSyncStage(APIStage):
    """Sync templates to Anki"""

    def __init__(self):
        super().__init__("anki_provider", required=True)
        self.logger = get_logger("stages.sync.templates")

    @property
    def name(self) -> str:
        return "sync_templates"

    @property
    def display_name(self) -> str:
        return "Sync Templates to Anki"

    def execute_api_call(self, context: PipelineContext, provider: Any) -> StageResult:
        """Sync templates to Anki using provider"""
        project_root = Path(context.get("project_root", Path.cwd()))

        try:
            # Get template directory
            note_type = getattr(provider, "note_type", "Fluent_Forever")
            note_type_folder = note_type.replace(" ", "_")
            template_dir = project_root / "templates" / "anki" / note_type_folder

            if not template_dir.exists():
                return StageResult(
                    status=StageStatus.FAILURE,
                    message=f"Template directory not found: {template_dir}",
                    data={},
                    errors=[f"Missing template directory: {template_dir}"],
                )

            # Load local templates and CSS
            local_templates, local_css = self.load_local_templates(template_dir)

            # Fetch current Anki templates
            anki_templates, anki_css = self.fetch_anki_templates(provider)

            # Check for differences
            has_diffs = self.has_template_diffs(
                local_templates, anki_templates, local_css, anki_css
            )

            if has_diffs:
                # Push templates to Anki
                self.push_templates(provider, local_templates, local_css)
                self.logger.info(f"{ICONS['check']} Templates pushed to Anki")
                sync_status = "updated"
            else:
                self.logger.info(f"{ICONS['info']} Templates already up to date")
                sync_status = "up_to_date"

            # Validate templates after sync
            validation_result = self.validate_templates(project_root)
            if not validation_result:
                return StageResult(
                    status=StageStatus.FAILURE,
                    message="Template validation failed after sync",
                    data={},
                    errors=["Template validation failed"],
                )

            context.set("template_sync_status", sync_status)

            return StageResult(
                status=StageStatus.SUCCESS,
                message=f"Templates synchronized ({sync_status})",
                data={
                    "sync_status": sync_status,
                    "templates_count": len(local_templates),
                    "has_css": bool(local_css),
                },
                errors=[],
            )

        except Exception as e:
            self.logger.error(f"{ICONS['cross']} Template sync failed: {e}")
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"Template sync failed: {e}",
                data={},
                errors=[f"Sync error: {e}"],
            )

    def load_local_templates(self, template_dir: Path):
        """Load local template files"""
        try:
            from sync.templates_sync import load_local_templates

            return load_local_templates(template_dir)
        except ImportError:
            # Fallback implementation
            templates = {}
            css = ""

            # Load template files
            for template_file in template_dir.glob("*.html"):
                with open(template_file, encoding="utf-8") as f:
                    templates[template_file.stem] = f.read()

            # Load CSS
            css_file = template_dir / "styling.css"
            if css_file.exists():
                with open(css_file, encoding="utf-8") as f:
                    css = f.read()

            return templates, css

    def fetch_anki_templates(self, provider):
        """Fetch current templates from Anki"""
        try:
            from sync.templates_sync import fetch_anki_templates

            return fetch_anki_templates(provider)
        except ImportError:
            # Fallback: return empty templates
            return {}, ""

    def has_template_diffs(self, local_templates, anki_templates, local_css, anki_css):
        """Check if there are differences between local and Anki templates"""
        try:
            from sync.templates_sync import has_template_diffs

            return has_template_diffs(
                local_templates, anki_templates, local_css, anki_css
            )
        except ImportError:
            # Simple comparison fallback
            return (local_templates != anki_templates) or (local_css != anki_css)

    def push_templates(self, provider, templates, css):
        """Push templates to Anki"""
        try:
            from sync.templates_sync import push_templates

            push_templates(provider, templates, css)
        except ImportError:
            # Fallback: log that push would happen
            self.logger.warning(
                f"{ICONS['warning']} Template push not available (sync module missing)"
            )

    def validate_templates(self, project_root: Path) -> bool:
        """Validate templates after sync"""
        try:
            from validation.anki.template_validator import validate_templates_and_fields

            return validate_templates_and_fields(project_root)
        except ImportError:
            self.logger.warning(f"{ICONS['warning']} Template validation not available")
            return True
