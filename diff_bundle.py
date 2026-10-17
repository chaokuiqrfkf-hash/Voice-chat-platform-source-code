# -*- coding: utf-8 -*-
"""新旧 bundle 结构差异对比 (旧=备份目录, 新=mirror)"""
import re, os, glob, difflib

OLD = glob.glob(r"c:\Users\Administrator\Pictures\11000\mirror-backup-*\assets\index-*.js")
OLD_JS = sorted(OLD)[-1]
_css = glob.glob(os.path.join(os.path.dirname(OLD_JS), "index-*.css"))
OLD_CSS = sorted(_css)[-1]
NEW_JS = r"c:\Users\Administrator\Pictures\11000\mirror\assets\index-Do8GJMrr.js"
NEW_CSS = r"c:\Users\Administrator\Pictures\11000\mirror\assets\index-D0huGlAk.css"

old = open(OLD_JS, encoding="utf-8", errors="replace").read()
new = open(NEW_JS, encoding="utf-8", errors="replace").read()
print(f"旧 JS: {OLD_JS}  ({len(old)} B)")
print(f"新 JS: {NEW_JS}  ({len(new)} B)  差 {len(new)-len(old):+d} B")

# 1) API 路径差异
pa = lambda s: set(re.findall(r'["\'`](/api/[A-Za-z0-9_./\-${}()?=]+)["\'`]', s))
oa, na = pa(old), pa(new)
print("\n=== API 新增 ===");  [print("  +", x) for x in sorted(na - oa)]
print("=== API 移除 ===");  [print("  -", x) for x in sorted(oa - na)]
if oa == na:
    print("  (完全一致, %d 个端点)" % len(oa))

# 2) 关键技术指纹
for kw in ["livekit", "SignalRequest", "WebSocket", "RTC", "rum_common", "myalicdn",
           "sentry", "gtag", "beacon", "data-view", "createRoom"]:
    co, cn = old.count(kw), new.count(kw)
    flag = "  <<< 变化" if co != cn else ""
    print(f"指纹 {kw:14s} 旧={co:4d} 新={cn:4d}{flag}")

# 3) 中文 UI 文案差异
strs = lambda s: set(re.findall(r'[-￟][-￟　-〿＀-￯\w，。·…！？：；（）/+\-]{1,40}', s))
os_, ns_ = strs(old), strs(new)
added_cn = sorted(ns_ - os_)
removed_cn = sorted(os_ - ns_)
print(f"\n=== 中文文案新增 ({len(added_cn)}) ===")
for x in added_cn[:60]:
    print("  +", x)
print(f"=== 中文文案移除 ({len(removed_cn)}) ===")
for x in removed_cn[:60]:
    print("  -", x)

# 4) CSS 差异
oc = open(OLD_CSS, encoding="utf-8", errors="replace").read()
nc = open(NEW_CSS, encoding="utf-8", errors="replace").read()
print(f"\n旧 CSS {len(oc)} B / 新 CSS {len(nc)} B / 差 {len(nc)-len(oc):+d} B")

# 5) 用行级 diff 找出新 JS 改动的代码段 (按分号粗切, 找不同行)
old_lines = [x for x in old.split(";") if x.strip()]
new_lines = [x for x in new.split(";") if x.strip()]
sm = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
print("\n=== JS 代码块差异 (opcode 段) ===")
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        continue
    print(f"\n--- {tag} 旧[{i1}:{i2}] 新[{j1}:{j2}] ---")
    for x in old_lines[i1:min(i2, i1+3)]:
        print("  旧:", x[:220])
    for x in new_lines[j1:min(j2, j1+3)]:
        print("  新:", x[:220])
