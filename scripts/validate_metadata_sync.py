from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = REPO_ROOT / "prompts"
INDEX_PATH = REPO_ROOT / "prompts-index.md"
EXPECTED_INDEX_HEADERS = [
    "Slug",
    "Domain",
    "Type",
    "中文标题",
    "English Title",
    "Canonical",
    "Locales",
    "Status",
    "Version",
    "Last Reviewed",
]
EXPECTED_REQUIRED_KEYS = {
    "id",
    "name",
    "domain",
    "prompt_type",
    "summary",
    "status",
    "version",
    "canonical_lang",
    "langs",
    "translation_policy",
    "purpose",
    "tags",
}
INDEX_TO_META_FIELD = {
    "Slug": "id",
    "Domain": "domain",
    "Type": "prompt_type",
    "中文标题": "name.zh-CN",
    "English Title": "name.en",
    "Canonical": "canonical_lang",
    "Locales": "langs",
    "Status": "status",
    "Version": "version",
    "Last Reviewed": "last_reviewed",
}


class ValidationError(Exception):
    pass


@dataclass(frozen=True)
class AssetRecord:
    slug: str
    domain: str
    meta_path: Path
    meta: dict[str, Any]


def parse_scalar(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
        return value[1:-1]
    return value


def parse_meta_yaml(path: Path) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8").splitlines()
    data: dict[str, Any] = {}
    current_key: str | None = None

    i = 0
    while i < len(lines):
        raw_line = lines[i]
        line_number = i + 1
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            i += 1
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent != 0:
            raise ValidationError(
                f"{path.relative_to(REPO_ROOT)}:{line_number}: unsupported indentation for top-level field"
            )

        if ":" not in raw_line:
            raise ValidationError(
                f"{path.relative_to(REPO_ROOT)}:{line_number}: expected key:value pair"
            )

        key, remainder = raw_line.split(":", 1)
        key = key.strip()
        remainder = remainder.strip()
        current_key = key

        if remainder:
            data[key] = parse_scalar(remainder)
            i += 1
            continue

        if i + 1 >= len(lines):
            raise ValidationError(
                f"{path.relative_to(REPO_ROOT)}:{line_number}: missing block for key '{key}'"
            )

        next_line = lines[i + 1]
        next_indent = (
            len(next_line) - len(next_line.lstrip(" ")) if next_line.strip() else 0
        )
        if (
            next_line.strip().startswith("- ")
            or next_indent == 2
            and next_line.strip().startswith("- ")
        ):
            items: list[str] = []
            i += 1
            while i < len(lines):
                candidate = lines[i]
                candidate_stripped = candidate.strip()
                if not candidate_stripped:
                    i += 1
                    continue
                candidate_indent = len(candidate) - len(candidate.lstrip(" "))
                if candidate_indent == 2 and candidate_stripped.startswith("- "):
                    items.append(parse_scalar(candidate_stripped[2:]))
                    i += 1
                    continue
                break
            data[key] = items
            continue

        if next_indent == 2:
            nested: dict[str, str] = {}
            i += 1
            while i < len(lines):
                candidate = lines[i]
                candidate_stripped = candidate.strip()
                if not candidate_stripped:
                    i += 1
                    continue
                candidate_indent = len(candidate) - len(candidate.lstrip(" "))
                if candidate_indent != 2:
                    break
                if ":" not in candidate_stripped:
                    raise ValidationError(
                        f"{path.relative_to(REPO_ROOT)}:{i + 1}: expected nested key:value pair under '{current_key}'"
                    )
                nested_key, nested_value = candidate_stripped.split(":", 1)
                nested[nested_key.strip()] = parse_scalar(nested_value)
                i += 1
            data[key] = nested
            continue

        raise ValidationError(
            f"{path.relative_to(REPO_ROOT)}:{line_number}: unsupported YAML block for '{key}'"
        )

    return data


def normalize_markdown_cell(cell: str) -> str:
    value = cell.strip()
    value = re.sub(r"`([^`]+)`", r"\1", value)
    return value.strip()


def split_markdown_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        raise ValidationError(f"Malformed markdown table row: {line}")
    return [normalize_markdown_cell(part) for part in stripped[1:-1].split("|")]


def parse_index(path: Path) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    table_lines = [line for line in lines if line.strip().startswith("|")]
    if len(table_lines) < 2:
        raise ValidationError(
            "prompts-index.md does not contain a valid markdown table"
        )

    headers = split_markdown_row(table_lines[0])
    if headers != EXPECTED_INDEX_HEADERS:
        raise ValidationError(
            "prompts-index.md header mismatch. "
            f"Expected {EXPECTED_INDEX_HEADERS}, got {headers}"
        )

    separator = split_markdown_row(table_lines[1])
    if any(not re.fullmatch(r":?-{3,}:?", cell) for cell in separator):
        raise ValidationError("prompts-index.md separator row is malformed")

    rows: list[dict[str, str]] = []
    for line in table_lines[2:]:
        values = split_markdown_row(line)
        if len(values) != len(headers):
            raise ValidationError(
                f"prompts-index.md row has {len(values)} cells; expected {len(headers)}: {line}"
            )
        rows.append(dict(zip(headers, values, strict=True)))

    return rows


def find_asset_records() -> list[AssetRecord]:
    records: list[AssetRecord] = []
    for meta_path in sorted(PROMPTS_DIR.glob("*/*/meta.yml")):
        meta = parse_meta_yaml(meta_path)
        slug = meta_path.parent.name
        domain = meta_path.parent.parent.name
        records.append(
            AssetRecord(slug=slug, domain=domain, meta_path=meta_path, meta=meta)
        )
    return records


def get_nested_value(meta: dict[str, Any], field_path: str) -> str:
    current: Any = meta
    for segment in field_path.split("."):
        if not isinstance(current, dict) or segment not in current:
            raise ValidationError(f"Missing mirrored field '{field_path}'")
        current = current[segment]

    if isinstance(current, list):
        return ", ".join(str(item) for item in current)
    return str(current)


def validate_asset_files(record: AssetRecord, errors: list[str]) -> None:
    expected_files = ["meta.yml", "prompt.zh-CN.md", "prompt.en.md"]
    for filename in expected_files:
        candidate = record.meta_path.parent / filename
        if not candidate.exists():
            errors.append(
                f"Missing required file for {record.slug}: {candidate.relative_to(REPO_ROOT)}"
            )


def validate_meta_structure(record: AssetRecord, errors: list[str]) -> None:
    missing_required = sorted(EXPECTED_REQUIRED_KEYS - record.meta.keys())
    if missing_required:
        errors.append(
            f"{record.meta_path.relative_to(REPO_ROOT)} is missing required metadata keys: {', '.join(missing_required)}"
        )

    if record.meta.get("id") != record.slug:
        errors.append(
            f"{record.meta_path.relative_to(REPO_ROOT)} has id '{record.meta.get('id')}', expected '{record.slug}'"
        )
    if record.meta.get("domain") != record.domain:
        errors.append(
            f"{record.meta_path.relative_to(REPO_ROOT)} has domain '{record.meta.get('domain')}', expected '{record.domain}'"
        )

    name = record.meta.get("name")
    if not isinstance(name, dict) or "zh-CN" not in name or "en" not in name:
        errors.append(
            f"{record.meta_path.relative_to(REPO_ROOT)} must define name.zh-CN and name.en"
        )

    langs = record.meta.get("langs")
    if not isinstance(langs, list) or not langs:
        errors.append(
            f"{record.meta_path.relative_to(REPO_ROOT)} must define langs as a non-empty list"
        )
    else:
        canonical = record.meta.get("canonical_lang")
        if canonical not in langs:
            errors.append(
                f"{record.meta_path.relative_to(REPO_ROOT)} has canonical_lang '{canonical}' not present in langs"
            )


def validate_index_sync(
    records: list[AssetRecord], rows: list[dict[str, str]], errors: list[str]
) -> None:
    row_by_slug: dict[str, dict[str, str]] = {}
    for row in rows:
        slug = row["Slug"]
        if slug in row_by_slug:
            errors.append(f"prompts-index.md contains duplicate row for slug '{slug}'")
            continue
        row_by_slug[slug] = row

    record_by_slug = {record.slug: record for record in records}

    for slug in sorted(record_by_slug):
        if slug not in row_by_slug:
            errors.append(f"Missing prompts-index.md row for asset '{slug}'")

    for slug in sorted(row_by_slug):
        if slug not in record_by_slug:
            errors.append(
                f"prompts-index.md contains orphan row for missing asset '{slug}'"
            )

    for slug, record in sorted(record_by_slug.items()):
        row = row_by_slug.get(slug)
        if row is None:
            continue
        for column, field_path in INDEX_TO_META_FIELD.items():
            try:
                expected = get_nested_value(record.meta, field_path)
            except ValidationError as exc:
                errors.append(f"{record.meta_path.relative_to(REPO_ROOT)}: {exc}")
                continue
            actual = row[column]
            if actual != expected:
                errors.append(
                    f"Index mismatch for '{slug}' column '{column}': expected '{expected}', got '{actual}'"
                )


def validate_index_order(rows: list[dict[str, str]], errors: list[str]) -> None:
    expected_order = sorted(rows, key=lambda row: (row["Domain"], row["Slug"]))
    actual_pairs = [(row["Domain"], row["Slug"]) for row in rows]
    expected_pairs = [(row["Domain"], row["Slug"]) for row in expected_order]
    if actual_pairs != expected_pairs:
        formatted_expected = ", ".join(
            f"{domain}/{slug}" for domain, slug in expected_pairs
        )
        formatted_actual = ", ".join(
            f"{domain}/{slug}" for domain, slug in actual_pairs
        )
        errors.append(
            "prompts-index.md row order must be grouped by Domain and sorted by Slug. "
            f"Expected [{formatted_expected}], got [{formatted_actual}]"
        )


def main() -> int:
    errors: list[str] = []

    try:
        rows = parse_index(INDEX_PATH)
        records = find_asset_records()
    except ValidationError as exc:
        print(f"Metadata sync validation failed: {exc}", file=sys.stderr)
        return 1

    for record in records:
        validate_asset_files(record, errors)
        validate_meta_structure(record, errors)

    validate_index_sync(records, rows, errors)
    validate_index_order(rows, errors)

    if errors:
        print("Metadata sync validation failed:", file=sys.stderr)
        for issue in errors:
            print(f"- {issue}", file=sys.stderr)
        return 1

    print(f"Metadata sync validation passed for {len(records)} assets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
