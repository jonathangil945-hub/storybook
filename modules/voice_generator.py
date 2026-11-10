
from pathlib import Path
import streamlit as st
import pyttsx3
import wave

OUT = Path("outputs/audio")
OUT.mkdir(parents=True, exist_ok=True)

# ==========================================
# CONFIGURACIÓN DE LA NARRACIÓN
# ==========================================

VOICE_RATE = 155
MIN_DURATION = 60  # Duración mínima deseada en segundos


# ==========================================
# GENERAR VOZ
# ==========================================

def generate_voice(text, index):

    path = OUT / f"voice_{index + 1}.wav"

    if not text or not text.strip():
        raise ValueError("El texto de la narración está vacío.")

    engine = None

    try:

        # Inicializar motor de voz de Windows
        engine = pyttsx3.init(driverName="sapi5")

        # ======================================
        # SELECCIONAR VOZ EN ESPAÑOL
        # ======================================

        voices = engine.getProperty("voices")

        spanish_voice = None

        for voice in voices:

            name = (voice.name or "").lower()
            voice_id = (voice.id or "").lower()

            if any(word in name + voice_id for word in [
                "spanish",
                "español",
                "sabina",
                "helena",
                "pablo"
            ]):

                spanish_voice = voice.id
                break

        if spanish_voice:
            engine.setProperty("voice", spanish_voice)

        # ======================================
        # CONFIGURAR VELOCIDAD Y VOLUMEN
        # ======================================

        engine.setProperty("rate", VOICE_RATE)
        engine.setProperty("volume", 1.0)

        # ======================================
        # GENERAR ARCHIVO
        # ======================================

        engine.save_to_file(
            text.strip(),
            str(path.resolve())
        )

        engine.runAndWait()

        engine.stop()
        engine = None

        # ======================================
        # VALIDAR AUDIO
        # ======================================

        if not path.exists() or path.stat().st_size < 1000:
            raise RuntimeError(
                "Windows no produjo un archivo de audio válido."
            )

        # Obtener duración real del audio WAV
        with wave.open(str(path), "rb") as audio:

            frames = audio.getnframes()
            sample_rate = audio.getframerate()

            duration = frames / float(sample_rate)

        word_count = len(text.split())

        message = (
            f"Voz local de Windows (SAPI5) | "
            f"Velocidad: {VOICE_RATE} palabras/minuto aprox. | "
            f"Palabras: {word_count} | "
            f"Duración real: {duration:.1f} segundos"
        )

        if duration < MIN_DURATION:

            message += (
                " | Aviso: la narración dura menos de un minuto."
            )

        return path, message

    except Exception as exc:

        raise RuntimeError(
            f"No se pudo generar la narración. "
            f"Comprueba las voces instaladas en Windows. "
            f"Detalle: {exc}"
        )

    finally:

        if engine is not None:

            try:
                engine.stop()
            except Exception:
                pass
