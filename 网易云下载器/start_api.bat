@echo off
chcp 65001 >nul
echo 正在启动 NeteaseCloudMusicApi...
if not exist "api-enhanced" (
    echo 首次运行，克隆 API 项目...
    git clone https://github.com/NeteaseCloudMusicApiEnhanced/api-enhanced.git
)
cd api-enhanced
if not exist "node_modules" (
    echo 安装依赖...
    call npm install
)
echo 启动 API 服务 (http://localhost:3000)
call npm start
