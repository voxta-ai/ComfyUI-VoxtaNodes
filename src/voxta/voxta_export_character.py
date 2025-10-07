import os
import logging
from typing import List
from .naming import determine_filename
from .helpers import IdFilenameBuilder, ImageExporter

try:  # pragma: no cover
    import folder_paths  # type: ignore
except Exception:  # pragma: no cover

    class folder_paths:  # type: ignore
        @staticmethod
        def get_output_directory() -> str:
            return os.path.join(os.getcwd(), "output")


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class VoxtaExportCharacter:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
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
            },
            "optional": {
                "voxta_data_path": ("STRING", {"default": "", "multiline": False}),
                "user_id": ("STRING", {"default": "", "multiline": False}),
                "character_id": ("STRING", {"default": "", "multiline": False}),
                "avatar_subfolder": ("STRING", {"default": "", "multiline": False}),
            },
        }

    INPUT_IS_LIST = True
    OUTPUT_NODE = True
    RETURN_TYPES = ()
    FUNCTION = "copy_and_rename"
    CATEGORY = "Voxta"

    def __init__(self):
        self.type = "output"

    @staticmethod
    def _save_image(image, final_path: str, fmt_params):
        arr = ImageExporter.to_numpy(image)
        ImageExporter.save_image(arr, final_path, fmt_params)

    @staticmethod
    def _coerce_scalar_str(value, default: str = "") -> str:
        if isinstance(value, (list, tuple)):
            if not value:
                return default
            value = value[0]
        if value is None:
            return default
        return str(value)

    @staticmethod
    def _sanitize_component(comp: str) -> str:
        if not comp:
            return ""
        cleaned = IdFilenameBuilder.sanitize_subfolder(comp)
        if cleaned == "renamed":
            return ""
        return cleaned

    def copy_and_rename(
        self,
        output_format=None,
        images=None,
        prompts=None,
        combination_ids=None,
        voxta_data_path=None,
        user_id=None,
        character_id=None,
        avatar_subfolder=None,
    ):
        logger.debug(
            "copy_and_rename(raw): voxta_data_path=%r user_id=%r character_id=%r avatar_subfolder=%r output_format=%r images=%s prompts=%s combination_ids=%s",
            voxta_data_path,
            user_id,
            character_id,
            avatar_subfolder,
            output_format,
            len(images) if images is not None else None,
            len(prompts) if prompts is not None else None,
            len(combination_ids) if combination_ids is not None else None,
        )

        output_format = self._coerce_scalar_str(output_format, ".webp lossy 90")
        voxta_data_path = self._coerce_scalar_str(voxta_data_path, "")
        user_id = self._coerce_scalar_str(user_id, "")
        character_id = self._coerce_scalar_str(character_id, "")
        avatar_subfolder = self._coerce_scalar_str(avatar_subfolder, "")

        ImageExporter.require_modules()  # pragma: no cover

        use_voxta_layout = all(v.strip() for v in [voxta_data_path, user_id, character_id])
        if use_voxta_layout:
            base = IdFilenameBuilder.sanitize_full_path(voxta_data_path)
            uid = self._sanitize_component(user_id)
            cid = self._sanitize_component(character_id)
            if base and uid and cid:
                root = os.path.join(base, "Users", uid, "Characters", cid, "Assets", "Avatars")
                mode = "voxta"
            else:
                root = folder_paths.get_output_directory()
                mode = "fallback_sanitized"
        else:
            root = folder_paths.get_output_directory()
            mode = "fallback_default"

        avatar_subfolder = IdFilenameBuilder.sanitize_subfolder(avatar_subfolder)
        if avatar_subfolder == "renamed":
            avatar_subfolder = ""

        os.makedirs(root, exist_ok=True)
        save_dir = os.path.join(root, avatar_subfolder) if avatar_subfolder else root
        os.makedirs(save_dir, exist_ok=True)

        logger.debug("export root (%s): %s subfolder=%s", mode, root, avatar_subfolder or "<none>")

        fmt = ImageExporter.determine_format(output_format)
        ext = fmt["ext"]

        if images is None:
            images = []
        if not isinstance(images, (list, tuple)):
            images = [images]
        if prompts is None:
            prompts = []
        if not isinstance(prompts, (list, tuple)):
            prompts = [prompts]
        if combination_ids is None:
            combination_ids = []
        if not isinstance(combination_ids, (list, tuple)):
            combination_ids = [combination_ids]

        if len(images) != len(prompts):
            raise ValueError("images and prompts length mismatch")
        if len(images) != len(combination_ids):
            raise ValueError("images and combination_ids length mismatch")

        stem_counts: dict[str, int] = {}
        results = []
        output_filenames: List[str] = []

        for idx, id_list in enumerate(combination_ids):
            ids = list(id_list) if isinstance(id_list, (list, tuple)) else [str(id_list)]
            filtered_ids = [s for s in ids if not (s.startswith("input_") and "_no_id_" in s)] or ids
            final_name = determine_filename(filtered_ids, stem_counts, ext, save_dir)
            final_path = os.path.join(save_dir, final_name)
            self._save_image(images[idx], final_path, fmt["params"])
            output_filenames.append(final_name)
            results.append(
                {
                    "filename": final_name,
                    "subfolder": avatar_subfolder if avatar_subfolder else os.path.basename(save_dir),
                    "type": self.type,
                    "mode": mode,
                }
            )

        logger.info("Saved %d images to %s", len(results), save_dir)
        return {"ui": {"images": results, "filenames": output_filenames, "mode": mode}}


NODE_CLASS_MAPPINGS = {"VoxtaExportCharacter": VoxtaExportCharacter}
NODE_DISPLAY_NAME_MAPPINGS = {"VoxtaExportCharacter": "Voxta: Export Character"}
