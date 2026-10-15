#!/usr/bin/env python3
"""Create and publish the Waiata Wednesday WhatsApp signup form in Klaviyo."""
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
FORM_NAME = os.environ.get(
    "KLAVIYO_FORM_NAME", "Waiata Wednesday WhatsApp Group Signup Embed"
)


def api_request(
    method: str, path: str, payload: dict[str, Any] | None = None
) -> tuple[int, dict[str, Any] | None, str]:
    api_key = os.environ.get("KLAVIYO_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("KLAVIYO_API_KEY is not configured")

    data = None
    headers = {
        "Authorization": f"Klaviyo-API-Key {api_key}",
        "Accept": "application/vnd.api+json",
        "Revision": REVISION,
        "User-Agent": "OwairoaWhanauSite/waiata-whatsapp-form-creator",
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/vnd.api+json"

    request = urllib.request.Request(
        API_BASE + path, data=data, method=method, headers=headers
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8", "replace")
            return response.status, json.loads(body) if body.strip() else None, body
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = None
        return exc.code, parsed, body


def field_block(
    kind: str,
    label: str,
    property_name: str,
    *,
    required: bool = False,
    placeholder: str = "",
) -> dict[str, Any]:
    properties: dict[str, Any] = {
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
    if kind == "phone_number":
        properties["property_name"] = "$phone_number"
        properties["sms_consent_type"] = ["phone_number_only"]
    return {
        "type": kind,
        "properties": properties,
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


def build_payload(list_id: str) -> dict[str, Any]:
    submit_button = {
        "type": "button",
        "properties": {
            "display_device": ["both"],
            "label": "Join the WhatsApp group",
            "additional_fields": [
                {"name": "Interest", "value": "Waiata Wednesday WhatsApp Group"},
                {"name": "Source", "value": "Ō Wairoa Whānau website"},
            ],
        },
        "styles": {
            "padding": {"top": 10, "right": 0, "bottom": 0, "left": 0},
            "width": "fill",
            "height": 50,
            "alignment": "center",
            "background_color": "#85200E",
            "hover_background_color": "#64180B",
            "color": "#FFFFFF",
            "border_styles": {
                "radius": 12,
                "color": "#85200E",
                "style": "solid",
                "thickness": 1,
            },
            "text_styles": {
                "font_family": "Inter",
                "font_size": 16,
                "font_weight": 700,
            },
        },
        "action": {
            "type": "next_step",
            "submit": True,
            "properties": {"list_id": list_id},
        },
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
                            "type": "embed",
                            "status": "draft",
                            "ab_test": False,
                            "channel": "WEB",
                            "message_priority": 50,
                            "triggers": [
                                {"type": "custom_javascript", "properties": {}}
                            ],
                            "teasers": [],
                            "styles": {
                                "width": "medium",
                                "minimum_height": 250,
                                "background_color": "#FFFFFF",
                                "overlay_color": "rgba(20,20,20,0.45)",
                                "padding": {
                                    "top": 24,
                                    "right": 24,
                                    "bottom": 24,
                                    "left": 24,
                                },
                                "margin": {
                                    "top": 0,
                                    "right": 0,
                                    "bottom": 0,
                                    "left": 0,
                                },
                                "input_styles": {
                                    "label_color": "#090303",
                                    "text_color": "#090303",
                                    "placeholder_color": "#5B524B",
                                    "background_color": "#FFFFFF",
                                    "border_color": "#E7DFD2",
                                    "border_focus_color": "#85200E",
                                    "focus_outline_color": "#85200E",
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
                                    "name": "Signup details",
                                    "columns": [
                                        {
                                            "rows": [
                                                row(
                                                    html_block(
                                                        "<h2>Waiata Wednesday WhatsApp Group</h2>"
                                                        "<p>Share your mobile number to join the whānau WhatsApp group for reminders and updates.</p>"
                                                        "<p><strong>Privacy note:</strong> WhatsApp group members may be able to see your phone number. You can leave the group at any time.</p>"
                                                    )
                                                ),
                                                row(
                                                    field_block(
                                                        "text",
                                                        "Your name",
                                                        "$first_name",
                                                        required=True,
                                                        placeholder="Your name",
                                                    )
                                                ),
                                                row(
                                                    field_block(
                                                        "phone_number",
                                                        "Mobile number",
                                                        "$phone_number",
                                                        required=True,
                                                        placeholder="022 123 4567",
                                                    )
                                                ),
                                                row(
                                                    field_block(
                                                        "text",
                                                        "Anything we should know?",
                                                        "waiata_whatsapp_note",
                                                        required=False,
                                                        placeholder="Optional",
                                                    )
                                                ),
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
                                                row(
                                                    html_block(
                                                        "<h2>Kia ora!</h2><p>Your number has been received. We’ll add you to the Waiata Wednesday WhatsApp group.</p>"
                                                    )
                                                )
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


def existing_form_id() -> str | None:
    query = urllib.parse.urlencode(
        {
            "filter": f'equals(name,"{FORM_NAME}")',
            "fields[form]": "id,name,status",
        }
    )
    status, parsed, _ = api_request("GET", f"/api/forms?{query}")
    if status == 200 and parsed and parsed.get("data"):
        return parsed["data"][0].get("id")
    return None


def publish_form(form_id: str) -> None:
    status, parsed, body = api_request(
        "POST", f"/api/forms/{urllib.parse.quote(form_id)}/actions/publish"
    )
    if status not in {200, 202, 204}:
        print(f"Publish form failed with status {status}")
        print(json.dumps(parsed, indent=2)[:4000] if parsed else body[:4000])
        raise SystemExit(1)


def verify_form(form_id: str) -> str:
    status, parsed, body = api_request(
        "GET", f"/api/forms/{urllib.parse.quote(form_id)}?fields[form]=id,name,status"
    )
    if status != 200 or not parsed:
        print(f"Verify form failed with status {status}")
        print(json.dumps(parsed, indent=2)[:4000] if parsed else body[:4000])
        raise SystemExit(1)
    form_status = str(parsed["data"]["attributes"].get("status", ""))
    if form_status.lower() not in {"live", "published"}:
        raise SystemExit(f"Expected live/published form, got status {form_status!r}")
    return form_status


def set_outputs(form_id: str, status: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as output:
            output.write(f"form_id={form_id}\n")
            output.write(f"status={status}\n")


def main() -> int:
    list_id = os.environ.get("KLAVIYO_FORM_LIST_ID", "RPbsS6").strip()
    if not list_id:
        raise SystemExit("KLAVIYO_FORM_LIST_ID is required")

    form_id = existing_form_id()
    if form_id:
        print(f"Form already exists: {form_id}")
    else:
        status, parsed, body = api_request("POST", "/api/forms", build_payload(list_id))
        if status != 201 or not parsed:
            print(f"Create form failed with status {status}")
            print(json.dumps(parsed, indent=2)[:4000] if parsed else body[:4000])
            return 1
        form_id = parsed["data"]["id"]
        print(f"Created Klaviyo form: {form_id}")

    publish_form(form_id)
    form_status = verify_form(form_id)
    print(f"Form ID: {form_id}")
    print(f"Status: {form_status}")
    set_outputs(form_id, form_status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
