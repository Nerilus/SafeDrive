"""Logging setup for SafeDrive.

Replaces the old ``log_detection`` function (bug #6) with Python's
standard ``logging`` module.
"""

import logging
import os


def setup_logging(log_dir: str | None = None, level: int = logging.INFO) -> None:
    """Configure the root logger with a console and optional file handler.

    Parameters
    ----------
    log_dir : str | None
        Directory for the log file.  If provided, a ``safedrive.log`` file
        is created there.
    level : int
        Logging level (default ``INFO``).
    """
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    handlers: list[logging.Handler] = [logging.StreamHandler()]

    if log_dir is not None:
        os.makedirs(log_dir, exist_ok=True)
        fh = logging.FileHandler(
            os.path.join(log_dir, "safedrive.log"), encoding="utf-8"
        )
        handlers.append(fh)

    logging.basicConfig(level=level, format=fmt, datefmt=datefmt, handlers=handlers)
