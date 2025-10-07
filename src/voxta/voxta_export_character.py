import os
import logging
from typing import List
from .naming import determine_filename
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

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Change to DEBUG to enable detailed tracing


class VoxtaExportCharacter:
    def __init__(self):
        self.type = "output"

    @classmethod
    def INPUT_TYPES(cls):
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
    OUTPUT_NODE = True
    RETURN_TYPES = ()
    FUNCTION = "copy_and_rename"
    CATEGORY = "Voxta"

    @staticmethod
    def _save_image(image, final_path: str, fmt_params):
        print(f"_save_image: final_path={final_path}, fmt_params={fmt_params}")
        """Convert to numpy (if needed) and save via ImageExporter.

        Not a pure passthrough: performs conversion and basic validations.
        """
        arr = ImageExporter.to_numpy(image)
        ImageExporter.save_image(arr, final_path, fmt_params)

    @staticmethod
    def _coerce_scalar_str(value, default: str = "") -> str:
        """Unwrap list/tuple-of-length-1 values coming from INPUT_IS_LIST batching.

        ComfyUI with INPUT_IS_LIST=True sends list objects for every required input.
        Scalar string parameters (paths, subfolder, format) arrive as ["actual"] when
        user enters a single value. This helper normalizes them before sanitation.
        """
        if isinstance(value, (list, tuple)):
            if not value:
                return default
            value = value[0]
        if value is None:
            return default
        return str(value)

    def copy_and_rename(
        self,
        target_full_path=None,
        target_subfolder=None,
        output_format=None,
        images=None,
        prompts=None,
        combination_ids=None,
    ):
        print("[VoxtaExportCharacter v2] !!!!!!!!!! copy_and_rename called")
        logger.warning(
            "copy_and_rename inputs(raw): target_full_path=%r(%s) target_subfolder=%r(%s) output_format=%r(%s) images=%s prompts=%s combination_ids=%s",
            target_full_path,
            type(target_full_path).__name__,
            target_subfolder,
            type(target_subfolder).__name__,
            output_format,
            type(output_format).__name__,
            len(images) if images is not None else None,
            len(prompts) if prompts is not None else None,
            len(combination_ids) if combination_ids is not None else None,
        )

        # Normalize scalar parameters that may have arrived wrapped in single-element lists
        target_full_path = self._coerce_scalar_str(target_full_path, "")
        target_subfolder = self._coerce_scalar_str(target_subfolder, "")
        output_format = self._coerce_scalar_str(output_format, ".webp lossy 90")

        logger.debug(
            "copy_and_rename inputs(normalized stage1): target_full_path=%r(%s) target_subfolder=%r(%s) output_format=%r(%s)",
            target_full_path,
            type(target_full_path).__name__,
            target_subfolder,
            type(target_subfolder).__name__,
            output_format,
            type(output_format).__name__,
        )

        # Extra defensive unwrapping in case something re-wrapped them upstream
        if isinstance(target_full_path, (list, tuple)):
            logger.debug("target_full_path still list after stage1: %r", target_full_path)
            target_full_path = target_full_path[0] if target_full_path else ""
        if isinstance(target_subfolder, (list, tuple)):
            logger.debug("target_subfolder still list after stage1: %r", target_subfolder)
            target_subfolder = target_subfolder[0] if target_subfolder else ""
        if isinstance(output_format, (list, tuple)):
            logger.debug("output_format still list after stage1: %r", output_format)
            output_format = output_format[0] if output_format else ".webp lossy 90"

        logger.debug(
            "copy_and_rename inputs(normalized final): target_full_path=%r(%s) target_subfolder=%r(%s) output_format=%r(%s)",
            target_full_path,
            type(target_full_path).__name__,
            target_subfolder,
            type(target_subfolder).__name__,
            output_format,
            type(output_format).__name__,
        )

        ImageExporter.require_modules()  # pragma: no cover

        # Now safe to sanitize
        target_subfolder = IdFilenameBuilder.sanitize_subfolder(target_subfolder)

        # Ensure list-like for multi export; if a single image sneaks in wrap it
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
            raise ValueError(f"Number of images ({len(images)}) must match number of prompts ({len(prompts)})")
        if len(images) != len(combination_ids):
            raise ValueError(f"Number of images ({len(images)}) must match number of combination_ids ({len(combination_ids)})")

        root = IdFilenameBuilder.sanitize_full_path(target_full_path) or folder_paths.get_output_directory()
        os.makedirs(root, exist_ok=True)
        save_dir = os.path.join(root, target_subfolder) if target_subfolder else root
        os.makedirs(save_dir, exist_ok=True)

        fmt = ImageExporter.determine_format(output_format)
        ext = fmt["ext"]

        stem_counts: dict[str, int] = {}
        results = []
        output_filenames: List[str] = []

        for idx, id_list in enumerate(combination_ids):
            ids = list(id_list) if isinstance(id_list, (list, tuple)) else [str(id_list)]
            # Filter out placeholder tokens that ComfyUI (or upstream nodes) may inject.
            filtered_ids = [s for s in ids if not (s.startswith("input_") and "_no_id_" in s)]
            if not filtered_ids:
                filtered_ids = ids  # fallback if everything was filtered
            if filtered_ids != ids:
                logger.debug("Filtered placeholder ids %s -> %s", ids, filtered_ids)
            ids = filtered_ids
            final_name = determine_filename(ids, stem_counts, ext, save_dir)
            image = images[idx]
            final_path = os.path.join(save_dir, final_name)
            self._save_image(image, final_path, fmt["params"])
            logger.warning("Mapped ids=%s -> filename=%s", ids, final_name)
            output_filenames.append(final_name)
            results.append(
                {
                    "filename": final_name,
                    "subfolder": target_subfolder if target_subfolder else os.path.basename(save_dir),
                    "type": self.type,
                }
            )

        logger.warning("Saved %d images to %s", len(results), save_dir)
        # Provide UI metadata in case ComfyUI wants to surface the saved files (harmless for output-only node)
        return {"ui": {"images": results, "filenames": output_filenames}}


NODE_CLASS_MAPPINGS = {
    "VoxtaExportCharacter": VoxtaExportCharacter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VoxtaExportCharacter": "Voxta: Export Character",
}
