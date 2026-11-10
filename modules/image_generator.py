
from pathlib import Path
import streamlit as st
import torch

OUT = Path("outputs/images")
OUT.mkdir(parents=True, exist_ok=True)

SD_MODEL = "stable-diffusion-v1-5/stable-diffusion-v1-5"


# ==========================================
# CARGAR STABLE DIFFUSION EN GPU
# ==========================================

@st.cache_resource(show_spinner="Cargando Stable Diffusion...")
def _load_sd():

    import torch
    import diffusers
    from diffusers import StableDiffusionPipeline

    st.write("Versión Diffusers:", diffusers.__version__)

    if not torch.cuda.is_available():
        raise RuntimeError("No se detectó una GPU compatible con CUDA.")

    print("GPU:", torch.cuda.get_device_name(0))

    pipe = StableDiffusionPipeline.from_pretrained(
        SD_MODEL,
        torch_dtype=torch.float16,
        use_safetensors=True
    )

    # Optimización de memoria: atención
    if callable(getattr(pipe, "enable_attention_slicing", None)):
        pipe.enable_attention_slicing()

    # Optimización de memoria: VAE
    if callable(getattr(pipe, "enable_vae_slicing", None)):
        pipe.enable_vae_slicing()
    else:
        print("Aviso: VAE slicing no está disponible.")

    # Descargar componentes a la GPU cuando se necesitan
    if callable(getattr(pipe, "enable_model_cpu_offload", None)):
        pipe.enable_model_cpu_offload()
    else:
        pipe.to("cuda")

    return pipe


# ==========================================
# GENERAR ILUSTRACIONES CON IA
# ==========================================

def generate_image(scene, story, index, use_sd):

    if not use_sd:
        raise RuntimeError(
            "Stable Diffusion está desactivado. "
            "Activa la opción de generación con IA."
        )

    try:

        # Comprobar GPU
        if not torch.cuda.is_available():
            raise RuntimeError("No se detectó CUDA.")

        st.write(
            "GPU detectada:",
            torch.cuda.get_device_name(0)
        )

        # Cargar modelo
        pipe = _load_sd()

        # Obtener descripción de la escena
        scene_description = scene.get(
            "image_prompt",
            scene.get("heading", "A magical storybook scene")
        )

        # Estilo gráfico
        style = """
        Beautiful children's storybook illustration,
        professional 3D animated cartoon style,
        expressive characters,
        vibrant colors,
        detailed environment,
        cinematic lighting,
        beautiful composition,
        high quality digital art,
        consistent character appearance
        """

        prompt = f"{style}, {scene_description}"

        negative_prompt = """
        blurry, low quality, pixelated,
        deformed face, distorted body,
        extra fingers, extra limbs,
        bad anatomy, watermark, text,
        poorly drawn, noise
        """

        # Generador aleatorio en GPU
        generator = torch.Generator(
            device="cuda"
        ).manual_seed(1234 + index)

        # Generación de imagen
        with torch.inference_mode():

            result = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=25,
                guidance_scale=7.5,
                height=512,
                width=512,
                generator=generator
            )

        image = result.images[0]

        # Guardar ilustración
        path = OUT / f"scene_{index + 1}.png"

        image.save(path)

        print(f"Imagen generada correctamente: {path}")

        return (
            path,
            "Stable Diffusion 1.5 - NVIDIA RTX 3050 CUDA"
        )

    except Exception as exc:

        print("=" * 45)
        print("ERROR AL GENERAR IMAGEN")
        print(repr(exc))
        print("=" * 45)

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        st.error("Falló la generación con Stable Diffusion.")
        st.exception(exc)

        raise
