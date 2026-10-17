# -*- coding: utf-8 -*-
"""Phase A6: 探测各API公开性，提取全部媒体URL"""
import re, os, json, urllib.request, urllib.error, ssl

BASE = "https://audio.vst666.cn"
ctx = ssl.create_default_context()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0 Safari/537.36"
def fetch(url, method="GET"):
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()

st, h, rooms_raw = fetch(BASE + "/api/rooms")
rooms = json.loads(rooms_raw)
print("=== rooms list ===")
media = set()
for rm in rooms.get("rooms", []):
    print(f"  id={rm['id']:>3} no={rm.get('roomNo'):>3} name={rm['name'][:20]:20s} type={rm.get('category')} online={rm.get('onlineCount')} owner={rm.get('ownerName')}")
    if rm.get("ownerAvatar"):
        media.add(rm["ownerAvatar"])

st2, h2, rt_raw = fetch(BASE + "/api/room-types")
rtypes = json.loads(rt_raw)
print("\n=== room-types ===")
print(json.dumps(rtypes, ensure_ascii=False, indent=1))

print("\n=== captcha ===")
stc, hc, cap = fetch(BASE + "/api/auth/captcha")
print("status:", stc, hc.get("Content-Type"), "len:", len(cap))
print(cap[:400].decode("utf-8", "replace"))

print("\n=== room detail for each room ===")
for rm in rooms.get("rooms", []):
    rid = rm["id"]
    s, hh, d = fetch(f"{BASE}/api/rooms/{rid}")
    print(f"  room {rid}: {s} {hh.get('Content-Type')} len={len(d)}")
    if s == 200:
        try:
            jd = json.loads(d)
            # 递归找 avatar 字段
            txt = json.dumps(jd, ensure_ascii=False)
            for u in re.findall(r'/api/media/[A-Za-z0-9_./\-]+', txt):
                media.add(u)
            open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_probe", f"room_{rid}.json"), "w", encoding="utf-8").write(
                json.dumps(jd, ensure_ascii=False, indent=2))
            print("    keys:", list(jd.keys()) if isinstance(jd, dict) else type(jd))
        except Exception as ex:
            print("    parse error:", ex)

print("\n=== other endpoints status (unauthenticated) ===")
for p in ["/api/rooms/0/speakers", "/api/rooms/0/chat", "/api/rooms/0/heartbeat",
          "/api/rooms/0/join", "/api/rooms/0/voice-token", "/api/rooms/0/admins",
          "/api/me/avatar", "/api/admin/users", "/api/auth/verify-email?token=x"]:
    s, hh, d = fetch(BASE + p, "GET")
    print(f"  GET {p:38s} -> {s} {d[:100].decode('utf-8','replace')}")

print("\n=== all media URLs (%d) ===" % len(media))
for u in sorted(media):
    print("  ", u)

# 验证媒体可访问
print("\n=== media HEAD/GET check ===")
for u in sorted(media)[:30]:
    s, hh, d = fetch(BASE + u)
    print(f"  {u} -> {s} {hh.get('Content-Type')} {hh.get('Content-Length')} bytes")
