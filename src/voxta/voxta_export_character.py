import os
from typing import List
from .helpers import IdFilenameBuilder, ImageExporter

# <TESTS>
try:  # pragma: no cover - exercised implicitly in real runtime
    import folder_paths  # type: ignore
except Exception:  # pragma: no cover

    class folder_paths:  # type: ignore
        @staticmethod
        def get_output_directory() -> str:
            return os.path.join(os.getcwd(), "output")
# </TESTS>


class VoxtaExportCharacter:
    def __init__(self):
        self.type = "output"
        self._output_dir = folder_paths.get_output_directory()
        self._builder = IdFilenameBuilder()
        self._exporter = ImageExporter()

    @classmethod
    def INPUT_TYPES(cls):  # UI uses new signature
        return {
            "required": {
                "target_full_path": ("STRING", {"default": "", "multiline": False}),
                "target_subfolder": ("STRING", {"default": "", "multiline": False}),
                "output_format": (
                    [
                        ".webp lossy 80",
                        ".webp lossy 90",
                        ".webp lossless",
                        ".png lossless",
                    ],
                    {"default": ".webp lossy 90"},
                ),
                "images": ("IMAGE",),
                "prompts": ("STRING", {"default": "", "multiline": True, "forceInput": True}),
                "combination_ids": ("PROMPTCOMBINATORIDS",),
            }
        }

    INPUT_IS_LIST = True
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "test"
    CATEGORY = "Voxta"

    ORIGINAL_FUNCTION = "copy_and_rename"
    ORIGINAL_CATEGORY = "voxta/outputs"

    def test(self, *args):  # pragma: no cover
        return self.copy_and_rename(*args)

    @staticmethod
    def _sanitize_subfolder(sub: str) -> str:
        return IdFilenameBuilder.sanitize_subfolder(sub)

    @staticmethod
    def _sanitize_full_path(path: str) -> str:
        return IdFilenameBuilder.sanitize_full_path(path)

    @staticmethod
    def _sanitize_id_filename(id_list: List[str]) -> str:
        return IdFilenameBuilder.sanitize_id_filename(id_list)

    @classmethod
    def _ensure_unique(cls, stem: str, ext: str, used: set[str]) -> str:
        return IdFilenameBuilder.ensure_unique(stem, ext, used)

    def _determine_format(self, option: str):
        return ImageExporter.determine_format(option)

    def _ensure_image_module(self):  # pragma: no cover
        ImageExporter.require_modules()

    # ---------------- Core save routines -----------------
    def _save_image(self, arr, final_path, fmt_params):
        ImageExporter.save_image(arr, final_path, fmt_params)

    # Public API supporting both signatures
    def copy_and_rename(
        self,
        target_full_path=None,
        target_subfolder=None,
        output_format=None,
        images=None,
        prompts=None,
        combination_ids=None,
    ):
        self._ensure_image_module()
        target_subfolder = self._sanitize_subfolder(target_subfolder)
        if len(images) != len(prompts):
            raise ValueError("Number of images must match number of prompts")
        if len(images) != len(combination_ids):
            raise ValueError("Number of images must match number of combination_ids")
        root = self._sanitize_full_path(target_full_path) or folder_paths.get_output_directory()
        os.makedirs(root, exist_ok=True)
        save_dir = os.path.join(root, target_subfolder) if target_subfolder else root
        os.makedirs(save_dir, exist_ok=True)
        fmt = self._determine_format(output_format)
        ext = fmt["ext"]
        # Counters per sanitized stem to produce _01, _02 etc.
        stem_counts: dict[str, int] = {}
        results = []
        output_filenames: List[str] = []
        for idx, id_list in enumerate(combination_ids):
            ids = list(id_list) if isinstance(id_list, (list, tuple)) else [str(id_list)]
            stem = self._sanitize_id_filename(ids)
            if not stem:
                stem = "image"
            count = stem_counts.get(stem, 0) + 1
            stem_counts[stem] = count
            suffix = f"{count:02d}"  # zero-padded at least 2 digits
            final_name = f"{stem}_{suffix}{ext}"
            # If collision (unlikely unless same stem + count already saved), bump until unique
            while os.path.exists(os.path.join(save_dir, final_name)):
                count += 1
                stem_counts[stem] = count
                suffix = f"{count:02d}"
                final_name = f"{stem}_{suffix}{ext}"
            image = images[idx]
            try:
                if hasattr(image, "cpu") and callable(getattr(image, "cpu")):
                    arr = image.squeeze(0).cpu().numpy()
                else:
                    arr = image
            except Exception:
                arr = image
            if arr is None:
                raise ValueError("Unsupported image type")
            final_path = os.path.join(save_dir, final_name)
            self._save_image(arr, final_path, fmt["params"])
            output_filenames.append(final_name)
            results.append(
                {
                    "filename": final_name,
                    "subfolder": target_subfolder if target_subfolder else os.path.basename(save_dir),
                    "type": self.type,
                }
            )
        print(f"Saved {len(results)} images to {save_dir}")
        return {"ui": {"images": results}, "filenames": output_filenames}


# A dictionary that contains all nodes you want to export with their names
NODE_CLASS_MAPPINGS = {
    "VoxtaExportCharacter": VoxtaExportCharacter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VoxtaExportCharacter": "Voxta: Export Character",
}
