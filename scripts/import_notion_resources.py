#!/usr/bin/env python3
"""Synchronise public resource pages between this Jekyll site and Notion."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import yaml

DATA_SOURCE_ID = "0bee3f8a-bf85-40fe-a36a-14de32553e8c"
DATABASE_ID = "faeb039e-8c4c-488e-8fcc-f213efc11640"
NOTION_VERSION = "2025-09-03"
MAX_RICH_TEXT_CHARS = 1900


def notion_request(path: str, token: str, method: str = "GET", payload: dict[str, Any] | None = None) -> dict[str, Any]:
    request = urllib.request.Request(
        "https://api.notion.com/v1/" + path.lstrip("/"),
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
        method=method,
        data=json.dumps(payload).encode("utf-8") if payload is not None else None,
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def query_rows(token: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cursor = None
    while True:
        payload: dict[str, Any] = {}
        if cursor:
            payload["start_cursor"] = cursor
        response = notion_request(f"data_sources/{DATA_SOURCE_ID}/query", token, "POST", payload)
        rows.extend(response.get("results", []))
        if not response.get("has_more") or not response.get("next_cursor"):
            return rows
        cursor = response["next_cursor"]


def property_value(properties: dict[str, Any], name: str) -> Any:
    value = properties.get(name, {})
    kind = value.get("type")
    if kind == "title":
        return "".join(item.get("plain_text", "") for item in value.get("title", []))
    if kind == "rich_text":
        return "".join(item.get("plain_text", "") for item in value.get("rich_text", []))
    if kind in {"checkbox", "number", "url"}:
        return value.get(kind)
    if kind in {"select", "status"}:
        selected = value.get(kind)
        return selected.get("name", "") if selected else ""
    if kind == "multi_select":
        return [item.get("name", "") for item in value.get(kind, [])]
    return ""


def chunks(value: str) -> list[dict[str, Any]]:
    return [
        {"type": "text", "text": {"content": value[start : start + MAX_RICH_TEXT_CHARS]}}
        for start in range(0, len(value), MAX_RICH_TEXT_CHARS)
    ] or []


def text_property(value: str) -> dict[str, Any]:
    return {"rich_text": chunks(value)}


def title_property(value: str) -> dict[str, Any]:
    return {"title": [{"type": "text", "text": {"content": value}}]}


def select_property(value: str) -> dict[str, Any]:
    return {"select": {"name": value}} if value else {"select": None}


def multi_select_property(values: list[str]) -> dict[str, Any]:
    return {"multi_select": [{"name": value} for value in values if value]}


def normalise_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def split_front_matter(text: str) -> tuple[dict[str, Any], str]:
    match = re.match(r"\A---[ \t]*\n(.*?)\n---[ \t]*", text, re.DOTALL)
    if not match:
        raise ValueError("resource file has no YAML front matter")
    return yaml.safe_load(match.group(1)) or {}, text[match.end() :]


def read_existing_resources(repo_root: Path) -> list[dict[str, Any]]:
    records = []
    for path in sorted((repo_root / "_resources").glob("*.md")):
        metadata, body = split_front_matter(path.read_text(encoding="utf-8"))
        metadata["_path"] = path
        metadata["_body"] = body
        metadata.setdefault("public", True)
        records.append(metadata)
    return records


def page_properties(record: dict[str, Any]) -> dict[str, Any]:
    tags = record.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    return {
        "Name": title_property(str(record.get("title") or "Untitled resource")),
        "English Title": text_property(str(record.get("title_en") or "")),
        "Website Slug": text_property(str(record.get("slug") or "")),
        "Website Path": text_property(str(Path(record["_path"]).name)),
        "Summary": text_property(str(record.get("summary") or "")),
        "Keywords": text_property(str(record.get("keywords") or "")),
        "Tags": multi_select_property([str(tag) for tag in tags]),
        "Featured": {"checkbox": bool(record.get("featured", False))},
        "Public": {"checkbox": bool(record.get("public", True))},
        "Display Order": {"number": record.get("order")},
        "Website Body Markdown": text_property(str(record.get("_body") or "")),
        "Content Status": select_property("Published" if record.get("public", True) else "Draft"),
    }


def push_existing(repo_root: Path, token: str, dry_run: bool = False) -> tuple[int, int]:
    rows = query_rows(token)
    by_title = {normalise_title(property_value(row.get("properties", {}), "Name")): row for row in rows}
    created = updated = 0
    for record in read_existing_resources(repo_root):
        title = str(record.get("title") or "")
        properties = page_properties(record)
        match = by_title.get(normalise_title(title))
        if match:
            if not dry_run:
                notion_request(f"pages/{match['id']}", token, "PATCH", {"properties": properties})
            updated += 1
        else:
            if not dry_run:
                created_page = notion_request(
                    "pages", token, "POST", {"parent": {"database_id": DATABASE_ID}, "properties": properties}
                )
                by_title[normalise_title(title)] = created_page
            created += 1
    return created, updated


def scalar(value: Any) -> str:
    return json.dumps(value if value is not None else "", ensure_ascii=False)


def build_markdown(row: dict[str, Any]) -> tuple[Path, str]:
    props = row.get("properties", {})
    title = str(property_value(props, "Name") or "Untitled resource")
    slug = str(property_value(props, "Website Slug") or normalise_title(title))
    filename = str(property_value(props, "Website Path") or f"{slug}.md")
    if not filename.endswith(".md"):
        filename += ".md"
    tags = property_value(props, "Tags") or []
    if isinstance(tags, str):
        tags = [tags]
    order = property_value(props, "Display Order")
    front_matter = [
        "---",
        "layout: resource",
        f"title: {scalar(title)}",
        f"title_en: {scalar(property_value(props, 'English Title'))}",
        f"slug: {scalar(slug)}",
        "tags:",
        *[f"  - {scalar(tag)}" for tag in tags],
        f"summary: {scalar(property_value(props, 'Summary'))}",
        f"keywords: {scalar(property_value(props, 'Keywords'))}",
        f"featured: {'true' if property_value(props, 'Featured') else 'false'}",
        f"public: {'true' if property_value(props, 'Public') else 'false'}",
        f"order: {order if order is not None else 999}",
        f"notion_page_id: {scalar(row['id'])}",
        "source_of_truth: notion",
        "---",
    ]
    body = str(property_value(props, "Website Body Markdown") or "")
    return Path("_resources") / filename, "\n".join(front_matter) + body


def pull_public(repo_root: Path, token: str, dry_run: bool = False) -> tuple[int, list[Path]]:
    written: list[Path] = []
    for row in query_rows(token):
        props = row.get("properties", {})
        if property_value(props, "Public") is not True:
            continue
        relative_path, content = build_markdown(row)
        path = repo_root / relative_path
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        written.append(relative_path)
    return len(written), written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--push-existing", action="store_true")
    parser.add_argument("--pull", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    if not args.push_existing and not args.pull:
        parser.error("choose --push-existing and/or --pull")
    token = os.environ.get("NOTION_API_KEY") or os.environ.get("NOTION_API_TOKEN")
    if not token:
        print("NOTION_API_KEY or NOTION_API_TOKEN is required", file=sys.stderr)
        return 2
    try:
        if args.push_existing:
            created, updated = push_existing(args.repo_root, token, args.dry_run)
            print(f"push_existing: created={created} updated={updated}")
        if args.pull:
            count, paths = pull_public(args.repo_root, token, args.dry_run)
            print(f"pull: public={count} files={','.join(str(path) for path in paths)}")
    except urllib.error.HTTPError as error:
        print(f"Notion API error {error.code}: {error.read().decode('utf-8', 'replace')}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
