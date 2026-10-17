# -*- coding: utf-8 -*-
"""提取规范化函数 un(用户)/jg(房间列表)/me(房间标识)/Yg speakers 渲染字段 + 个人模板关键字段"""
import re
js = open(r"c:\Users\Administrator\Pictures\11000\mirror\assets\index-Do8GJMrr.js",
          encoding="utf-8", errors="replace").read()

m = re.search(r'function un\(i\)\{', js)
print("########## un() 用户规范化 ##########")
print(js[m.start():m.start()+1100])

m = re.search(r'function jg\(', js)
print("\n########## jg() 房间列表规范化 ##########")
print(js[m.start():m.start()+1500])

m = re.search(r'function me\(', js)
print("\n########## me() 房间标识 ##########")
print(js[m.start():m.start()+300])

# 个人页表单字段
i = js.find('class="profile-form"')
print("\n########## 个人表单 ##########")
print(js[i-100:i+900])
