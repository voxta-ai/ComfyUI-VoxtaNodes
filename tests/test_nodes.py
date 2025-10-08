from importlib import import_module


def test_node_mappings_exposed():
    nodes_mod = import_module("voxta.nodes")
    mappings = getattr(nodes_mod, "NODE_CLASS_MAPPINGS", {})
    assert "VoxtaExportCharacter" in mappings, "VoxtaExportCharacter not registered"
    assert "VoxtaFilterExistingCombinations" in mappings, "VoxtaFilterExistingCombinations not registered"
