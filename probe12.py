# -*- coding: utf-8 -*-
import re
new = open(r'c:\Users\Administrator\Pictures\11000\mirror\assets\index-Do8GJMrr.js',
           encoding="utf-8", errors="replace").read()
for kw in ["serviceWorker", "document.location", "action=", "auth-form",
           "addEventListener(\"submit\"", "addEventListener('submit'", "submit"]:
    hits = [m.start() for m in re.finditer(re.escape(kw), new)]
    print(f"=== {kw}: {len(hits)} ===")
    for p in hits[:4]:
        print("  ", new[max(0, p-130):p+200].replace("\n", " ")[:360])
    print()
