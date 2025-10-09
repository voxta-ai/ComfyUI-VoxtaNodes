import pytest
import random
from voxta.voxta_filter_existing import VoxtaFilterExistingCombinations


def make_ids(*parts):
    return list(parts)


def test_filter_keeps_when_no_enumerated_exists(tmp_path):
    node = VoxtaFilterExistingCombinations()
    root = tmp_path / "root"
    sub = "chars"
    save_dir = root / sub
    save_dir.mkdir(parents=True)

    combos = [make_ids("Neutral", "Idle"), make_ids("Happy", "Wave")]
    prompts = ["p1", "p2"]
    res = node.execute(
        combination_ids=combos,
        prompts=prompts,
        output_path=[str(root)],
        subfolder=[sub],
        behavior=["new only"],
    )
    assert res["ui"]["skipped"][0] == 0
    assert res["ui"]["kept"][0] == 2
    assert res["result"][0] == combos


def test_filter_skips_when_index_01_exists(tmp_path):
    node = VoxtaFilterExistingCombinations()
    root = tmp_path / "root"
    sub = "chars"
    save_dir = root / sub
    save_dir.mkdir(parents=True)

    # Create Neutral_Idle_01 with any extension (webp)
    (save_dir / "Neutral_Idle_01.webp").write_bytes(b"X")

    combos = [make_ids("Neutral", "Idle"), make_ids("Happy", "Wave")]
    prompts = ["p1", "p2"]
    res = node.execute(
        combination_ids=combos,
        prompts=prompts,
        output_path=[str(root)],
        subfolder=[sub],
        behavior=["new only"],
    )
    assert res["ui"]["skipped"][0] == 1
    assert res["ui"]["kept"][0] == 1
    assert res["result"][0] == [combos[1]]


def test_filter_skips_when_other_index_exists(tmp_path):
    node = VoxtaFilterExistingCombinations()
    root = tmp_path / "root"
    sub = "chars"
    save_dir = root / sub
    save_dir.mkdir(parents=True)

    # Create index 02 only; simplified logic should still skip
    (save_dir / "Neutral_Idle_02.png").write_bytes(b"Z")

    combos = [make_ids("Neutral", "Idle"), make_ids("Happy", "Wave")]
    prompts = ["p1", "p2"]
    res = node.execute(
        combination_ids=combos,
        prompts=prompts,
        output_path=[str(root)],
        subfolder=[sub],
        behavior=["new only"],
    )
    assert res["ui"]["skipped"][0] == 1
    assert res["ui"]["kept"][0] == 1
    assert res["result"][0] == [combos[1]]


def test_filter_multiple_mixed(tmp_path):
    node = VoxtaFilterExistingCombinations()
    root = tmp_path / "root"
    sub = "chars"
    save_dir = root / sub
    save_dir.mkdir(parents=True)

    # Pre-create enumerations for two stems
    (save_dir / "Neutral_Idle_01.webp").write_bytes(b"A")
    (save_dir / "Angry_Attack_07.jpeg").write_bytes(b"B")

    combos = [
        make_ids("Neutral", "Idle"),
        make_ids("Happy", "Wave"),
        make_ids("Angry", "Attack"),
        make_ids("Calm", "Pose"),
    ]
    prompts = ["p1", "p2", "p3", "p4"]

    res = node.execute(
        combination_ids=combos,
        prompts=prompts,
        output_path=[str(root)],
        subfolder=[sub],
        behavior=["new only"],
    )
    # Two stems skipped, two kept
    assert res["ui"]["skipped"][0] == 2
    assert res["ui"]["kept"][0] == 2
    assert res["result"][0] == [combos[1], combos[3]]


