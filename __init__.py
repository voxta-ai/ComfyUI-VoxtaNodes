import sys
from pathlib import Path

# Ensure the internal src directory is on sys.path so that 'voxta' package can be imported
_pkg_dir = Path(__file__).parent
_src_dir = _pkg_dir / "src"
if _src_dir.is_dir():
    _src_path = str(_src_dir)
    if _src_path not in sys.path:
        sys.path.insert(0, _src_path)

from voxta.voxta_output_folder import VoxtaOutputFolder
from voxta.voxta_export_character import VoxtaExportCharacter
from voxta.voxta_filter_existing import VoxtaFilterExistingCombinations

WEB_DIRECTORY = "js"

# Build mappings
NODE_CLASS_MAPPINGS = {
    "VoxtaOutputFolder": VoxtaOutputFolder,
    "VoxtaExportCharacter": VoxtaExportCharacter,
    "VoxtaFilterExistingCombinations": VoxtaFilterExistingCombinations,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "VoxtaOutputFolder": "Voxta: Output Folder",
    "VoxtaExportCharacter": "Voxta: Export Character",
    "VoxtaFilterExistingCombinations": "Voxta: Filter Existing Combinations",
}

__all__ = [
    "WEB_DIRECTORY",
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "VoxtaOutputFolder",
    "VoxtaExportCharacter",
    "VoxtaFilterExistingCombinations",
]
