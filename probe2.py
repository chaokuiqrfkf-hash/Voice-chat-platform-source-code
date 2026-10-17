# -*- coding: utf-8 -*-
"""Phase A2: 深度分析主JS"""
import re, os, json

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_probe")
js = open(os.path.join(OUT, "assets_index-B8MkvovF.js"), "r", encoding="utf-8", errors="replace").read()
css = open(os.path.join(OUT, "assets_index-69qJLQz0.css"), "r", encoding="utf-8", errors="replace").read()

print("=== JS head (1200 chars) ===")
print(js[:1200])

print("\n=== File extensions referenced ===")
for ext in ["js", "css", "png", "jpg", "jpeg", "svg", "webp", "gif", "ico",
            "woff", "woff2", "ttf", "mp3", "wav", "m4a", "mp4", "json", "wasm"]:
    matches = re.findall(r'["\'`]([^"\'`]{0,80}?\.' + ext + r'(?:\?[^"\'`]*)?)["\'`]', js)
    matches = [m for m in matches if not m.startswith("data:")]
    if matches:
        uniq = sorted(set(matches))
        print(f"\n.{ext} ({len(uniq)} uniq):")
        for m in uniq[:40]:
            print("   ", m)

print("\n=== import/export statements (first 20) ===")
for m in re.findall(r'(?:import|export)[^;]{0,200}', js)[:20]:
    print("  ", m[:200])

print("\n=== WebSocket / ws URLs ===")
for m in sorted(set(re.findall(r'(wss?://[^"\'`\s)]+|["\'`]/ws[^"\'`]*["\'`])', js))):
    print("  ", m)
# socket.io / signalr / peer
for kw in ["socket.io", "SignalR", "PeerConnection", "webrtc", "mediasoup", "livekit", "agora", "trtc"]:
    if kw.lower() in js.lower():
        print("  FOUND keyword:", kw)

print("\n=== API base config ===")
for pat in [r'baseURL[^,;}]{0,120}', r'BASE_URL[^,;}]{0,120}', r'API_BASE[^,;}]{0,120}',
            r'VITE_[A-Z_]+', r'axios\.create\([^)]{0,200}']:
    for m in re.findall(pat, js)[:10]:
        print("  ", m[:200])

print("\n=== Router hints ===")
for kw in ["createWebHistory", "createWebHashHistory", "createRouter", "vue-router", "react-router", "history.pushState", "#/"]:
    idx = js.find(kw)
    print(f"  {kw}: {'@'+str(idx) if idx>=0 else 'not found'}")

print("\n=== Framework version strings ===")
for m in set(re.findall(r'(vue|react|svelte|solid|preact|@vue/[a-z-]+|pinia|element-plus|naive-ui|ant-design-vue|vant|tailwindcss)[/@][0-9.]+', js, re.I)):
    print("  ", m)

print("\n=== title / app name ===")
for m in set(re.findall(r'声趣[^"\'`]{0,30}', js)):
    print("  ", m)

print("\n=== CSS url() all ===")
for u in sorted(set(re.findall(r'url\((["\']?)([^)\'"]+)\1\)', css))):
    print("  ", u[1])

print("\n=== CSS @font-face / @import ===")
for m in re.findall(r'@(?:font-face|import)[^;]{0,300}', css)[:10]:
    print("  ", m[:300])

# 找路由表: 常见压缩后 path:"/xx" 前面可能是 component: 或 redirect
print("\n=== path-like strings ===")
paths = sorted(set(re.findall(r'["\'`](/(?:admin|room|auth|login|register|me|user|profile|index|home)?[A-Za-z0-9_/-]{1,40})["\'`]', js)))
for p in paths[:80]:
    print("  ", p)
