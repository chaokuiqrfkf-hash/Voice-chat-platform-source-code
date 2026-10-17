# -*- coding: utf-8 -*-
"""Phase A3: 框架指纹 + 端点探测"""
import re, os, json, urllib.request, urllib.error, ssl

BASE = "https://audio.vst666.cn"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_probe")
js = open(os.path.join(OUT, "assets_index-B8MkvovF.js"), "r", encoding="utf-8", errors="replace").read()

ctx = ssl.create_default_context()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"

def fetch(url, method="GET", body=None, ctype=None):
    headers = {"User-Agent": UA, "Accept": "*/*"}
    if ctype:
        headers["Content-Type"] = ctype
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()
    except Exception as e:
        return -1, {}, str(e).encode()

print("=== UI framework fingerprints ===")
checks = {
    "Vue defineComponent": "defineComponent" in js,
    "Vue createApp vnode": "createVNode" in js or "__v_isVNode" in js,
    "Vue ref/reactive": bool(re.search(r'\bref\b', js) and "reactive" in js),
    "React createElement": "createElement" in js,
    "React jsxRuntime": "jsxRuntime" in js or "react/jsx" in js,
    "Preact": "preact" in js.lower(),
    "Solid": "solid-js" in js.lower(),
    "Svelte": "svelte" in js.lower(),
    "Lit / customElements": "customElements.define" in js,
    "Alpine": "alpinejs" in js.lower() or "x-data" in js,
    "htm template": " htm" in js,
    "morphdom": "morphdom" in js.lower(),
    "jQuery": "jQuery" in js or "jquery" in js.lower(),
    "location.hash routing": "location.hash" in js,
    "pushState routing": "pushState" in js,
    "hashchange": "hashchange" in js,
    "popstate": "popstate" in js,
    "SignalR client": "signalr" in js.lower() or "HubConnection" in js,
    "livekit-client": "livekit" in js.lower(),
    "trtc-sdk": "trtc" in js.lower(),
    "engine.io/socket.io": "engine.io" in js or "socket.io" in js,
    "tailwind": "tailwind" in js.lower(),
    "howler/audio": "Howl" in js or "howler" in js.lower(),
}
for k, v in checks.items():
    print(f"  {k}: {v}")

# innerHTML 模板特征 & 大量 html 字符串
print("\n  innerHTML assignments:", len(re.findall(r'\.innerHTML\s*=', js)))
print("  querySelector count:", len(re.findall(r'querySelector', js)))
print("  addEventListener count:", len(re.findall(r'addEventListener', js)))
print("  fetch( count:", len(re.findall(r'fetch\(', js)))
print("  new WebSocket:", len(re.findall(r'new WebSocket', js)))
print("  signalR HttpHubConnection/HubConnectionBuilder:", len(re.findall(r'HubConnectionBuilder', js)))

# livekit / trtc 版本号
print("\n=== SDK version hints ===")
for m in set(re.findall(r'(livekit[a-z-]*|trtc[a-z-]*|signalr[a-z.-]*)["\'\s:]{1,4}["\']?([0-9]+\.[0-9]+\.[0-9]+)', js, re.I)):
    print("  ", m)
for m in set(re.findall(r'version["\']?\s*[:=]\s*["\']([0-9]+\.[0-9]+\.[0-9]+[^"\']{0,12})', js)):
    print("  version:", m)

print("\n=== fetch/ws call sites (context) ===")
for m in re.finditer(r'fetch\(', js):
    s = max(0, m.start()-120); print("  ...", js[s:m.start()+80].replace("\n", " ")[:230]); print()
for m in list(re.finditer(r'WebSocket|HubConnectionBuilder|livekit|LiveKit', js))[:8]:
    s = max(0, m.start()-100); print("  *", js[s:m.start()+120].replace("\n", " ")[:250]); print()

print("=== Endpoint probing ===")
paths = ["/robots.txt", "/sitemap.xml", "/favicon.ico", "/manifest.json",
         "/asset-manifest.json", "/vite.svg", "/.well-known/security.txt",
         "/api/rooms", "/api/room-types", "/api/auth/session", "/api/me",
         "/api/admin/overview", "/rooms", "/login", "/admin",
         "/assets/", "/index.html", "/api/"]
for p in paths:
    st, h, data = fetch(BASE + p)
    ct = h.get("Content-Type", "")
    preview = data[:150].decode("utf-8", "replace").replace("\n", " ") if isinstance(data, bytes) else str(data)[:150]
    print(f"  {p:35s} -> {st:>4} {ct[:35]:35s} len={len(data) if isinstance(data,bytes) else '-':>7}  {preview[:120]}")

# OPTIONS / CORS check
print("\n=== API response detail: /api/rooms ===")
st, h, data = fetch(BASE + "/api/rooms")
print("status:", st)
for k, v in h.items():
    print(f"  {k}: {v}")
print("body:", data[:600].decode("utf-8", "replace"))
