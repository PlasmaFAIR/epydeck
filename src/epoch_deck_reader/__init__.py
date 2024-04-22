from ast import literal_eval
from io import TextIOBase
from collections import defaultdict


def _strip_comment(line: str) -> str:
    comment_start = line.find("#")
    if comment_start < 0:
        return line

    return line[:comment_start]


def _join_lines(line: str, fh: TextIOBase) -> str:
    while "\\" in line:
        next_line = next(fh)
        clean_line = line.replace("\\", "").strip()
        line = f"{clean_line} {next_line.strip()}"

    return line


def _parse_block(line: str, fh: TextIOBase) -> dict:
    result = defaultdict(list)

    _, name = line.split(":")

    for line in fh:
        line = _strip_comment(line).strip()
        line = _join_lines(line, fh)

        if not line:
            continue

        if line.lower().startswith("end:"):
            _, end_name = line.split(":")
            if end_name != name:
                raise ValueError(f"Block name mismatch: expected '{name}', got '{end_name}'")
            break

        if line.lower().startswith("include_species:"):
            separator = ":"
        else:
            separator = "="

        key, value = line.split(separator)
        key = key.strip()

        try:
            value = literal_eval(value)
        except (ValueError, SyntaxError):
            value = value.strip()

        result[key].append(value)

    # Strip out useless lists
    result = {k: v[0] if len(v) == 1 else v for k, v in result.items()}

    return name, result


def parse(fh: TextIOBase) -> dict:
    """Parse a whole EPOCH input deck into a Python dict"""
    result = defaultdict(dict)

    for line in fh:
        line = _strip_comment(line).strip()
        line = _join_lines(line, fh)

        if not line:
            continue

        if line.lower().startswith("begin:"):
            block_name, block = _parse_block(line, fh)

            if "name" in block:
                block = {block["name"]: block}

            result[block_name] |= block

        if line.lower().startswith("import:"):
            # TODO
            continue

    return dict(result)
