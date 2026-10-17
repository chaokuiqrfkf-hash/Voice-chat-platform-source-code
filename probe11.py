# -*- coding: utf-8 -*-
"""Phase B4: 箭头函数形式的归一化工具"""
import re, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_probe")
js = open(os.path.join(OUT, "assets_index-B8MkvovF.js"), "r", encoding="utf-8", errors="replace").read()

for fn in ["Yn", "Yt", "xt", "un", "qg", "me", "ln", "Wg", "gr"]:
    m = re.search(r'(?:const|let|var|function)\s+' + fn + r'\s*=?\s*[\(=]', js)
    if not m:
        m = re.search(r'\b' + fn + r'=\(', js)
    if m:
        seg = js[m.start():m.start()+420].replace("\n", " ")
        print(f"### {fn} @{m.start()}: {seg}\n")
    else:
        print(f"### {fn}: NOT FOUND\n")
