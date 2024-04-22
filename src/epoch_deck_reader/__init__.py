from io import TextIOBase
from collections import defaultdict


def _strip_comment(line: str) -> str:
    comment_start = line.find("#")
    if comment_start < 0:
        return line

    return line[:comment_start]


def _join_lines(line: str, fh: TextIOBase) -> str:
    while "\\" in line:
        next_line = next(fh).strip()
        clean_line = line.replace("\\", "").strip()
        line = f"{clean_line} {next_line}"

    return line


def _parse_block(fh: TextIOBase) -> dict:
    result = defaultdict(list)

    for line in fh:
        line = _strip_comment(line).strip()
        line = _join_lines(line, fh)

        if not line:
            continue

        if line.lower().startswith("end:"):
            break

        key, value = line.split("=")
        result[key].append(value)

    return result


def parse(fh: TextIOBase) -> dict:
    result = dict()

    for line in fh:
        line = _strip_comment(line).strip()
        line = _join_lines(line, fh)

        if not line:
            continue

        if line.lower().startswith("begin:"):
            block_name, block = _parse_block(fh)
            result[block_name] = block

    return result
