# -*- coding: utf-8 -*-
"""Web 应用入口"""
import os
import json
from flask import Flask, render_template_string, request, jsonify
from config import API_BASE_URL, DOWNLOAD_DIR
from core import resolve_songs_from_input, create_downloader

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>网易云音乐下载器 - 原声母带</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0d1117;
            --surface: #161b22;
            --border: #30363d;
            --text: #e6edf3;
            --muted: #8b949e;
            --accent: #58a6ff;
            --success: #3fb950;
            --error: #f85149;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Noto Sans SC', -apple-system, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            padding: 2rem;
        }
        .container {
            max-width: 720px;
            margin: 0 auto;
        }
        h1 {
            font-size: 1.75rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            color: var(--muted);
            font-size: 0.9rem;
            margin-bottom: 2rem;
        }
        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .input-row {
            display: flex;
            gap: 0.75rem;
            margin-bottom: 1rem;
        }
        input[type="text"] {
            flex: 1;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            color: var(--text);
            font-size: 1rem;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: var(--accent);
        }
        input::placeholder { color: var(--muted); }
        button {
            background: var(--accent);
            color: #fff;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            white-space: nowrap;
        }
        button:hover { opacity: 0.9; }
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .quality-badge {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            font-size: 0.75rem;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            margin-left: 0.5rem;
        }
        .song-list {
            list-style: none;
        }
        .song-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.75rem 0;
            border-bottom: 1px solid var(--border);
            gap: 1rem;
        }
        .song-item:last-child { border-bottom: none; }
        .song-info {
            flex: 1;
            min-width: 0;
        }
        .song-name { font-weight: 500; }
        .song-artist { color: var(--muted); font-size: 0.9rem; }
        .msg {
            padding: 0.75rem 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        .msg.info { background: rgba(88,166,255,0.15); color: var(--accent); }
        .msg.error { background: rgba(248,81,73,0.15); color: var(--error); }
        .msg.success { background: rgba(63,185,80,0.15); color: var(--success); }
        .tip {
            font-size: 0.85rem;
            color: var(--muted);
            margin-top: 1rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>网易云音乐下载器</h1>
        <p class="subtitle">支持搜索、链接解析 · 音质可达原声母带 <span class="quality-badge">jymaster</span></p>

        <div class="card">
            <div class="input-row">
                <input type="text" id="input" placeholder="搜索歌曲 / 粘贴 music.163.com 链接 / 歌曲ID" autofocus>
                <button id="btnSearch">解析</button>
                <button id="btnDownload">下载全部</button>
            </div>
            <p class="tip">示例：周杰伦、https://music.163.com/#/song?id=1868553、https://music.163.com/playlist?id=123456</p>
        </div>

        <div id="messages"></div>
        <div class="card" id="resultCard" style="display:none">
            <h3 style="margin-bottom:1rem" id="resultTitle">歌曲列表</h3>
            <ul class="song-list" id="songList"></ul>
        </div>
    </div>

    <script>
        let currentSongs = [];
        const input = document.getElementById('input');
        const btnSearch = document.getElementById('btnSearch');
        const btnDownload = document.getElementById('btnDownload');
        const messages = document.getElementById('messages');
        const resultCard = document.getElementById('resultCard');
        const resultTitle = document.getElementById('resultTitle');
        const songList = document.getElementById('songList');

        function addMsg(text, type = 'info') {
            const div = document.createElement('div');
            div.className = `msg ${type}`;
            div.textContent = text;
            messages.appendChild(div);
            setTimeout(() => div.remove(), 5000);
        }

        async function search() {
            const q = input.value.trim();
            if (!q) { addMsg('请输入搜索词或链接', 'error'); return; }
            btnSearch.disabled = true;
            messages.innerHTML = '';
            try {
                const r = await fetch('/api/resolve?q=' + encodeURIComponent(q));
                const data = await r.json();
                if (!data.ok) {
                    addMsg(data.error || '解析失败', 'error');
                    resultCard.style.display = 'none';
                    return;
                }
                currentSongs = data.songs || [];
                resultTitle.textContent = `${data.source || '歌曲列表'} (${currentSongs.length} 首)`;
                songList.innerHTML = currentSongs.map(s => {
                    const ar = (s.ar || s.artists || []).map(a => a.name).join(', ');
                    return `<li class="song-item"><div class="song-info"><div class="song-name">${escapeHtml(s.name)}</div><div class="song-artist">${escapeHtml(ar)}</div></div></li>`;
                }).join('');
                resultCard.style.display = 'block';
                addMsg(`已解析 ${currentSongs.length} 首歌曲`, 'success');
            } catch (e) {
                addMsg('请求失败: ' + e.message, 'error');
            }
            btnSearch.disabled = false;
        }

        async function download() {
            if (currentSongs.length === 0) {
                addMsg('请先解析歌曲列表', 'error');
                return;
            }
            btnDownload.disabled = true;
            addMsg('开始下载...', 'info');
            try {
                const r = await fetch('/api/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ songs: currentSongs })
                });
                const data = await r.json();
                if (data.ok) {
                    addMsg(`成功下载 ${data.count || 0} 首`, 'success');
                } else {
                    addMsg(data.error || '下载失败', 'error');
                }
            } catch (e) {
                addMsg('下载失败: ' + e.message, 'error');
            }
            btnDownload.disabled = false;
        }

        function escapeHtml(s) {
            if (!s) return '';
            const div = document.createElement('div');
            div.textContent = s;
            return div.innerHTML;
        }

        input.addEventListener('keypress', e => { if (e.key === 'Enter') search(); });
        btnSearch.addEventListener('click', search);
        btnDownload.addEventListener('click', download);
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/api/resolve")
def api_resolve():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"ok": False, "error": "请输入内容"})
    try:
        from api_client import NeteaseAPIClient
        api = NeteaseAPIClient(base_url=API_BASE_URL)
        songs, source = resolve_songs_from_input(api, q)
        # 转为可序列化结构
        out = []
        for s in songs:
            out.append({
                "id": s.get("id"),
                "name": s.get("name"),
                "ar": s.get("ar") or s.get("artists"),
                "al": s.get("al"),
            })
        return jsonify({"ok": True, "songs": out, "source": source})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/api/download", methods=["POST"])
def api_download():
    data = request.get_json() or {}
    songs = data.get("songs") or []
    if not songs:
        return jsonify({"ok": False, "error": "无歌曲可下载"})
    try:
        downloader = create_downloader(api_url=API_BASE_URL, save_dir=DOWNLOAD_DIR)
        downloader.download_songs(songs)
        return jsonify({"ok": True, "count": len(songs)})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


def main():
    port = int(os.environ.get("PORT", 5000))
    print(f"启动 Web 服务: http://127.0.0.1:{port}")
    print("请确保已启动 NeteaseCloudMusicApi 服务 (默认 http://localhost:3000)")
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
