# -*- coding: utf-8 -*-
"""Phase A: 侦察脚本 - 下载主资源并分析技术栈/资源引用/API/路由"""
import re, os, json, urllib.request, ssl

BASE = "https://audio.vst666.cn/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_probe")
os.makedirs(OUT, exist_ok=True)

ctx = ssl.create_default_context()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return r.status, dict(r.headers), r.read()

status, headers, html = fetch(BASE)
open(os.path.join(OUT, "index.html"), "wb").write(html)
print("HTML status:", status, "len:", len(html))
print("Server:", headers.get("Server"), "| Content-Type:", headers.get("Content-Type"))

html_text = html.decode("utf-8", "replace")
js_refs = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html_text)
css_refs = re.findall(r'<link[^>]+href=["\']([^"\']+)["\']', html_text)
print("JS refs:", js_refs)
print("CSS refs:", css_refs)

# 下载主 JS/CSS
import urllib.parse
def save_ref(ref):
    url = urllib.parse.urljoin(BASE, ref)
    s, h, data = fetch(url)
    name = ref.lstrip("./").lstrip("/").replace("/", "_")
    path = os.path.join(OUT, name)
    open(path, "wb").write(data)
    print(f"  saved {ref} -> {name} ({len(data)} bytes, {h.get('Content-Type')})")
    return data

print("\n=== Download main assets ===")
js_data = b""
for r in js_refs:
    js_data += save_ref(r)
css_data = b""
for r in css_refs:
    css_data += save_ref(r)

js = js_data.decode("utf-8", "replace")
css = css_data.decode("utf-8", "replace")

print("\n=== Tech fingerprints ===")
fps = {
    "Vue3 createApp": "createApp" in js,
    "Vue runtime": "__vue_" in js or "Vue" in js[:50000],
    "React": ("react" in js.lower() and "useState" in js),
    "Vue Router": "createRouter" in js,
    "Pinia": "defineStore" in js or "pinia" in js.lower(),
    "Vuex": "$store" in js,
    "Vite build": "__vite" in js or "import.meta" in js,
    "Element Plus": "el-" in js or "element-plus" in js.lower(),
    "Axios": "axios" in js.lower(),
    "WebSocket": "WebSocket" in js or "ws://" in js or "wss://" in js,
}
for k, v in fps.items():
    print(f"  {k}: {v}")

print("\n=== Asset references in JS (assets/...) ===")
js_assets = set(re.findall(r'["\'`]((?:\.?/)?assets/[A-Za-z0-9_.\-/]+?\.[A-Za-z0-9]+)["\'`]', js))
for a in sorted(js_assets):
    print(" ", a)
print("count:", len(js_assets))

print("\n=== Chunk dynamic imports ===")
chunks = set(re.findall(r'["\'`]([\w./-]+?-[A-Za-z0-9_]{8}\.js)["\'`]', js))
for c in sorted(chunks):
    print(" ", c)
print("count:", len(chunks))

print("\n=== url() in CSS ===")
css_urls = set(re.findall(r'url\(["\']?([^"\')]+)["\']?\)', css))
for u in sorted(css_urls):
    print(" ", u)

print("\n=== HTTP/API endpoints in JS ===")
urls = set(re.findall(r'https?://[A-Za-z0-9_.\-:/?#%&=~]+', js))
api_like = [u for u in urls if "w3.org" not in u]
for u in sorted(api_like)[:60]:
    print(" ", u)
print("total absolute urls:", len(urls))

paths = set(re.findall(r'["\'`](/api/[A-Za-z0-9_./\-]+)["\'`]', js))
print("\n/api/ paths:", sorted(paths))

print("\n=== Router paths ===")
routes = set(re.findall(r'path:\s*["\'](/[A-Za-z0-9_:./\-]*)["\']', js))
for r_ in sorted(routes):
    print(" ", r_)

# 保存扫描结果
result = {"js_assets": sorted(js_assets), "chunks": sorted(chunks),
          "css_urls": sorted(css_urls), "absolute_urls": sorted(urls),
          "api_paths": sorted(paths), "routes": sorted(routes), "fingerprints": fps}
open(os.path.join(OUT, "probe_result.json"), "w", encoding="utf-8").write(
    json.dumps(result, ensure_ascii=False, indent=2))
print("\nProbe result saved to _probe/probe_result.json")
