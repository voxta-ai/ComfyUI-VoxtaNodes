"""Expose node mappings for ComfyUI discovery and tests."""

from voxta.voxta_export_character import (
    VoxtaExportCharacter,
    NODE_CLASS_MAPPINGS as EXPORT_CLASS_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as EXPORT_DISPLAY_MAPPINGS,
)
from voxta.voxta_filter_existing import (
    VoxtaFilterExistingCombinations,
    NODE_CLASS_MAPPINGS as FILTER_CLASS_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS as FILTER_DISPLAY_MAPPINGS,
)

# Merge mappings so ComfyUI sees both nodes
NODE_CLASS_MAPPINGS = {}
NODE_CLASS_MAPPINGS.update(EXPORT_CLASS_MAPPINGS)
NODE_CLASS_MAPPINGS.update(FILTER_CLASS_MAPPINGS)

NODE_DISPLAY_NAME_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS.update(EXPORT_DISPLAY_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(FILTER_DISPLAY_MAPPINGS)

__all__ = [
    "VoxtaExportCharacter",
    "VoxtaFilterExistingCombinations",
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
]
"""Voxta nodes package namespace for ComfyUI.

Provides NODE_CLASS_MAPPINGS so tools/tests can introspect available nodes.
"""
