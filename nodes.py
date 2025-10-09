"""Root-level node registry for ComfyUI.

Some ComfyUI setups import `nodes.py` in each custom_nodes folder to gather
NODE_CLASS_MAPPINGS. This file consolidates both Voxta nodes so the new filter
node is discoverable even if only `nodes.py` is scanned.
"""

import os
import sys

_root = os.path.dirname(__file__)
_src = os.path.join(_root, "src")
if os.path.isdir(_src) and _src not in sys.path:
    sys.path.insert(0, _src)

from voxta.voxta_export_character import VoxtaExportCharacter  # type: ignore
from voxta.voxta_filter_existing import VoxtaFilterExistingCombinations  # type: ignore
from voxta.voxta_output_folder import VoxtaOutputFolder  # type: ignore

NODE_CLASS_MAPPINGS = {
    "VoxtaExportCharacter": VoxtaExportCharacter,
    "VoxtaFilterExistingCombinations": VoxtaFilterExistingCombinations,
    "VoxtaOutputFolder": VoxtaOutputFolder,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VoxtaExportCharacter": "Voxta: Export Character",
    "VoxtaFilterExistingCombinations": "Voxta: Filter Existing Combinations",
    "VoxtaOutputFolder": "Voxta: Output Folder",
}

__all__ = [
    "VoxtaExportCharacter",
    "VoxtaFilterExistingCombinations",
    "VoxtaOutputFolder",
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
]
