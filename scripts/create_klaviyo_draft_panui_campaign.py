#!/usr/bin/env python3
"""Create a Klaviyo draft pānui campaign for the coming week.

This is intentionally kept in Klaviyo Draft status: it clones an existing sent
campaign, assigns fresh editable template content, and verifies the resulting
campaign is not scheduled/sent.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zoneinfo
from pathlib import Path
from typing import Any

API_BASE = "https://a.klaviyo.com"
REVISION = os.environ.get("KLAVIYO_REVISION", "2026-07-15")
SOURCE_CAMPAIGN_ID = os.environ.get("KLAVIYO_SOURCE_CAMPAIGN_ID", "01KXQCZH1HKNGGMF7KFFK86PA1")
SITE_URL = os.environ.get("SITE_URL", "https://owairoawhanau.co.nz").rstrip("/")
TZ = zoneinfo.ZoneInfo("Pacific/Auckland")


def api_request(method: str, path: str, api_key: str, payload: dict[str, Any] | None = None, query: dict[str, str] | None = None) -> dict[str, Any]:
    url = path if path.startswith("http") else API_BASE + path
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
            "User-Agent": "OwairoaWhanauDraftCampaign/1.0",
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


def text_content() -> str:
    return """Kia ora {{ person.first_name|default:'e hoa' }},

Pānui for the week of 9 August 2026.

This week:
• Today, Sunday 9 August, 2pm-5pm — Kaihaka Kapa Haka
• Friday 14 August, 9am-10am — Mahi Ngahere
• Saturday 15 August, 10am-12pm — Nga tae o Uenuku / Uenuku Rainbow Wānanga with Taini Drummond at Ō Wairoa Marae - Matariki Whare

The Uenuku wānanga is koha based, with all proceeds to the marae. Register for updates on the website.

