@echo off
echo 正在安装依赖...
pip install -r requirements.txt

echo 正在打包 AppGraveyard...
pyinstaller --onefile --windowed --name AppGraveyard appgraveyard.py

echo 打包完成！
echo 可执行文件位于: dist\AppGraveyard.exe
pause