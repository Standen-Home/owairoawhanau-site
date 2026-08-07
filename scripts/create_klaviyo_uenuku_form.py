#!/usr/bin/env python3
"""Create the Uenuku Rainbow Wānanga registration form in Klaviyo.

Runs in GitHub Actions using the repository KLAVIYO_API_KEY secret.
Prints the created form ID and writes it to GITHUB_OUTPUT when present.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

API_BASE = "https://a.klaviyo.com"
REVISION = os.environ.get("KLAVIYO_REVISION", "2026-07-15")
FORM_NAME = "Uenuku Rainbow Wānanga Registration"


def api_request(method: str, path: str, payload: dict[str, Any] | None = None) -> tuple[int, dict[str, Any] | None, str]:
    api_key = os.environ.get("KLAVIYO_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("KLAVIYO_API_KEY is not configured")

    data = None
    headers = {
        "Authorization": f"Klaviyo-API-Key {api_key}",
        "Accept": "application/vnd.api+json",
        "Revision": REVISION,
        "User-Agent": "OwairoaWhanauSite/uenuku-form-creator",
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/vnd.api+json"

    req = urllib.request.Request(API_BASE + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            body = res.read().decode("utf-8", "replace")
            return res.status, json.loads(body) if body.strip() else None, body
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = None
        return exc.code, parsed, body


def field_block(kind: str, label: str, property_name: str, *, required: bool = False, placeholder: str = "") -> dict[str, Any]:
    props: dict[str, Any] = {
        "display_device": ["both"],
        "label": label,
        "show_label": True,
        "placeholder": placeholder or label,
        "required": required,
        "property_name": property_name,
        "error_messages": {
            "required": "This field is required",
            "invalid": "Please check this field",
        },
    }
    if kind == "email":
        props["property_name"] = "$email"
    if kind == "phone_number":
        props["property_name"] = "$phone_number"
        props["sms_consent_type"] = ["phone_number_only"]
    return {
        "type": kind,
        "properties": props,
        "styles": {"padding": {"top": 6, "right": 0, "bottom": 6, "left": 0}},
    }


def html_block(content: str) -> dict[str, Any]:
    return {
        "type": "html_text",
        "properties": {"display_device": ["both"], "content": content},
        "styles": {"padding": {"top": 6, "right": 0, "bottom": 8, "left": 0}},
    }


def row(*blocks: dict[str, Any]) -> dict[str, Any]:
    return {"blocks": list(blocks)}


def build_payload(list_id: str | None) -> dict[str, Any]:
    submit_action: dict[str, Any] = {"type": "next_step", "submit": True, "properties": {}}
    if list_id:
        submit_action["properties"]["list_id"] = list_id

    submit_button = {
        "type": "button",
        "properties": {
            "display_device": ["both"],
            "label": "Register my interest",
            "additional_fields": [
                {"name": "Event", "value": FORM_NAME},
                {"name": "Event Date", "value": "Saturday 15 August 2026"},
                {"name": "Venue", "value": "At the whare"},
                {"name": "Koha", "value": "Koha based — all proceeds to the whare"},
            ],
        },
        "styles": {
            "padding": {"top": 10, "right": 0, "bottom": 0, "left": 0},
            "width": "fill",
            "height": 50,
            "alignment": "center",
            "background_color": "#2180B5",
            "hover_background_color": "#17658F",
            "color": "#FFFFFF",
            "border_styles": {"radius": 12, "color": "#2180B5", "style": "solid", "thickness": 1},
            "text_styles": {"font_family": "Inter", "font_size": 16, "font_weight": 700},
        },
        "action": submit_action,
    }

    close_button = {
        "type": "button",
        "properties": {"display_device": ["both"], "label": "Close"},
        "styles": {
            "padding": {"top": 10, "right": 0, "bottom": 0, "left": 0},
            "width": "fill",
            "height": 46,
            "alignment": "center",
            "background_color": "#EFCE2B",
            "color": "#090303",
            "border_styles": {"radius": 12, "color": "#EFCE2B", "style": "solid", "thickness": 1},
        },
        "action": {"type": "close", "submit": False, "properties": {}},
    }

    return {
        "data": {
            "type": "form",
            "attributes": {
                "name": FORM_NAME,
                "status": "draft",
                "ab_test": False,
                "definition": {
                    "versions": [
                        {
                            "name": "Main",
                            "type": "popup",
                            "location": "top_center",
                            "status": "draft",
                            "ab_test": False,
                            "channel": "WEB",
                            "message_priority": 50,
                            "triggers": [{"type": "custom_javascript", "properties": {}}],
                            "teasers": [],
                            "styles": {
                                "width": "medium",
                                "minimum_height": 250,
                                "background_color": "#FFFFFF",
                                "overlay_color": "rgba(20,20,20,0.45)",
                                "padding": {"top": 24, "right": 24, "bottom": 24, "left": 24},
                                "margin": {"top": 0, "right": 0, "bottom": 0, "left": 0},
                                "input_styles": {
                                    "label_color": "#090303",
                                    "text_color": "#090303",
                                    "placeholder_color": "#5B524B",
                                    "background_color": "#FFFFFF",
                                    "border_color": "#E7DFD2",
                                    "border_focus_color": "#2180B5",
                                    "focus_outline_color": "#2180B5",
                                    "corner_radius": 12,
                                    "field_height": 44,
                                },
                            },
                            "properties": {
                                "show_close_button": True,
                                "click_outside_to_close": ["both"],
                                "record_utm_params_on_submit": True,
                                "accessible_name": FORM_NAME,
                            },
                            "steps": [
                                {
                                    "name": "Registration details",
                                    "columns": [
                                        {
                                            "rows": [
                                                row(html_block("<h2>Uenuku Rainbow Wānanga</h2><p>Register your interest for the workshop with Taini Drummond.</p><p><strong>Saturday 15 August 2026</strong><br>At the whare • Time TBC<br>Koha based — all proceeds to the whare</p>")),
                                                row(field_block("text", "Your name", "$first_name", required=True, placeholder="Your name")),
                                                row(field_block("email", "Email", "$email", required=True, placeholder="you@example.com")),
                                                row(field_block("phone_number", "Phone", "$phone_number", required=False, placeholder="022 123 4567")),
                                                row(field_block("text", "Number attending", "uenuku_number_attending", required=True, placeholder="1")),
                                                row(field_block("text", "Names of anyone else coming", "uenuku_extra_names", required=False, placeholder="Names of other attendees")),
                                                row(field_block("text", "Anything Taini/Kate should know?", "uenuku_notes", required=False, placeholder="Accessibility, transport, or other notes")),
                                                row(submit_button),
                                            ]
                                        }
                                    ],
                                },
                                {
                                    "name": "Success",
                                    "columns": [
                                        {
                                            "rows": [
                                                row(html_block("<h2>Thank you</h2><p>Your interest has been sent through. We’ll be in touch with any updates.</p>")),
                                                row(close_button),
                                            ]
                                        }
                                    ],
                                },
                            ],
                        }
                    ]
                },
            },
        }
    }


def first_list_id() -> str | None:
    configured = os.environ.get("KLAVIYO_FORM_LIST_ID", "").strip()
    if configured:
        print(f"Using configured Klaviyo list for submissions: {configured}")
        return configured

    # Optional: use the first available list if the key has lists:read. If not, fall back
    # to the known Preview List ID discovered with the existing read key.
    status, parsed, _ = api_request("GET", "/api/lists?fields[list]=name,id&page[size]=1")
    if status == 200 and parsed and parsed.get("data"):
        item = parsed["data"][0]
        print(f"Using Klaviyo list for submissions: {item.get('attributes', {}).get('name', item.get('id'))} ({item.get('id')})")
        return item.get("id")

    fallback = "RPbsS6"
    print(f"List lookup skipped/unavailable (status {status}); using known Preview List ID {fallback}.")
    return fallback


def existing_form_id() -> str | None:
    query = urllib.parse.urlencode({"filter": f'equals(name,"{FORM_NAME}")', "fields[form]": "id,name,status"})
    status, parsed, _ = api_request("GET", f"/api/forms?{query}")
    if status == 200 and parsed and parsed.get("data"):
        return parsed["data"][0].get("id")
    return None


def set_output(form_id: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(f"form_id={form_id}\n")


def main() -> int:
    existing = existing_form_id()
    if existing:
        print(f"Form already exists: {existing}")
        set_output(existing)
        return 0

    payload = build_payload(first_list_id())
    status, parsed, body = api_request("POST", "/api/forms", payload)
    if status != 201 or parsed is None:
        print(f"Create form failed with status {status}")
        if parsed:
            print(json.dumps(parsed, indent=2)[:4000])
        else:
            print(body[:4000])
        return 1

    form_id = parsed["data"]["id"]
    print(f"Created Klaviyo form: {form_id}")
    print(f"Form name: {parsed['data']['attributes']['name']}")
    print(f"Status: {parsed['data']['attributes']['status']}")
    set_output(form_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
