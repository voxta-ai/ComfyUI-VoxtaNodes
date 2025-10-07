import os
import sys
import numpy as np
import pytest

# Ensure project root and src path are importable
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_dir = os.path.join(root_dir, "src")
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)


# ---------------- Shared helpers -----------------


def make_rgb(width: int = 16, height: int = 16, color: float = 0.5):
    """Return a simple RGB float32 image in [0,1]."""
    arr = np.ones((height, width, 3), dtype=np.float32) * color
    return arr


def make_rgba(width: int = 8, height: int = 8, a: float = 1.0):
    arr = np.zeros((height, width, 4), dtype=np.float32)
    arr[..., 0] = 0.2
    arr[..., 1] = 0.4
    arr[..., 2] = 0.6
    arr[..., 3] = a
    return arr


# ---------------- Fixtures -----------------


@pytest.fixture()
def node():
    from voxta.voxta_export_character import VoxtaExportCharacter

    return VoxtaExportCharacter()


@pytest.fixture()
def chdir_tmp(tmp_path):
    """Run test within an isolated working directory."""
    old = os.getcwd()
    os.chdir(tmp_path)
    try:
        yield tmp_path
    finally:
        os.chdir(old)
