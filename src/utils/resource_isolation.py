"""Resource isolation utilities for multi-pipeline support."""

from pathlib import Path
from typing import Any, Optional


def get_pipeline_media_paths(
    pipeline_name: str, project_root: Optional[Path] = None
) -> dict[str, Path]:
    """Get pipeline-specific media paths for resource isolation.

    Args:
        pipeline_name: Name of the pipeline
        project_root: Project root directory (defaults to current directory)

    Returns:
        Dictionary of media paths for this pipeline
    """
    if project_root is None:
        project_root = Path.cwd()

    # For backward compatibility, vocabulary uses the root media directory
    if pipeline_name == "vocabulary":
        base_media = project_root / "media"
        return {
            "base": base_media,
            "images": base_media / "images",
            "audio": base_media / "audio",
            "index": base_media / ".index.json",
        }

    # Other pipelines get their own subdirectories
    pipeline_media = project_root / "media" / pipeline_name
    return {
        "base": pipeline_media,
        "images": pipeline_media / "images",
        "audio": pipeline_media / "audio",
        "index": pipeline_media / ".index.json",
    }


def get_pipeline_template_paths(
    pipeline_name: str, anki_note_type: str, project_root: Optional[Path] = None
) -> dict[str, Path]:
    """Get pipeline-specific template paths for resource isolation.

    Args:
        pipeline_name: Name of the pipeline
        anki_note_type: Anki note type (e.g., 'Fluent Forever', 'Conjugation')
        project_root: Project root directory (defaults to current directory)

    Returns:
        Dictionary of template paths for this pipeline
    """
    if project_root is None:
        project_root = Path.cwd()

    template_base = project_root / "templates" / "anki" / anki_note_type
    return {
        "base": template_base,
        "front": template_base / "front.html",
        "back": template_base / "back.html",
        "styling": template_base / "styling.css",
        "manifest": template_base / "manifest.json",
    }


def get_pipeline_data_paths(
    pipeline_name: str, data_file: str, project_root: Optional[Path] = None
) -> dict[str, Path]:
    """Get pipeline-specific data paths for resource isolation.

    Args:
        pipeline_name: Name of the pipeline
        data_file: Primary data file name (e.g., 'vocabulary.json', 'conjugations.json')
        project_root: Project root directory (defaults to current directory)

    Returns:
        Dictionary of data paths for this pipeline
    """
    if project_root is None:
        project_root = Path.cwd()

    return {
        "base": project_root,
        "data_file": project_root / data_file,
        "staging": project_root / "staging",
        "config": project_root / "config" / "pipelines" / f"{pipeline_name}.json",
    }


def ensure_pipeline_directories(
    pipeline_name: str, anki_note_type: str, data_file: str, project_root: Optional[Path] = None
) -> None:
    """Ensure all required directories exist for a pipeline.

    Args:
        pipeline_name: Name of the pipeline
        anki_note_type: Anki note type
        data_file: Primary data file name
        project_root: Project root directory (defaults to current directory)
    """
    if project_root is None:
        project_root = Path.cwd()

    # Ensure media directories
    media_paths = get_pipeline_media_paths(pipeline_name, project_root)
    for path in media_paths.values():
        if path.suffix != ".json":  # Skip index file
            path.mkdir(parents=True, exist_ok=True)

    # Ensure template directories
    template_paths = get_pipeline_template_paths(
        pipeline_name, anki_note_type, project_root
    )
    template_paths["base"].mkdir(parents=True, exist_ok=True)

    # Ensure data directories
    data_paths = get_pipeline_data_paths(pipeline_name, data_file, project_root)
    data_paths["staging"].mkdir(parents=True, exist_ok=True)


def validate_pipeline_isolation(
    pipeline_name: str, anki_note_type: str
) -> dict[str, Any]:
    """Validate that pipeline resource isolation is working correctly.

    Args:
        pipeline_name: Name of the pipeline
        anki_note_type: Anki note type

    Returns:
        Validation results with any issues found
    """
    issues = []
    warnings = []

    project_root = Path.cwd()

    # Check media path isolation
    media_paths = get_pipeline_media_paths(pipeline_name, project_root)
    if pipeline_name != "vocabulary":
        # Non-vocabulary pipelines should have separate media directories
        if media_paths["base"] == project_root / "media":
            issues.append(
                f"Pipeline '{pipeline_name}' not properly isolated - using root media directory"
            )

    # Check template path isolation
    template_paths = get_pipeline_template_paths(
        pipeline_name, anki_note_type, project_root
    )
    expected_template_base = project_root / "templates" / "anki" / anki_note_type
    if template_paths["base"] != expected_template_base:
        issues.append(f"Pipeline '{pipeline_name}' template path mismatch")

    # Check for template conflicts
    for other_pipeline in ["vocabulary", "conjugation"]:
        if other_pipeline == pipeline_name:
            continue

        other_note_type = (
            "Fluent Forever" if other_pipeline == "vocabulary" else "Conjugation"
        )
        other_paths = get_pipeline_template_paths(
            other_pipeline, other_note_type, project_root
        )

        if template_paths["base"] == other_paths["base"]:
            issues.append(
                f"Template path conflict between '{pipeline_name}' and '{other_pipeline}'"
            )

    # Check data file isolation
    data_paths = get_pipeline_data_paths(
        pipeline_name,
        f"{pipeline_name}s.json"
        if pipeline_name != "vocabulary"
        else "vocabulary.json",
        project_root,
    )
    if not str(data_paths["data_file"]).endswith(".json"):
        warnings.append(f"Data file for '{pipeline_name}' should be a JSON file")

    return {"issues": issues, "warnings": warnings, "isolated": len(issues) == 0}
