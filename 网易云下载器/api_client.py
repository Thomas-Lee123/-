# -*- coding: utf-8 -*-
"""NeteaseCloudMusicApi 客户端"""
import requests
from typing import Any, Dict, List, Optional
from config import API_BASE_URL, DEFAULT_HEADERS


class NeteaseAPIError(Exception):
    """API 请求异常"""
    pass


class NeteaseAPIClient:
    """网易云音乐 API 客户端"""

    def __init__(self, base_url: str = None, cookie: str = None):
        self.base_url = (base_url or API_BASE_URL).rstrip("/")
        self.cookie = cookie
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def _get(self, path: str, params: Dict = None) -> Dict:
        """GET 请求"""
        url = f"{self.base_url}{path}"
        try:
            r = self.session.get(url, params=params, cookies=self._parse_cookie(), timeout=15)
            r.raise_for_status()
            data = r.json()
            if data.get("code") != 200:
                raise NeteaseAPIError(data.get("message", "Unknown error"))
            return data
        except requests.RequestException as e:
            raise NeteaseAPIError(f"请求失败: {e}") from e

    def _parse_cookie(self) -> Dict:
        """解析 cookie 字符串为字典"""
        if not self.cookie:
            return {}
        result = {}
        for item in self.cookie.split(";"):
            item = item.strip()
            if "=" in item:
                k, v = item.split("=", 1)
                result[k.strip()] = v.strip()
        return result

    def search(self, keywords: str, limit: int = 30, type: int = 1) -> Dict:
        """
        搜索
        type: 1=单曲, 10=专辑, 100=歌手, 1000=歌单
        """
        return self._get("/search", {"keywords": keywords, "limit": limit, "type": type})

    def get_song_detail(self, ids: List[int]) -> Dict:
        """获取歌曲详情"""
        return self._get("/song/detail", {"ids": ",".join(map(str, ids))})

    def get_song_url(
        self,
        song_id: int,
        level: str = "jymaster"
    ) -> Dict:
        """
        获取歌曲播放链接 (v1 接口，支持母带级音质)
        level: jymaster/hires/lossless/exhigh/standard
        """
        return self._get("/song/url/v1", {"id": song_id, "level": level})

    def get_album(self, album_id: int) -> Dict:
        """获取专辑详情"""
        return self._get("/album", {"id": album_id})

    def get_playlist_detail(self, playlist_id: int) -> Dict:
        """获取歌单详情（含部分歌曲）"""
        return self._get("/playlist/detail", {"id": playlist_id})

    def get_playlist_track_all(self, playlist_id: int, limit: int = 1000) -> Dict:
        """获取歌单全部歌曲"""
        return self._get("/playlist/track/all", {"id": playlist_id, "limit": limit})


def extract_song_ids_from_search(data: Dict) -> List[int]:
    """从搜索结果提取歌曲ID"""
    songs = data.get("result", {}).get("songs") or []
    return [s["id"] for s in songs]


def extract_songs_from_album(data: Dict) -> List[Dict]:
    """从专辑数据提取歌曲列表"""
    songs = data.get("songs") or []
    return songs


def extract_songs_from_playlist(data: Dict) -> List[Dict]:
    """从歌单数据提取歌曲列表"""
    # playlist/track/all 返回 song/detail 格式: { songs: [...] }
    songs = data.get("songs") or []
    if songs:
        return songs
    # playlist/detail 结构: playlist.tracks
    playlist = data.get("playlist") or data
    tracks = playlist.get("tracks") or []
    if tracks and isinstance(tracks[0], dict):
        if "id" in tracks[0]:
            return tracks
        if "track" in tracks[0]:
            return [t.get("track", t) for t in tracks]
    return []
