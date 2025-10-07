import sys
from pathlib import Path

# Ensure the internal src directory is on sys.path so that 'voxta' package can be imported
_pkg_dir = Path(__file__).parent
_src_dir = _pkg_dir / "src"
if _src_dir.is_dir():
    _src_path = str(_src_dir)
    if _src_path not in sys.path:
        sys.path.insert(0, _src_path)

# Import the node class from the installed / local package
from voxta.voxta_export_character import VoxtaExportCharacter  # type: ignore  # noqa: E402

NODE_CLASS_MAPPINGS = {
    "VoxtaExportCharacter": VoxtaExportCharacter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VoxtaExportCharacter": "Voxta: Export Character",
}

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "VoxtaExportCharacter",
]
