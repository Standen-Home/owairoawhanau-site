#!/usr/bin/env python3
"""Import sent Klaviyo campaigns as Jekyll Pānui posts.

This script is designed for GitHub Actions, but also works locally:

    KLAVIYO_API_KEY=... python3 scripts/import_klaviyo_panui.py --dry-run

It stores durable copies of imported newsletter HTML in _posts/ and downloads
meaningful inline images into assets/images/panui/{campaign-id}/.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import hashlib
import html
import json
import mimetypes
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable, Iterable

API_BASE = "https://a.klaviyo.com"
DEFAULT_REVISION = "2026-07-15"
DEFAULT_FILTER = r"pānui|panui|newsletter|news"


@dataclasses.dataclass
class ExistingImportIndex:
    campaign_ids: set[str]
    message_ids: set[str]
    content_hashes: set[str]
    slugs: set[str]


@dataclasses.dataclass
class ImportedPost:
    title: str
    date: str
    body_html: str
    campaign_id: str
    message_id: str
    content_hash: str
    klaviyo_web_url: str = ""
    source_url: str = ""
    preview_text: str = ""


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_text = ascii_text.lower()
    ascii_text = re.sub(r"[^a-z0-9]+", "-", ascii_text)
    return ascii_text.strip("-") or "panui"


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def load_existing_import_index(repo_root: Path) -> ExistingImportIndex:
    campaign_ids: set[str] = set()
    message_ids: set[str] = set()
    content_hashes: set[str] = set()
    slugs: set[str] = set()

    for post_path in (repo_root / "_posts").glob("*.md"):
        slugs.add(post_path.stem)
        try:
            text = post_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        front_matter = extract_front_matter(text)
        for key, target in (
            ("klaviyo_campaign_id", campaign_ids),
            ("klaviyo_message_id", message_ids),
            ("klaviyo_content_hash", content_hashes),
        ):
            value = front_matter.get(key, "").strip().strip('"\'')
            if value:
                target.add(value)

    return ExistingImportIndex(campaign_ids, message_ids, content_hashes, slugs)


def extract_front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    try:
        _, fm, _ = text.split("---\n", 2)
    except ValueError:
        return {}
    data: dict[str, str] = {}
    for line in fm.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def is_tracking_or_layout_image(src: str, attrs: str) -> bool:
    lower = f"{src} {attrs}".lower()
    if src.startswith("data:"):
        return True
    if any(token in lower for token in ("tracking", "track", "pixel", "beacon", "spacer", "transparent")):
        return True
    width = re.search(r'\bwidth=["\']?(\d+)', attrs, re.I)
    height = re.search(r'\bheight=["\']?(\d+)', attrs, re.I)
    if width and height and int(width.group(1)) <= 2 and int(height.group(1)) <= 2:
        return True
    return False


def extension_for(url: str, content_type: str) -> str:
    content_type = content_type.split(";", 1)[0].strip().lower()
    ext = mimetypes.guess_extension(content_type) if content_type else None
    if ext == ".jpe":
        ext = ".jpg"
    if ext:
        return ext
    path_ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
    if path_ext in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}:
        return path_ext
    return ".bin"


def download_url(url: str) -> tuple[bytes, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "OwairoaWhanauPanuiImporter/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read(), response.headers.get("Content-Type", "")


def rewrite_images(
    html_text: str,
    assets_dir: Path,
    public_prefix: str,
    download: Callable[[str], tuple[bytes, str]] = download_url,
) -> str:
    assets_dir.mkdir(parents=True, exist_ok=True)
    replacements: dict[str, str] = {}

    img_pattern = re.compile(r"<img\b(?P<attrs>[^>]*?)\bsrc=[\"'](?P<src>[^\"']+)[\"'](?P<tail>[^>]*)>", re.I)

    def replace(match: re.Match[str]) -> str:
        attrs = match.group("attrs") + match.group("tail")
        src = html.unescape(match.group("src"))
        if is_tracking_or_layout_image(src, attrs):
            return ""
        if not src.startswith(("http://", "https://")):
            return match.group(0)
        if src not in replacements:
            try:
                data, content_type = download(src)
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                print(f"WARNING: could not download image {src}: {exc}", file=sys.stderr)
                return match.group(0)
            digest = hashlib.sha256(data).hexdigest()[:16]
            ext = extension_for(src, content_type)
            filename = f"{digest}{ext}"
            target = assets_dir / filename
            if not target.exists():
                target.write_bytes(data)
            replacements[src] = f"{public_prefix.rstrip('/')}/{filename}"
        original = match.group(0)
        return re.sub(r"src=[\"'][^\"']+[\"']", f'src="{replacements[src]}"', original, count=1, flags=re.I)

    return img_pattern.sub(replace, html_text)


def build_post_file(post: ImportedPost) -> tuple[Path, str]:
    slug = slugify(post.title)
    rel_path = Path("_posts") / f"{post.date}-{slug}.md"
    lines = [
        "---",
        f"title: {yaml_string(post.title)}",
        f"date: {post.date}",
        "source: klaviyo",
        f"klaviyo_campaign_id: {yaml_string(post.campaign_id)}",
        f"klaviyo_message_id: {yaml_string(post.message_id)}",
        f"klaviyo_content_hash: {yaml_string(post.content_hash)}",
    ]
    if post.preview_text:
        lines.append(f"description: {yaml_string(post.preview_text)}")
    if post.klaviyo_web_url:
        lines.append(f"klaviyo_web_url: {yaml_string(post.klaviyo_web_url)}")
    if post.source_url:
        lines.append(f"klaviyo_source_url: {yaml_string(post.source_url)}")
    lines.extend(["---", "", post.body_html.strip(), ""])
    return rel_path, "\n".join(lines)


def nested_get(data: dict[str, Any], dotted: str, default: Any = "") -> Any:
    current: Any = data
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current


def api_get(path_or_url: str, api_key: str, revision: str, query: dict[str, str] | None = None) -> dict[str, Any]:
    if path_or_url.startswith("http"):
        url = path_or_url
    else:
        url = API_BASE + path_or_url
        if query:
            url += "?" + urllib.parse.urlencode(query, doseq=True)
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Klaviyo-API-Key {api_key}",
            "Accept": "application/vnd.api+json",
            "Revision": revision,
            "User-Agent": "OwairoaWhanauPanuiImporter/1.0",
        },
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in {429, 500, 502, 503, 504} and attempt < 3:
                time.sleep(2**attempt)
                continue
            body = exc.read().decode("utf-8", "replace")
            raise RuntimeError(f"Klaviyo API request failed {exc.code} for {url}: {body}") from exc

    raise RuntimeError(f"Klaviyo API request failed for {url}")


def paginated_api_get(path: str, api_key: str, revision: str, query: dict[str, str]) -> Iterable[dict[str, Any]]:
    next_url: str | None = path
    next_query: dict[str, str] | None = query
    while next_url:
        payload = api_get(next_url, api_key, revision, next_query)
        for item in payload.get("data", []):
            yield item
        next_url = nested_get(payload, "links.next", None)
        next_query = None


def normalize_date(value: Any) -> str:
    if isinstance(value, list) and value:
        value = value[0]
    if not value:
        return ""
    text = str(value).replace("Z", "+00:00")
    try:
        return dt.datetime.fromisoformat(text).date().isoformat()
    except ValueError:
        return text[:10]


def first_nonempty(*values: Any) -> str:
    for value in values:
        if isinstance(value, list) and value:
            value = value[0]
        if value:
            return str(value)
    return ""


def campaign_matches_filter(campaign: dict[str, Any], message: dict[str, Any], pattern: re.Pattern[str]) -> bool:
    attrs = campaign.get("attributes", {})
    msg_attrs = message.get("attributes", {})
    haystack = "\n".join(
        [
            str(nested_get(attrs, "name", "")),
            str(nested_get(msg_attrs, "definition.label", "")),
            str(nested_get(msg_attrs, "definition.content.subject", "")),
            str(nested_get(msg_attrs, "definition.content.title", "")),
        ]
    )
    return bool(pattern.search(haystack))


def extract_message_ids(campaign: dict[str, Any]) -> list[str]:
    relationships = nested_get(campaign, "relationships.campaign-messages.data", [])
    ids = [item.get("id", "") for item in relationships if isinstance(item, dict)]
    return [item for item in ids if item]


def is_sent_campaign(campaign: dict[str, Any]) -> bool:
    attrs = campaign.get("attributes", {})
    status = str(attrs.get("status", "")).strip().lower()
    if status in {"sent", "sent_or_partially_sent"}:
        return True
    if status and status not in {"draft", "scheduled", "cancelled", "canceled"}:
        return False
    return bool(attrs.get("send_time"))


def template_body_from_included(message_payload: dict[str, Any]) -> str:
    for item in message_payload.get("included", []):
        if item.get("type") != "template":
            continue
        attrs = item.get("attributes", {})
        return first_nonempty(
            attrs.get("html"),
            nested_get(attrs, "definition.html", ""),
            nested_get(attrs, "definition.content", ""),
        )
    return ""


def import_posts(repo_root: Path, api_key: str, revision: str, filter_regex: str, dry_run: bool = False) -> list[Path]:
    pattern = re.compile(filter_regex, re.I)
    existing = load_existing_import_index(repo_root)
    created: list[Path] = []

    campaign_query = {
        "include": "campaign-messages",
        "fields[campaign]": "created_at,updated_at,name,status,send_time,scheduled_at,archived",
        "fields[campaign-message]": "created_at,updated_at,definition,definition.content,definition.label,send_times",
        "filter": "equals(messages.channel,'email')",
        "page[size]": "100",
    }

    for campaign in paginated_api_get("/api/campaigns", api_key, revision, campaign_query):
        campaign_id = campaign.get("id", "")
        if campaign_id in existing.campaign_ids or not is_sent_campaign(campaign):
            continue
        message_ids = extract_message_ids(campaign)
        for message_id in message_ids:
            if message_id in existing.message_ids:
                continue
            message_payload = api_get(
                f"/api/campaign-messages/{urllib.parse.quote(message_id)}",
                api_key,
                revision,
                {
                    "include": "template,image",
                    "fields[campaign-message]": "created_at,updated_at,definition,definition.content,definition.label,definition.render_options,send_times",
                    "fields[template]": "html,name",
                    "fields[image]": "image_url,name,format,size",
                },
            )
            message = message_payload.get("data", {})
            if not campaign_matches_filter(campaign, message, pattern):
                continue

            attrs = message.get("attributes", {})
            subject = first_nonempty(
                nested_get(attrs, "definition.content.subject", ""),
                nested_get(attrs, "definition.label", ""),
                nested_get(campaign.get("attributes", {}), "name", ""),
                "Pānui",
            )
            body = first_nonempty(
                nested_get(attrs, "definition.content.body", ""),
                template_body_from_included(message_payload),
            )
            if not body:
                print(f"WARNING: skipping {campaign_id}/{message_id}; no message body found", file=sys.stderr)
                continue
            sent_date = normalize_date(first_nonempty(attrs.get("send_times"), attrs.get("created_at"), campaign.get("attributes", {}).get("created_at")))
            if not sent_date:
                print(f"WARNING: skipping {campaign_id}/{message_id}; no sent/created date found", file=sys.stderr)
                continue

            content_hash = hashlib.sha256(body.encode("utf-8")).hexdigest()
            if content_hash in existing.content_hashes:
                continue

            assets_rel = f"assets/images/panui/{slugify(campaign_id or message_id)}"
            rewritten_body = rewrite_images(body, repo_root / assets_rel, "/" + assets_rel)
            post = ImportedPost(
                title=html.unescape(subject).strip(),
                date=sent_date,
                body_html=rewritten_body,
                campaign_id=campaign_id,
                message_id=message_id,
                content_hash=content_hash,
                klaviyo_web_url=first_nonempty(
                    nested_get(attrs, "definition.content.web_url", ""),
                    nested_get(attrs, "definition.options.on_open.web_url", ""),
                ),
                source_url=f"https://www.klaviyo.com/campaign/{campaign_id}" if campaign_id else "",
                preview_text=first_nonempty(
                    nested_get(attrs, "definition.content.preview_text", ""),
                ),
            )
            rel_path, text = build_post_file(post)
            target = repo_root / rel_path
            if target.exists():
                # Final safety valve for same title/date imported from more than one campaign.
                rel_path = Path("_posts") / f"{post.date}-{slugify(post.title)}-{message_id[:8]}.md"
                target = repo_root / rel_path
            print(f"Importing {campaign_id}/{message_id} -> {rel_path}")
            if not dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text, encoding="utf-8")
            created.append(rel_path)
            existing.campaign_ids.add(campaign_id)
            existing.message_ids.add(message_id)
            existing.content_hashes.add(content_hash)
    return created


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root; defaults to current directory")
    parser.add_argument("--revision", default=os.environ.get("KLAVIYO_REVISION", DEFAULT_REVISION))
    parser.add_argument("--filter", default=os.environ.get("KLAVIYO_CAMPAIGN_FILTER", DEFAULT_FILTER), help="Regex matched against campaign/message names and subjects")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    api_key = os.environ.get("KLAVIYO_API_KEY", "").strip()
    if not api_key:
        print("ERROR: KLAVIYO_API_KEY is required.", file=sys.stderr)
        return 2
    repo_root = Path(args.repo_root).resolve()
    created = import_posts(repo_root, api_key, args.revision, args.filter, dry_run=args.dry_run)
    print(f"Created {len(created)} post(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