No longer want to receive these emails? {% unsubscribe %}
Manage preferences: {% manage_preferences %}
{{ organization.name }}
{{ organization.full_address }}
""".strip()


def campaign_html() -> str:
    """Return HTML that mirrors the recent Klaviyo pānui layout.

    The previous pānui format is simple and very Klaviyo-ish: pale site
    background, 600px white card, yellow strip at the top, right-aligned Ō Wairoa
    Marae Whanau header, centered date/event blocks, full-width poster image,
    horizontal dividers, closing text, maroon social/footer strip, and a waiata
    lyrics block.
    """
    poster_url = f"{SITE_URL}/assets/images/events/uenuku-rainbow-wananga-2026.png"
    register_url = f"{SITE_URL}/uenuku-rainbow-wananga/register/"
    calendar_url = f"{SITE_URL}/calendar/"
    contact_url = f"{SITE_URL}/contact/"
    facebook_icon = f"{SITE_URL}/assets/images/panui/01kwknzstzg8kaqzj32jt93fmx/311d80d6bdd83b45.png"
    email_icon = f"{SITE_URL}/assets/images/panui/01kwknzstzg8kaqzj32jt93fmx/6d549562fa389c2e.png"
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Ō Wairoa Marae Whanau | Pānui o te wiki</title>
  <style>
    body {{ margin:0; padding:0; background:#FBFAF7; -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; }}
    table, td {{ border-collapse:collapse; }}
    img {{ border:0; height:auto; line-height:100%; outline:none; text-decoration:none; max-width:100%; }}
    a {{ color:#85200E; font-weight:700; text-decoration:underline; }}
    p {{ margin:0; padding-bottom:1em; }}
    .wrapper {{ background:#FBFAF7; padding:10px; }}
    .container {{ width:100%; max-width:600px; background:#ffffff; margin:0 auto; }}
    .text {{ font-family:Inter, Arial, Helvetica, sans-serif; font-size:16px; line-height:1.3; color:#090303; }}
    .brand {{ text-align:right; font-family:Arial, Helvetica, sans-serif; font-size:24px; line-height:1.2; padding:9px 18px; }}
    .brand-accent {{ color:#85200E; font-weight:700; }}
    .center {{ text-align:center; }}
    .event-title {{ color:#090303; font-size:18px; font-weight:700; text-decoration:underline; }}
    .section-title {{ color:#85200E; font-size:24px; font-weight:700; }}
    .divider {{ border-top:solid 1px #CCCCCC; font-size:1px; line-height:1px; margin:0 auto; width:100%; }}
    @media only screen and (max-width:480px) {{ .text {{ padding-left:18px !important; padding-right:18px !important; }} }}
  </style>
</head>
<body>
  <div style="display:none;max-height:0;overflow:hidden;">Pānui o te wiki with this week’s events and Uenuku Rainbow Wānanga.</div>
  <div class="wrapper">
    <table role="presentation" class="container" align="center" width="100%" cellpadding="0" cellspacing="0">
      <tr><td style="background-color:#EFCE2B; padding:32px 20px 8px 20px;">&nbsp;</td></tr>
      <tr><td class="brand"><span class="brand-accent">| Ō Wairoa Marae</span> <strong>Whanau</strong></td></tr>
      <tr><td class="text" style="padding:9px 18px;">
        <p><span style="color:#403F3F;">Kia ora, {{{{ person.first_name|default:'e hoa' }}}}.</span></p>
        <p><span style="color:#403F3F;">Here is the pānui o te wiki for the coming week.</span></p>
      </td></tr>
      <tr><td style="padding:18px;"><div class="divider">&nbsp;</div></td></tr>

      <tr><td class="text center" style="padding:9px 18px; font-family:Arial, Helvetica, sans-serif;">
        <div style="font-size:28px; font-weight:700; padding-bottom:18px;">Panui o te wiki!</div>

        <p><span class="event-title">Sunday | 9 August 2026</span></p>
        <p><span style="font-size:18px;">Kaihaka Kapa Haka - 2pm to 5pm</span></p>

        <p><span class="event-title">Friday | 14 August 2026</span></p>
        <p><span style="font-size:18px;">Mahi Ngahere - 9am to 10am</span></p>

        <p><span class="event-title">Saturday | 15 August 2026</span></p>
        <p><span style="font-size:18px;">Nga tae o Uenuku | Uenuku Rainbow Wānanga with Taini Drummond</span></p>
        <p><span style="font-size:16px;">10am to 12pm<br>Ō Wairoa Marae - Matariki Whare<br>Koha based — all proceeds to the marae</span></p>
        <p><a href="{register_url}" target="_blank" rel="noopener noreferrer nofollow"><span style="font-size:16px;">Register for updates</span></a></p>
        <p><a href="{calendar_url}" target="_blank" rel="noopener noreferrer nofollow"><span style="font-size:16px;">Open the full calendar</span></a></p>
      </td></tr>

      <tr><td align="center" style="padding:0;">
        <a href="{register_url}" target="_blank" rel="noopener noreferrer nofollow"><img src="{poster_url}" alt="Poster for Nga tae o Uenuku Rainbow Wānanga with Taini Drummond" width="600" style="display:block; width:100%; max-width:600px;"></a>
      </td></tr>

      <tr><td style="padding:18px;"><div class="divider">&nbsp;</div></td></tr>
      <tr><td class="text" style="padding:9px 18px;">
        <div><span style="color:#3E3D3D;">As always - We look forward to seeing you soon.</span></div>
        <div><span style="color:#3E3D3D;"><br>Kia pai te ra! ☀️</span></div>
        <div><span style="color:#3E3D3D;">&nbsp;</span></div>
      </td></tr>

      <tr><td style="background-color:#85200E; padding:9px; text-align:center;">
        <a href="https://www.facebook.com/profile.php?id=100077399025413" target="_blank" style="display:inline-block; padding-right:10px;"><img alt="facebook" src="{facebook_icon}" width="32" style="width:32px;"></a>
        <a href="{contact_url}" target="_blank" style="display:inline-block;"><img alt="Email" src="{email_icon}" width="32" style="width:32px;"></a>
      </td></tr>

      <tr><td style="background-color:#FBFAF7; padding:9px 18px;">
        <div class="text center" style="background:#FFFFFF; padding:10px; font-family:Arial, Helvetica, sans-serif;">
          <div><span style="color:#85200E; font-size:18px;"><strong>Te Tuhi </strong></span><span style="font-size:18px;"><strong>Lyrics</strong></span></div>
          <div style="padding:8px 0;">&nbsp;</div>
          <div><strong>Mā te rāpa ka kitea</strong><br>Te Tuhi a Manawatere<br>Nō Ngāi Tai... te tupuna e<br>Te Waka... he huruhuru<br>Te Pōhutukawa ..i Wairoa<br>He tohu... he whaka-taukī<br>Mā te rāpa .. ka kitea x2</div>
        </div>
      </td></tr>

      <tr><td class="text center" style="background-color:#85200E; color:#ffffff; padding:9px 18px; font-size:14px;">Ō Wairoa Whānau</td></tr>
      <tr><td class="text center" style="background-color:#FBFAF7; color:#3E3D3D; padding:12px 18px; font-size:12px; font-family:Arial, Helvetica, sans-serif;">
        <div>No longer want to receive these emails? <a href="{{% unsubscribe %}}" style="color:#85200E; font-weight:700; text-decoration:underline;">Unsubscribe</a></div>
        <div><a href="{{% manage_preferences %}}" style="color:#85200E; font-weight:700; text-decoration:underline;">Manage preferences</a></div>
        <div>{{{{ organization.name }}}}</div>
        <div>{{{{ organization.full_address }}}}</div>
      </td></tr>
    </table>
  </div>
</body>
</html>"""


