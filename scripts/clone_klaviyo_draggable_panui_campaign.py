#!/usr/bin/env python3
"""Clone a Klaviyo campaign while preserving its drag-and-drop template.

This intentionally does not create/assign a CODE template. It keeps the cloned
campaign's existing template relationship so Kate can edit the email with the
Klaviyo drag-and-drop editor.
"""
from __future__ import annotations
import json, os, sys, time, urllib.error, urllib.parse, urllib.request
from typing import Any
from create_klaviyo_draft_panui_campaign import campaign_html as build_campaign_html, text_content as build_text_content
API_BASE='https://a.klaviyo.com'; REVISION=os.environ.get('KLAVIYO_REVISION','2026-07-15')
SOURCE_CAMPAIGN_ID=os.environ.get('KLAVIYO_SOURCE_CAMPAIGN_ID','01KXQCZH1HKNGGMF7KFFK86PA1')

def api_request(method: str, path: str, key: str, payload: dict[str, Any] | None=None, query: dict[str,str] | None=None) -> dict[str,Any]:
    url = path if path.startswith('http') else API_BASE + path
    if query: url += '?' + urllib.parse.urlencode(query, doseq=True)
    body = None if payload is None else json.dumps(payload).encode()
    req=urllib.request.Request(url,data=body,method=method,headers={'Authorization':f'Klaviyo-API-Key {key}','Accept':'application/vnd.api+json','Content-Type':'application/vnd.api+json','Revision':REVISION,'User-Agent':'OwairoaWhanauDraggableDraft/1.0'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req,timeout=45) as r:
                raw=r.read().decode(); return json.loads(raw) if raw.strip() else {}
        except urllib.error.HTTPError as e:
            err=e.read().decode('utf-8','replace')
            if e.code in {429,500,502,503,504} and attempt<3: time.sleep(2**attempt); continue
            raise RuntimeError(f'Klaviyo API {method} {url} failed {e.code}: {err}') from e
    raise RuntimeError(f'Klaviyo API {method} {url} failed after retries')

def first_message_and_template(campaign_id: str, key: str) -> dict[str, Any]:
    payload=api_request('GET', f'/api/campaigns/{urllib.parse.quote(campaign_id)}/campaign-messages', key, query={'include':'template','fields[campaign-message]':'id,definition','fields[template]':'id,name,editor_type,updated,created'})
    templates={i.get('id'): i for i in payload.get('included',[]) if i.get('type')=='template'}
    for msg in payload.get('data',[]):
        rel=(((msg.get('relationships') or {}).get('template') or {}).get('data') or {})
        tid=rel.get('id') or ''
        tmpl=templates.get(tid,{})
        attrs=tmpl.get('attributes') or {}
        definition=(msg.get('attributes') or {}).get('definition') or {}
        content=definition.get('content') or {}
        return {'message_id':msg.get('id'),'template_id':tid,'template_name':attrs.get('name'),'template_editor_type':attrs.get('editor_type'),'subject':content.get('subject')}
    raise RuntimeError(f'No messages found for campaign {campaign_id}')

def key_candidates():
    return [(n,k) for n,k in [('KLAVIYO_API_CREATE_KEY',os.environ.get('KLAVIYO_API_CREATE_KEY','').strip()),('KLAVIYO_API_KEY',os.environ.get('KLAVIYO_API_KEY','').strip())] if k]

def main() -> int:
    keys=key_candidates()
    if not keys:
        print('ERROR: Klaviyo key required', file=sys.stderr); return 2
    campaign_name=os.environ.get('KLAVIYO_DRAFT_CAMPAIGN_NAME','DRAFT ONLY - Ō Wairoa Whānau Pānui - Week of 17 Aug 2026 - draggable')
    subject=os.environ.get('KLAVIYO_DRAFT_SUBJECT','Ō Wairoa Whānau Pānui | Week of 17 August')
    preview=os.environ.get('KLAVIYO_DRAFT_PREVIEW','This week: Waiata Wednesday moves to Tuesday for the Howick Intermediate School Hui, plus Whakatika Te Reo, Mahi Ngahere, and Kaihaka Kapa Haka.')
    failures=[]
    for key_name,key in keys:
        try:
            clone_payload={'data':{'type':'campaign','id':SOURCE_CAMPAIGN_ID,'attributes':{'new_name':campaign_name}}}
            clone=api_request('POST','/api/campaign-clone',key,clone_payload,{'fields[campaign]':'id,name,status,scheduled_at,send_time'})
            campaign_id=clone.get('data',{}).get('id')
            if not campaign_id: raise RuntimeError(f'clone returned no campaign id: {clone}')
            info=first_message_and_template(campaign_id,key)
            editor=(info.get('template_editor_type') or '').upper()
            if editor == 'CODE':
                raise RuntimeError(f'cloned campaign unexpectedly uses CODE template {info}')
            msg_id=info['message_id']
            html_body = build_campaign_html()
            plain_body = build_text_content()
            required_tokens = ["{{ person.first_name|default:'e hoa' }}", "{% unsubscribe %}", "{% manage_preferences %}", "{{ organization.name }}", "{{ organization.full_address }}"]
            missing = [token for token in required_tokens if token not in html_body and token not in plain_body]
            if missing:
                raise RuntimeError(f'Generated campaign content is missing merge fields: {missing}')
            forbidden_customer_words = ['draft only', 'this campaign is draft', 'not scheduled', 'review/edit before sending']
            lower_content = (html_body + '\n' + plain_body).lower()
            leaked = [word for word in forbidden_customer_words if word in lower_content]
            if leaked:
                raise RuntimeError(f'Generated customer-facing content contains draft/scheduling wording: {leaked}')
            update_payload={'data':{'type':'campaign-message','id':msg_id,'attributes':{'definition':{'channel':'email','label':'Main email','content':{'subject':subject,'preview_text':preview,'body':html_body}}}}}
            api_request('PATCH', f'/api/campaign-messages/{urllib.parse.quote(str(msg_id))}', key, update_payload)
            verified=api_request('GET', f'/api/campaigns/{urllib.parse.quote(campaign_id)}', key, query={'fields[campaign]':'id,name,status,scheduled_at,send_time'}).get('data',{})
            attrs=verified.get('attributes') or {}
            if str(attrs.get('status','')).lower() not in {'draft',''}:
                raise RuntimeError(f'Expected draft status, got {attrs}')
            if attrs.get('scheduled_at') or attrs.get('send_time'):
                raise RuntimeError(f'Campaign appears scheduled/sent: {attrs}')
            info=first_message_and_template(campaign_id,key)
            summary={'campaign_id':campaign_id,'campaign_name':attrs.get('name') or campaign_name,'message_id':info.get('message_id'),'template_id':info.get('template_id'),'template_name':info.get('template_name'),'template_editor_type':info.get('template_editor_type'),'status':attrs.get('status'),'scheduled_at':attrs.get('scheduled_at'),'send_time':attrs.get('send_time'),'api_key_used':key_name}
            print(json.dumps(summary,ensure_ascii=False,indent=2))
            if out:=os.environ.get('GITHUB_OUTPUT'):
                with open(out,'a',encoding='utf-8') as fh:
                    for k,v in summary.items(): fh.write(f'{k}={v or ""}\n')
            return 0
        except RuntimeError as e:
            failures.append(f'{key_name}: {e}')
    raise RuntimeError('Could not create draggable draft. ' + ' | '.join(failures))
if __name__=='__main__': raise SystemExit(main())
