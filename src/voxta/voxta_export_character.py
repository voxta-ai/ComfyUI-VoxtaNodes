import os
import re
from .naming import determine_filename
from .helpers import IdFilenameBuilder, ImageExporter, FolderHelper, ComfyHelper

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
                "output_path": ("STRING", {"default": "", "multiline": False}),
                "subfolder": ("STRING", {"default": "Avatars/Default", "multiline": False}),
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
        output_format: list[str] | str,
        images: list[object],
        prompts: list[str],
        combination_ids: list[list[str]],
        output_path: list[str] | str,
        subfolder: list[str] | str,
        on_exists: list[str] | str,
    ):
        save_dir = FolderHelper.get_output_directory(output_path, subfolder)
        print("[Voxta] Filtering existing combinations in:", save_dir)

        output_format = ComfyHelper.comfy_input_to_str(output_format)
        on_exists = ComfyHelper.comfy_input_to_str(on_exists)
        if on_exists not in {"append", "overwrite", "skip"}:
            raise ValueError(f"Invalid on_exists option: {on_exists}")

        ImageExporter.require_modules()  # pragma: no cover

        fmt = ImageExporter.determine_format(output_format)
        ext = fmt["ext"]

        if len(images) != len(combination_ids):
            # Log all inputs for easier debugging
            print(f"[VOXTA] Error: images count {len(images)} != combination_ids count {len(combination_ids)}")
            for i, img in enumerate(images):
                print(f"  Image[{i}]: type={type(img)}")
            for i, cid in enumerate(combination_ids):
                print(f"  CombinationIDs[{i}]: {cid}")
            raise ValueError("images and combination_ids length mismatch")

        # Broadcast single prompt
        if len(prompts) == 1 and len(images) > 1:
            prompts = prompts * len(images)

        filenames = []
        skipped_count = 0

        def split_trailing_number(stem: str):
            m = re.match(r"^(.*?)(\d+)$", stem)
            if not m:
                return stem, None
            base, num = m.group(1), m.group(2)
            base = base.rstrip("._")
            if not base:
                return stem, None
            try:
                val = int(num)
            except ValueError:
                return stem, None
            if val < 1:
                val = 1
            if val > 99:
                val = 99
            return base, val

        # Cache max enumerations per base stem to avoid rescanning directory each time in append mode
        cached_max: dict[str, int] = {}

        for idx, id_list in enumerate(combination_ids):
            ids = list(id_list) if isinstance(id_list, (list, tuple)) else [str(id_list)]
            filtered_ids = [s for s in ids if not (s.startswith("input_") and "_no_id_" in s)] or ids

            # Determine stem and potential base index (only for saving). Do NOT mutate ids.
            raw_stem = IdFilenameBuilder.sanitize_id_filename(filtered_ids) or "image"
            base_stem, base_idx = split_trailing_number(raw_stem)

            if on_exists == "append":
                # Enumeration strategy:
                #   If no trailing digits -> use determine_filename (legacy behavior).
                #   If trailing digits -> treat them as starting index; enumerate using base stem.
                if base_idx is None:
                    final_name = determine_filename(filtered_ids, ext, save_dir)
                else:
                    # Find current max for base stem if not cached
                    if base_stem not in cached_max:
                        max_found = 0
                        pattern = re.compile(rf"^{re.escape(base_stem)}_(\d+){re.escape(ext)}$")
                        try:
                            for f in os.listdir(save_dir):
                                m2 = pattern.match(f)
                                if m2:
                                    n = int(m2.group(1))
                                    if n > max_found:
                                        max_found = n
                        except FileNotFoundError:
                            pass
                        cached_max[base_stem] = max_found
                    max_found = cached_max[base_stem]
                    # Choose next enumeration: if provided base is ahead, jump to it; else continue sequence
                    if base_idx <= max_found:
                        next_enum = max_found + 1
                    else:
                        next_enum = base_idx
                    if next_enum > 99:
                        raise ValueError(f"Exceeded 99 variations for stem '{base_stem}' in {save_dir}")
                    final_name = f"{base_stem}_{next_enum:02d}{ext}"
                    cached_max[base_stem] = next_enum
            else:
                # overwrite / skip modes: predictable enumeration order within this batch.
                # Use provided base index if any for first occurrence of a stem; subsequent ones increment.
                stem_key = base_stem if base_idx is not None else raw_stem
                if stem_key not in cached_max:
                    cached_max[stem_key] = (base_idx - 1) if base_idx else 0
                next_enum = cached_max[stem_key] + 1
                if base_idx and next_enum < base_idx:
                    next_enum = base_idx
                if next_enum > 99:
                    raise ValueError(f"Exceeded 99 variations for stem '{stem_key}' in batch")
                final_name = f"{stem_key}_{next_enum:02d}{ext}"
                cached_max[stem_key] = next_enum
                final_path = os.path.join(save_dir, final_name)
                if os.path.exists(final_path):
                    if on_exists == "skip":
                        skipped_count += 1
                        continue
                    # overwrite falls through

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
