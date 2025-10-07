from pathlib import Path

from voxta_export_character import VoxtaExportCharacter
from .conftest import make_rgba


def test_initialization():
    assert isinstance(VoxtaExportCharacter(), VoxtaExportCharacter)


def test_signature_and_meta():
    assert VoxtaExportCharacter.RETURN_TYPES == ()
    assert VoxtaExportCharacter.FUNCTION == "copy_and_rename"
    assert VoxtaExportCharacter.CATEGORY == "Voxta"


def test_with_custom_output_path_and_subfolder(tmp_path):
    node = VoxtaExportCharacter()
    images = [make_rgba(), make_rgba(a=0.5)]
    prompts = ["p1", "p2"]
    combination_ids = [["Neutral", "Idle"], ["Neutral", "Idle"]]

    custom_root = tmp_path / "custom_output"

    result = node.copy_and_rename(
        output_format=".webp lossy 80",
        images=images,
        prompts=prompts,
        combination_ids=combination_ids,
        output_path=str(custom_root),
        subfolder="my*sub:folder",
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

    result = node.copy_and_rename(
        output_format=".png lossless",
        images=images,
        prompts=prompts,
        combination_ids=combination_ids,
        # No output_path provided -> fallback
    )

    filenames = result["ui"]["filenames"]
    assert filenames == ["only_id_01.png"], filenames
    assert (Path("output") / filenames[0]).exists()
