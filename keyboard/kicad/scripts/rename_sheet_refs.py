#!/usr/bin/env python3
"""
Rename KiCad schematic symbol references for one hierarchical sheet.

Example:

    python rename_sheet_refs.py dormin.kicad_sch \
        --sheet Right \
        --suffix _R \
        --dry-run

Then, after reviewing:

    python rename_sheet_refs.py dormin.kicad_sch \
        --sheet Right \
        --suffix _R

The script:
  - Targets one hierarchical sheet by sheet name.
  - Finds symbols instantiated on that sheet.
  - Appends the requested suffix to their references.
  - Does not rename references already ending with the suffix.
  - Detects duplicate references before writing.
  - Creates a .bak backup before modifying the schematic.
  - Supports --dry-run.
  - Does not rewrite the entire S-expression file; only reference values
    are changed in-place.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


# ---------------------------------------------------------------------------
# KiCad S-expression helpers
# ---------------------------------------------------------------------------

UUID_RE = re.compile(
    r'\(uuid\s+"?([0-9a-fA-F-]+)"?\)'
)

SHEET_NAME_RE = re.compile(
    r'\(property\s+"Sheetname"\s+"((?:[^"\\]|\\.)*)"',
    re.MULTILINE,
)

REFERENCE_RE = re.compile(
    r'\(property\s+"Reference"\s+"((?:[^"\\]|\\.)*)"',
    re.MULTILINE,
)

# In the "instances" section, KiCad stores paths such as:
#
#   (path "/sheet-uuid/symbol-uuid"
#
PATH_RE = re.compile(
    r'\(path\s+"([^"]+)"'
)

INSTANCE_REFERENCE_RE = re.compile(
    r'\(reference\s+"((?:[^"\\]|\\.)*)"',
    re.MULTILINE,
)


@dataclass
class Span:
    start: int
    end: int


@dataclass
class Sheet:
    name: str
    uuid: str
    span: Span


@dataclass
class Symbol:
    uuid: str
    reference: str
    reference_span: Span
    instance_path: str


# ---------------------------------------------------------------------------
# Generic balanced S-expression scanning
# ---------------------------------------------------------------------------

def skip_string(text: str, i: int) -> int:
    """Return index immediately after a KiCad quoted string."""
    assert text[i] == '"'

    i += 1

    while i < len(text):
        if text[i] == "\\":
            i += 2
            continue

        if text[i] == '"':
            return i + 1

        i += 1

    raise ValueError("Unterminated string")


def find_matching_paren(text: str, start: int) -> int:
    """Find matching ')' for the '(' at start."""
    if text[start] != "(":
        raise ValueError("start must point to '('")

    depth = 0
    i = start

    while i < len(text):
        char = text[i]

        if char == '"':
            i = skip_string(text, i)
            continue

        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1

            if depth == 0:
                return i

        i += 1

    raise ValueError("Unbalanced S-expression")


def find_nodes(text: str, keyword: str) -> Iterable[Span]:
    """
    Find top-level occurrences of:

        (<keyword> ...)

    regardless of nesting depth.
    """
    pattern = re.compile(rf"\({re.escape(keyword)}(?=\s|\))")

    for match in pattern.finditer(text):
        start = match.start()

        try:
            end = find_matching_paren(text, start)
        except ValueError:
            continue

        yield Span(start, end + 1)


def unescape_kicad_string(value: str) -> str:
    """
    Decode the common KiCad escaped string sequences.

    We intentionally keep this conservative because sheet names and
    references normally contain plain ASCII.
    """
    return (
        value
        .replace(r"\\", "\\")
        .replace(r"\"", '"')
    )


def escape_kicad_string(value: str) -> str:
    """Escape a string for a KiCad quoted string."""
    return (
        value
        .replace("\\", r"\\")
        .replace('"', r"\"")
    )


# ---------------------------------------------------------------------------
# Sheet discovery
# ---------------------------------------------------------------------------

def find_sheets(text: str) -> list[Sheet]:
    sheets: list[Sheet] = []

    # KiCad hierarchical sheets use "(sheet ...)".
    for span in find_nodes(text, "sheet"):
        chunk = text[span.start:span.end]

        uuid_match = UUID_RE.search(chunk)
        name_match = SHEET_NAME_RE.search(chunk)

        if not uuid_match or not name_match:
            continue

        sheets.append(
            Sheet(
                name=unescape_kicad_string(name_match.group(1)),
                uuid=uuid_match.group(1),
                span=span,
            )
        )

    return sheets


# ---------------------------------------------------------------------------
# Symbol discovery
# ---------------------------------------------------------------------------

def find_symbol_nodes(text: str) -> Iterable[Span]:
    """
    Find placed schematic symbols.

    KiCad schematic files contain both:
      - lib_symbols definitions
      - actual placed symbols

    We deliberately exclude anything under the lib_symbols block.
    """
    lib_symbols_spans = list(find_nodes(text, "lib_symbols"))

    for span in find_nodes(text, "symbol"):
        # Skip symbol definitions inside lib_symbols.
        if any(
            parent.start < span.start < parent.end
            for parent in lib_symbols_spans
        ):
            continue

        yield span


def get_symbol_uuid(chunk: str) -> str | None:
    match = UUID_RE.search(chunk)
    return match.group(1) if match else None


def get_symbol_reference(
    chunk: str,
    absolute_start: int,
) -> tuple[str, Span] | None:
    """
    Find the first symbol property named "Reference".

    Returns the decoded value and absolute span covering only the value,
    not the surrounding quotes.
    """
    match = REFERENCE_RE.search(chunk)

    if not match:
        return None

    value = unescape_kicad_string(match.group(1))

    value_start = absolute_start + match.start(1)
    value_end = absolute_start + match.end(1)

    return value, Span(value_start, value_end)


# ---------------------------------------------------------------------------
# Instance/path discovery
# ---------------------------------------------------------------------------

def find_symbol_instance_paths(text: str) -> dict[str, str]:
    """
    Build:

        symbol UUID -> hierarchical sheet path

    from KiCad's (instances ...) data.

    A path looks approximately like:

        /sheet-uuid/symbol-uuid
    """
    result: dict[str, str] = {}

    instances_spans = list(find_nodes(text, "instances"))

    for instances_span in instances_spans:
        chunk = text[instances_span.start:instances_span.end]

        for path_match in PATH_RE.finditer(chunk):
            path = path_match.group(1)

            # The final UUID is the symbol UUID.
            parts = [part for part in path.split("/") if part]

            if not parts:
                continue

            symbol_uuid = parts[-1]
            result[symbol_uuid] = path

    return result


# ---------------------------------------------------------------------------
# Main rename logic
# ---------------------------------------------------------------------------

def collect_symbols_on_sheet(
    text: str,
    sheet: Sheet,
) -> list[Symbol]:
    symbols: list[Symbol] = []

    instance_paths = find_symbol_instance_paths(text)

    for symbol_span in find_symbol_nodes(text):
        chunk = text[symbol_span.start:symbol_span.end]

        symbol_uuid = get_symbol_uuid(chunk)

        if not symbol_uuid:
            continue

        reference_result = get_symbol_reference(
            chunk,
            symbol_span.start,
        )

        if not reference_result:
            continue

        reference, reference_span = reference_result

        instance_path = instance_paths.get(symbol_uuid)

        if not instance_path:
            continue

        # A symbol belonging directly to this sheet will have:
        #
        #   /<sheet UUID>/<symbol UUID>
        #
        # Nested sheets will contain additional UUID components.
        path_parts = [
            part for part in instance_path.split("/")
            if part
        ]

        if sheet.uuid not in path_parts[:-1]:
            continue

        symbols.append(
            Symbol(
                uuid=symbol_uuid,
                reference=reference,
                reference_span=reference_span,
                instance_path=instance_path,
            )
        )

    return symbols


def validate_references(
    text: str,
    changes: dict[str, str],
    target_symbols: list[Symbol],
) -> None:
    """
    Ensure the resulting references won't collide.

    We inspect all symbol Reference properties in the schematic.
    """
    existing: dict[str, str] = {}

    for symbol_span in find_symbol_nodes(text):
        chunk = text[symbol_span.start:symbol_span.end]

        uuid = get_symbol_uuid(chunk)

        ref_result = get_symbol_reference(
            chunk,
            symbol_span.start,
        )

        if not uuid or not ref_result:
            continue

        reference, _ = ref_result
        existing[reference] = uuid

    target_uuids = {symbol.uuid for symbol in target_symbols}

    # Remove current references of the symbols we're about to rename.
    for symbol in target_symbols:
        existing.pop(symbol.reference, None)

    collisions: list[str] = []

    for old_reference, new_reference in changes.items():
        if new_reference in existing:
            collisions.append(
                f"{old_reference} -> {new_reference}"
                f" conflicts with another symbol"
            )

    if collisions:
        raise RuntimeError(
            "Reference collisions detected:\n  - "
            + "\n  - ".join(collisions)
        )


def apply_changes(
    text: str,
    symbols: list[Symbol],
    suffix: str,
) -> tuple[str, list[tuple[str, str]]]:
    changes: dict[str, str] = {}

    for symbol in symbols:
        old = symbol.reference

        if old.endswith(suffix):
            continue

        new = old + suffix
        changes[old] = new

    if not changes:
        return text, []

    validate_references(text, changes, symbols)

    replacements: list[tuple[int, int, str]] = []
    summary: list[tuple[str, str]] = []

    for symbol in symbols:
        old = symbol.reference

        if old.endswith(suffix):
            continue

        new = old + suffix

        replacements.append(
            (
                symbol.reference_span.start,
                symbol.reference_span.end,
                escape_kicad_string(new),
            )
        )

        summary.append((old, new))

    # Apply from the end of the file backwards so offsets remain valid.
    result = text

    for start, end, replacement in sorted(
        replacements,
        reverse=True,
    ):
        result = (
            result[:start]
            + replacement
            + result[end:]
        )

    return result, summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Append a suffix to component references belonging "
            "to a specific KiCad hierarchical sheet."
        )
    )

    parser.add_argument(
        "schematic",
        type=Path,
        help="Path to the .kicad_sch file",
    )

    parser.add_argument(
        "--sheet",
        required=True,
        help='Hierarchical sheet name, e.g. "Right"',
    )

    parser.add_argument(
        "--suffix",
        default="_R",
        help='Suffix to append (default: "_R")',
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show changes without modifying the schematic",
    )

    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Do not create a .bak backup before writing",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    schematic: Path = args.schematic

    if not schematic.exists():
        print(
            f"ERROR: schematic does not exist: {schematic}",
            file=sys.stderr,
        )
        return 1

    if schematic.suffix != ".kicad_sch":
        print(
            "ERROR: expected a .kicad_sch file",
            file=sys.stderr,
        )
        return 1

    if not args.suffix:
        print(
            "ERROR: suffix cannot be empty",
            file=sys.stderr,
        )
        return 1

    try:
        text = schematic.read_text(
            encoding="utf-8",
        )
    except UnicodeDecodeError as exc:
        print(
            f"ERROR: could not decode schematic as UTF-8: {exc}",
            file=sys.stderr,
        )
        return 1

    # ---------------------------------------------------------------
    # Find requested sheet
    # ---------------------------------------------------------------

    sheets = find_sheets(text)

    matching_sheets = [
        sheet
        for sheet in sheets
        if sheet.name == args.sheet
    ]

    if not matching_sheets:
        print(
            f'ERROR: could not find hierarchical sheet "{args.sheet}".',
            file=sys.stderr,
        )

        if sheets:
            print("\nAvailable sheets:", file=sys.stderr)

            for sheet in sheets:
                print(
                    f"  - {sheet.name} "
                    f"(UUID: {sheet.uuid})",
                    file=sys.stderr,
                )

        return 1

    if len(matching_sheets) > 1:
        print(
            f'ERROR: multiple sheets named "{args.sheet}" found.',
            file=sys.stderr,
        )
        print(
            "Use unique sheet names.",
            file=sys.stderr,
        )
        return 1

    sheet = matching_sheets[0]

    print()
    print("KiCad Sheet Reference Renamer")
    print("=============================")
    print(f"Schematic : {schematic}")
    print(f"Sheet     : {sheet.name}")
    print(f"Sheet UUID: {sheet.uuid}")
    print(f"Suffix    : {args.suffix}")
    print()

    # ---------------------------------------------------------------
    # Find symbols
    # ---------------------------------------------------------------

    symbols = collect_symbols_on_sheet(
        text,
        sheet,
    )

    if not symbols:
        print(
            "No symbols were found on the requested sheet."
        )
        return 0

    modified_text, changes = apply_changes(
        text,
        symbols,
        args.suffix,
    )

    if not changes:
        print(
            "No changes required."
        )
        print(
            "All references already have the requested suffix."
        )
        return 0

    print("Planned changes:")
    print()

    for old, new in changes:
        print(f"  {old:<12} -> {new}")

    print()
    print(f"{len(changes)} reference(s) will be renamed.")

    # ---------------------------------------------------------------
    # Dry run
    # ---------------------------------------------------------------

    if args.dry_run:
        print()
        print("DRY RUN: schematic was not modified.")
        return 0

    # ---------------------------------------------------------------
    # Backup
    # ---------------------------------------------------------------

    if not args.no_backup:
        backup = schematic.with_suffix(
            schematic.suffix + ".bak"
        )

        shutil.copy2(
            schematic,
            backup,
        )

        print()
        print(f"Backup created: {backup}")

    # ---------------------------------------------------------------
    # Write
    # ---------------------------------------------------------------

    try:
        schematic.write_text(
            modified_text,
            encoding="utf-8",
            newline="",
        )
    except OSError as exc:
        print(
            f"ERROR: failed to write schematic: {exc}",
            file=sys.stderr,
        )
        return 1

    print()
    print(f"Updated: {schematic}")
    print("Done.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
