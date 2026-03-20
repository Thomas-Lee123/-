# -*- coding: utf-8 -*-
"""配置文件"""
import os

# NeteaseCloudMusicApi 服务地址（需先启动 API 服务）
API_BASE_URL = os.environ.get("NCM_API_URL", "http://localhost:3000")

# 下载保存目录
DOWNLOAD_DIR = os.environ.get("NCM_DOWNLOAD_DIR", "downloads")

# 音质等级（按优先级从高到低，获取不到时自动降级）
# jymaster=超清母带, hires=Hi-Res, lossless=无损, exhigh=极高(320kbps), standard=标准(128kbps)
QUALITY_LEVELS = ["jymaster", "hires", "lossless", "exhigh", "standard"]

# 默认请求头
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://music.163.com/",
}
