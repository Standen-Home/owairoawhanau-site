#!/usr/bin/env python3
"""Synchronise public waiata between this Jekyll site and Notion.

The repository remains the deployable output. Notion is the editable source once
`--push-existing` has been run and verified.
"""
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

DATA_SOURCE_ID = "298090a1-a19f-8012-91ca-000bb1fe288c"
DATABASE_ID = "298090a1-a19f-807d-b3e3-d3d963b56021"
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
        if not response.get("has_more"):
            return rows
        cursor = response.get("next_cursor")
        if not cursor:
            return rows


def rich_text_value(property_value: dict[str, Any] | None) -> str:
    if not property_value:
        return ""
    return "".join(item.get("plain_text", "") for item in property_value.get("rich_text", []))


def property_value(properties: dict[str, Any], name: str) -> Any:
    value = properties.get(name, {})
    kind = value.get("type")
    if kind == "title":
        return "".join(item.get("plain_text", "") for item in value.get("title", []))
    if kind == "rich_text":
        return rich_text_value(value)
    if kind in {"checkbox", "number", "url"}:
        return value.get(kind)
    if kind in {"select", "status"}:
        selected = value.get(kind)
        return selected.get("name", "") if selected else ""
    if kind == "multi_select":
        return [item.get("name", "") for item in value.get(kind, [])]
    if kind == "relation":
        return [item.get("id") for item in value.get(kind, [])]
    return ""


def chunk_text(value: str) -> list[dict[str, Any]]:
    return [
        {"type": "text", "text": {"content": value[start : start + MAX_RICH_TEXT_CHARS]}}
        for start in range(0, len(value), MAX_RICH_TEXT_CHARS)
    ] or []


def text_property(value: str) -> dict[str, Any]:
    return {"rich_text": chunk_text(value)}


def title_property(value: str) -> dict[str, Any]:
    return {"title": [{"type": "text", "text": {"content": value}}]}


def select_property(value: str) -> dict[str, Any]:
    return {"select": {"name": value}} if value else {"select": None}


def multi_select_property(values: list[str]) -> dict[str, Any]:
    return {"multi_select": [{"name": value} for value in values if value]}


def url_property(value: str) -> dict[str, Any]:
    return {"url": value or None}


def normalise_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def split_front_matter(text: str) -> tuple[dict[str, Any], str]:
    match = re.match(r"\A---[ \t]*\n(.*?)\n---[ \t]*", text, re.DOTALL)
    if not match:
        raise ValueError("waiata file has no YAML front matter")
    metadata = yaml.safe_load(match.group(1)) or {}
    return metadata, text[match.end() :]


def read_existing_waiata(repo_root: Path, public_only: bool = True) -> list[dict[str, Any]]:
    records = []
    for path in sorted((repo_root / "_waiata").glob("*.md")):
        if path.name == "sample-waiata.md":
            continue
        metadata, body = split_front_matter(path.read_text(encoding="utf-8"))
        if public_only and metadata.get("public") is not True:
            continue
        metadata["_path"] = path
        metadata["_body"] = body
        records.append(metadata)
    return records


def page_properties(record: dict[str, Any]) -> dict[str, Any]:
    tags = record.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    return {
        "Name": title_property(str(record.get("title") or record.get("name") or "Untitled waiata")),
        "Website Slug": text_property(str(record.get("slug") or "")),
        "Website Path": text_property(str(Path(record["_path"]).name)),
        "Public": {"checkbox": bool(record.get("public", False))},
        "Featured": {"checkbox": bool(record.get("featured", False))},
        "Display Order": {"number": record.get("order")},
        "Category": select_property(str(record.get("category") or "")),
        "Tags": multi_select_property([str(tag) for tag in tags]),
        "Artist": text_property(str(record.get("composer") or "")),
        "Source": text_property(str(record.get("source") or "")),
        "Audio URL": url_property(str(record.get("audio") or "")),
        "PDF URL": url_property(str(record.get("pdf") or "")),
        "Video URL": url_property(str(record.get("video_url") or "")),
        "Image URL": url_property(str(record.get("image") or "")),
        "Meaning": text_property(extract_section(str(record.get("_body") or ""), "Meaning")),
        "Everyone Lyrics": text_property(extract_lyrics(str(record.get("_body") or ""))),
        "Website Body Markdown": text_property(str(record.get("_body") or "")),
        "Content Status": select_property("Published" if record.get("public") is True else "Draft"),
    }


