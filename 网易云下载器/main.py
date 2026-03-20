# -*- coding: utf-8 -*-
"""命令行入口"""
import argparse
from config import API_BASE_URL, DOWNLOAD_DIR
from core import resolve_songs_from_input, create_downloader


def main():
    parser = argparse.ArgumentParser(description="网易云音乐下载器 - 支持搜索/链接解析，音质可达原声母带")
    parser.add_argument("input", nargs="?", help="搜索词、music.163.com 链接或歌曲ID")
    parser.add_argument("-o", "--output", default=DOWNLOAD_DIR, help="保存目录")
    parser.add_argument("--api", default=API_BASE_URL, help="API 服务地址")
    parser.add_argument("--cookie", help="网易云 Cookie（可选，用于会员音质）")
    args = parser.parse_args()

    if not args.input:
        print("用法: python main.py <搜索词|链接|歌曲ID> [-o 保存目录]")
        print("示例: python main.py 周杰伦")
        print("      python main.py https://music.163.com/#/song?id=1868553")
        return

    try:
        downloader = create_downloader(
            api_url=args.api,
            cookie=args.cookie,
            save_dir=args.output,
        )
        api = downloader.api
        songs, source = resolve_songs_from_input(api, args.input)
        if not songs:
            print("未找到歌曲")
            return
        print(f"解析到 {len(songs)} 首 ({source})")
        for i, s in enumerate(songs, 1):
            name = s.get("name", "")
            ar = ", ".join(a.get("name", "") for a in (s.get("ar") or s.get("artists") or []))
            print(f"  {i}. {name} - {ar}")
        print("\n开始下载...")
        downloader.download_songs(
            songs,
            on_each=lambda i, t, s, path: print(f"  [{i}/{t}] {'✓ ' + str(path.name) if path else '✗ 跳过'}")
        )
        print("\n下载完成")
    except Exception as e:
        print(f"错误: {e}")
        raise


if __name__ == "__main__":
    main()
