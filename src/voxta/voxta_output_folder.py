class VoxtaOutputFolder:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "output_path": ("STRING", {"default": "", "multiline": False}),
                "subfolder": ("STRING", {"default": "Avatars/Default", "multiline": False}),
            }
        }

    OUTPUT_IS_LIST = (False, False)
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("output_path", "subfolder")

    FUNCTION = "execute"
    CATEGORY = "Voxta"

    # noinspection PyMethodMayBeStatic
    def execute(self, output_path: list[str] | str, subfolder: list[str] | str):
        return output_path, subfolder


NODE_CLASS_MAPPINGS = {"VoxtaOutputFolder": VoxtaOutputFolder}
NODE_DISPLAY_NAME_MAPPINGS = {"VoxtaOutputFolder": "Voxta: Output Folder"}

__all__ = [
    "VoxtaOutputFolder",
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
]
