import os
import logging
import re
from .helpers import FolderHelper, IdFilenameBuilder

try:  # pragma: no cover
    import folder_paths  # type: ignore
except Exception:  # pragma: no cover

    class folder_paths:  # type: ignore
        @staticmethod
        def get_output_directory() -> str:
            return os.path.join(os.getcwd(), "output")


logger = logging.getLogger(__name__)


class VoxtaFilterExistingCombinations:
    """Filter existing combinations from PromptCombinator output.

    Simplified rule (index-aware):
    - If an ID ends with digits (e.g. Talking5), those digits define a desired base index.
      We only skip that combination if a file for the SAME stem (without digits) and the SAME index already exists.
    - If an ID does NOT end with digits, we fall back to the older behavior: skip if *any* enumerated file for that stem exists.
    This prevents unrelated numbered variants (Talking1 vs Talking2) from colliding and being over-filtered.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "combination_ids": ("PROMPTCOMBINATORIDS",),
                "prompts": ("STRING", {"forceInput": True}),
            },
            "optional": {
                "output_path": ("STRING", {"default": "", "multiline": False}),
                "subfolder": ("STRING", {"default": "Avatars/Default", "multiline": False}),
                "skip_existing_targets": ("BOOLEAN", {"default": True}),
            },
        }

    INPUT_IS_LIST = True
    RETURN_TYPES = ("PROMPTCOMBINATORIDS", "STRING")
    RETURN_NAMES = ("combination_ids", "prompts")
    OUTPUT_IS_LIST = (True, True)
    FUNCTION = "execute"
    CATEGORY = "Voxta"

    # noinspection PyMethodMayBeStatic
    def execute(
        self,
        combination_ids: list[list[str]],
        prompts: list[str],
        output_path: list[str],
        subfolder: list[str],
        skip_existing_targets: list[bool],
    ):
        bypass = not (skip_existing_targets[0] if skip_existing_targets else True)
        if bypass:
            summary = f"Kept all {len(combination_ids)} combinations (bypass)"
            return {
                "result": (combination_ids, prompts),
                "ui": {"summary": [summary], "skipped": [0], "kept": [len(combination_ids)]},
            }

        save_dir = FolderHelper.get_output_directory(output_path, subfolder)

        # Prompt broadcasting
        if len(prompts) == 1 and len(combination_ids) > 1:
            prompts = prompts * len(combination_ids)
        elif len(prompts) != len(combination_ids):
            raise ValueError("Prompt and combination ID lists must have same length or 1 prompt.")

        # Scan existing files once; collect enumerated indices per stem
        stem_indices: dict[str, set[int]] = {}
        if os.path.exists(save_dir):
            print("[Voxta] Scanning existing files in:", save_dir)
            for file in os.listdir(save_dir):
                m = re.match(r"^(?P<stem>.+?)_(?P<idx>\d{2})\.[A-Za-z0-9]+$", file)
                if not m:
                    continue
                stem = m.group("stem")
                idx = int(m.group("idx"))
                stem_indices.setdefault(stem, set()).add(idx)

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
            if val < 1 or val > 99:
                return base, None  # out-of-range ignored for filtering purposes
            return base, val

        kept_cids: list[list[str]] = []
        kept_prompts: list[str] = []
        skipped = 0

        for cid, prompt in zip(combination_ids, prompts):
            full_stem = IdFilenameBuilder.sanitize_id_filename(cid)
            base_stem, base_idx = split_trailing_number(full_stem)
            if base_idx is not None:
                existing = stem_indices.get(base_stem, set())
                if base_idx in existing:
                    skipped += 1
                    continue
            else:
                if stem_indices.get(full_stem):
                    skipped += 1
                    continue
            kept_cids.append(cid)
            kept_prompts.append(prompt)

        if not kept_cids:
            raise ValueError("All combinations were filtered out, nothing to generate.")

        summary = f"Kept {len(kept_cids)} of {len(combination_ids)} combinations."
        return {
            "result": (kept_cids, kept_prompts),
            "ui": {"summary": [summary], "skipped": [skipped], "kept": [len(kept_cids)]},
        }


NODE_CLASS_MAPPINGS = {"VoxtaFilterExistingCombinations": VoxtaFilterExistingCombinations}
NODE_DISPLAY_NAME_MAPPINGS = {"VoxtaFilterExistingCombinations": "Voxta: Filter Existing Combinations"}

__all__ = [
    "VoxtaFilterExistingCombinations",
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
]
