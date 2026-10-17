# -*- coding: utf-8 -*-
"""Phase A5: 分析应用代码段（UI模板/初始化/Fg定义），并拉取完整公开API数据"""
import re, os, json, urllib.request, urllib.error, ssl

BASE = "https://audio.vst666.cn"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_probe")
js = open(os.path.join(OUT, "assets_index-B8MkvovF.js"), "r", encoding="utf-8", errors="replace").read()

ctx = ssl.create_default_context()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0 Safari/537.36"
def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()

# Fg 定义
print("=== Fg (apiBase) definition ===")
for m in re.finditer(r'Fg\s*=', js):
    s=max(0,m.start()-100); print("  ", js[s:m.start()+150].replace("\n"," ")[:280])
# Qi csrf cookie
print("\n=== Qi cookie def ===")
for m in list(re.finditer(r'Qi\s*=', js))[:3]:
    s=max(0,m.start()-120); print("  ", js[s:m.start()+200].replace("\n"," ")[:330])

# 应用主体：定位 API 对象定义起点
idx = js.find('"/api/auth/login"')
print("\n=== API client module around", idx, "===")
print(js[idx-1500:idx+400])

# UI 模板: 找大段 html 字符串
print("\n\n=== Large HTML template literals ===")
for m in re.finditer(r'`<div[\s\S]{200,4000}?</div>`', js):
    print(f"--- tpl @ {m.start()} len={len(m.group(0))} ---")
    print(m.group(0)[:600])
    print("...")
