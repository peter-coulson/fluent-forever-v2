#!/usr/bin/env python3
"""
Anki Template Validator

Validates that local Anki templates (HTML/CSS) under templates/anki/<note_type>/
match the templates in Anki, and checks template field usage against the model
fields and configured schema fields.

Returns True if:
 - CSS and HTML match Anki exactly, and
 - No unknown placeholders are used in templates, and
 - Config vs Anki field names are consistent (ignoring non‑Anki fields in config).
"""

from __future__ import annotations

import json
import difflib
import re
from pathlib import Path
from typing import Set, Dict

from utils.logging_config import get_logger, setup_logging, ICONS
from apis.anki_client import AnkiClient
from apis.base_client import BaseAPIClient


logger = get_logger('validation.anki.templates')


def _sanitize_name(name: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", name.strip())
    safe = re.sub(r"_+", "_", safe).strip("_")
    return safe or "template"


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding='utf-8')


def _diff_and_log(label: str, a_text: str, b_text: str) -> bool:
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
        logger.error(line.rstrip("\n"))
    return False


def _extract_placeholders(html: str) -> Set[str]:
    # Matches {{...}} and captures the name, stripping section markers (#/^)
    names: Set[str] = set()
    for match in re.finditer(r"{{\s*([#\^/]?)([^}\s]+)[^}]*}}", html):
        raw = match.group(2)
        if raw:
            names.add(raw)
    return names


def validate_templates_and_fields(project_root: Path | None = None) -> bool:
    if project_root is None:
        project_root = Path(__file__).parent.parent.parent.parent

    # Ensure logging is configured for console output
    setup_logging()
    logger.info(f"{ICONS['search']} Validating local templates against Anki...")

    # Load config & Anki model info
    config = BaseAPIClient.load_config(project_root / 'config.json')
    anki = AnkiClient()
    if not anki.test_connection():
        logger.error(f"{ICONS['cross']} Cannot connect to AnkiConnect. Open Anki and enable AnkiConnect.")
        return False

    note_type = anki.note_type
    base_dir = project_root / 'templates' / 'anki' / _sanitize_name(note_type)
    manifest_path = base_dir / 'manifest.json'
    css_path = base_dir / 'styling.css'

    if not manifest_path.exists():
        logger.error(f"{ICONS['cross']} Missing manifest.json at {manifest_path}")
        return False

    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    except Exception as e:
        logger.error(f"{ICONS['cross']} Failed to read manifest.json: {e}")
        return False

    # Fetch from Anki
    tmpl_resp = anki.get_model_templates()
    if not tmpl_resp.success:
        logger.error(f"{ICONS['cross']} Failed to fetch Anki templates: {tmpl_resp.error_message}")
        return False
    anki_templates: Dict[str, Dict[str, str]] = tmpl_resp.data or {}

    css_resp = anki.get_model_styling()
    if not css_resp.success:
        logger.error(f"{ICONS['cross']} Failed to fetch Anki styling: {css_resp.error_message}")
        return False
    anki_css = css_resp.data.get('css', '') if isinstance(css_resp.data, dict) else str(css_resp.data or '')

    fields_resp = anki.get_model_field_names()
    if not fields_resp.success:
        logger.error(f"{ICONS['cross']} Failed to fetch Anki model fields: {fields_resp.error_message}")
        return False
    model_fields: Set[str] = set(fields_resp.data or [])

    # Compare CSS
    all_ok = _diff_and_log('styling.css', _read_text(css_path), anki_css)

    # Compare HTML templates
    local_templates_map = {t['name']: t for t in manifest.get('templates', []) if 'name' in t}
    local_names = set(local_templates_map.keys())
    anki_names = set(anki_templates.keys())

    extra_local = sorted(local_names - anki_names)
    missing_local = sorted(anki_names - local_names)
    if extra_local:
        all_ok = False
        logger.error(f"{ICONS['cross']} Extra local templates not in Anki: {extra_local}")
    if missing_local:
        all_ok = False
        logger.error(f"{ICONS['cross']} Templates present in Anki but missing locally: {missing_local}")

    # Placeholders check across all templates
    allowed_builtins = {"FrontSide"}
    used_placeholders: Set[str] = set()

    for name in sorted(local_names & anki_names):
        entry = local_templates_map[name]
        front_rel = entry.get('front', '')
        back_rel = entry.get('back', '')
        front_local = _read_text(base_dir / front_rel)
        back_local = _read_text(base_dir / back_rel)
        anki_tpl = anki_templates.get(name, {}) or {}
        anki_front = anki_tpl.get('Front', '') if isinstance(anki_tpl, dict) else ''
        anki_back = anki_tpl.get('Back', '') if isinstance(anki_tpl, dict) else ''

        if not _diff_and_log(f"{name} - Front", front_local, anki_front):
            all_ok = False
        if not _diff_and_log(f"{name} - Back", back_local, anki_back):
            all_ok = False

        used_placeholders |= _extract_placeholders(front_local)
        used_placeholders |= _extract_placeholders(back_local)

    # Validate template placeholders vs model fields
    unknown_in_templates = sorted([p for p in used_placeholders if p not in model_fields and p not in allowed_builtins])
    if unknown_in_templates:
        all_ok = False
        logger.error(f"{ICONS['cross']} Unknown placeholders used in templates (not model fields): {unknown_in_templates}")

    # Validate config schema vs model fields (ignore non-Anki fields)
    cfg_fields = set(config['validation']['vocabulary_schema']['meaning_entry']['required_fields'])
    # Only compare fields that are actually model fields
    cfg_anki_fields = cfg_fields & model_fields
    model_only = model_fields - cfg_anki_fields
    cfg_only = cfg_anki_fields - model_fields  # will be empty by construction

    if model_only:
        logger.warning(f"{ICONS['warning']} Fields present in Anki model but not listed in config required_fields: {sorted(model_only)}")
    if cfg_only:
        logger.warning(f"{ICONS['warning']} Fields listed in config but not present in Anki model: {sorted(cfg_only)}")

    return all_ok


def main() -> int:
    ok = validate_templates_and_fields()
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())


