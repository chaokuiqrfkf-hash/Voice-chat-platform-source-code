# -*- coding: utf-8 -*-
"""认证/注册/建房/管理员操作的精确入参与返回处理"""
import re

js = open(r"c:\Users\Administrator\Pictures\11000\mirror\assets\index-Do8GJMrr.js",
          encoding="utf-8", errors="replace").read()

def block(name, pattern, span=1600, n=1):
    for k, m in enumerate(re.finditer(pattern, js)):
        if k >= n: break
        print(f"\n########## {name} @ {m.start()} ##########")
        print(js[m.start():m.start()+span])

block("登录提交 gv", r'async function gv\(', 1500)
block("发送注册码 iv", r'async function iv\(', 1800)
block("创建房间 vv", r'async function vv\(', 1200)
block("踢人 _v", r'async function _v\(', 800)
block("管理员设置", r'admins\(me\(', 500)
