import subprocess as subp
import hashlib
import time
import urllib.parse
from functools import reduce
import os
from os import path
import json
import re
from BookerDownloadTool.ext_cookie import extract_cookies_multi_browsers
from BookerDownloadTool.util import cookie_dict_to_str
import requests

UID = '27174700'

# WBI 签名固定重排表（从 B 站前端 JS 中提取，为固定常量）
MIXIN_KEY_ENC_TAB = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43,
    5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16,
    24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59,
    6, 63, 57, 62, 11, 36, 20, 34, 44, 52,
]


def _get_mixin_key(img_key: str, sub_key: str) -> str:
    """将 img_key 与 sub_key 按固定表重排，取前 32 位作为 mixin_key"""
    orig = img_key + sub_key
    return reduce(lambda s, i: s + orig[i], MIXIN_KEY_ENC_TAB, "")[:32]


def _enc_wbi(params: dict, img_key: str, sub_key: str) -> dict:
    """为请求参数添加 wts 与 w_rid，完成 WBI 签名"""
    mixin_key = _get_mixin_key(img_key, sub_key)
    params["wts"] = round(time.time())
    params = dict(sorted(params.items()))  # 按 key 排序
    query = urllib.parse.urlencode(params)
    params["w_rid"] = hashlib.md5((query + mixin_key).encode()).hexdigest()
    return params


def _get_wbi_keys(session: requests.Session) -> tuple[str, str]:
    """从 nav 接口获取当日的 img_key 与 sub_key"""
    resp = session.get("https://api.bilibili.com/x/web-interface/nav")
    resp.raise_for_status()
    data = resp.json()["data"]["wbi_img"]
    img_url = data["img_url"]
    sub_url = data["sub_url"]
    img_key = img_url.rsplit("/", 1)[-1].split(".")[0]
    sub_key = sub_url.rsplit("/", 1)[-1].split(".")[0]
    return img_key, sub_key


def get_all_user_bvids(uid: int, max_retries: int = 3) -> list[str]:
    """
    获取指定 B 站用户（UP 主）的全部视频 BV 号。

    参数:
        uid: B 站用户 ID（即 mid，可从空间页 URL space.bilibili.com/<uid> 中获取）
        max_retries: 单个分页请求的最大重试次数

    返回:
        BV 号字符串列表，按接口默认排序（通常为发布时间倒序）
    """
    cookies = extract_cookies_multi_browsers('bilibili.com')
    cookies = cookie_dict_to_str(cookies)
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": f"https://space.bilibili.com/{uid}/video",
        'Cookie': cookies,
    })

    # 1. 获取当日 WBI 密钥（img_key / sub_key 每日轮换）
    img_key, sub_key = _get_wbi_keys(session)

    all_bvids: list[str] = []
    pn = 1
    ps = 50  # 每页条数，50 为常见上限，可适当调低

    while True:
        print(f'开始获取用户【{uid}】第 {pn} 页视频')
        params = _enc_wbi(
            {"mid": uid, "pn": pn, "ps": ps, "order": "pubdate"},
            img_key,
            sub_key,
        )

        url = "https://api.bilibili.com/x/space/wbi/arc/search"
        resp = None
        for attempt in range(max_retries):
            resp = session.get(url, params=params)
            if resp.status_code == 200:
                break
            time.sleep(1 + attempt)  # 简单退避，降低风控触发概率
        else:
            raise RuntimeError(
                f"请求失败，最后一次状态码: {resp.status_code if resp else '无响应'}"
            )

        payload = resp.json()
        if payload.get("code") != 0:
            raise RuntimeError(f"B站接口返回错误: {payload.get('message', '未知错误')}")

        data = payload.get("data", {})
        page_info = data.get("page", {})
        vlist = data.get("list", {}).get("vlist", []) or []

        for item in vlist:
            bvid = item.get("bvid")
            if bvid:
                all_bvids.append(bvid)

        total = page_info.get("count", 0)
        if len(all_bvids) >= total or not vlist:
            break

        pn += 1
        time.sleep(1)  # 页间延时，避免触发频率限制

    return all_bvids


def main():
    bvid_fname = f'../asset/{UID}.json'
    if path.isfile(bvid_fname):
        bvids = json.loads(open(bvid_fname, encoding='utf8').read())
    else:
        bvids = get_all_user_bvids(UID)
        open(bvid_fname, 'w', encoding='utf8').write(json.dumps(bvids))
    print(f"共获取 {len(bvids)} 个 BV 号：{bvids[:10]} ...")
    exi_bvids = []
    exi_fname = '../asset/exi_bvids.txt'
    if path.isfile(exi_fname):
        exi_bvids = open(exi_fname, encoding='utf8').read().split('\n')
        exi_bvids = [l.strip() for l in exi_bvids if l.strip()]
    print(f"已存在 {len(exi_bvids)} 个 BV 号：{exi_bvids[:10]} ...")
    exi_bvids = set(exi_bvids)
    os.makedirs('img', exist_ok=True)
    os.makedirs('../docs/img', exist_ok=True)
    for bv in bvids:
        if bv in exi_bvids: continue
        print(bv)
        subp.run([
            'dl-ytp', f'https://www.bilibili.com/video/{bv}',
            '--cookies-from-browser', 'firefox',
        ], shell=True)
        mp4_fnames = [f for f in os.listdir() if f.endswith('.mp4')]
        for f in mp4_fnames:
            nf = re.sub(r'[\[\]\x20', '-', f)
            os.rename(f, nf)
        subp.run([
            'auto-video', 'note', '.'
        ], shell=True)
        md_fnames = [f for f in os.listdir() if f.endswith('.md')]
        for f in md_fnames:
            print(f)
            fmp4 = f.replace('.md', '.mp4')
            if path.isfile(fmp4): os.remove(fmp4)
            os.rename(f, f'../docs/{f}')
        for f in os.listdir('img'):
            print(f)
            os.rename(f'img/{f}', f'../docs/img/{f}')
        open(exi_fname, 'a', encoding='utf8').write(bv + '\n')
        


# 使用示例
if __name__ == "__main__":
   main()