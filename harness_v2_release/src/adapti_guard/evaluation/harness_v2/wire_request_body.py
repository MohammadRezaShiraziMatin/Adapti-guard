"""Wire body utilities (Amendment 9 final — no transport-layer capture)."""
from __future__ import annotations

import base64
import json
from typing import Any


def encode_wire_body_base64(body: bytes) -> str:
    return base64.standard_b64encode(body).decode("ascii")


def decode_wire_body_base64(encoded: str) -> bytes:
    return base64.standard_b64decode(encoded.encode("ascii"))


def assert_stored_wire_matches_sent(stored_row: dict[str, Any], sent: bytes) -> None:
    """Raise AssertionError if ledger wire bytes differ from transport payload."""
    stored_b64 = stored_row.get("request_wire_body_base64")
    if stored_b64 is None:
        raise AssertionError("ledger row missing request_wire_body_base64")
    stored_bytes = decode_wire_body_base64(stored_b64)
    if stored_bytes != sent:
        raise AssertionError("stored wire body must match transport bytes exactly")


def _skip_json_value(text: str, i: int) -> int:
    n = len(text)
    while i < n and text[i] in " \t\n\r":
        i += 1
    if i >= n:
        return i
    c = text[i]
    if c == '"':
        i += 1
        esc = False
        while i < n:
            ch = text[i]
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                return i + 1
            i += 1
        return n
    if c in "-0123456789":
        i += 1
        while i < n and text[i] in "0123456789.eE+-":
            i += 1
        return i
    if c in "{[":
        open_c, close_c = ("{", "}") if c == "{" else ("[", "]")
        depth = 0
        in_str = False
        esc = False
        while i < n:
            ch = text[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            else:
                if ch == '"':
                    in_str = True
                elif ch == open_c:
                    depth += 1
                elif ch == close_c:
                    depth -= 1
                    if depth == 0:
                        return i + 1
            i += 1
        return n
    if text.startswith("true", i):
        return i + 4
    if text.startswith("false", i):
        return i + 5
    if text.startswith("null", i):
        return i + 4
    raise ValueError(f"unexpected JSON at {i!r}: {text[i : i + 20]!r}")


def _find_top_level_key_span(text: str, field: str) -> tuple[int, int]:
    """Return [start, end) byte span to delete for one top-level key (incl. one adjacent comma)."""
    key_token = f'"{field}"'
    n = len(text)
    depth = 0
    in_str = False
    esc = False
    i = 0
    while i < n:
        c = text[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            if depth == 1 and text.startswith(key_token, i):
                key_start = i
                val_start = i + len(key_token)
                while val_start < n and text[val_start] in " \t\n\r":
                    val_start += 1
                if val_start >= n or text[val_start] != ":":
                    raise ValueError(f"malformed key {field!r}")
                value_end = _skip_json_value(text, val_start + 1)
                end = value_end
                while end < n and text[end] in " \t\n\r":
                    end += 1
                delete_start = key_start
                j = key_start - 1
                while j >= 0 and text[j] in " \t\n\r":
                    j -= 1
                if j >= 0 and text[j] == ",":
                    delete_start = j
                elif end < n and text[end] == ",":
                    end += 1
                return delete_start, end
            in_str = True
            i += 1
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        i += 1
    raise ValueError(f"top-level field {field!r} not found")


def remove_top_level_json_field(body: bytes, field: str) -> bytes:
    """Remove one top-level key; output valid JSON; all other bytes unchanged."""
    text = body.decode("utf-8")
    start, end = _find_top_level_key_span(text, field)
    new_text = text[:start] + text[end:]
    json.loads(new_text)
    return new_text.encode("utf-8")