def test_filter_prompts_filtered_with_combinations(tmp_path):
    node = VoxtaFilterExistingCombinations()
    root = tmp_path / "root"
    sub = "chars"
    save_dir = root / sub
    save_dir.mkdir(parents=True)
    # Existing file for first combo
    (save_dir / "Neutral_Idle_01.png").write_bytes(b"X")

    combos = [["Neutral", "Idle"], ["Happy", "Wave"]]
    prompts = ["neutral idle prompt", "happy wave prompt"]

    res = node.execute(
        combination_ids=combos,
        prompts=prompts,
        output_path=[str(root)],
        subfolder=[sub],
        behavior=["new only"],
    )
    assert res["ui"]["skipped"][0] == 1
    assert res["ui"]["kept"][0] == 1
    assert res["result"][0] == [combos[1]]
    assert res["result"][1] == ["happy wave prompt"]


def test_filter_prompts_broadcast_mode(tmp_path):
    node = VoxtaFilterExistingCombinations()
    root = tmp_path / "root"
    sub = "chars"
    save_dir = root / sub
    save_dir.mkdir(parents=True)

    # No existing files so both pass; single prompt should broadcast
    combos = [["A", "B"], ["C", "D"]]
    prompts = ["shared prompt"]
    res = node.execute(
        combination_ids=combos,
        prompts=prompts,
        output_path=[str(root)],
        subfolder=[sub],
        behavior=["new only"],
    )
    assert res["ui"]["kept"][0] == 2
    assert res["result"][1] == ["shared prompt", "shared prompt"]


def test_filter_prompts_true_length_mismatch_raises(tmp_path):
    node = VoxtaFilterExistingCombinations()
    root = tmp_path / "root"
    sub = "chars"
    (root / sub).mkdir(parents=True)
    combos = [["A", "B"], ["C", "D"], ["E", "F"]]
    prompts = ["p1", "p2"]  # length neither 1 nor equal to combos -> error
    with pytest.raises(ValueError):
        node.execute(
            combination_ids=combos,
            prompts=prompts,
            output_path=[str(root)],
            subfolder=[sub],
            behavior=["new only"],
        )


def test_filter_handles_list_wrapped_path(tmp_path):
    node = VoxtaFilterExistingCombinations()
    root = tmp_path / "root"
    sub = "chars"
    (root / sub).mkdir(parents=True)
    # Pre-create a file to trigger skip
    (root / sub / "Stem_Test_01.png").write_bytes(b"X")
    combos = [["Stem", "Test"], ["Other", "One"]]
    prompts = ["p1", "p2"]
    # Simulate ComfyUI list-wrapping scalar inputs
    res = node.execute(
        combination_ids=combos,
        prompts=prompts,
        output_path=[str(root)],
        subfolder=[sub],
        behavior=["new only"],
    )
    assert res["ui"]["skipped"][0] == 1
    assert res["ui"]["kept"][0] == 1
    assert res["result"][0] == [combos[1]]
    assert res["result"][1] == ["p2"]


def test_behavior_all_mode(tmp_path):
    node = VoxtaFilterExistingCombinations()
    root = tmp_path / "root"
    sub = "chars"
    save_dir = root / sub
    save_dir.mkdir(parents=True)
    # Create files that would normally cause skipping
    (save_dir / "Neutral_Idle_01.png").write_bytes(b"X")
    (save_dir / "Happy_Wave_01.png").write_bytes(b"X")
    combos = [["Neutral", "Idle"], ["Happy", "Wave"]]
    prompts = ["p1", "p2"]
    res = node.execute(
        combination_ids=combos,
        prompts=prompts,
        output_path=[str(root)],
        subfolder=[sub],
        behavior=["all"],
    )
    assert res["result"][0] == combos
    assert res["result"][1] == ["p1", "p2"]
    assert res["ui"]["skipped"][0] == 0
    assert res["ui"]["summary"][0].startswith("Kept all")


