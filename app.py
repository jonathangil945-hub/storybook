

import streamlit as st
import torch
from pathlib import Path

from modules.story_generator import generate_story
from modules.image_generator import generate_image
from modules.voice_generator import generate_voice
from modules.sound_generator import generate_sound

from utils.file_manager import save_story
from utils.book_view import render_book


# ==========================================
# CONFIGURACIÓN
# ==========================================

st.set_page_config(
    page_title="Storybook AI",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&display=swap');

.stApp {
    background: linear-gradient(145deg, #17120f, #292019);
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    padding-top: 2rem;
    max-width: 1450px;
}

h1, h2, h3 {
    font-family: 'Cinzel', Georgia, serif !important;
}

[data-testid="stSidebar"] {
    background: #211913;
    border-right: 1px solid #59432c;
}

.stButton button, .stFormSubmitButton button {
    border-radius: 12px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# ENCABEZADO
# ==========================================

st.title("📖 Storybook AI")

st.caption(
    "Un estudio de cuentos mágicos: crea historias, "
    "ilustraciones, narraciones y ambientes sonoros."
)


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.header("⚙️ Configuración")

    use_sd = st.checkbox(
        "Usar Stable Diffusion 1.5",
        value=True,
        key="use_stable_diffusion"
    )

    st.divider()

    st.subheader("Estado del equipo")

    cuda_available = torch.cuda.is_available()

    if cuda_available:
        gpu_name = torch.cuda.get_device_name(0)
        st.success("GPU NVIDIA detectada")
        st.write(f"**GPU:** {gpu_name}")
        st.write("**CUDA:** Disponible")
    else:
        st.warning("CUDA no está disponible.")
        st.write("Revisa PyTorch y los controladores NVIDIA.")

    st.divider()

    st.subheader("Modelos actuales")

    st.write("**Texto:** Qwen2.5-0.5B-Instruct")
    st.write("**Imagen:** Stable Diffusion 1.5")
    st.write("**Voz:** Windows SAPI")
    st.write("**Sonido:** Generador local")

    st.divider()

    st.caption(
        "Los modelos se pueden actualizar independientemente "
        "de la interfaz del libro."
    )


# ==========================================
# FORMULARIO DE CREACIÓN
# ==========================================

st.subheader("✨ Crear una nueva historia")

with st.form("story_form"):

    idea = st.text_area(
        "¿Qué historia quieres crear?",
        placeholder=(
            "Ejemplo: Un pequeño dragón descubre una "
            "puerta secreta en un bosque encantado..."
        ),
        height=110
    )

    genre = st.selectbox(
        "Género de la historia",
        [
            "Aventura",
            "Fantasía",
            "Misterio",
            "Terror",
            "Ciencia ficción",
            "Infantil"
        ]
    )

    num_scenes = st.selectbox(
        "¿Cuántos capítulos tendrá tu libro?",
        options=[3, 5, 8, 10],
        index=1,
        help=(
            "Cada capítulo tendrá una ilustración y una narración. "
            "La portada y la página final se agregan automáticamente."
        )
    )

    st.caption(
        f"Tu libro tendrá {num_scenes} capítulos, "
        "además de la portada y la página final."
    )

    submitted = st.form_submit_button(
        "✨ Crear mi cuento",
        use_container_width=True,
        type="primary"
    )


# ==========================================
# LIMPIAR RECURSOS ANTERIORES
# ==========================================

def clear_previous_resources():

    prefixes = [
        "imgpath",
        "imgmode",
        "voicepath",
        "voicemsg",
        "soundpath"
    ]

    # El máximo permitido actualmente es de 10 capítulos.
    for i in range(10):
        for prefix in prefixes:
            st.session_state.pop(f"{prefix}{i}", None)

    st.session_state.pop("story", None)
    st.session_state.pop("output_folder", None)


# ==========================================
# GENERACIÓN
# ==========================================

if submitted:

    if not idea.strip():

        st.error("Escribe una idea para crear tu cuento.")

    elif use_sd and not cuda_available:

        st.error(
            "No se detectó CUDA. No se puede utilizar Stable Diffusion "
            "con la configuración actual."
        )

    else:

        clear_previous_resources()

        try:

            # ----------------------------------
            # GENERAR HISTORIA
            # ----------------------------------

            with st.spinner(
                f"✍️ Escribiendo tu historia de {num_scenes} capítulos..."
            ):

                story = generate_story(
                    idea.strip(),
                    genre,
                    num_scenes
                )

                if (
                    not story
                    or len(story.get("scenes", [])) != num_scenes
                ):
                    raise ValueError(
                        f"La historia debe contener exactamente "
                        f"{num_scenes} capítulos."
                    )

                st.session_state["story"] = story
                st.session_state["idea"] = idea.strip()
                st.session_state["genre"] = genre
                st.session_state["num_scenes"] = num_scenes

            st.success(
                f"¡La historia de {num_scenes} capítulos está lista!"
            )

            # ----------------------------------
            # GENERAR RECURSOS
            # ----------------------------------

            st.divider()
            st.subheader("🎬 Preparando tu libro")

            progress = st.progress(0)
            status = st.empty()

            # Dos tareas por capítulo sin imágenes:
            # voz y sonido.
            # Tres tareas si también se generan imágenes.

            tasks_per_scene = 3 if use_sd else 2
            total_tasks = num_scenes * tasks_per_scene

            completed = 0
            errors = []

            for i, scene in enumerate(story["scenes"]):

                status.info(
                    f"Preparando capítulo {i + 1} de {num_scenes}: "
                    f"{scene.get('heading', '')}"
                )

                # ----------------------------------
                # ILUSTRACIÓN
                # ----------------------------------

                if use_sd:

                    try:
                        image_path, image_mode = generate_image(
                            scene,
                            story,
                            i,
                            use_sd
                        )

                        if image_path and Path(image_path).is_file():

                            st.session_state[f"imgpath{i}"] = str(image_path)
                            st.session_state[f"imgmode{i}"] = image_mode

                        else:
                            errors.append(
                                f"Capítulo {i + 1}: ilustración no disponible."
                            )

                    except Exception as exc:

                        errors.append(
                            f"Capítulo {i + 1}: error en ilustración: {exc}"
                        )

                    completed += 1
                    progress.progress(completed / total_tasks)

                # ----------------------------------
                # NARRACIÓN
                # ----------------------------------

                try:

                    voice_path, voice_message = generate_voice(
                        scene["text"],
                        i
                    )

                    if voice_path and Path(voice_path).is_file():

                        st.session_state[f"voicepath{i}"] = str(voice_path)
                        st.session_state[f"voicemsg{i}"] = voice_message

                    else:
                        errors.append(
                            f"Capítulo {i + 1}: narración no disponible."
                        )

                except Exception as exc:

                    errors.append(
                        f"Capítulo {i + 1}: error en narración: {exc}"
                    )

                completed += 1
                progress.progress(completed / total_tasks)

                # ----------------------------------
                # AMBIENTE SONORO
                # ----------------------------------

                try:

                    sound_path = generate_sound(
                        scene.get("sound_prompt", scene["heading"]),
                        i
                    )

                    if sound_path and Path(sound_path).is_file():

                        st.session_state[f"soundpath{i}"] = str(sound_path)

                    else:
                        errors.append(
                            f"Capítulo {i + 1}: ambiente sonoro no disponible."
                        )

                except Exception as exc:

                    errors.append(
                        f"Capítulo {i + 1}: error en sonido: {exc}"
                    )

                completed += 1
                progress.progress(completed / total_tasks)

            progress.progress(1.0)
            status.success("¡Tu libro está terminado!")

            if errors:

                with st.expander("⚠️ Advertencias de generación"):

                    for error in errors:
                        st.warning(error)

        except Exception as exc:

            st.error(f"No se pudo completar el cuento: {exc}")


# ==========================================
# MOSTRAR LIBRO DIGITAL
# ==========================================

if "story" in st.session_state:

    story = st.session_state["story"]

    num_scenes = len(story["scenes"])

    st.divider()

    col1, col2 = st.columns([3, 1])

    with col1:

        st.subheader("📚 Tu libro está listo")

        st.caption(
            f"Género: {st.session_state['genre']} · "
            f"{num_scenes} capítulos"
        )

    with col2:

        if st.button(
            "💾 Guardar cuento",
            use_container_width=True,
            type="primary"
        ):

            try:

                folder = save_story(
                    story,
                    st.session_state["idea"],
                    st.session_state["genre"]
                )

                st.session_state["output_folder"] = str(folder)

            except Exception as exc:

                st.error(f"No se pudo guardar: {exc}")

    if st.session_state.get("output_folder"):

        st.success(
            f"Cuento guardado en: {st.session_state['output_folder']}"
        )

    # ----------------------------------
    # PREPARAR RUTAS DE RECURSOS
    # ----------------------------------

    image_paths = [
        st.session_state.get(f"imgpath{i}")
        for i in range(num_scenes)
    ]

    voice_paths = [
        st.session_state.get(f"voicepath{i}")
        for i in range(num_scenes)
    ]

    sound_paths = [
        st.session_state.get(f"soundpath{i}")
        for i in range(num_scenes)
    ]

    # ----------------------------------
    # MOSTRAR LIBRO
    # ----------------------------------

    render_book(
        story=story,
        genre=st.session_state["genre"],
        image_paths=image_paths,
        voice_paths=voice_paths,
        sound_paths=sound_paths
    )


# ==========================================
# PIE DE PÁGINA
# ==========================================

st.divider()

st.caption(
    "📖 Storybook AI · Historias creadas con inteligencia artificial."
)
