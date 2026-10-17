# -*- coding: utf-8 -*-
"""反推管理端：入口判定/加载函数 dt/各tab字段/邮件配置/用户操作入参"""
import re

js = open(r"c:\Users\Administrator\Pictures\11000\mirror\assets\index-Do8GJMrr.js",
          encoding="utf-8", errors="replace").read()

def block(name, pattern, span=1500):
    m = re.search(pattern, js)
    print(f"\n########## {name} @ {m.start() if m else None} ##########")
    if m:
        print(js[m.start():m.start()+span])

# 管理入口判定 (data-page admin / isAdmin)
for kw in ['"admin"', "isAdmin", "adminForbidden"]:
    hits = [m.start() for m in re.finditer(re.escape(kw), js)]
    print(f"=== {kw}: {len(hits)} hits {hits[:6]}")
    for p in hits[:3]:
        print("   ", js[max(0,p-120):p+160].replace("\n"," ")[:300])
    print()

# admin 数据加载函数 dt
block("admin loader dt()", r'async function dt\(\)', 1800)
