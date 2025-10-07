from .src.voxta.voxta_export_character import VoxtaExportCharacter

NODE_CLASS_MAPPINGS = {
    "VoxtaExportCharacter": VoxtaExportCharacter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VoxtaExportCharacter": "Voxta: Export Character",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "VoxtaExportCharacter"]
