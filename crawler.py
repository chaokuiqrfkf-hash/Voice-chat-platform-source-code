# -*- coding: utf-8 -*-
"""
声趣语音 (https://audio.vst666.cn/) 1:1 镜像爬虫
=================================================
站点形态: Vite 构建的单 bundle 原生 JS SPA + 同源 Express JSON API
公开资源: /  index.html
          /assets/index-*.js, /assets/index-*.css
          /api/rooms, /api/room-types, /api/auth/session, /api/auth/captcha
          /api/media/avatars/*.webp (URL 由 rooms 数据返回)
全部静态资源内联, 无外链字体/图片 (favicon 线上亦为 404)。

用法: python crawler.py [--out frontend]
产物: frontend/  (由 Go 后端 backend/ 同源托管 /)
"""
import argparse
import gzip
import io
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE_HOST = "audio.vst666.cn"
BASE = f"https://{BASE_HOST}/"
HERE = os.path.dirname(os.path.abspath(__file__))

_parser = argparse.ArgumentParser()
_parser.add_argument("--out", default=os.path.join(HERE, "frontend"),
                     help="镜像输出目录 (默认 frontend/)")
_args = _parser.parse_args()
MIRROR = _args.out
FIXTURES = os.path.join(MIRROR, "fixtures")
MEDIA_ROOT = os.path.join(MIRROR, "api", "media")  # 与 URL 路径一致, 便于静态映射

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
CTX = ssl.create_default_context()

