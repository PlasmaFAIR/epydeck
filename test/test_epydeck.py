import epydeck


def test_deep_update():
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

    patch = {
        "repeated_block": {"first": {"b": 7}},
        "block": {"b": 7.8, "e": True, "d": "20 * femto"}}

    expected = {
        "repeated_block": {
            "first": {"name": "first", "a": 1, "b": 7, "c": 3},
            "second": {"name": "second", "a": 4, "b": 5, "c": 6},
        },
        "block": {
            "a": 1,
            "b": 7.8,
            "c": "electron",
            "d": "20 * femto",
            "e": True,
            "f": True,
        },
    }

    result = epydeck.deep_update(deck, patch)

    assert result == expected
