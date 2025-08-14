#!/usr/bin/env python3
"""
Validate that local Anki templates (HTML/CSS) match those currently in Anki.

- Compares files under templates/anki/<note_type_sanitized>/ against AnkiConnect
  model templates and styling for the configured note type.
- Logs unified diffs for any differences.
- Returns True (exit 0) if identical, otherwise False (exit 1).

Usage:
  python validate_anki_templates.py
"""

import json
import difflib
import sys
import re
from pathlib import Path

# Ensure src is importable
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from utils.logging_config import setup_logging, ICONS  # noqa: E402
from apis.anki_client import AnkiClient  # noqa: E402


def sanitize_name(name: str) -> str:
    """Filesystem-safe folder for note type (mirror export naming)."""
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", name.strip())
    safe = re.sub(r"_+", "_", safe).strip("_")
    return safe or "template"


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding='utf-8')


def diff_and_log(logger, label: str, a_text: str, b_text: str) -> bool:
    """Return True if equal; otherwise log a unified diff and return False."""
    if a_text == b_text:
        logger.info(f"{ICONS['check']} {label}: MATCH")
        return True

    logger.error(f"{ICONS['cross']} {label}: DIFFERS")
    a_lines = a_text.splitlines(keepends=True)
    b_lines = b_text.splitlines(keepends=True)
    diff = difflib.unified_diff(
        a_lines,
        b_lines,
        fromfile=f"local/{label}",
        tofile=f"anki/{label}",
        lineterm=""
    )
    for line in diff:
        # Print diff lines directly; logger formatting keeps colors minimal
        logger.error(line.rstrip("\n"))
    return False


def validate_templates() -> bool:
    logger = setup_logging()
    logger.info(f"{ICONS['search']} Validating local templates against Anki...")

    client = AnkiClient()
    if not client.test_connection():
        logger.error(f"{ICONS['cross']} Cannot connect to AnkiConnect. Open Anki and enable AnkiConnect.")
        return False

    note_type = client.note_type
    base_dir = PROJECT_ROOT / 'templates' / 'anki' / sanitize_name(note_type)
    manifest_path = base_dir / 'manifest.json'
    css_path = base_dir / 'styling.css'
    templates_dir = base_dir / 'templates'

    if not manifest_path.exists():
        logger.error(f"{ICONS['cross']} Missing manifest.json at {manifest_path}")
        return False

    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    except Exception as e:
        logger.error(f"{ICONS['cross']} Failed to read manifest.json: {e}")
        return False

    # Fetch from Anki
    tmpl_resp = client.get_model_templates()
    if not tmpl_resp.success:
        logger.error(f"{ICONS['cross']} Failed to fetch Anki templates: {tmpl_resp.error_message}")
        return False
    anki_templates = tmpl_resp.data or {}

    css_resp = client.get_model_styling()
    if not css_resp.success:
        logger.error(f"{ICONS['cross']} Failed to fetch Anki styling: {css_resp.error_message}")
        return False
    anki_css = ''
    if isinstance(css_resp.data, dict):
        anki_css = css_resp.data.get('css', '')
    else:
        anki_css = str(css_resp.data or '')

    # Compare CSS
    local_css = read_text(css_path)
    all_match = diff_and_log(logger, 'styling.css', local_css, anki_css)

    # Build local map from manifest
    local_templates_map = {t['name']: t for t in manifest.get('templates', []) if 'name' in t}

    # Check for missing/extra templates
    local_names = set(local_templates_map.keys())
    anki_names = set(anki_templates.keys())

    extra_local = sorted(local_names - anki_names)
    missing_local = sorted(anki_names - local_names)

    if extra_local:
        all_match = False
        logger.error(f"{ICONS['cross']} Extra local templates not in Anki: {extra_local}")
    if missing_local:
        all_match = False
        logger.error(f"{ICONS['cross']} Templates present in Anki but missing locally: {missing_local}")

    # Compare shared templates' front/back HTML
    shared = sorted(local_names & anki_names)
    for name in shared:
        entry = local_templates_map[name]
        front_rel = entry.get('front', '')
        back_rel = entry.get('back', '')

        front_local = read_text(base_dir / front_rel)
        back_local = read_text(base_dir / back_rel)

        anki_tpl = anki_templates.get(name, {}) or {}
        anki_front = anki_tpl.get('Front', '') if isinstance(anki_tpl, dict) else ''
        anki_back = anki_tpl.get('Back', '') if isinstance(anki_tpl, dict) else ''

        if not diff_and_log(logger, f"{name} - Front", front_local, anki_front):
            all_match = False
        if not diff_and_log(logger, f"{name} - Back", back_local, anki_back):
            all_match = False

    if all_match:
        logger.info(f"{ICONS['check']} Templates and styling match Anki for note type '{note_type}'.")
    else:
        logger.error(f"{ICONS['cross']} Differences found between local templates and Anki for '{note_type}'.")

    return all_match


if __name__ == "__main__":
    ok = validate_templates()
    sys.exit(0 if ok else 1)


