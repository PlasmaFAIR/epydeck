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
            key, value = line.split(":")
            result[key.strip()].append(value.strip())
            continue

        key, value = line.split("=")
        result[key.strip()].append(value.strip())

    return name, result


def parse(fh: TextIOBase) -> dict:
    result = defaultdict(list)

    for line in fh:
        line = _strip_comment(line).strip()
        line = _join_lines(line, fh)

        if not line:
            continue

        if line.lower().startswith("begin:"):
            block_name, block = _parse_block(line, fh)
            result[block_name].append(block)

        if line.lower().startswith("import:"):
            # TODO
            continue

    return result
