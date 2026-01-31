@echo off
echo Building AppGraveyard...

REM 安装依赖
pip install -r requirements.txt

REM 使用 PyInstaller 打包
pyinstaller --onefile --windowed --name AppGraveyard appgraveyard_fixed.py

echo Build complete!
echo Executable is in the dist folder.
pause