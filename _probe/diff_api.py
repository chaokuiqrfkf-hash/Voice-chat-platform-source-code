# -*- coding: utf-8 -*-
"""比对新旧 bundle 的 API 路由集合与 admin 相关代码段"""
import glob
import re

old_js = open(sorted(glob.glob("frontend-backup-*/assets/index-CcyPlFAq.js"))[-1], encoding="utf-8").read()
new_js = open("frontend/assets/index-Nh60ZYT8.js", encoding="utf-8").read()

# 1. 全部 /api/ 路由字符串对比
pat = r'["\'](/api/[A-Za-z0-9_/:${}.\-]*)'
old_api = set(re.findall(pat, old_js))
new_api = set(re.findall(pat, new_js))
print("旧 bundle API 路由数:", len(old_api), " 新:", len(new_api))
print("新增:", sorted(new_api - old_api))
print("移除:", sorted(old_api - new_api))

# 2. admin 相关代码段对比
def admin_segments(js):
    segs = []
    for kw in ["isAdmin", "adminForbidden", "/api/admin/"]:
        for m in re.finditer(re.escape(kw), js):
            segs.append(js[max(0, m.start() - 80):m.start() + 200])
    return segs

oa, na = admin_segments(old_js), admin_segments(new_js)
print()
print("admin 关键词片段数 旧:", len(oa), " 新:", len(na), " 完全一致:", sorted(oa) == sorted(na))

# 3. fetch 封装/请求头处理方式对比 (credentials / CSRF)
for kw in ["X-CSRF", "csrfToken", "credentials"]:
    print(kw, "旧:", old_js.count(kw), " 新:", new_js.count(kw))
