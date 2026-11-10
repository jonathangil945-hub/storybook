# Storybook AI

Aplicación local en Python + Streamlit para generar cuentos de exactamente cinco escenas.

## Componentes

- **Texto:** `Qwen/Qwen2.5-0.5B-Instruct` desde Hugging Face, ejecutado localmente con Transformers y PyTorch.
- **Imagen opcional:** Stable Diffusion 1.5 mediante Diffusers. Requiere configurar PyTorch con CUDA y suficiente VRAM.
- **Voz:** pyttsx3 con las voces instaladas en Windows (síntesis local del sistema).
- **Sonido:** efectos ambientales WAV compuestos localmente con NumPy.
- **Interfaz:** Streamlit.

## Requisitos

- Windows 10/11 de 64 bits.
- Python 3.10 o 3.11 recomendado.
- 8 GB de RAM: cerrar aplicaciones pesadas y generar una escena a la vez.
- Conexión a Internet para la instalación y primera descarga del modelo Qwen.
- Espacio libre en disco para dependencias y pesos.

## Instalación rápida

1. Descomprime el ZIP.
2. Abre la carpeta `storybook_ai`.
3. Haz doble clic en `run_windows.bat` o ejecuta desde PowerShell:

```powershell
py -3 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
streamlit run app.py
```

La primera ejecución descargará Qwen desde Hugging Face. La descarga puede tardar y requiere Internet. Una vez almacenado en la caché local, Transformers puede reutilizarlo sin descargarlo de nuevo.

## Ilustraciones con Stable Diffusion

La opción está desactivada por defecto porque no conocemos todavía la VRAM exacta de tu NVIDIA. La aplicación puede generar una ilustración local de respaldo con Pillow, pero **esa imagen no es generada por IA**.

Para usar Stable Diffusion:
1. Confirma el modelo de GPU y su VRAM con `nvidia-smi`.
2. Instala una versión de PyTorch con CUDA compatible con tu GPU desde https://pytorch.org/get-started/locally/.
3. Instala Diffusers: `pip install -r requirements-images.txt`.
4. Activa “Intentar ilustraciones con Stable Diffusion 1.5” en la barra lateral.

Stable Diffusion 1.5 puede no caber en GPU de poca VRAM. Si se produce un error de memoria, desactiva la opción o configura un modelo más ligero. La primera descarga del modelo de imagen también requiere Internet.

## Voz y sonido

- La voz utiliza las voces SAPI instaladas en Windows. La calidad e idioma dependen de las voces disponibles en el equipo.
- El sonido se genera localmente como un efecto ambiental sintético de demostración. Para la entrega final se recomienda mejorar la variedad de ambientes por escena o incorporar recursos con licencia documentada.

## Estructura

```text
storybook_ai/
├── app.py
├── requirements.txt
├── requirements-images.txt
├── run_windows.bat
├── install_images_optional.bat
├── modules/
├── utils/
├── assets/
└── outputs/
```

## Limitaciones de esta versión inicial

- Qwen es un modelo pequeño; puede necesitar reintentos o revisión narrativa.
- Se valida que haya exactamente cinco escenas; si el modelo falla, se muestra un relato de respaldo claramente indicado.
- La consistencia visual entre escenas todavía necesita una ficha de personaje más estricta y pruebas.
- Stable Diffusion es opcional y requiere una configuración CUDA compatible.
- El sonido de esta versión es una ambientación procedural, no un modelo generativo de audio.

## Licencias y uso responsable

Revisar las licencias y condiciones vigentes de cada modelo, voz y recurso antes de redistribuir pesos o publicar resultados. Este repositorio contiene código, no incluye los pesos de los modelos.
