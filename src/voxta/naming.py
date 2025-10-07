"""Filename determination utilities for Voxta nodes.

This module isolates the logic for producing enumerated, sanitized filenames
so that it can be unit-tested independently from the node class.
"""

from __future__ import annotations

import os
import logging
from typing import List, Dict
from .helpers import IdFilenameBuilder

logger = logging.getLogger(__name__)


def determine_filename(ids: List[str], stem_counts: Dict[str, int], ext: str, save_dir: str) -> str:
    """Return a unique filename for the provided id list.

    Strategy:
    1. Sanitize the id list into a stem.
    2. Maintain an in-memory counter per stem (stem_counts) to append a zero-padded index.
    3. If a file with the computed name already exists on disk, increment until free.

    Parameters
    ----------
    ids: list[str]
        Sequence of identifiers (already strings) used to build the stem.
    stem_counts: dict[str, int]
        Mutable mapping of stem -> last used count (updated in-place).
    ext: str
        File extension including leading dot, e.g. ".png".
    save_dir: str
        Destination directory to check for existing collisions.

    Returns
    -------
    str
        A filename like "Neutral_Thinking_01.png".
    """
    stem = IdFilenameBuilder.sanitize_id_filename(ids)
    if not stem:
        stem = "image"

    count = stem_counts.get(stem, 0) + 1
    stem_counts[stem] = count

    def build_name(c: int) -> str:
        return f"{stem}_{c:02d}{ext}"

    final_name = build_name(count)
    # Bump until unique on disk
    while os.path.exists(os.path.join(save_dir, final_name)):
        count += 1
        stem_counts[stem] = count
        final_name = build_name(count)

    logger.debug("determine_filename: ids=%s stem=%s assigned=%s", ids, stem, final_name)
    return final_name


__all__ = ["determine_filename"]