def dnd_display() -> dict[str, str]:
    return {"show_on": "all"}


def dnd_text_block(content: str, *, align: str = "left", size: int = 16, color: str = "#090303", weight: str = "400") -> dict[str, Any]:
    return {
        "content_type": "block",
        "type": "text",
        "data": {
            "content": content,
            "display_options": dnd_display(),
            "styles": {
                "font_family": "Arial, Helvetica, sans-serif",
                "font_size": size,
                "font_weight": weight,
                "line_height": 1.3,
                "color": color,
                "text_align": align,
                "block_padding_top": 9,
                "block_padding_right": 18,
                "block_padding_bottom": 9,
                "block_padding_left": 18,
            },
        },
    }


def dnd_image_block(src: str, alt: str, href: str | None = None) -> dict[str, Any]:
    return {
        "content_type": "block",
        "type": "image",
        "data": {
            "properties": {"dynamic": False, "src": src, "alt_text": alt, "href": href},
            "display_options": dnd_display(),
            "styles": {
                "align": "center",
                "width": 600,
                "max_width": 600,
                "block_padding_top": 0,
                "block_padding_right": 0,
                "block_padding_bottom": 0,
                "block_padding_left": 0,
            },
        },
    }


def dnd_button_block(label: str, href: str) -> dict[str, Any]:
    return {
        "content_type": "block",
        "type": "button",
        "data": {
            "content": label,
            "properties": {"href": href},
            "display_options": dnd_display(),
            "styles": {
                "background_color": "#85200E",
                "color": "#FFFFFF",
                "font_family": "Arial, Helvetica, sans-serif",
                "font_size": 16,
                "font_weight": "700",
                "text_align": "center",
                "border_radius": 4,
                "inner_padding_top": 12,
                "inner_padding_right": 18,
                "inner_padding_bottom": 12,
                "inner_padding_left": 18,
                "block_padding_top": 12,
                "block_padding_right": 18,
                "block_padding_bottom": 12,
                "block_padding_left": 18,
            },
        },
    }


def dnd_rule_block() -> dict[str, Any]:
    return {
        "content_type": "block",
        "type": "horizontal_rule",
        "data": {
            "display_options": dnd_display(),
            "styles": {
                "border_color": "#CCCCCC",
                "border_style": "solid",
                "border_width": 1,
                "block_padding_top": 18,
                "block_padding_right": 18,
                "block_padding_bottom": 18,
                "block_padding_left": 18,
            },
        },
    }


