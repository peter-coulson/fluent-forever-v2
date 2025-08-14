#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(PROJECT_ROOT / 'src'))

from utils.logging_config import setup_logging  # noqa: E402
from regenerate_images import main as _main  # type: ignore  # noqa: E402


def main() -> int:
    setup_logging()
    return _main()


if __name__ == '__main__':
    raise SystemExit(main())


