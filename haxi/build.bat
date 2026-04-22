@echo off
chcp 65001 >nul
echo ========================================
echo Black2 哈希计算工具 - 打包脚本
echo ========================================
echo.

echo [步骤 1/3] 检查 PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller 未安装，正在安装...
    pip install pyinstaller
    if errorlevel 1 (
        echo ❌ PyInstaller 安装失败！
        pause
        exit /b 1
    )
) else (
    echo ✅ PyInstaller 已安装
)
echo.

echo [步骤 2/3] 清理旧文件...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "*.spec" del /q "*.spec"
echo ✅ 清理完成
echo.

echo [步骤 3/3] 开始打包...
pyinstaller --onefile ^
    --windowed ^
    --name "Black2_Hash_Calculator" ^
    --icon=NONE ^
    hash_calculator.py

if errorlevel 1 (
    echo.
    echo ❌ 打包失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ 打包成功！
echo ========================================
echo.
echo 生成的文件位置：dist\Black2_Hash_Calculator.exe
echo.
echo 可以将此 exe 文件分发给用户使用
echo.
pause
