#!/usr/bin/env python3
"""
Templates Sync

Compares local templates with Anki and pushes updates when diffs are found.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

from utils.logging_config import get_logger, ICONS
from apis.anki_client import AnkiClient


logger = get_logger('sync.templates')


def load_local_templates(base_dir: Path) -> Tuple[List[Dict[str, str]], str]:
    manifest = json.loads((base_dir / 'manifest.json').read_text(encoding='utf-8'))
    css = (base_dir / 'styling.css').read_text(encoding='utf-8') if (base_dir / 'styling.css').exists() else ''

    templates_payload: List[Dict[str, str]] = []
    for t in manifest.get('templates', []):
        name = t['name']
        front = (base_dir / t['front']).read_text(encoding='utf-8')
        back = (base_dir / t['back']).read_text(encoding='utf-8')
        templates_payload.append({
            'Name': name,
            'Front': front,
            'Back': back
        })
    return templates_payload, css


def fetch_anki_templates(anki: AnkiClient) -> Tuple[Dict[str, Dict[str, str]], str]:
    tmpl = anki.get_model_templates()
    css = anki.get_model_styling()
    return (tmpl.data or {}), (css.data.get('css', '') if isinstance(css.data, dict) else str(css.data or ''))


def has_template_diffs(local: List[Dict[str, str]], anki_map: Dict[str, Dict[str, str]], local_css: str, anki_css: str) -> bool:
    if local_css != anki_css:
        return True
    anki_by_name = {k: v for k, v in anki_map.items()}
    local_names = {t['Name'] for t in local}
    if set(anki_by_name.keys()) != local_names:
        return True
    for t in local:
        name = t['Name']
        if name not in anki_by_name:
            return True
        if t['Front'] != anki_by_name[name].get('Front', ''):
            return True
        if t['Back'] != anki_by_name[name].get('Back', ''):
            return True
    return False


def push_templates(anki: AnkiClient, local_templates: List[Dict[str, str]], local_css: str) -> bool:
    css_resp = anki.update_model_styling(local_css)
    if not css_resp.success:
        logger.error(f"{ICONS['cross']} Failed to update model styling: {css_resp.error_message}")
        return False
    upd_resp = anki.update_model_templates(local_templates)
    if not upd_resp.success:
        logger.error(f"{ICONS['cross']} Failed to update model templates: {upd_resp.error_message}")
        return False
    logger.info(f"{ICONS['check']} Updated Anki model styling and templates")
    return True


