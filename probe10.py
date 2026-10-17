# -*- coding: utf-8 -*-
"""Phase B3: 登录/初始化/user字段/成员工具函数"""
import re, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_probe")
js = open(os.path.join(OUT, "assets_index-B8MkvovF.js"), "r", encoding="utf-8", errors="replace").read()

def show(name, pattern, span=1400, n=1):
    print(f"\n########## {name} ##########")
    for i, m in enumerate(re.finditer(pattern, js)):
        if i >= n: break
        s = m.start()
        print(js[max(0, s-60):s+span].replace("\n", " "))
        print()

# 初始化 ga()
show("ga() 启动初始化", r'(?:async )?function ga\(\)\{')
# session 处理
show("W.session() 返回处理", r'\.authenticated', 900, 2)
# Yn 成员归一化
show("Yn() 成员归一化", r'function Yn\(')
# Yt 角色
show("Yt() 角色判断", r'function Yt\(')
# xt 头像
show("xt() 头像渲染", r'function xt\(')
# me ln mn hn
for fn in ["me", "ln", "mn", "hn", "Wg"]:
    m = re.search(r'function %s\([^)]*\)\{' % fn, js)
    if m:
        print(f"\n### {fn}:", js[m.start():m.start()+260].replace("\n"," "))
# Ct bitrate map
m = re.search(r'Ct\s*=\s*\{', js)
if m: print("\n### Ct:", js[m.start():m.start()+160])
