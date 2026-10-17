# -*- coding: utf-8 -*-
"""Phase B2: ct()房间刷新 + Jg()房间模板 + 字段结构反推"""
import re, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_probe")
js = open(os.path.join(OUT, "assets_index-B8MkvovF.js"), "r", encoding="utf-8", errors="replace").read()

# ct 函数定义 (房间数据同步)
m = re.search(r'(?:async )?function ct\([^)]*\)\{', js)
print("=== ct() 定义 @", m.start() if m else None, "===")
if m:
    print(js[m.start():m.start()+2200])

# Jg 房间模板完整
m2 = re.search(r'function Jg\(\)\{', js)
print("\n\n=== Jg() 房间模板 @", m2.start() if m2 else None, "===")
if m2:
    print(js[m2.start():m2.start()+5200])
