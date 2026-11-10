
import json
import streamlit as st
import torch

from transformers import AutoTokenizer, AutoModelForCausalLM


# ==========================================
# CONFIGURACIÓN DEL MODELO
# ==========================================

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.float16 if DEVICE == "cuda" else torch.float32

MIN_WORDS = 130
MAX_WORDS = 150

MIN_SCENES = 1
MAX_SCENES = 10


# ==========================================
# CARGAR MODELO
# ==========================================

@st.cache_resource(show_spinner="Cargando modelo Qwen...")
def load_model():

    st.write("Dispositivo de generación:", DEVICE)

    if DEVICE == "cuda":
        st.write("GPU detectada:", torch.cuda.get_device_name(0))

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=DTYPE,
        low_cpu_mem_usage=True
    )

    model = model.to(DEVICE)
    model.eval()

    return tokenizer, model


# ==========================================
# HISTORIA DE RESPALDO
# ==========================================

def _fallback(idea, genre, num_scenes):

    stages = [
        "El comienzo de la aventura",
        "Una pista inesperada",
        "Un descubrimiento sorprendente",
        "El desafío más difícil",
        "La decisión importante",
        "Un nuevo obstáculo",
        "La verdad oculta",
        "El momento decisivo",
        "La última prueba",
        "Un final inolvidable"
    ]

    descriptions = [
        "La aventura comenzó de una manera inesperada. El protagonista descubrió que aquel día sería diferente a todos los anteriores. Mientras observaba su entorno, encontró pequeños detalles que despertaron su curiosidad. Decidió investigar y descubrir qué estaba sucediendo.",

        "Durante su recorrido apareció una pista que parecía tener relación con el misterio. El protagonista examinó cuidadosamente cada detalle y comenzó a comprender que nada había ocurrido por casualidad. Aunque tenía algunas dudas, decidió continuar investigando.",

        "Después de investigar durante un buen tiempo, el protagonista encontró algo extraordinario. Aquel descubrimiento cambió su manera de comprender lo que estaba sucediendo. Sin embargo, también descubrió que todavía quedaban muchas preguntas por responder.",

        "La situación comenzó a complicarse y apareció un obstáculo que parecía imposible de superar. El protagonista sintió miedo, pero recordó todo lo que había aprendido durante el recorrido. Sabía que debía encontrar una solución antes de que fuera demasiado tarde.",

        "El protagonista comprendió que debía tomar una decisión importante. Pensó cuidadosamente en las consecuencias y recordó a las personas que lo habían acompañado. Finalmente, reunió el valor necesario para continuar, aunque no sabía exactamente qué encontraría después.",

        "Cuando parecía que todo estaba solucionado, surgió una nueva dificultad. El protagonista tuvo que observar la situación desde otra perspectiva y buscar una alternativa. Poco a poco descubrió que la respuesta podía encontrarse en los detalles que había pasado por alto.",

        "Una verdad inesperada salió a la luz. El protagonista comprendió finalmente por qué habían sucedido tantas cosas durante la aventura. Aquello que parecía un problema sin explicación comenzó a tener sentido y le permitió descubrir una nueva posibilidad.",

        "Llegó el momento de actuar. El protagonista reunió sus fuerzas y utilizó todo lo que había aprendido para enfrentar la situación. Aunque el resultado todavía era incierto, decidió no rendirse y confiar en sus propias capacidades.",

        "La última prueba puso a prueba su inteligencia, paciencia y valentía. El protagonista tuvo que superar sus temores y demostrar cuánto había cambiado desde el comienzo de la aventura. Con esfuerzo y determinación consiguió encontrar una solución.",

        "Finalmente, la aventura llegó a su desenlace. El protagonista comprendió que cada dificultad había dejado una enseñanza importante. Recordó los momentos difíciles, las personas que lo ayudaron y todos los descubrimientos que había realizado. Ahora podía mirar hacia el futuro con tranquilidad."
    ]

    scenes = []

    for index in range(num_scenes):

        scenes.append({
            "heading": stages[index],
            "text": (
                f"{descriptions[index]} "
                f"Todo lo ocurrido estaba relacionado con la aventura "
                f"que comenzó cuando {idea.lower()}. "
                f"El protagonista continuó adelante en un mundo de "
                f"{genre.lower()}, observando cuidadosamente lo que "
                f"sucedía a su alrededor. Aunque todavía existían "
                f"incertidumbres, comprendió que cada experiencia "
                f"le permitía aprender algo nuevo. Recordó la importancia "
                f"de actuar con paciencia, escuchar a los demás y no "
                f"abandonar sus objetivos ante las dificultades. "
                f"Con esa idea en mente, se preparó para afrontar "
                f"lo que viniera después."
            ),
            "image_prompt": (
                f"High quality {genre} children's storybook illustration, "
                f"consistent main character, same physical appearance, "
                f"cinematic composition, beautiful detailed environment, "
                f"scene {index + 1}: {descriptions[index]}"
            ),
            "sound_prompt": (
                "Atmospheric cinematic background ambience, "
                "gentle environmental sounds, suitable for a "
                f"{genre} children's storybook scene."
            )
        })

    return {
        "title": "El secreto de una gran aventura",
        "scenes": scenes
    }


