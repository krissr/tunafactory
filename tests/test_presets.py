from tunafactory.run.presets import select_preset


def test_select_preset_boundaries():
    assert select_preset(1000) == "small"
    assert select_preset(10000) == "medium"
    assert select_preset(100000) == "large"
