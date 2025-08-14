#!/usr/bin/env python3
"""
Media Generation Orchestrator

Generates missing media (images/audio) for specific CardIDs using OpenAI/Forvo
based on vocabulary.json. Enforces idempotence, validates inputs/outputs, and
provides detailed logging.
"""

from __future__ import annotations

import json
import hashlib
import time
from dataclasses import dataclass
from types import SimpleNamespace
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from utils.logging_config import get_logger, setup_logging, ICONS
from apis.base_client import BaseAPIClient
from apis.openai_client import OpenAIClient
from apis.forvo_client import ForvoClient
from apis.base_client import ensure_media_directories
from validation.internal.vocabulary_validator import VocabularyValidator
from validation.internal import media_validator as internal_media_validator


logger = get_logger('sync.media_generation')


@dataclass
class GenerationPlan:
    card_ids: List[str]
    words_needed: Set[str]
    images_needed: Set[str]
    audio_needed: Set[str]
    images_to_generate: Set[str]
    audio_to_generate: Set[str]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def hash_prompt(word: str, prompt: str) -> str:
    h = hashlib.sha256()
    h.update((word + '|' + (prompt or '')).encode('utf-8'))
    return h.hexdigest()[:16]


def load_vocabulary(project_root: Path) -> dict:
    return load_json(project_root / 'vocabulary.json')


def validate_vocabulary(project_root: Path) -> bool:
    config = BaseAPIClient.load_config(project_root / 'config.json')
    vocab = load_vocabulary(project_root)
    validator = VocabularyValidator(config)
    ok = validator.validate(vocab)
    if not ok:
        logger.error(validator.get_report())
    else:
        logger.info(f"{ICONS['check']} vocabulary.json structure valid")
    return ok


def build_meaning_index(vocab: dict) -> Dict[str, dict]:
    idx: Dict[str, dict] = {}
    for word_obj in vocab.get('words', {}).values():
        for meaning in word_obj.get('meanings', []):
            cid = str(meaning.get('CardID', '')).strip()
            if cid:
                idx[cid] = meaning
    return idx


def compute_requested_media(project_root: Path, card_ids: List[str]) -> Tuple[Set[str], Set[str], Set[str]]:
    vocab = load_vocabulary(project_root)
    idx = build_meaning_index(vocab)
    images: Set[str] = set()
    audio: Set[str] = set()
    words: Set[str] = set()
    for cid in card_ids:
        m = idx.get(cid)
        if not m:
            logger.warning(f"{ICONS['warning']} CardID not found in vocabulary.json: {cid}")
            continue
        if m.get('ImageFile'):
            images.add(m['ImageFile'])
        snd = m.get('WordAudio', '')
        if snd.startswith('[sound:') and snd.endswith(']'):
            audio.add(snd[7:-1])
        word = str(m.get('SpanishWord', '')).strip()
        if word:
            words.add(word)
    return images, audio, words


def compute_missing_media(project_root: Path) -> Tuple[Set[str], Set[str]]:
    # Reuse existing validator to find missing local media vs vocabulary refs
    result = internal_media_validator.validate_local_vs_vocabulary()
    return set(result.missing_images), set(result.missing_audio)


def plan_generation(project_root: Path, card_ids: List[str]) -> GenerationPlan:
    vocab = load_vocabulary(project_root)
    idx = build_meaning_index(vocab)
    req_images, req_audio, words_needed = compute_requested_media(project_root, card_ids)
    missing_images, missing_audio = compute_missing_media(project_root)
    # Union: requested with missing
    images_union = req_images | missing_images
    audio_union = req_audio | missing_audio
    # Filter union to only the requested CardIDs and those missing in any card
    # Images: union already correct since missing_images are by filename
    # Audio is by word; keep as-is
    media_folder = Path(project_root / 'media')
    images_to_generate: Set[str] = set()
    for img in sorted(images_union):
        if not (media_folder / 'images' / img).exists():
            images_to_generate.add(img)
    audio_to_generate: Set[str] = set()
    for aud in sorted(audio_union):
        if not (media_folder / 'audio' / aud).exists():
            audio_to_generate.add(aud)
    return GenerationPlan(
        card_ids=card_ids,
        words_needed=words_needed,
        images_needed=images_union,
        audio_needed=audio_union,
        images_to_generate=images_to_generate,
        audio_to_generate=audio_to_generate,
    )


def load_provenance(project_root: Path) -> dict:
    prov_path = project_root / 'media' / '.index.json'
    if prov_path.exists():
        try:
            return load_json(prov_path)
        except Exception:
            return {}
    return {}


def save_provenance(project_root: Path, provenance: dict) -> None:
    save_json(project_root / 'media' / '.index.json', provenance)


def ensure_lock(project_root: Path) -> Path:
    lock_path = project_root / '.media_sync.lock'
    if lock_path.exists():
        raise RuntimeError("Another media generation run appears to be in progress (lockfile exists). If safe, delete .media_sync.lock and retry.")
    lock_path.write_text(str(time.time()), encoding='utf-8')
    return lock_path


def release_lock(lock_path: Path) -> None:
    try:
        lock_path.unlink(missing_ok=True)  # type: ignore[arg-type]
    except Exception:
        pass


