#!/usr/bin/env python3
"""Validate and summarize a canonical Quandora Strategy Result Bundle without extraction."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import stat
import sys
import zipfile
from pathlib import Path
from typing import Any

EXPECTED_KIND = "STRATEGY_RESULT_BUNDLE"
MAX_ARCHIVE_BYTES = 512 * 1024 * 1024
MAX_MEMBER_BYTES = 128 * 1024 * 1024
MAX_TOTAL_BYTES = 512 * 1024 * 1024
MAX_MEMBERS = 256
MAX_JSON_BYTES = 8 * 1024 * 1024
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class BundleError(Exception):
    pass


def _safe_name(name: str) -> None:
    parts = name.split("/")
    if (
        not name
        or len(name) > 512
        or name.startswith("/")
        or re.match(r"^[A-Za-z]:", name)
        or "\\" in name
        or any(ord(character) < 32 or ord(character) == 127 for character in name)
        or any(part in {"", ".", ".."} for part in parts)
    ):
        raise BundleError(f"unsafe ZIP path: {name!r}")


def _reject_constant(value: str) -> None:
    raise BundleError(f"non-finite JSON token: {value}")


def _read_json(archive: zipfile.ZipFile, name: str) -> Any:
    info = archive.getinfo(name)
    if info.file_size > MAX_JSON_BYTES:
        raise BundleError(f"selected JSON member is too large: {name}")
    try:
        return json.loads(archive.read(info), parse_constant=_reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BundleError(f"invalid UTF-8 JSON member: {name}") from exc


def _hash_member(archive: zipfile.ZipFile, info: zipfile.ZipInfo) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    try:
        with archive.open(info, "r") as stream:
            while True:
                chunk = stream.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_MEMBER_BYTES:
                    raise BundleError(f"member exceeds the size limit: {info.filename}")
                digest.update(chunk)
    except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
        raise BundleError(f"member cannot be read safely: {info.filename}") from exc
    return size, digest.hexdigest()


def _series_stats(values: Any, path: str) -> dict[str, Any]:
    if not isinstance(values, list):
        raise BundleError(f"six-chart series is not an array: {path}")
    finite: list[float] = []
    missing = 0
    for value in values:
        if value is None:
            missing += 1
            continue
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise BundleError(f"six-chart series contains a non-numeric value: {path}")
        number = float(value)
        if not math.isfinite(number):
            raise BundleError(f"six-chart series contains a non-finite value: {path}")
        finite.append(number)
    summary: dict[str, Any] = {
        "points": len(values),
        "finite_points": len(finite),
        "missing_points": missing,
    }
    if finite:
        summary.update(
            {
                "minimum": min(finite),
                "maximum": max(finite),
                "mean": sum(finite) / len(finite),
                "first_finite": finite[0],
                "last_finite": finite[-1],
            }
        )
    return summary


def _summarize_six_charts(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise BundleError("six_charts_data.json is not an object")
    summary = {
        key: payload.get(key)
        for key in (
            "available",
            "schema_version",
            "generated_at",
            "window",
            "params",
            "cross_section",
            "missing_styles",
        )
        if key in payload
    }
    charts = payload.get("charts")
    if charts is None:
        summary["charts"] = None
        return summary
    if not isinstance(charts, dict):
        raise BundleError("six_charts_data.json charts is not an object")
    chart_summaries: dict[str, Any] = {}
    for chart_name, chart in sorted(charts.items()):
        if not isinstance(chart_name, str) or not isinstance(chart, dict):
            raise BundleError("six-chart entry is invalid")
        x_values = chart.get("x")
        if not isinstance(x_values, list):
            raise BundleError(f"six-chart x axis is not an array: {chart_name}")
        series = chart.get("series")
        if not isinstance(series, dict):
            raise BundleError(f"six-chart series is not an object: {chart_name}")
        series_summaries = {
            name: _series_stats(values, f"{chart_name}.{name}")
            for name, values in sorted(series.items())
            if isinstance(name, str)
        }
        if len(series_summaries) != len(series):
            raise BundleError(f"six-chart series name is invalid: {chart_name}")
        chart_summaries[chart_name] = {
            "title": chart.get("title"),
            "kind": chart.get("kind"),
            "x_label": chart.get("x_label"),
            "x_points": len(x_values),
            "plot": chart.get("plot"),
            "legend": chart.get("legend"),
            "series": series_summaries,
        }
    summary["charts"] = chart_summaries
    return summary


def inspect_bundle(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise BundleError("archive path is not a regular file")
    archive_size = path.stat().st_size
    if not 0 < archive_size <= MAX_ARCHIVE_BYTES:
        raise BundleError("archive size is outside the supported bounds")

    try:
        archive = zipfile.ZipFile(path, "r")
    except (OSError, zipfile.BadZipFile) as exc:
        raise BundleError("archive is not a readable ZIP") from exc

    with archive:
        infos = archive.infolist()
        if not 1 <= len(infos) <= MAX_MEMBERS:
            raise BundleError("archive member count is outside the supported bounds")
        names: set[str] = set()
        total_size = 0
        for info in infos:
            _safe_name(info.filename)
            if info.filename in names:
                raise BundleError(f"duplicate ZIP member: {info.filename}")
            names.add(info.filename)
            if info.is_dir() or info.flag_bits & 0x1:
                raise BundleError(f"directory or encrypted member is not allowed: {info.filename}")
            file_type = (info.external_attr >> 16) & 0o170000
            if file_type not in {0, stat.S_IFREG}:
                raise BundleError(f"non-regular member is not allowed: {info.filename}")
            if info.file_size > MAX_MEMBER_BYTES:
                raise BundleError(f"member exceeds the size limit: {info.filename}")
            total_size += info.file_size
            if total_size > MAX_TOTAL_BYTES:
                raise BundleError("archive expands beyond the supported total size")

        if "artifact_manifest.json" not in names:
            raise BundleError("artifact_manifest.json is missing")
        manifest = _read_json(archive, "artifact_manifest.json")
        required = {
            "schema_version",
            "projection_schema_version",
            "bundle_kind",
            "canonical_run_id",
            "snapshot_revision",
            "bundle_status",
            "safe_filename",
            "content_type",
            "items",
        }
        if not isinstance(manifest, dict) or not required <= set(manifest):
            raise BundleError("manifest does not match the required result-bundle shape")
        if manifest["bundle_kind"] != EXPECTED_KIND:
            raise BundleError(f"expected {EXPECTED_KIND}, found {manifest['bundle_kind']!r}")
        if manifest["content_type"] != "application/zip":
            raise BundleError("manifest content_type is not application/zip")
        items = manifest["items"]
        if not isinstance(items, list) or len(items) > MAX_MEMBERS:
            raise BundleError("manifest items are invalid or unbounded")

        included_paths: set[str] = set()
        status_counts: dict[str, int] = {}
        verified = 0
        omissions: list[dict[str, Any]] = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise BundleError(f"manifest item {index} is not an object")
            item_name = item.get("name")
            status_value = item.get("status")
            if not isinstance(item_name, str) or not item_name or not isinstance(status_value, str):
                raise BundleError(f"manifest item {index} lacks a valid name or status")
            status_counts[status_value] = status_counts.get(status_value, 0) + 1
            if status_value != "included":
                omissions.append(
                    {
                        "name": item_name,
                        "status": status_value,
                        "reason_code": item.get("reason_code"),
                    }
                )
                continue
            zip_path = item.get("zip_path")
            size_bytes = item.get("size_bytes")
            sha256 = item.get("sha256")
            if not isinstance(zip_path, str):
                raise BundleError(f"included item {item_name!r} lacks zip_path")
            _safe_name(zip_path)
            if zip_path in included_paths or zip_path not in names:
                raise BundleError(f"included item path is duplicate or missing: {zip_path}")
            if type(size_bytes) is not int or size_bytes < 0:
                raise BundleError(f"included item has invalid size: {zip_path}")
            if not isinstance(sha256, str) or not SHA256_RE.fullmatch(sha256):
                raise BundleError(f"included item has invalid SHA-256: {zip_path}")
            actual_size, actual_sha256 = _hash_member(archive, archive.getinfo(zip_path))
            if actual_size != size_bytes or actual_sha256 != sha256:
                raise BundleError(f"included item integrity mismatch: {zip_path}")
            included_paths.add(zip_path)
            verified += 1

        if names - {"artifact_manifest.json"} != included_paths:
            raise BundleError("ZIP membership does not exactly match included manifest items")

        selected: dict[str, Any] = {}
        for name in (
            "run_summary.json",
            "artifacts/summary.json",
            "artifacts/performance.json",
            "artifacts/attribution.json",
        ):
            if name in included_paths:
                selected[name] = _read_json(archive, name)
        six_chart_path = "artifacts/six_charts_data.json"
        six_charts = (
            _summarize_six_charts(_read_json(archive, six_chart_path))
            if six_chart_path in included_paths
            else None
        )

        return {
            "archive": str(path.resolve()),
            "archive_size_bytes": archive_size,
            "bundle_kind": manifest["bundle_kind"],
            "bundle_status": manifest["bundle_status"],
            "manifest_schema_version": manifest["schema_version"],
            "projection_schema_version": manifest["projection_schema_version"],
            "canonical_run_id": manifest["canonical_run_id"],
            "snapshot_revision": manifest["snapshot_revision"],
            "member_count": len(infos),
            "verified_included_items": verified,
            "status_counts": status_counts,
            "omissions": omissions,
            "selected_json": selected,
            "six_charts_summary": six_charts,
            "outer_digest_note": "Verify the whole ZIP against MCP ticket or chunk metadata.",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "archive", type=Path, help="Path to the canonical Strategy Result Bundle ZIP"
    )
    args = parser.parse_args()
    try:
        result = inspect_bundle(args.archive)
    except BundleError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps({"ok": True, **result}, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
