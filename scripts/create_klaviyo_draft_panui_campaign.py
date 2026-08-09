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
    poster_url = f"{SITE_URL}/assets/images/events/uenuku-rainbow-wananga-2026.png"
    register_url = f"{SITE_URL}/uenuku-rainbow-wananga/register/"
    calendar_url = f"{SITE_URL}/calendar/"
    news_url = f"{SITE_URL}/news/"
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Ō Wairoa Whānau Pānui</title>
</head>
<body style="margin:0;background:#f5efe7;color:#25170f;font-family:Inter,Arial,sans-serif;">
  <div style="display:none;max-height:0;overflow:hidden;">Draft only — week ahead pānui including today and the Uenuku Rainbow Wānanga.</div>
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f5efe7;">
    <tr><td align="center" style="padding:24px 12px;">
      <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:640px;background:#fffaf3;border-radius:20px;overflow:hidden;border:1px solid #ead9c2;">
        <tr><td style="background:#5b2a16;color:#fff;padding:28px 30px;">
          <p style="margin:0 0 8px;font-size:13px;letter-spacing:.08em;text-transform:uppercase;">DRAFT ONLY — not scheduled</p>
          <h1 style="margin:0;font-size:30px;line-height:1.15;">Ō Wairoa Whānau Pānui</h1>
          <p style="margin:10px 0 0;font-size:17px;">Week of 9 August 2026</p>
        </td></tr>
        <tr><td style="padding:28px 30px;">
          <p style="font-size:17px;line-height:1.55;margin:0 0 18px;">Kia ora e te whānau, here is the draft week-ahead pānui, based on the last two pānui style: clear dates first, then the key kaupapa and links.</p>

          <h2 style="font-size:22px;margin:26px 0 12px;color:#5b2a16;">This week</h2>
          <ul style="padding-left:22px;font-size:16px;line-height:1.6;margin:0 0 22px;">
            <li><strong>Today, Sunday 9 August, 2pm-5pm:</strong> Kaihaka Kapa Haka</li>
            <li><strong>Friday 14 August, 9am-10am:</strong> Mahi Ngahere</li>
            <li><strong>Saturday 15 August, 10am-12pm:</strong> Nga tae o Uenuku / Uenuku Rainbow Wānanga with Taini Drummond</li>
          </ul>

          <div style="border:2px solid #7b5ac7;border-radius:18px;padding:20px;background:#f7f3ff;margin:24px 0;">
            <h2 style="font-size:24px;margin:0 0 10px;color:#25154d;">Nga tae o Uenuku — Uenuku Rainbow Wānanga</h2>
            <p style="font-size:16px;line-height:1.55;margin:0 0 14px;">Come together for a Uenuku Rainbow workshop, shared learning, whanaungatanga, and support for the whare.</p>
            <p style="font-size:16px;line-height:1.55;margin:0 0 14px;"><strong>When:</strong> Saturday 15 August, 10am - 12pm<br><strong>Where:</strong> Ō Wairoa Marae - Matariki Whare<br><strong>Koha:</strong> Koha based — all proceeds to the marae<br><strong>Enquiries:</strong> Taini 022 567 6059</p>
            <p style="margin:18px 0;"><a href="{register_url}" style="background:#5b2a16;color:#fff;text-decoration:none;border-radius:999px;padding:12px 18px;display:inline-block;font-weight:700;">Register for updates</a></p>
            <a href="{register_url}"><img src="{poster_url}" alt="Poster for Nga tae o Uenuku Uenuku Rainbow Wānanga with Taini Drummond" style="width:100%;max-width:520px;border-radius:14px;display:block;margin:10px auto 0;"></a>
          </div>

          <h2 style="font-size:22px;margin:26px 0 12px;color:#5b2a16;">Also from recent pānui</h2>
          <p style="font-size:16px;line-height:1.55;margin:0 0 12px;">The recent pānui centred Matariki, whānau connection, waiata/kapa haka, and practical event information. This draft keeps the same rhythm: what is happening, when to come, and where to click next.</p>
          <p style="margin:18px 0 0;"><a href="{calendar_url}" style="color:#85200e;font-weight:700;">Open the calendar</a> &nbsp;|&nbsp; <a href="{news_url}" style="color:#85200e;font-weight:700;">Read past pānui</a></p>
        </td></tr>
        <tr><td style="background:#efe2d1;padding:18px 30px;font-size:13px;line-height:1.5;color:#5b4638;">
          Draft campaign created for review only. Do not schedule/send until approved.
        </td></tr>
      </table>
    </td></tr>
  </table>
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
    api_key = (os.environ.get("KLAVIYO_API_CREATE_KEY") or os.environ.get("KLAVIYO_API_KEY") or "").strip()
    if not api_key:
        print("ERROR: KLAVIYO_API_CREATE_KEY/KLAVIYO_API_KEY is required", file=sys.stderr)
        return 2

    date_label = dt.datetime.now(TZ).strftime("%Y-%m-%d")
    draft_name = os.environ.get("KLAVIYO_DRAFT_CAMPAIGN_NAME", f"DRAFT ONLY - Ō Wairoa Whānau Pānui - Week of 9 Aug 2026 ({date_label})")
    subject = os.environ.get("KLAVIYO_DRAFT_SUBJECT", "Ō Wairoa Whānau Pānui | Week of 9 August")
    preview = os.environ.get("KLAVIYO_DRAFT_PREVIEW", "This week: kapa haka today, Mahi Ngahere, and the Uenuku Rainbow Wānanga on Saturday 15 August.")

    # Create and assign the HTML template before cloning/sending anything. This
    # verifies template permissions without changing any campaign state.
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
    template = api_request("POST", "/api/templates", api_key, template_payload, {"fields[template]": "id,name,editor_type"})
    template_id = template.get("data", {}).get("id")
    if not template_id:
        raise RuntimeError(f"Template creation did not return an id: {template}")

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

    verified = api_request("GET", f"/api/campaigns/{urllib.parse.quote(campaign_id)}", api_key, {"fields[campaign]": "id,name,status,scheduled_at,send_time"}).get("data", {})
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
