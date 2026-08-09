#!/usr/bin/env python3
"""Replace text inside a Klaviyo template definition/html/text.

Used for safe API edit checks on draft pānui templates. It never schedules or
sends a campaign; it only updates the specified template content.
"""
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


def api_request(method: str, path: str, api_key: str, payload: dict[str, Any] | None = None, query: dict[str, str] | None = None) -> dict[str, Any]:
    url = API_BASE + path
    if query:
        url += "?" + urllib.parse.urlencode(query, doseq=True)
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": f"Klaviyo-API-Key {api_key}",
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json",
            "Revision": REVISION,
            "User-Agent": "OwairoaWhanauTemplateTextUpdate/1.0",
        },
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw.strip() else {}
        except urllib.error.HTTPError as exc:
            body_text = exc.read().decode("utf-8", "replace")
            if exc.code in {429, 500, 502, 503, 504} and attempt < 3:
                time.sleep(2**attempt)
                continue
            raise RuntimeError(f"Klaviyo API {method} {url} failed {exc.code}: {body_text}") from exc
    raise RuntimeError(f"Klaviyo API {method} {url} failed after retries")


def replace_in_obj(value: Any, old: str, new: str) -> tuple[Any, int]:
    if isinstance(value, str):
        count = value.count(old)
        return value.replace(old, new), count
    if isinstance(value, list):
        total = 0
        out_list: list[Any] = []
        for item in value:
            replaced, count = replace_in_obj(item, old, new)
            out_list.append(replaced)
            total += count
        return out_list, total
    if isinstance(value, dict):
        total = 0
        out_dict: dict[str, Any] = {}
        for key, item in value.items():
            replaced, count = replace_in_obj(item, old, new)
            out_dict[key] = replaced
            total += count
        return out_dict, total
    return value, 0


def key_candidates() -> list[tuple[str, str]]:
    return [
        (name, key)
        for name, key in [
            ("KLAVIYO_API_CREATE_KEY", os.environ.get("KLAVIYO_API_CREATE_KEY", "").strip()),
            ("KLAVIYO_API_KEY", os.environ.get("KLAVIYO_API_KEY", "").strip()),
        ]
        if key
    ]


def main() -> int:
    template_id = os.environ.get("KLAVIYO_TEMPLATE_ID", "").strip()
    old_text = os.environ.get("KLAVIYO_OLD_TEXT", "")
    new_text = os.environ.get("KLAVIYO_NEW_TEXT", "")
    if not template_id or not old_text:
        print("ERROR: KLAVIYO_TEMPLATE_ID and KLAVIYO_OLD_TEXT are required", file=sys.stderr)
        return 2

    failures: list[str] = []
    for key_name, api_key in key_candidates():
        try:
            payload = api_request(
                "GET",
                f"/api/templates/{urllib.parse.quote(template_id)}",
                api_key,
                {
                    "additional-fields[template]": "definition",
                    "fields[template]": "id,name,editor_type,definition,html,text",
                },
            )
            data = payload.get("data", {})
            attrs = data.get("attributes", {})
            editor_type = attrs.get("editor_type")
            update_attrs: dict[str, Any] = {}
            total = 0
            if attrs.get("definition") is not None:
                definition, count = replace_in_obj(attrs["definition"], old_text, new_text)
                update_attrs["definition"] = definition
                total += count
            for field in ("html", "text"):
                if isinstance(attrs.get(field), str):
                    replaced, count = replace_in_obj(attrs[field], old_text, new_text)
                    update_attrs[field] = replaced
                    total += count
            if total == 0:
                raise RuntimeError(f"Text not found in template {template_id}: {old_text!r}")
            update_payload = {"data": {"type": "template", "id": template_id, "attributes": update_attrs}}
            api_request("PATCH", f"/api/templates/{urllib.parse.quote(template_id)}", api_key, update_payload)
            summary = {"template_id": template_id, "editor_type": editor_type, "replacements": total, "api_key_used": key_name}
            print(json.dumps(summary, ensure_ascii=False, indent=2))
            if github_output := os.environ.get("GITHUB_OUTPUT"):
                with open(github_output, "a", encoding="utf-8") as fh:
                    for key, value in summary.items():
                        fh.write(f"{key}={value}\n")
            return 0
        except RuntimeError as exc:
            failures.append(f"{key_name}: {exc}")
    raise RuntimeError("Could not update Klaviyo template text. " + " | ".join(failures))


if __name__ == "__main__":
    raise SystemExit(main())
