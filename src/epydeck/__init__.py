from ast import literal_eval
from collections import defaultdict
from io import StringIO, TextIOBase
from re import search

# Specific deck keywords that use : instead of =
special_keywords = ["include_species", "identify"]


def _strip_comment(line: str) -> str:
    """Remove comments from line"""

    comment_start = line.find("#")
    if comment_start < 0:
        return line

    return line[:comment_start]


def _join_lines(line: str, fh: TextIOBase) -> str:
    """Handle escaped newlines"""
    while "\\" in line:
        next_line = next(fh)
        clean_line = line.replace("\\", "").strip()
        line = f"{clean_line} {next_line.strip()}"

    return line


def _parse_block(line: str, fh: TextIOBase) -> dict:
    """Parse a single options block into a dict."""
    result = defaultdict(list)
    _, name = line.split(":")
    comment_index = 0  # Track index for standalone comments
    comment_indices = defaultdict(int)  # Track indices for each key

    for line in fh:
        line = _join_lines(line, fh).strip()

        # Handle empty lines
        if not line:
            continue

        # Handle end of block
        if line.lower().startswith("end:"):
            _, end_name = line.split(":")
            if end_name != name:
                raise ValueError(
                    f"Block name mismatch: expected '{name}', got '{end_name}'"
                )
            break

        # Handle standalone comments
        if line.startswith("#"):
            comment_key = f"comment_{comment_index}"
            result[comment_key].append(line[1:].strip())
            comment_index += 1
            continue

        # Handle inline comments (e.g., key = value # comment)
        if "#" in line:
            line, comment = line.split("#", 1)
            line = line.strip()
            comment = comment.strip()
        else:
            comment = None

        # Handle special keywords
        if any(line.lower().startswith(f"{keyword}:") for keyword in special_keywords):
            separator = ":"
        else:
            separator = "="

        key, value = line.split(separator)
        key = key.strip()

        try:
            value = literal_eval(value.strip())
        except (ValueError, SyntaxError):
            value = value.strip()

        # Convert T/F strings to booleans
        if value == "F":
            value = False
        elif value == "T":
            value = True

        # Store the value
        result[key].append(value)

        # Store the inline comment, if present
        if comment:
            comment_index = comment_indices[key]
            comment_key = f"{key}_inline_comment_{comment_index}"
            result[comment_key] = comment
            comment_indices[key] += 1  # Increment index for this key

    # Simplify lists to single values if only one item
    result = {k: v[0] if len(v) == 1 else v for k, v in result.items()}

    return name, result


def load(fh: TextIOBase) -> tuple[dict, list]:
    """Load a whole EPOCH input deck into a Python dict and return block order"""
    result = defaultdict(dict)
    block_order = []

    for line in fh:
        line = _strip_comment(line).strip()
        line = _join_lines(line, fh)

        if not line:
            continue

        if line.lower().startswith("begin:"):
            block_name, block = _parse_block(line, fh)

            if "name" in block:
                nested_block_name = block["name"]
                block_order.append(f"{block_name}:{nested_block_name}")
                block = {nested_block_name: block}
                result[block_name] |= block
            else:
                if block_name not in result:
                    result[block_name] = [block]
                    block_order.append(f"{block_name}_0")
                else:
                    result[block_name].append(block)
                    block_order.append(f"{block_name}_{len(result[block_name]) - 1}")

        if line.lower().startswith("import:"):
            # TODO
            continue

    # Simplify lists to single dict if only one item and update block_order
    for key, value in result.items():
        if isinstance(value, list) and len(value) == 1:
            result[key] = value[0]
            block_order[block_order.index(f"{key}_0")] = key

    return dict(result), block_order


def loads(text: str) -> tuple[dict, list]:
    """Load an EPOCH deck from a string"""

    with StringIO(text) as fh:
        return load(fh)


def _dump_line(fh: TextIOBase, key: str, value, inline_comment: str = None):
    """
    Writes a single line to the file, handling special keywords and inline comments.
    """
    separator = ":" if key in special_keywords else " = "

    # Format booleans as T/F
    if isinstance(value, bool):
        value = "T" if value else "F"

    # Write the line
    line = f"  {key}{separator}{value}"
    if inline_comment:
        line += f" # {inline_comment}"
    fh.write(f"{line}\n")


def _dump_block(fh: TextIOBase, name: str, block: dict):
    """Dump a single block to a file."""
    fh.write(f"begin:{name}\n")

    for key, values in block.items():
        if not isinstance(values, list):
            values = [values]

        # Write standalone comments
        if key.startswith("comment_"):
            for i, value in enumerate(values):
                fh.write(f"  # {value}\n")
            continue

        # Skip inline comments
        if "inline_comment" in key:
            continue

        for i, value in enumerate(values):
            # Check for associated inline comments
            comment_key = f"{key}_inline_comment_{i}"
            inline_comment = block.get(comment_key, None)

            # Write the key-value pair with or without inline comment
            _dump_line(fh, key, value, inline_comment)

    fh.write(f"end:{name}\n\n")


def dump(deck: dict, fh: TextIOBase, block_order: list = None) -> None:
    """Write EPOCH deck to the open file object"""
    block_order = block_order or list(deck.keys())

    for block_name in block_order:
        block = deck.get(block_name, {})

        if search(r"_\d$", block_name):
            block_name, index = block_name.rsplit("_", 1)
            block = deck[block_name][int(index)]
        elif ":" in block_name:
            block_name, nested_block_name = block_name.split(":")
            block = deck[block_name][nested_block_name]

        # Is this one of multiple blocks?
        if isinstance(list(block.values())[0], dict):
            for subblock in block.values():
                _dump_block(fh, block_name, subblock)
        else:
            _dump_block(fh, block_name, block)


def dumps(deck: dict, block_order: list = None) -> str:
    """Write EPOCH deck to string"""
    fh = StringIO()
    dump(deck, fh, block_order)
    return fh.getvalue()


def deep_update(deck: dict, *deck_patches: dict) -> dict:
    """Update `deck` recursively (like `dict.update` without
    clobbering the nested dicts)

    Lightly adapted from pydantic, MIT licence
    """
    updated_deck = deck.copy()
    for deck_patch in deck_patches:
        for k, v in deck_patch.items():
            if (
                k in updated_deck
                and isinstance(updated_deck[k], dict)
                and isinstance(v, dict)
            ):
                updated_deck[k] = deep_update(updated_deck[k], v)
            else:
                updated_deck[k] = v
    return updated_deck
