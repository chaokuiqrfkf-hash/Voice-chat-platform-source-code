# -*- coding: utf-8 -*-
"""Phase A4: 完整API清单 / 媒体URL / SDK确认 / 页面初始化调用"""
import re, os, json

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_probe")
js = open(os.path.join(OUT, "assets_index-B8MkvovF.js"), "r", encoding="utf-8", errors="replace").read()

print("=== ALL /api/ strings ===")
api_strs = sorted(set(re.findall(r'["\'`](/api/[A-Za-z0-9_./\-${}()]+)["\'`]', js)))
for a in api_strs:
    print("  ", a)

print("\n=== template-literal API calls: `${...}...` ===")
for m in sorted(set(re.findall(r'`\$\{[A-Za-z0-9_.]+\}(/api/[^`]+)`', js))):
    print("  ", m)
for m in sorted(set(re.findall(r'`(/api/[^`]*)`', js))):
    print("  ", m)

print("\n=== /api/media references ===")
for m in sorted(set(re.findall(r'["\'`](/api/media/[A-Za-z0-9_./\-]+)["\'`]', js))):
    print("  ", m)
for m in re.finditer(r'/api/media', js):
    s = max(0, m.start()-150); print("   CTX:", js[s:m.start()+120].replace("\n"," ")[:300])

print("\n=== trtc / SignalR real? ===")
for kw in ["trtc", "TRTC", "SignalR", "signalr", "SignalRClient", "qcloud", "tencentcloud"]:
    hits = [m.start() for m in re.finditer(re.escape(kw), js)]
    print(f"  {kw}: {len(hits)} hits", hits[:5])
    for pos in hits[:2]:
        print("     CTX:", js[max(0,pos-80):pos+100].replace("\n"," ")[:200])

print("\n=== livekit room connect config ===")
for kw in ["wss://", "ws://", "/rtc", "/signal", "rtc.", "livekit"]:
    hits = [m.start() for m in re.finditer(re.escape(kw), js)]
    if hits:
        print(f"  {kw}: {len(hits)} hits")
        for pos in hits[:3]:
            print("     CTX:", js[max(0,pos-100):pos+130].replace("\n"," ")[:260])

print("\n=== app init / bootstrap hints ===")
for kw in ["DOMContentLoaded", "boot", "init()", "App(", "render(", "mount(", "/api/rooms"]:
    hits = [m.start() for m in re.finditer(re.escape(kw), js)]
    if hits:
        print(f"  {kw}: {len(hits)} hits @ {hits[:4]}")
        for pos in hits[:2]:
            print("     CTX:", js[max(0,pos-120):pos+160].replace("\n"," ")[:300])

print("\n=== views/screens names (Chinese UI strings around show/hide) ===")
views = sorted(set(re.findall(r'data-view=["\']([^"\']+)["\']', js)))
print("  data-view:", views)
ids = sorted(set(re.findall(r'id=["\'](view-[A-Za-z0-9_-]+|page-[A-Za-z0-9_-]+|screen-[A-Za-z0-9_-]+)["\']', js)))
print("  view/page ids:", ids[:50])
# 所有 id= 引用
allids = sorted(set(re.findall(r'getElementById\(["\']([^"\']+)["\']', js)))
print("\n  getElementById ids (%d):" % len(allids))
for i in allids:
    print("   -", i)
