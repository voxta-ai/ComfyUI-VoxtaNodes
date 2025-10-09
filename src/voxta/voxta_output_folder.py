from .helpers import ComfyHelper, FolderHelper


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
        # Unwrap comfy list inputs to scalars
        root_raw = ComfyHelper.comfy_input_to_str(output_path, "")
        sub_raw = ComfyHelper.comfy_input_to_str(subfolder, "")
        if root_raw:
            # Create directory (sanitization + creation handled by FolderHelper)
            FolderHelper.get_output_directory(root_raw, sub_raw)
        return root_raw, sub_raw


NODE_CLASS_MAPPINGS = {"VoxtaOutputFolder": VoxtaOutputFolder}
NODE_DISPLAY_NAME_MAPPINGS = {"VoxtaOutputFolder": "Voxta: Output Folder"}

__all__ = [
    "VoxtaOutputFolder",
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
]
