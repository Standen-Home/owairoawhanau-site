#!/usr/bin/env python3
"""Create an unscheduled Klaviyo correction campaign for Kaihaka Kapa Haka."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import create_klaviyo_draft_panui_campaign as base

SITE_URL = base.SITE_URL
ORIGINAL_STYLES = base.campaign_definition()["styles"]


def correction_text() -> str:
    return """Kia ora {{ person.first_name|default:'e hoa' }},

Correction to this week’s pānui:

Kaihaka Kapa Haka is on today, Sunday 18 October 2026, at 3.00pm.

Please disregard the previous date of Sunday 25 October.

We apologise for the incorrect date and look forward to seeing you this afternoon.

No longer want to receive these emails? {% unsubscribe %}
Manage preferences: {% manage_preferences %}
{{ organization.name }}
{{ organization.full_address }}
""".strip()


def correction_html() -> str:
    return """<!doctype html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body style="margin:0;background:#FBFAF7;font-family:Arial,Helvetica,sans-serif;color:#090303;">
<div style="display:none;max-height:0;overflow:hidden;">Correction: Kaihaka Kapa Haka is on today at 3.00pm.</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#FBFAF7;"><tr><td align="center" style="padding:10px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;background:#FFFFFF;">
<tr><td style="background:#EFCE2B;padding:32px 20px 8px;">&nbsp;</td></tr>
<tr><td style="text-align:right;font-size:24px;padding:9px 18px;"><strong style="color:#85200E;">| Ō Wairoa Marae</strong> <strong>Whanau</strong></td></tr>
<tr><td style="padding:18px;font-size:16px;line-height:1.4;">Kia ora, {{ person.first_name|default:'e hoa' }}.</td></tr>
<tr><td style="padding:18px;text-align:center;border-top:1px solid #CCCCCC;">
<h1 style="font-size:28px;margin:0 0 22px;">Correction to this week’s pānui</h1>
<p style="font-size:18px;"><strong><u>Today | Sunday 18 October 2026</u></strong></p>
<p style="font-size:24px;color:#85200E;"><strong>Kaihaka Kapa Haka — 3.00pm</strong></p>
<p style="font-size:16px;">Please disregard the previous date of Sunday 25 October.</p>
<p style="font-size:16px;">We apologise for the incorrect date and look forward to seeing you this afternoon.</p>
</td></tr>
<tr><td style="padding:18px;border-top:1px solid #CCCCCC;font-size:16px;line-height:1.4;">Kia pai te rā! ☀️</td></tr>
<tr><td style="background:#85200E;color:#FFFFFF;text-align:center;padding:12px;">Ō Wairoa Whānau</td></tr>
<tr><td style="background:#FBFAF7;text-align:center;padding:12px 18px;font-size:12px;">
No longer want to receive these emails? <a href="{% unsubscribe %}">Unsubscribe</a><br>
<a href="{% manage_preferences %}">Manage preferences</a><br>
{{ organization.name }}<br>{{ organization.full_address }}
</td></tr>
</table></td></tr></table>
</body></html>"""


def correction_definition() -> dict:
    event_text = """
<div style="text-align:center;"><strong style="font-size:28px;">Correction to this week’s pānui</strong></div>
<p style="text-align:center;"><br><strong><u>Today | Sunday 18 October 2026</u></strong></p>
<p style="text-align:center;color:#85200E;font-size:24px;"><strong>Kaihaka Kapa Haka — 3.00pm</strong></p>
<p style="text-align:center;font-size:16px;">Please disregard the previous date of Sunday 25 October.</p>
<p style="text-align:center;font-size:16px;">We apologise for the incorrect date and look forward to seeing you this afternoon.</p>
""".strip()
    footer_text = """
<div style="text-align:center;font-size:12px;">No longer want to receive these emails? <a href="{% unsubscribe %}">Unsubscribe</a><br><a href="{% manage_preferences %}">Manage preferences</a><br>{{ organization.name }}<br>{{ organization.full_address }}</div>
""".strip()
    return {
        "body": {
            "properties": {},
            "styles": {"background_color": "#FBFAF7", "width": 600},
            "sections": [
                base.dnd_section([base.dnd_text_block("&nbsp;", align="center", color="#EFCE2B")], background="#EFCE2B"),
                base.dnd_section([base.dnd_text_block('<div style="text-align:right;"><span style="color:#85200E;"><strong>| Ō Wairoa Marae</strong></span> <strong>Whanau</strong></div>', align="right", size=24, weight="700")]),
                base.dnd_section([base.dnd_text_block("Kia ora, {{ person.first_name|default:'e hoa' }}.", color="#403F3F")]),
                base.dnd_section([base.dnd_rule_block()]),
                base.dnd_section([base.dnd_text_block(event_text, align="center", size=18)]),
                base.dnd_section([base.dnd_rule_block(), base.dnd_text_block("Kia pai te rā! ☀️", color="#3E3D3D")]),
                base.dnd_section([base.dnd_text_block("Ō Wairoa Whānau", align="center", color="#FFFFFF")], background="#85200E"),
                base.dnd_section([base.dnd_text_block(footer_text, align="center", size=12, color="#3E3D3D")], background="#FBFAF7"),
            ],
        },
        "styles": ORIGINAL_STYLES,
    }


def main() -> int:
    base.text_content = correction_text
    base.campaign_html = correction_html
    base.campaign_definition = correction_definition
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
