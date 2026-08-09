#!/usr/bin/env python3
"""Summarise Klaviyo template content fields for debugging editor type/definition."""
from __future__ import annotations
import json, os, sys, time, urllib.error, urllib.parse, urllib.request
from typing import Any
API_BASE='https://a.klaviyo.com'; REVISION=os.environ.get('KLAVIYO_REVISION','2026-07-15')

def api_get(path, key, query=None):
    url=API_BASE+path
    if query: url += '?' + urllib.parse.urlencode(query, doseq=True)
    req=urllib.request.Request(url,headers={'Authorization':f'Klaviyo-API-Key {key}','Accept':'application/vnd.api+json','Revision':REVISION})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req,timeout=45) as r: return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            body=e.read().decode('utf-8','replace')
            if e.code in {429,500,502,503,504} and attempt<3: time.sleep(2**attempt); continue
            raise RuntimeError(f'{e.code}: {body}')

def walk(x: Any, path=''):
    if isinstance(x, dict):
        for k,v in x.items(): yield from walk(v, f'{path}.{k}' if path else k)
    elif isinstance(x, list):
        for i,v in enumerate(x): yield from walk(v, f'{path}[{i}]')
    elif isinstance(x, str):
        s=' '.join(x.split())
        if len(s) >= 15 and any(c.isalpha() for c in s):
            yield path, s[:260]

def main():
    key=(os.environ.get('KLAVIYO_API_CREATE_KEY') or os.environ.get('KLAVIYO_API_KEY') or '').strip()
    tid=os.environ.get('KLAVIYO_TEMPLATE_ID','').strip()
    if not key or not tid:
        print('missing key or KLAVIYO_TEMPLATE_ID', file=sys.stderr); return 2
    payload=api_get(f'/api/templates/{urllib.parse.quote(tid)}', key, {'additional-fields[template]':'definition','fields[template]':'id,name,editor_type,definition,html,text,updated,created'})
    data=payload.get('data',{}); attrs=data.get('attributes',{})
    print(json.dumps({'id':data.get('id'),'name':attrs.get('name'),'editor_type':attrs.get('editor_type'),'has_definition':bool(attrs.get('definition')),'has_html':bool(attrs.get('html')),'has_text':bool(attrs.get('text'))},ensure_ascii=False,indent=2))
    print('--- STRINGS ---')
    for path,s in list(walk(attrs.get('definition')))[:200]:
        print(f'{path}: {s}')
    return 0
if __name__=='__main__': raise SystemExit(main())
