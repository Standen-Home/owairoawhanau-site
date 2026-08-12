#!/usr/bin/env python3
"""Look up a Klaviyo form by id or name and print safe status details."""
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
            "User-Agent": "OwairoaWhanauFormLookup/1.0",
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


def first_version_summary(definition: Any) -> dict[str, Any]:
    versions = []
    if isinstance(definition, dict):
        versions = definition.get("versions") or []
    if not versions:
        return {}
    version = versions[0] if isinstance(versions[0], dict) else {}
    return {
        "version_type": version.get("type"),
        "version_status": version.get("status"),
        "step_count": len(version.get("steps") or []),
        "trigger_types": [t.get("type") for t in (version.get("triggers") or []) if isinstance(t, dict)],
    }


def summarize(item: dict[str, Any]) -> dict[str, Any]:
    attrs = item.get("attributes") or {}
    out = {
        "form_id": item.get("id"),
        "name": attrs.get("name"),
        "status": attrs.get("status"),
        "created": attrs.get("created"),
        "updated": attrs.get("updated"),
    }
    out.update(first_version_summary(attrs.get("definition")))
    return out


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
    form_id = os.environ.get("KLAVIYO_FORM_ID", "").strip()
    form_name = os.environ.get("KLAVIYO_FORM_NAME", "Uenuku Rainbow Wānanga Registration Embed").strip()
    if not form_id and not form_name:
        print("ERROR: KLAVIYO_FORM_ID or KLAVIYO_FORM_NAME is required", file=sys.stderr)
        return 2
    failures: list[str] = []
    for key_name, api_key in key_candidates():
        try:
            if form_id:
                payload = api_get(
                    f"/api/forms/{urllib.parse.quote(form_id)}",
                    api_key,
                    {"additional-fields[form]": "[definition]", "fields[form]": "id,name,status,definition,created,updated"},
                )
                results = [summarize(payload.get("data", {}))]
            else:
                payload = api_get(
                    "/api/forms",
                    api_key,
                    {"filter": f'equals(name,"{form_name}")', "additional-fields[form]": "[definition]", "fields[form]": "id,name,status,definition,created,updated"},
                )
                results = [summarize(item) for item in payload.get("data", [])]
            print(json.dumps({"api_key_used": key_name, "results": results}, ensure_ascii=False, indent=2))
            if github_output := os.environ.get("GITHUB_OUTPUT"):
                first = results[0] if results else {}
                with open(github_output, "a", encoding="utf-8") as fh:
                    for key, value in first.items():
                        fh.write(f"{key}={value or ''}\n")
            return 0
        except RuntimeError as exc:
            failures.append(f"{key_name}: {exc}")
    raise RuntimeError("Could not look up Klaviyo form. " + " | ".join(failures))


if __name__ == "__main__":
    raise SystemExit(main())
