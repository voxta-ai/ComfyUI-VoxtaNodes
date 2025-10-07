from pathlib import Path
from voxta.naming import determine_filename


def test_determine_filename_enumeration(tmp_path):
    save_dir = tmp_path
    stem_counts = {}
    ids = ["Neutral", "Thinking"]
    name1 = determine_filename(ids, stem_counts, ".png", str(save_dir))
    assert name1 == "Neutral_Thinking_01.png"
    # Touch the file to force on-disk collision logic
    (save_dir / name1).write_text("dummy")

    name2 = determine_filename(ids, stem_counts, ".png", str(save_dir))
    assert name2 == "Neutral_Thinking_02.png"

    # Ensure counter persisted
    assert stem_counts["Neutral_Thinking"] == 2


def test_determine_filename_sanitization(tmp_path):
    save_dir = tmp_path
    stem_counts = {}
    ids = ["A*B", "C:D"]
    name = determine_filename(ids, stem_counts, ".png", str(save_dir))
    # Expect illegal characters replaced with underscores and enumeration
    assert name == "A_B_C_D_01.png"
    assert Path(save_dir, name).exists() is False  # function does not create the file
