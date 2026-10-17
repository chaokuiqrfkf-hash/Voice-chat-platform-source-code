# -*- coding: utf-8 -*-
"""Phase A7: 彻查 dev 残留: @vite/client / 127.0.0.1 / 8088 / 跳转逻辑"""
import re, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_probe")
js = open(os.path.join(OUT, "assets_index-B8MkvovF.js"), "r", encoding="utf-8", errors="replace").read()
html = open(os.path.join(OUT, "index.html"), "r", encoding="utf-8", errors="replace").read()

for kw in ["@vite/client", "127.0.0.1", "localhost", ":8088", "8088",
           "location.href", "location.assign", "location.replace", "window.open",
           "import.meta", "DEV", "MODE", "VITE_"]:
    hits = [m.start() for m in re.finditer(re.escape(kw), js)]
    print(f"\n=== {kw}: {len(hits)} hits ===")
    for pos in hits[:6]:
        print("  @%d:" % pos, js[max(0, pos-160):pos+200].replace("\n", " ")[:400])

print("\n\n=== HTML @vite? ===", "@vite" in html)
# 注册成功后的跳转
print("\n=== register flow ===")
i = js.find("data-auth-register")
while i != -1 and i < len(js):
    seg = js[i:i+1200]
    if "register" in seg:
        print(seg[:1200]); break
    i = js.find("data-auth-register", i+1)

# 找 register 提交处理
for m in re.finditer(r'\.register\(|W\.register|auth/register', js):
    s=m.start(); print("\nREG CTX:", js[max(0,s-300):s+500].replace("\n"," ")[:800])