# ==========================================
# EXTRAER JSON
# ==========================================

def _extract_json(generated):

    decoder = json.JSONDecoder()

    for position, character in enumerate(generated):

        if character == "{":

            try:
                data, _ = decoder.raw_decode(generated[position:])

                if isinstance(data, dict):
                    return data

            except json.JSONDecodeError:
                continue

    raise ValueError(
        "Qwen generó un JSON incompleto o incorrecto."
    )


# ==========================================
# VALIDAR HISTORIA
# ==========================================

def _validate_story(data, num_scenes):

    if not isinstance(data, dict):
        raise ValueError("La respuesta no es un objeto JSON.")

    title = data.get("title")
    scenes = data.get("scenes")

    if not isinstance(title, str) or not title.strip():
        raise ValueError("El título no es válido.")

    if not isinstance(scenes, list) or len(scenes) != num_scenes:
        raise ValueError(
            f"La historia debe contener exactamente "
            f"{num_scenes} capítulos."
        )

    required_fields = [
        "heading",
        "text",
        "image_prompt",
        "sound_prompt"
    ]

    validated_scenes = []

    for index, scene in enumerate(scenes):

        if not isinstance(scene, dict):
            raise ValueError(
                f"El capítulo {index + 1} no es válido."
            )

        for field in required_fields:

            value = scene.get(field)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"Falta {field} en el capítulo {index + 1}."
                )

        word_count = len(scene["text"].split())

        if word_count < MIN_WORDS or word_count > MAX_WORDS:
            raise ValueError(
                f"El capítulo {index + 1} tiene {word_count} palabras. "
                f"Se necesitan entre {MIN_WORDS} y {MAX_WORDS}."
            )

        validated_scenes.append({
            "heading": scene["heading"].strip(),
            "text": scene["text"].strip(),
            "image_prompt": scene["image_prompt"].strip(),
            "sound_prompt": scene["sound_prompt"].strip()
        })

    return {
        "title": title.strip(),
        "scenes": validated_scenes
    }


# ==========================================
# GENERAR HISTORIA CON QWEN
# ==========================================

