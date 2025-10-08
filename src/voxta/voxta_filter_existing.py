import os
import logging
import re
from .helpers import FolderHelper
from .naming import IdFilenameBuilder

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

    Takes prompts and combination_ids from PromptCombinator and filters out
    combinations that already have files on disk.
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

        # Handle prompt broadcasting
        if len(prompts) == 1 and len(combination_ids) > 1:
            prompts = prompts * len(combination_ids)
        elif len(prompts) != len(combination_ids):
            raise ValueError("Prompt and combination ID lists must have same length or 1 prompt.")

        kept_cids = []
        kept_prompts = []
        skipped_count = 0

        existing_stems = set()
        if os.path.exists(save_dir):
            print("[Voxta] Scanning existing files in:", save_dir)
            for file in os.listdir(save_dir):
                stem, _ = os.path.splitext(file)
                print("[Voxta] Found existing file:", file, "-> stem:", stem)
                # Strip any existing enumeration like _01, _02
                stem = re.sub(r"_\d{2,}$", "", stem)
                existing_stems.add(stem)

        for cid, prompt in zip(combination_ids, prompts):
            stem = IdFilenameBuilder.sanitize_id_filename(cid)
            print("[Voxta] Checking stem: %s", cid, stem)
            if stem in existing_stems:
                skipped_count += 1
                print("[Voxta] Skipping existing combination: %s (stem: %s)", cid, stem)
                continue
            kept_cids.append(cid)
            kept_prompts.append(prompt)

        if not kept_cids:
            raise ValueError("All combinations were filtered out, nothing to generate.")

        summary = f"Kept {len(kept_cids)} of {len(combination_ids)} combinations."
        return {
            "result": (kept_cids, kept_prompts),
            "ui": {"summary": [summary], "skipped": [skipped_count], "kept": [len(kept_cids)]},
        }


NODE_CLASS_MAPPINGS = {"VoxtaFilterExistingCombinations": VoxtaFilterExistingCombinations}
NODE_DISPLAY_NAME_MAPPINGS = {"VoxtaFilterExistingCombinations": "Voxta: Filter Existing Combinations"}

__all__ = [
    "VoxtaFilterExistingCombinations",
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
]
