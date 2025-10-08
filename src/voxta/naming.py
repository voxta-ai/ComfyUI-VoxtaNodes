"""Filename determination utilities for Voxta nodes.

This module isolates the logic for producing enumerated, sanitized filenames
so that it can be unit-tested independently from the node class.
"""

from __future__ import annotations

import os
import logging
import re
from typing import List

from .helpers import IdFilenameBuilder

logger = logging.getLogger(__name__)


def determine_filename(ids: List[str], ext: str, save_dir: str) -> str:
    """Return a unique filename for the provided id list.

    Strategy:
    1. Sanitize the id list into a stem.
    2. Find existing files on disk with the same stem.
    3. Determine the highest existing enumeration and add one.

    Raises
    ------
    ValueError
        If more than 99 enumerations are needed (i.e., Neutral_Idle_99 already exists).
    """
    stem = IdFilenameBuilder.sanitize_id_filename(ids)
    if not stem:
        stem = "image"

    # Regex to find stem_XX.ext
    pattern = re.compile(f"^{re.escape(stem)}_(\\d+){re.escape(ext)}$")

    max_found = 0
    try:
        for f in os.listdir(save_dir):
            match = pattern.match(f)
            if match:
                num = int(match.group(1))
                if num > max_found:
                    max_found = num
    except FileNotFoundError:
        # Directory may not exist yet, which is fine
        pass

    count = max_found + 1

    if count > 99:
        raise ValueError(f"Exceeded 99 variations for stem '{stem}' in {save_dir}")

    final_name = f"{stem}_{count:02d}{ext}"

    logger.debug("determine_filename: ids=%s stem=%s assigned=%s", ids, stem, final_name)
    return final_name


__all__ = ["determine_filename"]