def _generate_response(
    tokenizer,
    model,
    idea,
    genre,
    num_scenes,
    retry=False
):

    if retry:

        instruction = f"""
        Tu generación anterior no cumplió los requisitos.

        Genera nuevamente la historia completa.

        REQUISITOS:
        - Exactamente {num_scenes} capítulos.
        - Cada capítulo debe tener entre 130 y 150 palabras.
        - No omitas ningún capítulo.
        - No resumas la narración.
        - Mantén la continuidad de personajes y acontecimientos.
        - Comprueba que exista un desenlace completo.
        - Devuelve exclusivamente JSON válido.
        """

    else:

        instruction = f"""
        Escribe un cuento completo y bien desarrollado
        basado en la idea proporcionada.

        REQUISITOS OBLIGATORIOS:

        1. Exactamente {num_scenes} capítulos.
        2. Cada capítulo debe contener entre 130 y 150 palabras.
        3. La historia debe tener continuidad entre capítulos.
        4. Mantén los mismos personajes y características físicas.
        5. Describe acciones, lugares, emociones y diálogos.
        6. Utiliza español natural y fácil de comprender.
        7. Evita repetir acontecimientos o párrafos.
        8. No escribas resúmenes.
        9. Los prompts de imágenes y sonidos deben estar en inglés.
        10. La historia debe tener un inicio, desarrollo y desenlace.

        ESTRUCTURA NARRATIVA:

        Distribuye el desarrollo de la historia entre los
        {num_scenes} capítulos.

        El primer capítulo debe presentar el mundo y los personajes.
        Los capítulos intermedios deben desarrollar la aventura,
        los conflictos y los descubrimientos.
        El último capítulo debe resolver el conflicto principal
        y ofrecer un desenlace satisfactorio.

        Si hay pocos capítulos, concentra las etapas narrativas.
        Si hay muchos capítulos, desarrolla los acontecimientos
        progresivamente sin repetir contenido.

        Cada capítulo debe contener:
        heading, text, image_prompt y sound_prompt.

        Devuelve exclusivamente JSON válido.
        """

    structure = {
        "title": "Título original del cuento",
        "scenes": [
            {
                "heading": "Nombre del capítulo",
                "text": (
                    "Narración extensa en español de entre "
                    "130 y 150 palabras."
                ),
                "image_prompt": (
                    "Detailed English illustration prompt, "
                    "consistent characters and environment."
                ),
                "sound_prompt": (
                    "Detailed English sound ambience description."
                )
            }
            for _ in range(num_scenes)
        ]
    }

    messages = [
        {
            "role": "system",
            "content": (
                "Eres un escritor profesional especializado "
                "en cuentos infantiles y libros ilustrados. "
                "Escribes historias coherentes, originales y "
                "bien desarrolladas. Tu respuesta debe ser "
                "exclusivamente un objeto JSON válido. "
                "No uses Markdown ni agregues explicaciones. "
                "Respeta todos los campos solicitados."
            )
        },
        {
            "role": "user",
            "content": (
                f"IDEA: {idea}\n"
                f"GÉNERO: {genre}\n"
                f"CANTIDAD DE CAPÍTULOS: {num_scenes}\n"
                f"{instruction}\n"
                f"ESTRUCTURA JSON:\n"
                f"{json.dumps(structure, ensure_ascii=False)}"
            )
        }
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt"
    )

    inputs = {
        key: value.to(DEVICE)
        for key, value in inputs.items()
    }

    # Más capítulos requieren más tokens de salida.
    max_tokens = min(7000, max(3000, num_scenes * 650))

    with torch.inference_mode():

        output = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=True,
            temperature=0.65 if not retry else 0.55,
            top_p=0.90,
            repetition_penalty=1.08,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id
        )

    generated = tokenizer.decode(
        output[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True
    )

    data = _extract_json(generated)

    return _validate_story(data, num_scenes)


# ==========================================
# FUNCIÓN PRINCIPAL
# ==========================================

def generate_story(idea, genre, num_scenes=5):

    if not isinstance(num_scenes, int) or not (
        MIN_SCENES <= num_scenes <= MAX_SCENES
    ):
        raise ValueError(
            f"La cantidad de capítulos debe estar entre "
            f"{MIN_SCENES} y {MAX_SCENES}."
        )

    try:

        tokenizer, model = load_model()

        # Primer intento
        try:

            return _generate_response(
                tokenizer,
                model,
                idea,
                genre,
                num_scenes,
                retry=False
            )

        except Exception as first_error:

            st.warning(
                "La primera respuesta de Qwen no cumplió "
                "los requisitos. Intentando nuevamente..."
            )

            # Segundo intento
            try:

                return _generate_response(
                    tokenizer,
                    model,
                    idea,
                    genre,
                    num_scenes,
                    retry=True
                )

            except Exception as second_error:

                raise RuntimeError(
                    f"Fallaron los dos intentos. "
                    f"Primer error: {first_error}. "
                    f"Segundo error: {second_error}"
                )

    except Exception as exc:

        st.error(
            f"No fue posible generar la historia con Qwen: {exc}"
        )

        st.warning(
            "Se utilizará una historia de respaldo."
        )

        return _fallback(idea, genre, num_scenes)
