@echo off
chcp 65001 >nul
echo 网易云音乐下载器
echo.
echo 请先在另一个窗口运行 start_api.bat 启动 API 服务
echo 或确保 http://localhost:3000 已运行
echo.
pause
pip install -r requirements.txt -q
python app.py
