@echo off
cd /d "%~dp0"
call venv\Scripts\activate
echo ATENCION: esta instalacion puede requerir varios GB de disco y VRAM.
echo Para una GPU NVIDIA compatible, consulta primero README.md y la version CUDA de PyTorch.
pip install -r requirements-images.txt
echo PyTorch CPU debe sustituirse por una compilacion CUDA compatible con tu tarjeta.
pause
