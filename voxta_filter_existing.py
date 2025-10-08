"""Shim to expose VoxtaFilterExistingCombinations at repository root for ComfyUI discovery.

ComfyUI scans top-level .py files in a custom_nodes folder; this file re-exports
and registers the filter node so it appears alongside the exporter.
"""

import os
import sys

_root = os.path.dirname(__file__)
_src = os.path.join(_root, "src")
if os.path.isdir(_src) and _src not in sys.path:
    sys.path.insert(0, _src)

try:
    from voxta.voxta_filter_existing import VoxtaFilterExistingCombinations  # noqa: F401
except Exception:  # pragma: no cover
    raise

NODE_CLASS_MAPPINGS = {"VoxtaFilterExistingCombinations": VoxtaFilterExistingCombinations}
NODE_DISPLAY_NAME_MAPPINGS = {"VoxtaFilterExistingCombinations": "Voxta: Filter Existing Combinations"}

__all__ = [
    "VoxtaFilterExistingCombinations",
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
]
