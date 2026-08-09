#!/usr/bin/env python3
"""Look up the Klaviyo template attached to a campaign message."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

API_BASE = "https://a.klaviyo.com"
REVISION = os.environ.get("KLAVIYO_REVISION", "2026-07-15")


def api_get(path: str, api_key: str, query: dict[str, str] | None = None) -> dict[str, Any]:
    url = API_BASE + path
    if query:
        url += "?" + urllib.parse.urlencode(query, doseq=True)
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Klaviyo-API-Key {api_key}",
            "Accept": "application/vnd.api+json",
            "Revision": REVISION,
            "User-Agent": "OwairoaWhanauKlaviyoLookup/1.0",
        },
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")
            if exc.code in {429, 500, 502, 503, 504} and attempt < 3:
                time.sleep(2**attempt)
                continue
            raise RuntimeError(f"Klaviyo API GET {url} failed {exc.code}: {body}") from exc
    raise RuntimeError(f"Klaviyo API GET {url} failed after retries")


def first_nonempty(*values: Any) -> str:
    for value in values:
        if value:
            return str(value)
    return ""


def main() -> int:
    api_key = (os.environ.get("KLAVIYO_API_CREATE_KEY") or os.environ.get("KLAVIYO_API_KEY") or "").strip()
    campaign_id = (os.environ.get("KLAVIYO_CAMPAIGN_ID") or "").strip()
    if not api_key or not campaign_id:
        print("ERROR: KLAVIYO_API_KEY/KLAVIYO_API_CREATE_KEY and KLAVIYO_CAMPAIGN_ID are required", file=sys.stderr)
        return 2

    campaign = api_get(
        f"/api/campaigns/{urllib.parse.quote(campaign_id)}",
        api_key,
        {"fields[campaign]": "id,name,status,send_time,scheduled_at"},
    ).get("data", {})

    messages_payload = api_get(
        f"/api/campaigns/{urllib.parse.quote(campaign_id)}/campaign-messages",
        api_key,
        {
            "include": "template",
            "fields[campaign-message]": "id,definition,updated_at,created_at",
            "fields[template]": "id,name,editor_type,updated,created",
        },
    )
    included_templates = {item.get("id"): item for item in messages_payload.get("included", []) if item.get("type") == "template"}
    results: list[dict[str, Any]] = []
    for message in messages_payload.get("data", []):
        rel_template = (((message.get("relationships") or {}).get("template") or {}).get("data") or {})
        template_id = rel_template.get("id") or ""
        template = included_templates.get(template_id, {})
        template_attrs = template.get("attributes") or {}
        msg_attrs = message.get("attributes") or {}
        definition = msg_attrs.get("definition") or {}
        content = definition.get("content") or {}
        results.append(
            {
                "message_id": message.get("id"),
                "message_label": definition.get("label"),
                "subject": content.get("subject"),
                "template_id": template_id,
                "template_name": template_attrs.get("name"),
                "template_editor_type": template_attrs.get("editor_type"),
            }
        )

    summary = {
        "campaign_id": campaign_id,
        "campaign_name": (campaign.get("attributes") or {}).get("name"),
        "campaign_status": (campaign.get("attributes") or {}).get("status"),
        "send_time": (campaign.get("attributes") or {}).get("send_time"),
        "scheduled_at": (campaign.get("attributes") or {}).get("scheduled_at"),
        "messages": results,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if github_output := os.environ.get("GITHUB_OUTPUT"):
        first = results[0] if results else {}
        with open(github_output, "a", encoding="utf-8") as fh:
            fh.write(f"campaign_id={campaign_id}\n")
            fh.write(f"campaign_name={summary.get('campaign_name') or ''}\n")
            fh.write(f"message_id={first.get('message_id') or ''}\n")
            fh.write(f"template_id={first.get('template_id') or ''}\n")
            fh.write(f"template_name={first.get('template_name') or ''}\n")
            fh.write(f"template_editor_type={first.get('template_editor_type') or ''}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