def test_filter_all_skipped_raises(tmp_path):
    node = VoxtaFilterExistingCombinations()
    root = tmp_path / "root"
    sub = "chars"
    save_dir = root / sub
    save_dir.mkdir(parents=True)
    (save_dir / "Neutral_Idle_01.png").write_bytes(b"X")
    (save_dir / "Happy_Wave_01.png").write_bytes(b"X")
    combos = [["Neutral", "Idle"], ["Happy", "Wave"]]
    prompts = ["p1", "p2"]
    with pytest.raises(ValueError):
        node.execute(
            combination_ids=combos,
            prompts=prompts,
            output_path=[str(root)],
            subfolder=[sub],
            behavior=["new only"],
        )


def test_single_first_prefers_new(tmp_path):
    node = VoxtaFilterExistingCombinations()
    root = tmp_path / "root"
    sub = "chars"
    save_dir = root / sub
    save_dir.mkdir(parents=True)
    # existing for first combo so new first should be second
    (save_dir / "A_B_01.png").write_bytes(b"X")
    combos = [["A", "B"], ["C", "D"], ["E", "F"]]
    prompts = ["p1", "p2", "p3"]
    res = node.execute(
        combination_ids=combos,
        prompts=prompts,
        output_path=[str(root)],
        subfolder=[sub],
        behavior=["single (first)"],
    )
    # Should pick first new -> index 1
    assert res["result"][0] == [combos[1]]
    assert res["result"][1] == ["p2"]
    assert res["ui"]["kept"][0] == 1
    assert res["ui"]["skipped"][0] == 2


def test_single_last_prefers_new(tmp_path):
    node = VoxtaFilterExistingCombinations()
    root = tmp_path / "root"
    sub = "chars"
    save_dir = root / sub
    save_dir.mkdir(parents=True)
    # existing for last combo so last new should be middle
    (save_dir / "E_F_01.png").write_bytes(b"X")
    combos = [["A", "B"], ["C", "D"], ["E", "F"]]
    prompts = ["p1", "p2", "p3"]
    res = node.execute(
        combination_ids=combos,
        prompts=prompts,
        output_path=[str(root)],
        subfolder=[sub],
        behavior=["single (last)"],
    )
    # New combos indices: 0,1 ; last new is 1
    assert res["result"][0] == [combos[1]]
    assert res["result"][1] == ["p2"]


def test_single_random_prefers_new(tmp_path, monkeypatch):
    node = VoxtaFilterExistingCombinations()
    root = tmp_path / "root"
    sub = "chars"
    save_dir = root / sub
    save_dir.mkdir(parents=True)
    (save_dir / "A_B_01.png").write_bytes(b"X")
    combos = [["A", "B"], ["C", "D"], ["E", "F"]]
    prompts = ["p1", "p2", "p3"]

    # new indices would be 1,2 -> force choose index 2
    def fake_choice(seq):
        return seq[-1]

    monkeypatch.setattr(random, "choice", fake_choice)

    res = node.execute(
        combination_ids=combos,
        prompts=prompts,
        output_path=[str(root)],
        subfolder=[sub],
        behavior=["single (random)"],
    )
    assert res["result"][0] == [combos[2]]
    assert res["result"][1] == ["p3"]


def test_single_when_no_new_uses_existing(tmp_path):
    node = VoxtaFilterExistingCombinations()
    root = tmp_path / "root"
    sub = "chars"
    save_dir = root / sub
    save_dir.mkdir(parents=True)
    # make all existing
    (save_dir / "A_B_01.png").write_bytes(b"X")
    (save_dir / "C_D_01.png").write_bytes(b"X")
    combos = [["A", "B"], ["C", "D"]]
    prompts = ["p1", "p2"]

    # single (first) should fallback to first existing
    res = node.execute(
        combination_ids=combos,
        prompts=prompts,
        output_path=[str(root)],
        subfolder=[sub],
        behavior=["single (first)"],
    )
    assert res["result"][0] == [combos[0]]
    # single (last)
    res2 = node.execute(
        combination_ids=combos,
        prompts=prompts,
        output_path=[str(root)],
        subfolder=[sub],
        behavior=["single (last)"],
    )
    assert res2["result"][0] == [combos[-1]]
