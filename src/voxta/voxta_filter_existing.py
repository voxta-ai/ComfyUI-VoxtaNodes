import os
import logging
import re
import random
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
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "output_path": ("STRING", {"default": "", "multiline": False}),
                "subfolder": ("STRING", {"default": "Avatars/Default", "multiline": False}),
                "combination_ids": ("PROMPTCOMBINATORIDS",),
                "prompts": ("STRING", {"forceInput": True}),
                "behavior": (
                    [
                        "all",
                        "new only",
                        "single (first)",
                        "single (last)",
                        "single (random)",
                    ],
                    {"default": "all"},
                ),
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
        output_path: list[str] | str,
        subfolder: list[str] | str,
        behavior: list[str] | str,
    ):
        # Normalize behavior (ComfyUI often wraps scalars in lists)
        if isinstance(behavior, list):
            behavior_value = behavior[0] if behavior else "all"
        else:
            behavior_value = behavior or "all"

        save_dir = FolderHelper.get_output_directory(output_path, subfolder)
        print("[Voxta] Filtering existing combinations in:", save_dir)

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

        exists_flags: list[bool] = []
        stems: list[str] = []
        indices: list[int | None] = []
        for cid in combination_ids:
            full_stem = IdFilenameBuilder.sanitize_id_filename(cid)
            base_stem, base_idx = split_trailing_number(full_stem)
            stems.append(base_stem if base_idx is not None else full_stem)
            indices.append(base_idx)
            if base_idx is not None:
                existing = stem_indices.get(base_stem, set())
                exists_flags.append(base_idx in existing)
            else:
                exists_flags.append(bool(stem_indices.get(full_stem)))

        total = len(combination_ids)

        # Behavior handling
        if behavior_value == "all":
            kept_cids = combination_ids
            kept_prompts = prompts
            skipped = 0
            summary = f"Kept all {total} combinations (all)."
        else:
            # Determine new (non-existing) combos
            new_indices = [i for i, exists in enumerate(exists_flags) if not exists]
            if behavior_value == "new only":
                if not new_indices:
                    raise ValueError("All combinations were filtered out, nothing to generate.")
                kept_cids = [combination_ids[i] for i in new_indices]
                kept_prompts = [prompts[i] for i in new_indices]
                skipped = total - len(new_indices)
                summary = f"Kept {len(kept_cids)} of {total} combinations."
            elif behavior_value.startswith("single"):
                candidate_indices = new_indices if new_indices else list(range(total))
                if behavior_value == "single (first)":
                    pick_index = candidate_indices[0]
                elif behavior_value == "single (last)":
                    pick_index = candidate_indices[-1]
                elif behavior_value == "single (random)":
                    pick_index = random.choice(candidate_indices)
                else:
                    raise ValueError(f"Unsupported behavior: {behavior_value}")
                kept_cids = [combination_ids[pick_index]]
                kept_prompts = [prompts[pick_index]]
                skipped = total - 1
                source = "new" if pick_index in new_indices else "existing"
                summary = f"Selected 1 combination ({behavior_value}, {source})."
            else:
                raise ValueError(f"Unsupported behavior: {behavior_value}")

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
