from pathlib import Path

from voxta_export_character import VoxtaExportCharacter

from .conftest import make_rgba  # reuse helper


def test_initialization():
    assert isinstance(VoxtaExportCharacter(), VoxtaExportCharacter)


def test_return_types():
    assert VoxtaExportCharacter.RETURN_TYPES == ("IMAGE",)
    assert VoxtaExportCharacter.FUNCTION == "test"
    assert VoxtaExportCharacter.CATEGORY == "Voxta"


def test_new_signature_with_full_path(chdir_tmp, tmp_path):
    node = VoxtaExportCharacter()
    images = [make_rgba(), make_rgba(a=0.5)]
    prompts = ["prompt one", "prompt two"]
    # duplicate id set -> enumerate _01, _02
    combination_ids = [["Neutral", "Thinking"], ["Neutral", "Thinking"]]

    target_dir = tmp_path / "custom_root"

    result = node.copy_and_rename(
        str(target_dir),  # target_full_path
        "my*sub:folder",  # target_subfolder (sanitize)
        ".webp lossy 80",  # output_format
        images,
        prompts,
        combination_ids,
    )

    filenames = result["filenames"]
    assert filenames == ["Neutral_Thinking_01.webp", "Neutral_Thinking_02.webp"], f"Unexpected filenames: {filenames}"

    save_dir = target_dir / "my_sub_folder"
    for f in filenames:
        assert (save_dir / f).exists()


def test_new_signature_default_root(chdir_tmp):
    node = VoxtaExportCharacter()
    images = [make_rgba()]
    prompts = ["only prompt"]
    combination_ids = [["only", "id"]]

    result = node.copy_and_rename(
        "",  # empty full path -> default output
        "export",  # subfolder
        ".png lossless",
        images,
        prompts,
        combination_ids,
    )

    filenames = result["filenames"]
    assert filenames == ["only_id_01.png"], f"Unexpected filename: {filenames}"
    assert (Path("output") / "export" / filenames[0]).exists()