def dnd_section(blocks: list[dict[str, Any]], *, background: str = "#FFFFFF") -> dict[str, Any]:
    return {
        "content_type": "section",
        "type": "section",
        "data": {
            "properties": {},
            "display_options": dnd_display(),
            "styles": {
                "background_color": background,
                "content_color": "#FFFFFF",
                "content_color_type": "section",
                "inner_padding_top": 0,
                "inner_padding_right": 0,
                "inner_padding_bottom": 0,
                "inner_padding_left": 0,
                "column_align": "top",
                "column_direction": "ltr",
                "stack_on_mobile": True,
            },
        },
        "rows": [{"data": {}, "columns": [{"data": {}, "blocks": blocks}]}],
    }


def campaign_definition() -> dict[str, Any]:
    """Build a Klaviyo SYSTEM_DRAGGABLE definition with editable blocks."""
    poster_url = f"{SITE_URL}/assets/images/events/uenuku-rainbow-wananga-2026.png"
    register_url = f"{SITE_URL}/uenuku-rainbow-wananga/register/"
    calendar_url = f"{SITE_URL}/calendar/"
    event_text = """
<div style="text-align:center;"><strong style="font-size:28px;">Panui o te wiki!</strong></div>
<p style="text-align:center;"><br><strong><u>Sunday | 9 August 2026</u></strong><br>Kaihaka Kapa Haka - 2pm to 5pm</p>
<p style="text-align:center;"><strong><u>Friday | 14 August 2026</u></strong><br>Mahi Ngahere - 9am to 10am</p>
<p style="text-align:center;"><strong><u>Saturday | 15 August 2026</u></strong><br>Nga tae o Uenuku | Uenuku Rainbow Wānanga with Taini Drummond<br>10am to 12pm<br>Ō Wairoa Marae - Matariki Whare<br>Koha based — all proceeds to the marae</p>
""".strip()
    waiata_text = """
<div style="text-align:center;"><strong style="color:#85200E; font-size:18px;">Te Tuhi </strong><strong style="font-size:18px;">Lyrics</strong><br><br><strong>Mā te rāpa ka kitea</strong><br>Te Tuhi a Manawatere<br>Nō Ngāi Tai... te tupuna e<br>Te Waka... he huruhuru<br>Te Pōhutukawa ..i Wairoa<br>He tohu... he whaka-taukī<br>Mā te rāpa .. ka kitea x2</div>
""".strip()
    footer_text = """
<div style="text-align:center; font-size:12px;">No longer want to receive these emails? <a href="{% unsubscribe %}">Unsubscribe</a><br><a href="{% manage_preferences %}">Manage preferences</a><br>{{ organization.name }}<br>{{ organization.full_address }}</div>
""".strip()
    return {
        "body": {
            "properties": {},
            "styles": {"background_color": "#FBFAF7", "width": 600},
            "sections": [
                dnd_section([dnd_text_block("&nbsp;", align="center", color="#EFCE2B")], background="#EFCE2B"),
                dnd_section([dnd_text_block('<div style="text-align:right;"><span style="color:#85200E;"><strong>| Ō Wairoa Marae</strong></span> <strong>Whanau</strong></div>', align="right", size=24, weight="700")]),
                dnd_section([dnd_text_block("Kia ora, {{ person.first_name|default:'e hoa' }}.<br><br>Here is the pānui o te wiki for the coming week.", color="#403F3F")]),
                dnd_section([dnd_rule_block()]),
                dnd_section([dnd_text_block(event_text, align="center", size=18), dnd_button_block("Register for updates", register_url), dnd_button_block("Open the full calendar", calendar_url)]),
                dnd_section([dnd_image_block(poster_url, "Poster for Nga tae o Uenuku Rainbow Wānanga with Taini Drummond", register_url)]),
                dnd_section([dnd_rule_block(), dnd_text_block("As always - We look forward to seeing you soon.<br><br>Kia pai te ra! ☀️", color="#3E3D3D")]),
                dnd_section([dnd_text_block("Ō Wairoa Whānau", align="center", color="#FFFFFF")], background="#85200E"),
                dnd_section([dnd_text_block(waiata_text, align="center")], background="#FBFAF7"),
                dnd_section([dnd_text_block(footer_text, align="center", size=12, color="#3E3D3D")], background="#FBFAF7"),
            ],
        },
        "styles": [
            {"style_type": "base-styles", "properties": {"is_user_draggable": True, "mobile_optimizations": True}, "styles": {"background_color": "#FBFAF7"}},
            {"style_type": "text-styles", "styles": {"font_family": "Arial, Helvetica, sans-serif", "font_size": 16, "color": "#090303"}},
            {"style_type": "heading-1-styles", "styles": {"font_family": "Arial, Helvetica, sans-serif", "font_size": 28, "color": "#090303"}},
            {"style_type": "heading-2-styles", "styles": {"font_family": "Arial, Helvetica, sans-serif", "font_size": 24, "color": "#85200E"}},
            {"style_type": "heading-3-styles", "styles": {"font_family": "Arial, Helvetica, sans-serif", "font_size": 20, "color": "#090303"}},
            {"style_type": "heading-4-styles", "styles": {"font_family": "Arial, Helvetica, sans-serif", "font_size": 18, "color": "#090303"}},
            {"style_type": "link-styles", "styles": {"color": "#85200E", "font_weight": "700", "text_decoration": "underline"}},
            {"style_type": "mobile-styles", "properties": {}, "styles": {}},
        ],
    }


