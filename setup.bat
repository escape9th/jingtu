@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo === [1/3] 创建虚拟环境 ===
py -3.11 -m venv .venv
echo === [2/3] 激活虚拟环境 ===
call .venv\Scripts\activate.bat
echo === [3/3] 安装依赖（清华镜像） ===
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.
echo 安装完成！双击 demo.bat 试用，或 server.bat 启动服务。
pause
