import pathlib

import epydeck


def test_basic_block():
    text = """
    begin:block
      a = 1
      b = 2e3
      c = electron
      d = 10 * femto
      e = F
      f = T
    end:block
    """

    data, block_order = epydeck.loads(text)

    expected = {
        "block": {
            "a": 1,
            "b": 2e3,
            "c": "electron",
            "d": "10 * femto",
            "e": False,
            "f": True,
        }
    }
    expected_block_order = ["block"]

    assert expected == data
    assert expected_block_order == block_order


def test_basic_block_with_name():
    text = """
    begin:block
      name = first
      a = 1
      b = 2
      c = 3
    end:block
    """

    data, block_order = epydeck.loads(text)

    expected = {"block": {"first": {"name": "first", "a": 1, "b": 2, "c": 3}}}
    expected_block_order = ["block:first"]

    assert expected == data
    assert expected_block_order == block_order


def test_basic_block_with_comment():
    text = """
    begin:block
      a = 1
      # This is a comment
      b = 2
      c = 3
    end:block
    """

    data, block_order = epydeck.loads(text)

    expected = {
        "block": {
            "a": 1,
            "comment_0": "This is a comment",
            "b": 2,
            "c": 3,
        }
    }
    expected_block_order = ["block"]

    assert expected == data
    assert expected_block_order == block_order


def test_basic_block_with_inline_comment():
    text = """
    begin:block
      a = 1
      b = 2 # This is a comment
      c = 3
    end:block
    """

    data, block_order = epydeck.loads(text)

    expected = {
        "block": {
            "a": 1,
            "b": 2,
            "b_inline_comment_0": "This is a comment",
            "c": 3,
        }
    }
    expected_block_order = ["block"]

    assert expected == data
    assert expected_block_order == block_order


def test_repeated_line():
    text = """
    begin:block
      a = 1
      b = 2
      c = 3
      c = 4
    end:block
    """

    data, _ = epydeck.loads(text)

    expected = {"block": {"a": 1, "b": 2, "c": [3, 4]}}

    assert expected == data


def test_repeated_block():
    text = """
    begin:block
      name = first
      a = 1
      b = 2
      c = 3
    end:block

    begin:block
      name = second
      a = 4
      b = 5
      c = 6
    end:block
    """

    data, block_order = epydeck.loads(text)

    expected = {
        "block": {
            "first": {"name": "first", "a": 1, "b": 2, "c": 3},
            "second": {"name": "second", "a": 4, "b": 5, "c": 6},
        }
    }
    expected_block_order = ["block:first", "block:second"]

    assert expected == data
    assert expected_block_order == block_order


def test_include_species():
    text = """
    begin:dist_fn
      a = 1
      include_species:Electron
      include_species:Proton
    end:dist_fn
    """

    data, _ = epydeck.loads(text)

    expected = {"dist_fn": {"a": 1, "include_species": ["Electron", "Proton"]}}

    assert expected == data


def test_include_identify():
    text = """
    begin:dist_fn
      a = 1
      identify:Electron
      identify:Proton
    end:dist_fn
    """

    data, _ = epydeck.loads(text)

    expected = {"dist_fn": {"a": 1, "identify": ["Electron", "Proton"]}}

    assert expected == data


def test_read_file():
    filename = pathlib.Path(__file__).parent / "cone.deck"

    with open(filename) as f:
        data, block_order = epydeck.load(f)

    assert "control" in data
    assert len(data["control"]) == 2
    assert "species" in data
    assert "proton" in data["species"]
    assert "electron" in data["species"]

    expected_block_order = [
        "control_0",
        "boundaries",
        "control_1",
        "constant",
        "species:proton",
        "species:electron",
        "laser",
        "output_global",
        "output:normal",
        "output:large",
        "dist_fn:x_px",
        "dist_fn:x_px_py",
    ]

    assert expected_block_order == block_order
