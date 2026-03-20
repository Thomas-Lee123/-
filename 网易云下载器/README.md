# 网易云音乐下载器

支持搜索、网站链接解析，音质可达**原声母带**（jymaster）级别。

**GitHub:** https://github.com/Thomas-Lee123/-

## 功能

- **搜索**：输入关键词搜索歌曲
- **链接解析**：粘贴 `music.163.com` 的歌曲/专辑/歌单链接
- **高音质**：优先 jymaster（超清母带）→ hires → lossless → exhigh → standard

## 环境要求

- Python 3.8+
- Node.js 18+（用于运行 NeteaseCloudMusicApi）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动 NeteaseCloudMusicApi 服务

本下载器依赖 [NeteaseCloudMusicApiEnhanced](https://github.com/NeteaseCloudMusicApiEnhanced/api-enhanced) 获取音乐链接。

```bash
# 克隆 API 项目
git clone https://github.com/NeteaseCloudMusicApiEnhanced/api-enhanced.git
cd api-enhanced
npm install
npm start
```

默认在 `http://localhost:3000` 启动。

### 3. 运行下载器

**Web 界面：**
```bash
python app.py
```
打开 http://127.0.0.1:5000

**命令行：**
```bash
python main.py "周杰伦"
python main.py "https://music.163.com/#/song?id=1868553"
python main.py "https://music.163.com/playlist?id=7050074027"
```

## 配置

可通过环境变量或修改 `config.py`：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `NCM_API_URL` | API 服务地址 | http://localhost:3000 |
| `NCM_DOWNLOAD_DIR` | 下载保存目录 | downloads |
| `PORT` | Web 服务端口 | 5000 |

## 音质说明

- **jymaster**：超清母带（需黑胶会员，部分歌曲支持）
- **hires**：Hi-Res 高解析度
- **lossless**：无损 FLAC
- **exhigh**：极高 320kbps
- **standard**：标准 128kbps

未登录或非会员时，部分高音质可能不可用，会自动降级。

## 会员音质

如需下载会员专属音质，可设置 Cookie：

1. 登录 [music.163.com](https://music.163.com)
2. 浏览器 F12 → 应用/存储 → Cookie → 复制 `MUSIC_U` 等
3. 环境变量：`NETEASE_COOKIE="MUSIC_U=xxx; ..."`
4. 或在 API 项目根目录创建 `.env`，添加 `NETEASE_COOKIE=...`

## 推送到 GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/Thomas-Lee123/-.git
git push -u origin main
```

> 若仓库 `Thomas-Lee123/-` 尚未创建，请先在 [GitHub 新建仓库](https://github.com/new)。

## 免责声明

本项目仅供学习交流，请勿用于商业用途。下载的音乐版权归网易云音乐及版权方所有，请支持正版。
