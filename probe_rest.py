# -*- coding: utf-8 -*-
"""补充契约: 房间类型表单Fv/个人页Zg/房间类型模板剩余/聊天设置/心跳等级"""
import re
js = open(r"c:\Users\Administrator\Pictures\11000\mirror\assets\index-Do8GJMrr.js",
          encoding="utf-8", errors="replace").read()

m = re.search(r'async function Fv\(', js)
print("########## Fv 房间类型保存 ##########")
print(js[m.start():m.start()+1400])

i = js.find("data-admin-room-type-new")
print("\n########## 房间类型模板尾部 (新增/编辑表单) ##########")
# 找到房间类型编辑表单模板
j = js.find('room-type-edit', i)
print(js[j-200:j+2200] if j>0 else js[i:i+2500])
