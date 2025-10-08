from pathlib import Path

from voxta_export_character import VoxtaExportCharacter
from .conftest import make_rgba


def test_initialization():
    assert isinstance(VoxtaExportCharacter(), VoxtaExportCharacter)


def test_signature_and_meta():
    assert VoxtaExportCharacter.RETURN_TYPES == ()
    assert VoxtaExportCharacter.FUNCTION == "execute"
    assert VoxtaExportCharacter.CATEGORY == "Voxta"


def test_with_custom_output_path_and_subfolder(tmp_path):
    node = VoxtaExportCharacter()
    images = [make_rgba(), make_rgba(a=0.5)]
    prompts = ["p1", "p2"]
    combination_ids = [["Neutral", "Idle"], ["Neutral", "Idle"]]

    custom_root = tmp_path / "custom_output"

    result = node.execute(
        output_format=[".webp lossy 80"],
        images=images,
        prompts=prompts,
        combination_ids=combination_ids,
        output_path=[str(custom_root)],
        subfolder=["my*sub:folder"],
        on_exists=["append"],
    )

    filenames = result["ui"]["filenames"]
    assert filenames == ["Neutral_Idle_01.webp", "Neutral_Idle_02.webp"], filenames

    expected_dir = custom_root / "my_sub_folder"
    for f in filenames:
        assert (expected_dir / f).exists()


def test_fallback_default_root(chdir_tmp):
    node = VoxtaExportCharacter()
    images = [make_rgba()]
    prompts = ["only"]
    combination_ids = [["only", "id"]]

    result = node.execute(
        output_format=[".png lossless"],
        images=images,
        prompts=prompts,
        combination_ids=combination_ids,
        output_path=[],
        subfolder=[],
        on_exists=[],
    )

    filenames = result["ui"]["filenames"]
    assert filenames == ["only_id_01.png"], filenames
    assert (Path("output") / filenames[0]).exists()


# ---------------- New tests for on_exists behavior -----------------


def test_on_exists_overwrite(tmp_path):
    node = VoxtaExportCharacter()
    root = tmp_path / "root"
    sub = "chars"
    target_dir = root / sub
    target_dir.mkdir(parents=True)

    # Pre-create file that should be overwritten
    pre_file = target_dir / "Neutral_Idle_01.webp"
    pre_file.write_bytes(b"OLD")
    old_size = pre_file.stat().st_size

    images = [make_rgba()]
    prompts = ["p"]
    combination_ids = [["Neutral", "Idle"]]

    res = node.execute(
        output_format=[".webp lossy 90"],
        images=images,
        prompts=prompts,
        combination_ids=combination_ids,
        output_path=[str(root)],
        subfolder=[sub],
        on_exists=["overwrite"],
    )

    filenames = res["ui"]["filenames"]
    assert filenames == ["Neutral_Idle_01.webp"], filenames
    new_size = pre_file.stat().st_size
    assert new_size != old_size  # overwritten with real image
    assert res["ui"]["skipped"] == [0]
    assert res["ui"]["on_exists"] == ["overwrite"]


def test_on_exists_skip(tmp_path):
    node = VoxtaExportCharacter()
    root = tmp_path / "root"
    sub = "chars"
    target_dir = root / sub
    target_dir.mkdir(parents=True)

    pre_file = target_dir / "Neutral_Idle_01.webp"
    pre_file.write_bytes(b"ORIGINAL")
    original_content = pre_file.read_bytes()

    images = [make_rgba()]
    prompts = ["p"]
    combination_ids = [["Neutral", "Idle"]]

    res = node.execute(
        output_format=[".webp lossy 80"],
        images=images,
        prompts=prompts,
        combination_ids=combination_ids,
        output_path=[str(root)],
        subfolder=[sub],
        on_exists=["skip"],
    )

    # Should skip saving new file
    assert res["ui"]["filenames"] == []
    assert res["ui"]["skipped"] == [1]
    assert pre_file.read_bytes() == original_content  # unchanged
    assert res["ui"]["on_exists"] == ["skip"]
