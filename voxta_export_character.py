"""Shim module to allow `import voxta_export_character` in tests and user code.

This re-exports VoxtaExportCharacter and also ensures the filter node is registered
in environments that only load this root file (some ComfyUI discovery modes).
"""

import os, sys

_root = os.path.dirname(__file__)
_src = os.path.join(_root, "src")
if os.path.isdir(_src) and _src not in sys.path:
    sys.path.insert(0, _src)

from voxta.voxta_export_character import VoxtaExportCharacter as _VoxtaExportCharacter  # noqa: F401

try:
    from voxta.voxta_filter_existing import VoxtaFilterExistingCombinations as _VoxtaFilterExistingCombinations  # noqa: F401
except Exception:  # pragma: no cover
    _VoxtaFilterExistingCombinations = None

# Primary export for backward compatibility
VoxtaExportCharacter = _VoxtaExportCharacter

# Provide NODE_CLASS_MAPPINGS if not already defined elsewhere
NODE_CLASS_MAPPINGS = {"VoxtaExportCharacter": VoxtaExportCharacter}
NODE_DISPLAY_NAME_MAPPINGS = {"VoxtaExportCharacter": "Voxta: Export Character"}
if _VoxtaFilterExistingCombinations is not None:
    NODE_CLASS_MAPPINGS["VoxtaFilterExistingCombinations"] = _VoxtaFilterExistingCombinations
    NODE_DISPLAY_NAME_MAPPINGS["VoxtaFilterExistingCombinations"] = "Voxta: Filter Existing Combinations"

__all__ = [
    "VoxtaExportCharacter",
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
]
