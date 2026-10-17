# -*- coding: utf-8 -*-
"""Phase B1: 房间页数据流反推 - 进房流程/依赖接口/数据结构"""
import re, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_probe")
js = open(os.path.join(OUT, "assets_index-B8MkvovF.js"), "r", encoding="utf-8", errors="replace").read()

def ctx(kw, before=80, after=600, n=3, label=None):
    print(f"\n########## {label or kw} ##########")
    for i, m in enumerate(re.finditer(re.escape(kw), js)):
        if i >= n: break
        s = m.start()
        print(f"--- @{s} ---")
        print(js[max(0, s-before):s+after].replace("\n", " "))
        print()

# 1) 进房动作处理
ctx("joinRoom", 400, 900, 2, "joinRoom 调用点")
# 2) room 页面初始化 hv
ctx("hv()", 100, 200, 3, "hv 定义/调用")
# 3) voice token
ctx("voiceToken", 300, 700, 2, "voiceToken 调用点")
