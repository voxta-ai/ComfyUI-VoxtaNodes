import os
from .naming import determine_filename
from .helpers import IdFilenameBuilder, ImageExporter, FolderHelper

try:  # pragma: no cover
    import folder_paths  # type: ignore
except Exception:  # pragma: no cover

    class folder_paths:  # type: ignore
        @staticmethod
        def get_output_directory() -> str:
            return os.path.join(os.getcwd(), "output")


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
                # Single unified output path. If empty, falls back to ComfyUI output directory.
                "output_path": ("STRING", {"default": "", "multiline": False}),
                # Optional subfolder under the chosen root.
                "subfolder": ("STRING", {"default": "Avatars/Default", "multiline": False}),
                # How to handle an existing filename on disk.
                # append   -> current behavior: find next free enumerated name.
                # overwrite-> reuse the enumerated name even if exists and overwrite the file.
                # skip     -> if the enumerated name exists, do not save (omit from results).
                "on_exists": (
                    ["append", "overwrite", "skip"],
                    {"default": "append"},
                ),
            },
        }

    INPUT_IS_LIST = True

    OUTPUT_NODE = True
    RETURN_TYPES = ()

    FUNCTION = "execute"
    CATEGORY = "Voxta"

    def __init__(self):
        self.type = "output"

    # noinspection PyMethodMayBeStatic
    def execute(
        self,
        output_format: list[str],
        images: list[object],
        prompts: list[str],
        combination_ids: list[list[str]],
        output_path: list[str],
        subfolder: list[str],
        on_exists: list[str],
    ):
        save_dir = FolderHelper.get_output_directory(output_path, subfolder)
        output_format = output_format[0] if output_format else ".webp lossy 90"
        on_exists = on_exists[0] if on_exists else "append"
        if on_exists not in {"append", "overwrite", "skip"}:
            raise ValueError(f"Invalid on_exists option: {on_exists}")

        ImageExporter.require_modules()  # pragma: no cover

        fmt = ImageExporter.determine_format(output_format)
        ext = fmt["ext"]

        if len(images) != len(prompts) and len(prompts) > 1:
            raise ValueError("images and prompts length mismatch")
        if len(images) != len(combination_ids):
            raise ValueError("images and combination_ids length mismatch")

        # Broadcast single prompt
        if len(prompts) == 1 and len(images) > 1:
            prompts = prompts * len(images)

        filenames = []
        skipped_count = 0

        for idx, id_list in enumerate(combination_ids):
            ids = list(id_list) if isinstance(id_list, (list, tuple)) else [str(id_list)]
            filtered_ids = [s for s in ids if not (s.startswith("input_") and "_no_id_" in s)] or ids

            if on_exists == "append":
                final_name = determine_filename(filtered_ids, ext, save_dir)
            else:
                # For 'overwrite' and 'skip', we need a predictable but not necessarily unique filename.
                # We'll generate a base name and then check for existence.
                stem = IdFilenameBuilder.sanitize_id_filename(filtered_ids) or "image"
                # This logic is simple, assumes a single batch. A more robust implementation
                # might need to be aware of previous batches if the node is re-run.
                # For now, we'll use a simple enumeration for this batch.
                final_name = f"{stem}_{idx + 1:02d}{ext}"

                final_path = os.path.join(save_dir, final_name)
                if os.path.exists(final_path):
                    if on_exists == "skip":
                        skipped_count += 1
                        continue  # do not save or report
                    # on_exists == "overwrite", so fall through and overwrite

            final_path = os.path.join(save_dir, final_name)
            arr = ImageExporter.to_numpy(images[idx])
            ImageExporter.save_image(arr, final_path, fmt["params"])
            filenames.append(final_name)

            print(f"[VOXTA] Saved character image: {final_path}")

        return {
            "ui": {
                "filenames": filenames,
                "skipped": [skipped_count],
                "on_exists": [on_exists],
                "image_count": [len(filenames)],
            }
        }


NODE_CLASS_MAPPINGS = {"VoxtaExportCharacter": VoxtaExportCharacter}
NODE_DISPLAY_NAME_MAPPINGS = {"VoxtaExportCharacter": "Voxta: Export Character"}
