# -*- coding: utf-8 -*-
"""核心业务逻辑"""
from typing import List, Optional
from api_client import (
    NeteaseAPIClient,
    extract_song_ids_from_search,
    extract_songs_from_album,
    extract_songs_from_playlist,
)
from url_parser import parse_music163_url, LinkType, ParsedLink
from downloader import MusicDownloader


def resolve_songs_from_input(
    api: NeteaseAPIClient,
    text: str,
) -> tuple:
    """
    根据输入解析并获取歌曲列表
    输入可以是: 搜索关键词、music.163.com 链接、纯数字歌曲ID
    返回 (songs: List[dict], source_name: str)
    """
    text = (text or "").strip()
    if not text:
        return [], ""

    # 1. 尝试解析为 music.163.com 链接
    parsed = parse_music163_url(text)
    if parsed:
        if parsed.link_type == LinkType.SONG:
            detail = api.get_song_detail([int(parsed.id)])
            songs = detail.get("songs") or []
            return songs, f"单曲"
        if parsed.link_type == LinkType.ALBUM:
            data = api.get_album(int(parsed.id))
            songs = extract_songs_from_album(data)
            album_name = (data.get("album") or {}).get("name", "专辑")
            return songs, album_name
        if parsed.link_type == LinkType.PLAYLIST:
            data = api.get_playlist_track_all(int(parsed.id))
            songs = extract_songs_from_playlist(data)
            return songs, "歌单"

    # 2. 尝试作为纯数字 ID（单曲）
    if text.isdigit() and len(text) >= 6:
        detail = api.get_song_detail([int(text)])
        songs = detail.get("songs") or []
        if songs:
            return songs, "单曲"

    # 3. 作为搜索关键词
    data = api.search(text, limit=30)
    ids = extract_song_ids_from_search(data)
    if not ids:
        return [], "搜索"
    detail = api.get_song_detail(ids)
    songs = detail.get("songs") or []
    return songs, f"搜索「{text}」"


def create_downloader(api_url: str = None, cookie: str = None, save_dir: str = None):
    """创建下载器实例"""
    api = NeteaseAPIClient(base_url=api_url, cookie=cookie)
    return MusicDownloader(api_client=api, save_dir=save_dir)
