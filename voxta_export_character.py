"""Shim module to allow `import voxta_export_character` in tests and user code.

This simply re-exports VoxtaExportCharacter from the packaged source location.
"""

from voxta.voxta_export_character import VoxtaExportCharacter  # noqa: F401
