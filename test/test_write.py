import epydeck
from textwrap import dedent


def test_basic_block():
    expected = dedent(
        """\
        begin:block
          a = 1
          b = 2.3
          c = electron
          d = 10 * femto
          e = F
          f = T
        end:block

        """
    )

    deck = {
        "block": {
            "a": 1,
            "b": 2.3,
            "c": "electron",
            "d": "10 * femto",
            "e": False,
            "f": True,
        }
    }
    result = epydeck.dumps(deck)

    assert expected == result


def test_repeated_line():
    expected = dedent(
        """\
        begin:block
          a = 1
          b = 2
          c = 3
          c = 4
        end:block

        """
    )

    deck = {"block": {"a": 1, "b": 2, "c": [3, 4]}}
    result = epydeck.dumps(deck)

    assert expected == result


def test_repeated_block():
    expected = dedent(
        """\
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
    )

    deck = {
        "block": {
            "first": {"name": "first", "a": 1, "b": 2, "c": 3},
            "second": {"name": "second", "a": 4, "b": 5, "c": 6},
        }
    }
    result = epydeck.dumps(deck)

    assert expected == result


def test_include_species():
    expected = dedent(
        """\
        begin:dist_fn
          a = 1
          include_species:Electron
          include_species:Proton
        end:dist_fn
    
        """
    )

    deck = {"dist_fn": {"a": 1, "include_species": ["Electron", "Proton"]}}
    result = epydeck.dumps(deck)

    assert expected == result


def test_include_identify():
    expected = dedent(
        """\
        begin:dist_fn
          a = 1
          identify:Electron
          identify:Proton
        end:dist_fn
    
        """
    )

    deck = {"dist_fn": {"a": 1, "identify": ["Electron", "Proton"]}}
    result = epydeck.dumps(deck)

    assert expected == result


def test_write_to_file(tmp_path):
    deck = {
        "repeated_block": {
            "first": {"name": "first", "a": 1, "b": 2, "c": 3},
            "second": {"name": "second", "a": 4, "b": 5, "c": 6},
        },
        "block": {
            "a": 1,
            "b": 2.3,
            "c": "electron",
            "d": "10 * femto",
            "e": False,
            "f": True,
        },
    }

    filename = tmp_path / "test.in"
    with open(filename, "w") as f:
        epydeck.dump(deck, f)

    with open(filename, "r") as f:
        data = epydeck.load(f)

    assert data == deck
