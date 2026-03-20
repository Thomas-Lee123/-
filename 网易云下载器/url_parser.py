# -*- coding: utf-8 -*-
"""网易云音乐链接解析器"""
import re
from urllib.parse import urlparse, parse_qs
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class LinkType(Enum):
    """链接类型"""
    SONG = "song"
    ALBUM = "album"
    PLAYLIST = "playlist"
    UNKNOWN = "unknown"


@dataclass
class ParsedLink:
    """解析后的链接信息"""
    link_type: LinkType
    id: str
    raw_url: str


def parse_music163_url(url: str) -> Optional[ParsedLink]:
    """
    解析 music.163.com 链接，提取类型和ID
    
    支持的格式:
    - https://music.163.com/#/song?id=1431606759
    - https://music.163.com/song?id=1431606759
    - https://music.163.com/#/album?id=122305109
    - https://music.163.com/#/playlist?id=7050074027
    - https://y.music.163.com/m/song?id=xxx
    """
    if not url or "163.com" not in url:
        return None

    url = url.strip()
    parsed = urlparse(url)
    path = (parsed.path or "").lower()
    fragment = (parsed.fragment or "").lower()
    query_str = parsed.query or ""

    # 合并 fragment 中的参数 (#/song?id=xxx)
    if fragment and "?" in fragment:
        parts = fragment.split("?", 1)
        path_hint = parts[0].lstrip("/")
        frag_query = parts[1]
        query_str = frag_query if not query_str else f"{query_str}&{frag_query}"
    else:
        path_hint = fragment.split("?")[0].lstrip("/") if fragment else ""

    # 确定链接类型
    link_type = None
    for part in [path, path_hint]:
        if "/song" in part or part == "song":
            link_type = LinkType.SONG
            break
        if "/album" in part or part == "album":
            link_type = LinkType.ALBUM
            break
        if "/playlist" in part or part == "playlist":
            link_type = LinkType.PLAYLIST
            break
    if not link_type:
        return None

    params = parse_qs(query_str)
    id_val = params.get("id", [None])[0]
    if not id_val or not str(id_val).isdigit():
        return None

    return ParsedLink(link_type=link_type, id=str(id_val), raw_url=url)


def extract_id_from_text(text: str) -> Optional[str]:
    """从文本中提取纯数字ID（可能是歌曲ID）"""
    match = re.search(r'\b(\d{6,})\b', text)
    return match.group(1) if match else None
