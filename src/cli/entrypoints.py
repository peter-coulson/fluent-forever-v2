#!/usr/bin/env python3
from pathlib import Path
import sys

from utils.logging_config import setup_logging, ICONS


def sync_anki_all():
    setup_logging()
    from sync_anki_all import main as _main  # type: ignore
    sys.exit(_main())


def media_generate():
    setup_logging()
    from cli.media_generate import main as _main  # type: ignore
    sys.exit(_main())


def regenerate_images():
    setup_logging()
    from cli.regenerate_images import main as _main  # type: ignore
    sys.exit(_main())


def run_media_then_sync():
    setup_logging()
    from cli.run_media_then_sync import main as _main  # type: ignore
    sys.exit(_main())


