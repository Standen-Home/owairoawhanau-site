#!/usr/bin/env python3
"""Create a Klaviyo draft pānui campaign for the coming week.

This is intentionally DRAFT ONLY: it clones an existing sent campaign, assigns a
fresh HTML template, and verifies the resulting campaign is not scheduled/sent.
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
    return """Kia ora e te whānau,

Draft pānui for the week of 9 August 2026.

This week:
• Today, Sunday 9 August, 2pm-5pm — Kaihaka Kapa Haka
• Friday 14 August, 9am-10am — Mahi Ngahere
• Saturday 15 August, 10am-12pm — Nga tae o Uenuku / Uenuku Rainbow Wānanga with Taini Drummond at Ō Wairoa Marae - Matariki Whare

The Uenuku wānanga is koha based, with all proceeds to the marae. Register for updates on the website.

This campaign is draft only and has not been scheduled.
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
  <div style="display:none;max-height:0;overflow:hidden;">Draft only — pānui o te wiki with this week’s events and Uenuku Rainbow Wānanga.</div>
  <div class="wrapper">
    <table role="presentation" class="container" align="center" width="100%" cellpadding="0" cellspacing="0">
      <tr><td style="background-color:#EFCE2B; padding:32px 20px 8px 20px;">&nbsp;</td></tr>
      <tr><td class="brand"><span class="brand-accent">| Ō Wairoa Marae</span> <strong>Whanau</strong></td></tr>
      <tr><td class="text" style="padding:9px 18px;">
        <p><span style="color:#403F3F;">Kia ora, e hoa.</span></p>
        <p><span style="color:#403F3F;">Here is the draft pānui o te wiki for the coming week. Please review/edit before sending — this campaign is draft only and has not been scheduled.</span></p>
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
    </table>
  </div>
</body>
</html>"""


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
    template_payload = {
        "data": {
            "type": "template",
            "attributes": {
                "name": f"{draft_name} template",
                "editor_type": "CODE",
                "html": campaign_html(),
                "text": text_content(),
            },
        }
    }
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
