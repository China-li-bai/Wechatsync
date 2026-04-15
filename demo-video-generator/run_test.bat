@echo off
chcp 65001 >nul
echo ======================================================================
echo 🚀 Demo Video Generator - UV测试
echo ======================================================================
echo.

echo [1/4] 检查Python环境...
python --version
if errorlevel 1 (
    echo ❌ Python未安装
    exit /b 1
)
echo ✅ Python已安装
echo.

echo [2/4] 安装依赖...
pip install pyyaml jinja2 playwright -q
if errorlevel 1 (
    echo ❌ 依赖安装失败
    exit /b 1
)
echo ✅ 依赖已安装
echo.

echo [3/4] 安装Playwright浏览器...
python -m playwright install chromium --with-deps
if errorlevel 1 (
    echo ⚠️  Playwright浏览器安装可能失败，但继续测试
)
echo.

echo [4/4] 运行测试...
python test_uv_workflow.py

echo.
echo ======================================================================
echo 测试完成
echo ======================================================================
pause
