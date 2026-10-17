# -*- coding: utf-8 -*-
import re
css = open(r"c:\Users\Administrator\Pictures\11000\mirror\assets\index-D0huGlAk.css",
           encoding="utf-8", errors="replace").read()
js = open(r"c:\Users\Administrator\Pictures\11000\mirror\assets\index-Do8GJMrr.js",
          encoding="utf-8", errors="replace").read()

i = css.find(".empty{")
print("=== .empty 规则原始上下文 (前260字符, 确认是否裸类选择器) ===")
print(css[max(0, i-260):i+230])

print("\n=== JS 模板中所有 class 含 empty 词的用法 ===")
for m in sorted(set(re.findall(r'class=\\?"([^"\\]*\\bempty\\b[^"\\]*)\\?"', js))):
    print("  ", m)

print("\n=== 线上 CSS 与本地一致性核对（大小/哈希文件名） ===")
import os
p = r"c:\Users\Administrator\Pictures\11000\mirror\assets\index-D0huGlAk.css"
print("  本地:", os.path.getsize(p), "字节, 文件:", os.path.basename(p))

# seat.empty 特异性 vs .empty：列出两条规则对 grid-column 的声明情况
print("\n=== 命中空麦位(button.seat.empty) 的所有规则及 grid-column 声明 ===")
for sel, body in re.findall(r'([^{}]+)\{([^{}]*)\}', css):
    s = sel.strip()
    if re.fullmatch(r'\.empty', s) or s == '.seat.empty':
        print(f"  {s}  (特异性 {s.count('.')} 个类)")
        print("    grid-column:", (re.search(r'grid-column\s*:\s*([^;]+)', b) or [None, "<未声明>"])[1]
              if (b := body) else "")
        print("    原文:", body.strip()[:200])
