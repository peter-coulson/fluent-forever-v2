#!/usr/bin/env python3
"""
Media Sync

Ensures all referenced media in vocabulary.json exist in Anki media collection.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Set, Tuple

from utils.logging_config import get_logger, ICONS
from apis.anki_client import AnkiClient


logger = get_logger('sync.media')


def load_vocabulary(vocab_path: Path) -> Dict:
    return json.loads(vocab_path.read_text(encoding='utf-8'))


def referenced_media(vocab: Dict) -> Tuple[Set[str], Set[str]]:
    images: Set[str] = set()
    audio: Set[str] = set()
    for word_data in vocab.get('words', {}).values():
        for meaning in word_data.get('meanings', []):
            img = meaning.get('ImageFile')
            if img:
                images.add(img)
            snd = meaning.get('WordAudio', '')
            if snd.startswith('[sound:') and snd.endswith(']'):
                audio.add(snd[7:-1])
    return images, audio


def list_anki_media(anki: AnkiClient) -> Tuple[Set[str], Set[str]]:
    imgs = anki.get_media_files('*.png')
    auds = anki.get_media_files('*.mp3')
    return set(imgs.data or []), set(auds.data or [])


def compute_missing(ref_images: Set[str], ref_audio: Set[str], anki_images: Set[str], anki_audio: Set[str]) -> Tuple[Set[str], Set[str]]:
    return ref_images - anki_images, ref_audio - anki_audio


def push_missing_media(anki: AnkiClient, project_root: Path, missing_images: Set[str], missing_audio: Set[str]) -> Dict[str, int]:
    media_root = project_root / 'media'
    pushed = {"images": 0, "audio": 0, "errors": 0}
    for img in sorted(missing_images):
        p = media_root / 'images' / img
        if p.exists():
            resp = anki.store_media_file(p, img)
            if resp.success:
                pushed["images"] += 1
            else:
                logger.error(f"{ICONS['cross']} Failed to push image {img}: {resp.error_message}")
                pushed["errors"] += 1
        else:
            logger.error(f"{ICONS['cross']} Local image not found: {p}")
            pushed["errors"] += 1
    for snd in sorted(missing_audio):
        p = media_root / 'audio' / snd
        if p.exists():
            resp = anki.store_media_file(p, snd)
            if resp.success:
                pushed["audio"] += 1
            else:
                logger.error(f"{ICONS['cross']} Failed to push audio {snd}: {resp.error_message}")
                pushed["errors"] += 1
        else:
            logger.error(f"{ICONS['cross']} Local audio not found: {p}")
            pushed["errors"] += 1
    if pushed["images"] or pushed["audio"]:
        logger.info(f"{ICONS['check']} Pushed media → images: {pushed['images']}, audio: {pushed['audio']}")
    return pushed