def extract_section(body: str, heading: str) -> str:
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", body, re.MULTILINE | re.IGNORECASE)
    if not match:
        return ""
    rest = body[match.end() :]
    next_heading = re.search(r"^##\s+", rest, re.MULTILINE)
    return rest[: next_heading.start() if next_heading else len(rest)].strip()


def extract_lyrics(body: str) -> str:
    match = re.search(r"<pre class=[\"']lyrics[\"']>(.*?)</pre>", body, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else extract_section(body, "Kupu")


def push_existing(repo_root: Path, token: str, dry_run: bool = False) -> tuple[int, int]:
    existing = read_existing_waiata(repo_root)
    rows = query_rows(token)
    by_title = {normalise_title(property_value(row.get("properties", {}), "Name")): row for row in rows}
    created = updated = 0
    for record in existing:
        title = str(record.get("title") or "")
        match = by_title.get(normalise_title(title))
        properties = page_properties(record)
        if match:
            if not dry_run:
                notion_request(f"pages/{match['id']}", token, "PATCH", {"properties": properties})
            updated += 1
        else:
            if not dry_run:
                created_page = notion_request(
                    "pages",
                    token,
                    "POST",
                    {"parent": {"database_id": DATABASE_ID}, "properties": properties},
                )
                by_title[normalise_title(title)] = created_page
            created += 1
    return created, updated


def yaml_scalar(value: Any) -> str:
    return json.dumps(value if value is not None else "", ensure_ascii=False)


def build_markdown(row: dict[str, Any]) -> tuple[Path, str]:
    props = row.get("properties", {})
    title = str(property_value(props, "Name") or "Untitled waiata")
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
        "layout: waiata",
        f"title: {yaml_scalar(title)}",
        f"title_en: {yaml_scalar('')}",
        f"slug: {yaml_scalar(slug)}",
        f"category: {yaml_scalar(property_value(props, 'Category'))}",
        "tags:",
        *[f"  - {yaml_scalar(tag)}" for tag in tags],
        f"composer: {yaml_scalar(property_value(props, 'Artist'))}",
        f"source: {yaml_scalar(property_value(props, 'Source'))}",
        f"featured: {'true' if property_value(props, 'Featured') else 'false'}",
        f"public: {'true' if property_value(props, 'Public') else 'false'}",
        f"audio: {yaml_scalar(property_value(props, 'Audio URL'))}",
        f"pdf: {yaml_scalar(property_value(props, 'PDF URL'))}",
        f"video_url: {yaml_scalar(property_value(props, 'Video URL'))}",
        f"image: {yaml_scalar(property_value(props, 'Image URL'))}",
        f"order: {order if order is not None else 999}",
        f"notion_page_id: {yaml_scalar(row['id'])}",
        "source_of_truth: notion",
        "---",
    ]
    body = str(property_value(props, "Website Body Markdown") or "")
    return Path("_waiata") / filename, "\n".join(front_matter) + body


def pull_public(repo_root: Path, token: str, dry_run: bool = False) -> tuple[int, list[Path]]:
    rows = query_rows(token)
    written: list[Path] = []
    for row in rows:
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
    parser.add_argument("--push-existing", action="store_true", help="seed/update Notion from public _waiata Markdown")
    parser.add_argument("--pull", action="store_true", help="write public Notion rows into _waiata")
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
