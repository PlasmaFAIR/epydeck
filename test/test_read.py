from epoch_deck_reader import parse

from io import StringIO


def test_basic_block():
    text = """
    begin:block
      a = 1
      b = 2e3
      c = electron
      d = 10 * femto
    end:block
    """

    with StringIO(text) as fh:
        data = parse(fh)

    expected = {"block": {"a": 1, "b": 2e3, "c": "electron", "d": "10 * femto"}}

    assert expected == data


def test_repeated_line():
    text = """
    begin:block
      a = 1
      b = 2
      c = 3
      c = 4
    end:block
    """

    with StringIO(text) as fh:
        data = parse(fh)

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

    with StringIO(text) as fh:
        data = parse(fh)

    expected = {
        "block": {
            "first": {"name": "first", "a": 1, "b": 2, "c": 3},
            "second": {"name": "second", "a": 4, "b": 5, "c": 6},
        }
    }

    assert expected == data


def test_include_species():
    text = """
    begin:dist_fn
      a = 1
      include_species: electron
      include_species: proton
    end:dist_fn
    """

    with StringIO(text) as fh:
        data = parse(fh)

    expected = {"dist_fn": {"a": 1, "include_species": ["electron", "proton"]}}

    assert expected == data
