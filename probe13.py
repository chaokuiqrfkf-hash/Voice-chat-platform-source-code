# -*- coding: utf-8 -*-
"""提取房间页相关 CSS 规则作为设计规格基线"""
import re

css = open(r"c:\Users\Administrator\Pictures\11000\mirror\assets\index-D0huGlAk.css",
           encoding="utf-8", errors="replace").read()

# 去掉注释，按 } 切分规则
rules = re.findall(r'([^{}]+)\{([^{}]*)\}', css)
targets = [".room-layout", ".room-header", ".room-main", ".member-pane",
           ".stage", ".stage-cover", ".seat-grid", ".seat", ".seat.empty",
           ".seat-pager", ".chat-pane", ".chat-head", ".messages",
           ".room-controls", ".control", ".voice-unavailable",
           ".member-row", ".room-live"]

for sel, body in rules:
    sel_n = sel.strip()
    for t in targets:
        # 精确包含该选择器词
        if re.search(r'(^|[\s,>])' + re.escape(t) + r'([\s,>:]|$)', sel_n) or sel_n == t:
            print(f"{sel_n} {{ {body.strip()} }}")
            break
