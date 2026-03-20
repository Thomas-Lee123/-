@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 推送到 GitHub: Thomas-Lee123/-
echo.

if not exist .git (
    git init
    echo 已初始化 Git
)
git add .
git status
git commit -m "网易云音乐下载器 - 支持搜索/链接解析/原声母带音质" 2>nul || git commit -m "Update"
git branch -M main 2>nul
git remote remove origin 2>nul
git remote add origin https://github.com/Thomas-Lee123/-.git
echo.
echo 执行: git push -u origin main
git push -u origin main
pause