def generate_images(project_root: Path, plan: GenerationPlan, dry_run: bool) -> Tuple[int, int]:
    """Returns (generated, skipped)"""
    if not plan.images_to_generate:
        return 0, 0
    ensure_media_directories(BaseAPIClient.load_config(project_root / 'config.json'))
    provenance = load_provenance(project_root)
    vocab = load_vocabulary(project_root)
    idx = build_meaning_index(vocab)
    client = None if dry_run else OpenAIClient()
    generated = 0
    skipped = 0
    for img in sorted(plan.images_to_generate):
        # Find a meaning that references this image
        meaning = next((m for m in idx.values() if m.get('ImageFile') == img), None)
        if not meaning:
            logger.warning(f"{ICONS['warning']} No meaning found for image {img}; skipping")
            skipped += 1
            continue
        word = meaning.get('SpanishWord', '')
        prompt = meaning.get('prompt', '')
        prompt_h = hash_prompt(word, prompt)
        # Check provenance drift
        prov = provenance.get(img)
        if prov and prov.get('prompt_hash') != prompt_h:
            logger.warning(f"{ICONS['warning']} Prompt changed for {img}; existing file will be kept. Use --force-regenerate to update.")
        if dry_run:
            logger.info(f"{ICONS['info']} DRY-RUN image → {img} (word={word})")
            continue
        resp = client.generate_image(prompt, img) if client else SimpleNamespace(success=False, error_message="dry-run")
        if resp.success:
            provenance[img] = {
                'word': word,
                'prompt_hash': prompt_h,
                'provider': 'openai',
                'created_at': time.time(),
            }
            generated += 1
            logger.info(f"{ICONS['check']} Image generated: {img}")
        else:
            logger.error(f"{ICONS['cross']} Image generation failed for {img}: {resp.error_message}")
    save_provenance(project_root, provenance)
    return generated, skipped


def generate_audio(project_root: Path, plan: GenerationPlan, dry_run: bool) -> Tuple[int, int]:
    if not plan.audio_to_generate:
        return 0, 0
    ensure_media_directories(BaseAPIClient.load_config(project_root / 'config.json'))
    client = None if dry_run else ForvoClient()
    generated = 0
    skipped = 0
    # Map audio filename back to word
    # We only know filenames like word.mp3; extract stem
    for aud in sorted(plan.audio_to_generate):
        word = Path(aud).stem
        if dry_run:
            logger.info(f"{ICONS['info']} DRY-RUN audio → {aud} (word={word})")
            continue
        resp = client.download_pronunciation(word, aud) if client else SimpleNamespace(success=False, error_message="dry-run")
        if resp.success:
            generated += 1
            logger.info(f"{ICONS['check']} Audio downloaded: {aud}")
        else:
            logger.error(f"{ICONS['cross']} Audio download failed for {aud}: {resp.error_message}")
    return generated, skipped


def estimate_cost(plan: GenerationPlan, project_root: Path) -> float:
    # Images have cost; audio from Forvo free tier assumed $0 here
    config = BaseAPIClient.load_config(project_root / 'config.json')
    cpi = config['apis']['openai']['cost_per_image']
    return float(cpi) * len(plan.images_to_generate)


def run_media_generation(
    project_root: Path,
    card_ids: List[str],
    max_new: Optional[int] = None,
    dry_run: bool = True,
    force_regenerate: bool = False,
    skip_images: bool = False,
    skip_audio: bool = False,
) -> bool:
    setup_logging()
    # Ensure config is loaded from the provided project_root, not a previous cached location
    try:
        BaseAPIClient._shared_config = None  # type: ignore[attr-defined]
    except Exception:
        pass
    
    # Load max_new from config if not provided
    if max_new is None:
        config = BaseAPIClient.load_config(project_root / 'config.json')
        max_new = config.get('media_generation', {}).get('max_new_items', 5)
        
    if not validate_vocabulary(project_root):
        return False

    lock_path: Path | None = None
    try:
        lock_path = ensure_lock(project_root)
        plan = plan_generation(project_root, card_ids)

        # Enforce max cap
        total_new = (0 if skip_images else len(plan.images_to_generate)) + (0 if skip_audio else len(plan.audio_to_generate))
        if total_new > max_new and not dry_run:
            logger.error(f"{ICONS['cross']} Too many new media items to generate: {total_new} > {max_new}. Use --max to override or run with --dry-run to preview.")
            return False

        # Cost estimate
        est = estimate_cost(plan, project_root)
        logger.info(f"{ICONS['chart']} Plan: inputs={len(card_ids)} | images_needed={len(plan.images_needed)} | audio_needed={len(plan.audio_needed)}")
        logger.info(f"{ICONS['chart']} To generate: images={0 if skip_images else len(plan.images_to_generate)}, audio={0 if skip_audio else len(plan.audio_to_generate)} | est_cost=${est:.2f}")

        # Execute
        if not dry_run:
            if not skip_images:
                generate_images(project_root, plan, dry_run=False)
            if not skip_audio:
                generate_audio(project_root, plan, dry_run=False)
        else:
            # Dry-run previews
            if not skip_images:
                generate_images(project_root, plan, dry_run=True)
            if not skip_audio:
                generate_audio(project_root, plan, dry_run=True)

        # Post validation
        missing_images, missing_audio = compute_missing_media(project_root)
        # Filter to the relevant set (requested + missing union)
        relevant_missing_images = missing_images & plan.images_needed
        relevant_missing_audio = missing_audio & plan.audio_needed
        if relevant_missing_images or relevant_missing_audio:
            logger.error(f"{ICONS['cross']} Post-run missing media remain:")
            if relevant_missing_images:
                logger.error(f"   images: {sorted(relevant_missing_images)}")
            if relevant_missing_audio:
                logger.error(f"   audio: {sorted(relevant_missing_audio)}")
            return False

        logger.info(f"{ICONS['check']} Media generation complete and validated")
        return True

    except Exception as e:
        logger.error(f"{ICONS['cross']} Media generation failed: {e}")
        return False
    finally:
        if lock_path:
            release_lock(lock_path)


