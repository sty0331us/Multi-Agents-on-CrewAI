"""Logging bootstrap for CLI and crew runs."""

from __future__ import annotations

import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO", fmt: Optional[str] = None) -> None:
    """Configure root logging once for the process."""
    log_format = fmt or "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    root = logging.getLogger()
    if root.handlers:
        root.setLevel(level.upper())
        return

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(log_format))
    root.addHandler(handler)
    root.setLevel(level.upper())

    # Quiet noisy third-party loggers in production runs
    for noisy in ("httpx", "httpcore", "openai", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
