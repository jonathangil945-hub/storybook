@echo off
cd /d "%~dp0"
if not exist venv (
  py -3 -m venv venv
)
call venv\Scripts\activate
python -m pip install --upgrade pip
echo Instalando PyTorch CPU (para el modelo de texto)...
pip install torch --index-url https://download.pytorch.org/whl/cpu
echo Instalando dependencias de Storybook...
pip install -r requirements.txt
echo.
echo Instalacion terminada. Ejecutando Storybook...
streamlit run app.py
pause
