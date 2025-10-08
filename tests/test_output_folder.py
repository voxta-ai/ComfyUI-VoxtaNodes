from voxta.voxta_output_folder import VoxtaOutputFolder
from voxta.voxta_filter_existing import VoxtaFilterExistingCombinations
from voxta.voxta_export_character import VoxtaExportCharacter
from .conftest import make_rgba


def test_output_folder_creates_directory(tmp_path):
    node = VoxtaOutputFolder()
    root = tmp_path / "myroot"
    sub = "My:Sub*Folder"
    res = node.execute(output_path=[str(root)], subfolder=[sub])
    # Returns tuple of raw values
    assert res == (str(root), sub)
    # Directory on disk should be sanitized version
    sanitized_sub = "My_Sub_Folder"
    expected_dir = root / sanitized_sub
    assert expected_dir.exists()


def test_output_folder_empty_defaults(chdir_tmp):
    node = VoxtaOutputFolder()
    (root, sub) = node.execute(output_path=[], subfolder=[])  # use comfy default output
    assert root == ""
    assert sub == ""


def test_integration_with_filter(tmp_path):
    folder_node = VoxtaOutputFolder()
    root = tmp_path / "root"
    sub = "chars"
    out_root, out_sub = folder_node.execute(output_path=[str(root)], subfolder=[sub])

    filter_node = VoxtaFilterExistingCombinations()
    combos = [["A", "B"]]
    prompts = ["p"]
    # Pass plain strings to simulate direct connection (no list wrapping)
    res = filter_node.execute(
        combination_ids=combos,
        prompts=prompts,
        output_path=out_root,  # type: ignore[arg-type]
        subfolder=out_sub,  # type: ignore[arg-type]
        do_not_render_if_already_exists=[True],
    )
    assert res["ui"]["kept"][0] == 1


def test_integration_with_export(tmp_path):
    folder_node = VoxtaOutputFolder()
    root = tmp_path / "root"
    sub = "chars"
    out_root, out_sub = folder_node.execute(output_path=[str(root)], subfolder=[sub])

    export_node = VoxtaExportCharacter()
    images = [make_rgba()]
    prompts = ["p"]
    combos = [["Neutral", "Idle"]]
    res = export_node.execute(
        output_format=[".webp lossy 80"],
        images=images,
        prompts=prompts,
        combination_ids=combos,
        output_path=out_root,  # type: ignore[arg-type]
        subfolder=out_sub,  # type: ignore[arg-type]
        on_exists=["append"],
    )
    assert res["ui"]["filenames"] == ["Neutral_Idle_01.webp"]
