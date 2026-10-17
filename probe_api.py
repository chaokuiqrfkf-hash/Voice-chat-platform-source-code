# -*- coding: utf-8 -*-
"""精确反推新 bundle 的全部 API 调用点: W 对象方法定义 + 调用处入参/返回使用"""
import re

js = open(r"c:\Users\Administrator\Pictures\11000\mirror\assets\index-Do8GJMrr.js",
          encoding="utf-8", errors="replace").read()

# 1) W(API对象) 完整定义: 从 const W={ 到匹配结束
i = js.find('session:()=>H("/api/auth/session")')
start = js.rfind("const W=", 0, i)
if start < 0:
    start = js.rfind("W={", 0, i)
seg = js[start:start+3200]
print("=== API 对象定义 ===")
print(seg[:3200])