manifest = {"base": BASE, "fetchedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "resources": []}


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def save_manifest():
    with open(os.path.join(MIRROR, "crawl_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def fetch(url, retries=3, timeout=30):
    """带重试的 GET; 自动处理 gzip。返回 (status, headers, bytes, final_url)。"""
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA,
                "Accept": "*/*",
                "Accept-Encoding": "gzip",
                "Accept-Language": "zh-CN,zh;q=0.9",
            })
            with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
                data = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    data = gzip.decompress(data)
                return r.status, {k: v for k, v in r.headers.items()}, data, r.url
        except urllib.error.HTTPError as e:
            data = e.read()
            if e.headers.get("Content-Encoding") == "gzip":
                try:
                    data = gzip.decompress(data)
                except OSError:
                    pass
            return e.code, {k: v for k, v in (e.headers or {}).items()}, data, url
        except Exception as e:  # 网络抖动重试
            last = e
            time.sleep(1 + attempt)
    raise RuntimeError(f"fetch failed {url}: {last}")


def local_path_for_url(url):
    """URL 路径 -> mirror 内本地相对路径 (目录索引 -> index.html)。"""
    p = urllib.parse.urlparse(url).path
    p = urllib.parse.unquote(p.lstrip("/"))
    if p == "" or p.endswith("/"):
        p = (p + "index.html") if p else "index.html"
    return p


def store(url, data, sub=None):
    rel = local_path_for_url(url) if sub is None else sub
    path = os.path.join(MIRROR, rel.replace("/", os.sep))
    ensure_dir(os.path.dirname(path))
    with open(path, "wb") as f:
        f.write(data)
    return rel


def record(url, status, headers, rel, note=""):
    manifest["resources"].append({
        "url": url, "status": status,
        "contentType": headers.get("Content-Type", ""),
        "contentLength": len(headers.get("Content-Encoding") and "" or "") and -1 or None,
        "bytes": os.path.getsize(os.path.join(MIRROR, rel.replace("/", os.sep))) if rel else None,
        "local": rel, "etag": headers.get("ETag"),
        "lastModified": headers.get("Last-Modified"), "note": note,
    })
    print(f"  [{status}] {url}  -> {rel}  ({(os.path.getsize(os.path.join(MIRROR, rel.replace('/', os.sep))) if rel else 0)} B)")


# ---------------------------------------------------------------- 1. 入口 HTML
def crawl_entry():
    """下载入口并返回 (同源资源URL列表, [(原URL,本地相对路径)] 跨域资源映射)。
    入口 HTML 中的跨域 <script>/<link> 下载到 vendor/ 并改写引用,
    保证镜像离线自洽 (如阿里云 RUM rum_common.js)。"""
    print("[1/6] 入口 HTML")
    status, headers, data, final = fetch(BASE)
    assert status == 200, f"入口异常: {status}"
    html = data.decode("utf-8")
    same_refs, vendor_map = [], []

    for m in re.finditer(r'((?:src|href)=)["\']([^"\']+)["\']', html):
        attr, raw = m.group(1), m.group(2)
        if raw.startswith(("data:", "blob:", "javascript:", "#", "mailto:")):
            continue
        u = urllib.parse.urljoin(final, raw)
        host = urllib.parse.urlparse(u).netloc
        if host == BASE_HOST:
            same_refs.append(u)
        elif attr == "src=" and urllib.parse.urlparse(u).path.endswith(".js"):
            # 跨域脚本 (监控/统计类): 本地化到 vendor/<host>/<file>
            pu = urllib.parse.urlparse(u)
            fname = os.path.basename(pu.path) or "remote.js"
            rel = f"vendor/{host}/{fname}"
            s2, h2, d2, f2 = fetch(u)
            if s2 == 200 and d2:
                path = os.path.join(MIRROR, rel.replace("/", os.sep))
                ensure_dir(os.path.dirname(path))
                with open(path, "wb") as f:
                    f.write(d2)
                record(u, s2, h2, rel, note="cross-origin script localized")
                vendor_map.append((raw, "./" + rel))
            else:
                print(f"  !! 跨域脚本下载失败 {u} -> {s2}")

    # 改写入口 HTML 中的跨域脚本地址
    for raw, local in vendor_map:
        html = html.replace(f'"{raw}"', f'"{local}"').replace(f"'{raw}'", f"'{local}'")

    # 清理旧 hash 资源 (构建产物每次部署 hash 全变)
    assets_dir = os.path.join(MIRROR, "assets")
    if os.path.isdir(assets_dir):
        import shutil
        shutil.rmtree(assets_dir, ignore_errors=True)
        print("  已清理旧 assets/ 目录")

    out = html.encode("utf-8")
    rel = store(final, out)
    record(final, status, headers, rel, note="入口已本地化重写" if vendor_map else "")
    return sorted(set(same_refs)), vendor_map


# ---------------------------------------------------------------- 2. 构建资源
def crawl_assets(refs):
    print("[2/6] 构建资源 (JS/CSS/图标)")
    saved = {}
    queue = list(refs)
    seen = set()
    while queue:
        u = queue.pop(0)
        if u in seen:
            continue
        seen.add(u)
        status, headers, data, final = fetch(u)
        if status != 200:
            print(f"  !! {u} -> {status}")
            continue
        rel = store(final, data)
        record(final, status, headers, rel)
        saved[urllib.parse.urlparse(final).path] = rel
        # 防御性二次扫描: bundle/CSS 内若引用额外 assets/ 资源也下载
        if rel.endswith((".js", ".css")):
            text = data.decode("utf-8", "replace")
            for m in re.findall(r'["\'`](\.?/)?(assets/[A-Za-z0-9_.\-/]+?\.[A-Za-z0-9]{2,5})["\'`]', text):
                extra = urllib.parse.urljoin(final, (m[0] or "./") + m[1])
                if urllib.parse.urlparse(extra).path not in saved and extra not in seen:
                    queue.append(extra)
            # Vite 资源内联: new URL("xxx-hash.png", import.meta.url) — 相对 JS 所在目录解析
            for m in re.findall(r'new URL\(\s*["\']([^"\']+?\.[A-Za-z0-9]{2,5})["\']\s*,\s*import\.meta\.url\s*\)', text):
                extra = urllib.parse.urljoin(final, m)
                if urllib.parse.urlparse(extra).netloc == BASE_HOST and \
                        urllib.parse.urlparse(extra).path not in saved and extra not in seen:
                    queue.append(extra)
            # CSS url(...) 内的相对资源
            if rel.endswith(".css"):
                for m in re.findall(r'url\((["\']?)([^)\'"]+)\1\)', text):
                    ref = m[1]
                    if ref.startswith(("data:", "http://", "https://")):
                        continue
                    extra = urllib.parse.urljoin(final, ref)
                    if urllib.parse.urlparse(extra).netloc == BASE_HOST and \
                            urllib.parse.urlparse(extra).path not in saved and extra not in seen:
                        queue.append(extra)
    return saved


# ---------------------------------------------------------------- 3. 公开 API 快照
def crawl_public_api(rounds=5, interval=1.2):
    print("[3/6] 公开 API 快照 (rooms 连续采样合并动态数据)")
    ensure_dir(FIXTURES)

    def get_json(path):
        s, h, d, _ = fetch(urllib.parse.urljoin(BASE, path))
        return s, h, d

    # session
    s, h, d = get_json("/api/auth/session")
    open(os.path.join(FIXTURES, "session.json"), "wb").write(d)
    record(BASE + "api/auth/session", s, h, "fixtures/session.json")

    # room-types
    s, h, d = get_json("/api/room-types")
    open(os.path.join(FIXTURES, "room-types.json"), "wb").write(d)
    record(BASE + "api/room-types", s, h, "fixtures/room-types.json")

    # captcha (一次性 SVG, 仅做静态快照)
    s, h, d = get_json("/api/auth/captcha")
    open(os.path.join(FIXTURES, "captcha.json"), "wb").write(d)
    record(BASE + "api/auth/captcha", s, h, "fixtures/captcha.json", note="一次性验证码快照")

    # rooms: 多轮采样, 合并房间与头像 URL (站点为实时数据)
    merged_rooms = {}
    order = []
    media_urls = set()
    raw_samples = []
    for i in range(rounds):
        s, h, d = get_json("/api/rooms")
        if s != 200:
            print(f"  rooms 采样 {i+1}: {s}")
            time.sleep(interval)
            continue
        snap = json.loads(d.decode("utf-8"))
        raw_samples.append(snap)
        for rm in snap.get("rooms", []):
            rid = str(rm.get("id"))
            if rid not in merged_rooms:
                order.append(rid)
            merged_rooms[rid] = rm  # 后出现的覆盖 (在线人数等更新)
            if rm.get("ownerAvatar"):
                media_urls.add(rm["ownerAvatar"])
        print(f"  rooms 采样 {i+1}/{rounds}: {len(snap.get('rooms', []))} 个房间, 累计 {len(merged_rooms)}")
        time.sleep(interval)

    rooms_doc = {"rooms": [merged_rooms[k] for k in order]}
    out = json.dumps(rooms_doc, ensure_ascii=False, separators=(",", ":"))
    with open(os.path.join(FIXTURES, "rooms.json"), "w", encoding="utf-8") as f:
        f.write(out)
    with open(os.path.join(FIXTURES, "rooms.pretty.json"), "w", encoding="utf-8") as f:
        json.dump(rooms_doc, f, ensure_ascii=False, indent=2)
    manifest["resources"].append({"url": BASE + "api/rooms", "status": 200,
        "contentType": "application/json", "local": "fixtures/rooms.json",
        "note": f"{rounds} 轮采样合并, 采集于 {manifest['fetchedAt']}"})
    print(f"  rooms 合并快照: {len(order)} 个房间")
    return sorted(media_urls), merged_rooms


# ---------------------------------------------------------------- 4. 媒体文件
def crawl_media(media_urls):
    print("[4/6] 媒体文件 (头像 webp)")
    seen = set(media_urls)
    # 历史观察到的头像 (曾出现在 rooms 数据中, 房间删除后文件常保留)
    historical = [
        "/api/media/avatars/29bd693844269b8835c76048e8bea9d1a1bfaa4d41c0b6b9.webp",
    ]
    for h in historical:
        seen.add(h)
    got = 0
    for path in sorted(seen):
        url = urllib.parse.urljoin(BASE, path)
        s, hdr, d, _ = fetch(url)
        if s == 200 and d:
            rel = path.lstrip("/")
            full = os.path.join(MIRROR, rel.replace("/", os.sep))
            ensure_dir(os.path.dirname(full))
            with open(full, "wb") as f:
                f.write(d)
            record(url, s, hdr, rel)
            got += 1
        else:
            print(f"  [{s}] (跳过) {url}")
    print(f"  媒体下载完成: {got}/{len(seen)}")


# ---------------------------------------------------------------- 6. 校验
def crawl_verify(saved_assets):
    print("[6/6] 完整性校验")
    problems = []
    # HTML 引用的每个资源必须在本地存在 (含本地化的 vendor/ 资源)
    html = open(os.path.join(MIRROR, "index.html"), "r", encoding="utf-8").read()
    for m in re.finditer(r'(?:src|href)=["\']([^"\']+)["\']', html):
        ref = m.group(1)
        if ref.startswith(("http://", "https://", "data:", "//")):
            problems.append(f"入口仍引用外部资源(未本地化): {ref}")
            continue
        p = urllib.parse.unquote(urllib.parse.urlparse(ref).path.lstrip("/"))
        if not p:
            continue
        if not os.path.exists(os.path.join(MIRROR, p.replace("/", os.sep))):
            problems.append(f"缺失资源: {ref}")
    # rooms 快照里引用的头像必须存在
    rooms = json.load(open(os.path.join(FIXTURES, "rooms.json"), encoding="utf-8"))
    for rm in rooms.get("rooms", []):
        av = rm.get("ownerAvatar")
        if av:
            lp = os.path.join(MIRROR, urllib.parse.unquote(av.lstrip("/")).replace("/", os.sep))
            if not os.path.exists(lp):
                problems.append(f"缺失头像: {av}")
            else:
                # 数据中的路径保持线上原样, 回放服务器按路径映射
                pass
    if problems:
        print("  发现问题:")
        for p in problems:
            print("   -", p)
    else:
        print("  全部通过: HTML 引用资源 / 头像引用均可在本地解析")
    return problems


def main():
    ensure_dir(MIRROR)
    ensure_dir(FIXTURES)
    ensure_dir(MEDIA_ROOT)
    # 重置清单 (增量更新会留下已下线资源)
    manifest["resources"] = []
    t0 = time.time()
    refs, vendor_map = crawl_entry()
    assets = crawl_assets(refs)
    media_urls, rooms = crawl_public_api()
    crawl_media(media_urls)
    # 清理已不存在于最新快照的旧 room-*.json
    live_rids = {str(r.get("id")) for r in rooms.values()}
    for fn in os.listdir(FIXTURES):
        mm = re.match(r'room-(\d+)\.json$', fn)
        if mm and mm.group(1) not in live_rids:
            os.remove(os.path.join(FIXTURES, fn))
            print(f"  清理过期房间快照: {fn}")
    problems = crawl_verify(assets)
    save_manifest()
    print(f"\n完成, 用时 {time.time()-t0:.1f}s, 共 {len(manifest['resources'])} 个资源")
    if vendor_map:
        print(f"本地化跨域脚本 {len(vendor_map)} 个: {[local for _, local in vendor_map]}")
    print(f"镜像目录: {MIRROR}")
    print("本地回放: python frontend/server.py  ->  http://127.0.0.1:8088")


if __name__ == "__main__":
    main()
