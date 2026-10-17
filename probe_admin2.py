# -*- coding: utf-8 -*-
"""提取管理模板 sv() 与认证/个人/建房/管理员操作的字段"""
import re

js = open(r"c:\Users\Administrator\Pictures\11000\mirror\assets\index-Do8GJMrr.js",
          encoding="utf-8", errors="replace").read()

i = js.find("function sv(){")
print("########## 管理模板 sv() ##########")
print(js[i:i+6000])
