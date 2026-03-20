# -*- coding: utf-8 -*-
"""音乐下载器"""
import os
import re
import requests
from pathlib import Path
from typing import Callable, List, Optional
from mutagen import File as MutagenFile
from config import DOWNLOAD_DIR, QUALITY_LEVELS, DEFAULT_HEADERS
from api_client import NeteaseAPIClient, NeteaseAPIError


def sanitize_filename(name: str) -> str:
    """清理文件名中的非法字符"""
    return re.sub(r'[<>:"/\\|?*]', "_", name).strip() or "unknown"


def get_file_ext(url: str, content_type: str = "") -> str:
    """根据 URL 或 Content-Type 确定文件扩展名"""
    url_lower = (url or "").lower()
    if ".mp3" in url_lower or "mpeg" in content_type:
        return ".mp3"
    if ".flac" in url_lower or "flac" in content_type:
        return ".flac"
    if ".m4a" in url_lower or "mp4" in content_type:
        return ".m4a"
    return ".mp3"  # 默认


class MusicDownloader:
    """音乐下载器"""

    def __init__(
        self,
        api_client: NeteaseAPIClient,
        save_dir: str = None,
        quality_levels: List[str] = None,
        on_progress: Callable[[int, int, str], None] = None,
    ):
        self.api = api_client
        self.save_dir = Path(save_dir or DOWNLOAD_DIR)
        self.quality_levels = quality_levels or QUALITY_LEVELS.copy()
        self.on_progress = on_progress
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def _get_download_url(self, song_id: int) -> tuple:
        """
        获取可用的下载链接，按音质从高到低尝试
        返回 (url, level) 或 (None, None)
        """
        for level in self.quality_levels:
            try:
                resp = self.api.get_song_url(song_id, level=level)
                data = resp.get("data") or []
                if data and isinstance(data, list):
                    item = data[0]
                    url = item.get("url")
                    if url:
                        return url, level
            except NeteaseAPIError:
                continue
        return None, None

    def _download_file(
        self,
        url: str,
        save_path: Path,
    ) -> bool:
        """下载文件到本地"""
        try:
            r = self.session.get(url, stream=True, timeout=60)
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            done = 0
            with open(save_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        done += len(chunk)
                        if self.on_progress:
                            self.on_progress(done, total, str(save_path))
            return True
        except Exception as e:
            if save_path.exists():
                save_path.unlink()
            raise e

    def _write_metadata(
        self,
        path: Path,
        title: str,
        artist: str,
        album: str = "",
    ):
        """写入元数据"""
        try:
            f = MutagenFile(str(path))
            if f is None:
                return
            f["title"] = title
            f["artist"] = artist
            if album:
                f["album"] = album
            f.save()
        except Exception:
            pass

    def download_song(
        self,
        song_id: int,
        title: str = "",
        artist: str = "",
        album: str = "",
    ) -> Optional[Path]:
        """
        下载单曲
        若未提供 title/artist，会调用 API 获取
        """
        if not title or not artist:
            try:
                detail = self.api.get_song_detail([song_id])
                songs = detail.get("songs") or []
                if songs:
                    s = songs[0]
                    title = title or s.get("name", "")
                    artist = artist or ", ".join(
                        a.get("name", "") for a in (s.get("ar") or [])
                    )
                    album = album or (s.get("al", {}) or {}).get("name", "")
            except NeteaseAPIError:
                title = title or f"song_{song_id}"
                artist = artist or "Unknown"

        url, level = self._get_download_url(song_id)
        if not url:
            raise NeteaseAPIError(f"无法获取歌曲 {song_id} 的播放链接（可能需会员或版权限制）")

        ext = get_file_ext(url, "")
        filename = f"{sanitize_filename(title)} - {sanitize_filename(artist)}{ext}"
        self.save_dir.mkdir(parents=True, exist_ok=True)
        save_path = self.save_dir / filename

        self._download_file(url, save_path)
        self._write_metadata(save_path, title, artist, album)
        return save_path

    def download_songs(
        self,
        songs: List[dict],
        on_each: Callable[[int, int, dict, Optional[Path]], None] = None,
    ) -> List[Path]:
        """
        批量下载
        songs: [{"id": xx, "name": xx, "ar": [...]}, ...]
        """
        results = []
        total = len(songs)
        for i, s in enumerate(songs):
            song_id = s.get("id") or s.get("track", {}).get("id")
            if not song_id:
                continue
            name = s.get("name") or s.get("track", {}).get("name", "")
            ar = s.get("ar") or s.get("track", {}).get("ar") or s.get("artists") or []
            artist = ", ".join(a.get("name", "") for a in ar) if ar else "Unknown"
            al = s.get("al") or s.get("track", {}).get("al") or {}
            album = al.get("name", "") if isinstance(al, dict) else ""

            try:
                path = self.download_song(song_id, name, artist, album)
                results.append(path)
                if on_each:
                    on_each(i + 1, total, s, path)
            except Exception as e:
                if on_each:
                    on_each(i + 1, total, s, None)
                raise e
        return results