def first_message_id(campaign_id: str, api_key: str) -> str:
    payload = api_request("GET", f"/api/campaigns/{urllib.parse.quote(campaign_id)}/campaign-messages", api_key)
    messages = payload.get("data", [])
    if not messages:
        rel = api_request("GET", f"/api/campaigns/{urllib.parse.quote(campaign_id)}/relationships/campaign-messages", api_key)
        messages = rel.get("data", [])
    for message in messages:
        if message.get("id"):
            return message["id"]
    raise RuntimeError(f"No campaign message found for cloned campaign {campaign_id}")


def main() -> int:
    candidate_keys = [
        ("KLAVIYO_API_CREATE_KEY", os.environ.get("KLAVIYO_API_CREATE_KEY", "").strip()),
        ("KLAVIYO_API_KEY", os.environ.get("KLAVIYO_API_KEY", "").strip()),
    ]
    candidate_keys = [(name, key) for name, key in candidate_keys if key]
    if not candidate_keys:
        print("ERROR: KLAVIYO_API_CREATE_KEY/KLAVIYO_API_KEY is required", file=sys.stderr)
        return 2

    date_label = dt.datetime.now(TZ).strftime("%Y-%m-%d")
    draft_name = os.environ.get("KLAVIYO_DRAFT_CAMPAIGN_NAME", f"DRAFT ONLY - Ō Wairoa Whānau Pānui - Week of 9 Aug 2026 ({date_label})")
    subject = os.environ.get("KLAVIYO_DRAFT_SUBJECT", "Ō Wairoa Whānau Pānui | Week of 9 August")
    preview = os.environ.get("KLAVIYO_DRAFT_PREVIEW", "This week: kapa haka today, Mahi Ngahere, and the Uenuku Rainbow Wānanga on Saturday 15 August.")

    # Create and assign the HTML template before cloning/sending anything. This
    # verifies template permissions without changing any campaign state. Try both
    # configured secrets because older repo secrets may have different scopes.
    html_body = campaign_html()
    plain_body = text_content()
    required_merge_tokens = [
        "{{ person.first_name|default:'e hoa' }}",
        "{% unsubscribe %}",
        "{% manage_preferences %}",
        "{{ organization.name }}",
        "{{ organization.full_address }}",
    ]
    missing_tokens = [token for token in required_merge_tokens if token not in html_body and token not in plain_body]
    if missing_tokens:
        raise RuntimeError(f"Generated campaign content is missing merge fields: {missing_tokens}")

    template_editor_type = os.environ.get("KLAVIYO_TEMPLATE_EDITOR_TYPE", "SYSTEM_DRAGGABLE").strip().upper()
    if template_editor_type not in {"CODE", "USER_DRAGGABLE", "SYSTEM_DRAGGABLE"}:
        raise RuntimeError("KLAVIYO_TEMPLATE_EDITOR_TYPE must be CODE, USER_DRAGGABLE, or SYSTEM_DRAGGABLE")

    template_attributes: dict[str, Any] = {
        "name": f"{draft_name} template",
        "editor_type": template_editor_type,
        "text": plain_body,
    }
    if template_editor_type == "SYSTEM_DRAGGABLE":
        template_attributes["definition"] = campaign_definition()
    else:
        template_attributes["html"] = html_body

    template_payload = {"data": {"type": "template", "attributes": template_attributes}}
    template = None
    template_id = ""
    api_key = ""
    failures: list[str] = []
    for key_name, candidate_api_key in candidate_keys:
        try:
            template = api_request("POST", "/api/templates", candidate_api_key, template_payload, {"fields[template]": "id,name,editor_type"})
            template_id = template.get("data", {}).get("id", "")
            if template_id:
                api_key = candidate_api_key
                print(f"Using {key_name} for Klaviyo draft campaign creation.")
                break
            failures.append(f"{key_name}: template creation returned no id")
        except RuntimeError as exc:
            failures.append(f"{key_name}: {exc}")
    if not template_id or not api_key:
        raise RuntimeError("Could not create Klaviyo template with any configured key. " + " | ".join(failures))

    clone_payload = {"data": {"type": "campaign", "id": SOURCE_CAMPAIGN_ID, "attributes": {"new_name": draft_name}}}
    clone = api_request("POST", "/api/campaign-clone", api_key, clone_payload, {"fields[campaign]": "id,name,status,scheduled_at,send_time"})
    campaign = clone.get("data", {})
    campaign_id = campaign.get("id")
    if not campaign_id:
        raise RuntimeError(f"Campaign clone did not return an id: {clone}")

    message_id = first_message_id(campaign_id, api_key)
    update_payload = {
        "data": {
            "type": "campaign-message",
            "id": message_id,
            "attributes": {
                "definition": {
                    "channel": "email",
                    "label": "Main email",
                    "content": {"subject": subject, "preview_text": preview},
                }
            },
        }
    }
    api_request("PATCH", f"/api/campaign-messages/{urllib.parse.quote(message_id)}", api_key, update_payload)

    assign_payload = {
        "data": {
            "type": "campaign-message",
            "id": message_id,
            "relationships": {"template": {"data": {"type": "template", "id": template_id}}},
        }
    }
    api_request("POST", "/api/campaign-message-assign-template", api_key, assign_payload)

    verified = api_request(
        "GET",
        f"/api/campaigns/{urllib.parse.quote(campaign_id)}",
        api_key,
        query={"fields[campaign]": "id,name,status,scheduled_at,send_time"},
    ).get("data", {})
    attrs = verified.get("attributes", {})
    if str(attrs.get("status", "")).lower() not in {"draft", ""}:
        raise RuntimeError(f"Expected draft status, got: {attrs}")
    if attrs.get("scheduled_at") or attrs.get("send_time"):
        raise RuntimeError(f"Campaign appears scheduled/sent, got: {attrs}")

    summary = {
        "campaign_id": campaign_id,
        "campaign_name": attrs.get("name") or draft_name,
        "message_id": message_id,
        "template_id": template_id,
        "template_editor_type": template_editor_type,
        "status": attrs.get("status", "draft"),
        "scheduled_at": attrs.get("scheduled_at"),
        "send_time": attrs.get("send_time"),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if github_output := os.environ.get("GITHUB_OUTPUT"):
        with Path(github_output).open("a", encoding="utf-8") as fh:
            for key, value in summary.items():
                fh.write(f"{key}={value or ''}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
