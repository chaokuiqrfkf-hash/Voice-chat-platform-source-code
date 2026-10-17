# -*- coding: utf-8 -*-
"""提取新 bundle 中房间页模板与麦位分组逻辑 (新版)"""
import re

js = open(r"c:\Users\Administrator\Pictures\11000\mirror\assets\index-Do8GJMrr.js",
          encoding="utf-8", errors="replace").read()

i = js.find('class="room-layout"')
# 向前找到模板函数起点 return`
start = js.rfind("return`", 0, i)
print("=== 房间模板 return` 起点 @", start, " room-layout @", i, "===")
seg = js[start:i]
print("[模板前导逻辑]")
print(seg[-1600:])
print("\n[模板 HTML 主体]")
print(js[i:i+3400])
