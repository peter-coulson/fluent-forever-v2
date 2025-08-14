#!/usr/bin/env python3
"""
Cards Sync

Upserts notes in Anki to match vocabulary.json as the golden source.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterator, Tuple

from utils.logging_config import get_logger, ICONS
from apis.anki_client import AnkiClient


logger = get_logger('sync.cards')


def load_vocabulary(vocab_path: Path) -> Dict:
    return json.loads(vocab_path.read_text(encoding='utf-8'))


def iter_vocab_cards(vocab: Dict) -> Iterator[Dict[str, str]]:
    for word, wdata in vocab.get('words', {}).items():
        for meaning in wdata.get('meanings', []):
            # meaning already follows Anki field naming in your schema
            yield meaning


def find_note_by_cardid(anki: AnkiClient, card_id: str, deck_name: str) -> Tuple[int | None, Dict[str, str]]:
    q = f'deck:"{deck_name}" CardID:"{card_id}"'
    found = anki.find_notes(q)
    if not found.success:
        return None, {}
    ids = found.data or []
    if not ids:
        return None, {}
    info = anki.notes_info(ids)
    if not info.success or not info.data:
        return None, {}
    note = info.data[0]
    fields = {k: v['value'] for k, v in note['fields'].items()}
    return note['noteId'], fields


def compare_fields(local_fields: Dict[str, str], anki_fields: Dict[str, str]) -> Dict[str, Tuple[str, str]]:
    diffs: Dict[str, Tuple[str, str]] = {}
    for k, v in local_fields.items():
        lv = str(v).strip()
        av = str(anki_fields.get(k, '')).strip()
        if lv != av:
            diffs[k] = (av, lv)
    return diffs


def upsert_cards(anki: AnkiClient, vocab: Dict, force_media: bool = False) -> Dict[str, int]:
    deck = anki.deck_name
    summary = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}
    for local in iter_vocab_cards(vocab):
        card_id = str(local.get('CardID', ''))
        if not card_id:
            logger.error(f"{ICONS['cross']} Missing CardID; skipping entry")
            summary["errors"] += 1
            continue
        note_id, anki_fields = find_note_by_cardid(anki, card_id, deck)
        if note_id is None:
            # ensure media stored if present in fields (best-effort)
            # ImageFile is filename; WordAudio is [sound:filename]
            # media already handled by media sync; here we simply add note
            resp = anki.create_card(local)
            if resp.success:
                summary["created"] += 1
            else:
                logger.error(f"{ICONS['cross']} Failed to create card {card_id}: {resp.error_message}")
                summary["errors"] += 1
            continue
        # compare and update
        diffs = compare_fields(local, anki_fields)
        if not diffs:
            summary["skipped"] += 1
            continue
        upd = anki.update_note_fields(note_id, local)
        if upd.success:
            summary["updated"] += 1
        else:
            logger.error(f"{ICONS['cross']} Failed to update {card_id}: {upd.error_message}")
            summary["errors"] += 1
    return summary


