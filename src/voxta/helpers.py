import os
import re
from typing import Iterable

try:  # pragma: no cover
    import folder_paths  # type: ignore
except Exception:  # pragma: no cover

    class folder_paths:  # type: ignore
        @staticmethod
        def get_output_directory() -> str:
            return os.path.join(os.getcwd(), "output")


try:  # pragma: no cover
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None  # type: ignore

try:  # pragma: no cover
    import numpy as np
except Exception:  # pragma: no cover
    np = None  # type: ignore


class FolderHelper:
    """Helper to manage folder paths."""

    @staticmethod
    def get_output_directory(target: list[str], subfolder: list[str]) -> str:
        output_path = target[0].strip() if len(target) else folder_paths.get_output_directory()
        os.makedirs(output_path, exist_ok=True)
        subfolder = subfolder[0] if len(subfolder) else ""
        if subfolder:
            subfolder = FolderHelper.sanitize_subfolder(subfolder)
            output_path = os.path.join(output_path, subfolder)
            os.makedirs(output_path, exist_ok=True)
        return output_path

    @staticmethod
    def sanitize_subfolder(sub: str) -> str:
        sub = re.sub(r'[:*?"<>|]+', "_", sub or "").strip()
        if sub in {".", ".."}:
            sub = ""
        sub = sub.replace(".", "")
        return sub or ""

    @staticmethod
    def sanitize_full_path(path: str) -> str:
        path = path.strip()
        if not path:
            return ""
        path = os.path.expanduser(os.path.expandvars(path))
        return os.path.abspath(path)


class IdFilenameBuilder:
    """Responsible for sanitizing pieces and building unique filenames for new interface."""

    @staticmethod
    def sanitize_id_filename(id_list: Iterable[str]) -> str:
        # Remove entries that contain the substring _no_id_
        id_list = [i for i in id_list if "_no_id_" not in i]
        # Join with underscore and aggressively sanitize; collapse repeats.
        raw = "_".join(id_list)
        raw = raw.replace(" ", "_")
        raw = re.sub(r"[^A-Za-z0-9_.]", "_", raw)
        raw = re.sub(r"_+", "_", raw)  # collapse multiple underscores
        raw = raw.strip("_.")
        return raw or "image"

    @staticmethod
    def ensure_unique(stem: str, ext: str, used: set[str]) -> str:
        candidate = stem
        counter = 1
        while f"{candidate}{ext}" in used:
            candidate = f"{stem}_{counter}"
            counter += 1
        final = f"{candidate}{ext}"
        used.add(final)
        return final


class ImageExporter:
    """Encapsulates image format determination and saving logic."""

    FORMAT_MAP = {
        ".png lossless": {"ext": ".png", "params": {"format": "PNG", "compress_level": 4}},
        ".webp lossless": {"ext": ".webp", "params": {"format": "WEBP", "lossless": True, "quality": 100, "method": 6}},
        ".webp lossy 80": {"ext": ".webp", "params": {"format": "WEBP", "lossless": False, "quality": 80, "method": 6}},
        ".webp lossy 90": {"ext": ".webp", "params": {"format": "WEBP", "lossless": False, "quality": 90, "method": 6}},
    }

    @staticmethod
    def require_modules():  # pragma: no cover
        if Image is None:
            raise RuntimeError("Pillow is required (missing PIL.Image).")
        if np is None:
            raise RuntimeError("NumPy is required (missing numpy module).")

    @classmethod
    def determine_format(cls, option: str):
        return cls.FORMAT_MAP.get(option, cls.FORMAT_MAP[".webp lossy 90"])  # default

    @staticmethod
    def to_numpy(image):
        try:
            if hasattr(image, "cpu") and callable(getattr(image, "cpu")):
                return image.squeeze(0).cpu().numpy()
            return image
        except Exception:
            return image

    @staticmethod
    def save_image(arr, final_path: str, fmt_params):
        if arr is None:
            raise ValueError("Unsupported image type")
        if arr.ndim == 4 and arr.shape[0] == 1:
            arr = arr[0]
        if arr.max() <= 1.5:
            arr = arr * 255.0
        arr = arr.clip(0, 255).astype("uint8")
        # Let Pillow infer mode; ensure shape is (H,W,3) or (H,W,4)
        if arr.ndim != 3 or arr.shape[2] not in (3, 4):
            raise ValueError("Image array must be HxWx3 or HxWx4 after preprocessing")
        img = Image.fromarray(arr)
        img.save(final_path, **fmt_params)  # type: ignore[arg-type]
