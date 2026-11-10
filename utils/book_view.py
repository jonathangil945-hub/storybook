
from pathlib import Path
import base64
import html
import json
import mimetypes

import streamlit.components.v1 as components


def _file_to_data_uri(file_path):
    """Convierte un archivo local en una URI que puede usar el navegador."""
    if not file_path:
        return None

    path = Path(file_path)

    if not path.is_file():
        return None

    mime_type, _ = mimetypes.guess_type(str(path))
    mime_type = mime_type or "application/octet-stream"

    with open(path, "rb") as file:
        encoded = base64.b64encode(file.read()).decode("utf-8")

    return f"data:{mime_type};base64,{encoded}"


def render_book(story, genre, image_paths, voice_paths, sound_paths):
    """Renderiza el libro digital interactivo."""

    scenes = story.get("scenes", [])

    book_data = []

    for index, scene in enumerate(scenes):
        book_data.append({
            "heading": scene.get("heading", f"Capítulo {index + 1}"),
            "text": scene.get("text", ""),
            "image": _file_to_data_uri(image_paths[index]),
            "voice": _file_to_data_uri(voice_paths[index]),
            "sound": _file_to_data_uri(sound_paths[index]),
        })

    title = html.escape(str(story.get("title", "Un cuento maravilloso")))
    genre_safe = html.escape(str(genre))

    payload = json.dumps(
        book_data,
        ensure_ascii=False
    ).replace("</", "<\\/")

    document = r"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=Cormorant+Garamond:wght@400;500;600;700&family=Great+Vibes&display=swap" rel="stylesheet">

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 20px 12px 30px;
    background:
        radial-gradient(ellipse at center, #60432f 0%, #291c18 65%, #130e0c 100%);
    color: #382619;
    font-family: 'Cormorant Garamond', Georgia, serif;
    min-height: 100vh;
}

button {
    font-family: inherit;
}

.book-shell {
    max-width: 1120px;
    margin: 0 auto;
}

.book-heading {
    text-align: center;
    color: #f5e6c5;
    margin-bottom: 22px;
}

.book-heading .small-label {
    font-family: 'Cinzel', serif;
    font-size: 10px;
    letter-spacing: 5px;
    color: #d5b778;
    text-transform: uppercase;
}

.book-heading h1 {
    font-family: 'Cinzel', serif;
    font-size: clamp(22px, 4vw, 38px);
    font-weight: 500;
    margin: 10px 0 4px;
    text-shadow: 0 3px 12px #000;
}

.book-heading p {
    color: #d9c7a5;
    font-size: 17px;
    margin: 0;
}

.book-stage {
    perspective: 2200px;
    position: relative;
    padding: 12px 0 24px;
}

.book {
    position: relative;
    display: grid;
    grid-template-columns: 1fr 1fr;
    min-height: 610px;
    border-radius: 7px 13px 13px 7px;
    box-shadow:
        0 24px 55px rgba(0,0,0,.55),
        0 4px 8px rgba(0,0,0,.4);
    background: #d9c39a;
    overflow: hidden;
    transition: transform .45s ease;
}

.book::before {
    content: "";
    position: absolute;
    z-index: 5;
    left: 50%;
    top: 0;
    bottom: 0;
    width: 20px;
    transform: translateX(-50%);
    background: linear-gradient(
        90deg,
        rgba(55,34,19,.20),
        rgba(255,246,220,.45),
        rgba(55,34,19,.20)
    );
    pointer-events: none;
}

.page {
    min-width: 0;
    position: relative;
    overflow: hidden;
    padding: 24px;
    background:
        radial-gradient(ellipse at 20% 15%, rgba(255,255,255,.34), transparent 45%),
        radial-gradient(ellipse at 80% 85%, rgba(139,95,48,.12), transparent 45%),
        repeating-linear-gradient(
            0deg,
            rgba(120,83,43,.025) 0px,
            rgba(120,83,43,.025) 1px,
            transparent 1px,
            transparent 4px
        ),
        #f0dfbb;
}

.left-page {
    border-right: 1px solid rgba(104,70,35,.25);
    box-shadow: inset -12px 0 22px rgba(74,48,23,.08);
}

.right-page {
    box-shadow: inset 12px 0 22px rgba(74,48,23,.08);
}

.page::after {
    content: "";
    position: absolute;
    inset: 12px;
    border: 1px solid rgba(153,111,51,.58);
    outline: 1px solid rgba(153,111,51,.18);
    outline-offset: 4px;
    pointer-events: none;
}

.page-content {
    position: relative;
    z-index: 2;
    height: 100%;
}

.ornament {
    text-align: center;
    color: #a17b3e;
    font-family: 'Cinzel', serif;
    letter-spacing: 5px;
    font-size: 13px;
    margin-bottom: 15px;
}

.chapter-label {
    text-align: center;
    color: #99733a;
    text-transform: uppercase;
    font-family: 'Cinzel', serif;
    letter-spacing: 3px;
    font-size: 10px;
    margin: 2px 0 10px;
}

.chapter-title {
    font-family: 'Cinzel', serif;
    font-size: clamp(18px, 2vw, 25px);
    line-height: 1.3;
    text-align: center;
    font-weight: 600;
    color: #56391f;
    margin: 0 0 18px;
}

.story-text {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: clamp(16px, 1.65vw, 20px);
    line-height: 1.55;
    text-align: justify;
    color: #392b20;
    white-space: pre-line;
    overflow-wrap: anywhere;
}

.story-text::first-letter {
    float: left;
    font-family: 'Cinzel', serif;
    font-size: 4.1em;
    line-height: .78;
    padding: 7px 9px 0 0;
    color: #966c2e;
    text-shadow: 1px 1px #e8cf93;
}

.illustration-frame {
    position: relative;
    height: 470px;
    width: 100%;
    border: 5px solid #b28b4b;
    outline: 1px solid #74552d;
    outline-offset: 4px;
    background: #d1bd97;
    box-shadow: 0 9px 22px rgba(50,31,15,.25);
    overflow: hidden;
}

.illustration-frame img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.no-image {
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    color: #80633a;
    text-align: center;
    padding: 20px;
    font-family: 'Cinzel', serif;
}

.no-image span {
    font-size: 55px;
    margin-bottom: 15px;
}

.image-caption {
    text-align: center;
    margin-top: 17px;
    color: #8b6a37;
    font-family: 'Great Vibes', cursive;
    font-size: 27px;
}

.page-number {
    position: absolute;
    bottom: 14px;
    left: 0;
    right: 0;
    text-align: center;
    color: #9b7945;
    font-size: 13px;
    font-style: italic;
}

.cover {
    grid-column: 1 / -1;
    background:
        radial-gradient(ellipse at center, rgba(179,142,80,.12), transparent 65%),
        linear-gradient(135deg, #352319, #67452b 50%, #291a13);
    color: #f4e3bd;
    min-height: 610px;
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 35px;
    position: relative;
}

.cover::before {
    content: "";
    position: absolute;
    inset: 17px;
    border: 2px solid #c7a45f;
    outline: 1px solid rgba(220,190,126,.5);
    outline-offset: 6px;
}

.cover-inner {
    position: relative;
    z-index: 2;
    max-width: 700px;
}

.cover-ornament {
    font-family: 'Cinzel', serif;
    color: #e0bd75;
    letter-spacing: 7px;
    font-size: 14px;
    margin-bottom: 20px;
}

.cover h2 {
    font-family: 'Cinzel', serif;
    font-size: clamp(28px, 5vw, 48px);
    line-height: 1.2;
    font-weight: 500;
    color: #f8e8c4;
    text-shadow: 0 4px 15px #000;
    margin: 15px 0;
}

.cover-image {
    width: min(100%, 430px);
    height: 260px;
    object-fit: cover;
    border: 4px solid #c7a45f;
    box-shadow: 0 12px 30px rgba(0,0,0,.5);
    margin: 15px auto;
}

.cover-genre {
    color: #e1c997;
    font-family: 'Cormorant Garamond', serif;
    font-size: 21px;
    font-style: italic;
    margin-top: 12px;
}

.cover-decoration {
    color: #d5b778;
    font-size: 30px;
    margin: 12px;
}

.end-page {
    grid-column: 1 / -1;
    min-height: 610px;
    background:
        radial-gradient(ellipse at center, #f6e8c9, #e4cda1);
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
}

.end-page h2 {
    font-family: 'Great Vibes', cursive;
    font-size: 85px;
    color: #8a642f;
    margin: 15px 0;
    font-weight: 400;
}

.end-page p {
    font-family: 'Cormorant Garamond', serif;
    font-size: 24px;
    color: #644b2d;
}

.nav-area {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 22px;
    margin-top: 15px;
}

.nav-button {
    border: 1px solid #c9a765;
    color: #f4e5c6;
    background: linear-gradient(145deg, #79542f, #49301e);
    width: 52px;
    height: 52px;
    border-radius: 50%;
    font-size: 27px;
    cursor: pointer;
    box-shadow: 0 5px 15px rgba(0,0,0,.3);
    transition: all .2s ease;
}

.nav-button:hover:not(:disabled) {
    transform: scale(1.09);
    background: #98703d;
}

.nav-button:disabled {
    opacity: .35;
    cursor: not-allowed;
}

.page-indicator {
    color: #e9d5ae;
    font-family: 'Cinzel', serif;
    font-size: 12px;
    letter-spacing: 2px;
    min-width: 135px;
    text-align: center;
}

.audio-panel {
    max-width: 650px;
    margin: 22px auto 0;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}

.audio-card {
    background: rgba(30,20,15,.68);
    border: 1px solid rgba(207,174,112,.4);
    border-radius: 12px;
    padding: 12px 15px;
    color: #f1dfbd;
}

.audio-card strong {
    display: block;
    font-family: 'Cinzel', serif;
    font-size: 10px;
    letter-spacing: 1.5px;
    margin-bottom: 8px;
}

.audio-card span {
    color: #d5bd91;
    font-size: 14px;
}

.audio-status {
    text-align: center;
    color: #ddc99f;
    font-size: 14px;
    margin-top: 12px;
    min-height: 20px;
}

.start-button {
    margin-top: 20px;
    padding: 13px 30px;
    border: 1px solid #e2c27c;
    border-radius: 30px;
    color: #382515;
    background: linear-gradient(135deg, #e8cc8e, #b98a46);
    font-family: 'Cinzel', serif;
    font-weight: 700;
    letter-spacing: 1px;
    font-size: 13px;
    cursor: pointer;
    box-shadow: 0 7px 20px rgba(0,0,0,.35);
}

.start-button:hover {
    filter: brightness(1.1);
    transform: translateY(-2px);
}

.fade-page {
    animation: pageReveal .48s ease both;
}

@keyframes pageReveal {
    from {
        opacity: .25;
        transform: rotateY(-5deg) translateX(12px);
    }
    to {
        opacity: 1;
        transform: rotateY(0) translateX(0);
    }
}


/* ==========================================
   DISEÑO RESPONSIVE PARA CELULARES
========================================== */

@media (max-width: 700px) {

    body {
        padding: 10px 5px 20px;
        background:
            radial-gradient(ellipse at center, #60432f, #211510);
    }

    .book-shell {
        width: 100%;
        max-width: 100%;
    }

    .book-heading {
        margin-bottom: 12px;
        padding: 0 8px;
    }

    .book-heading .small-label {
        font-size: 9px;
        letter-spacing: 3px;
    }

    .book-heading h1 {
        font-size: clamp(20px, 6vw, 29px);
        line-height: 1.3;
    }

    .book-heading p {
        font-size: 15px;
    }

    .book-stage {
        padding: 5px 0 12px;
        perspective: none;
    }

    /* En celular las dos páginas se apilan:
       primero la ilustración y después el texto. */

    .book {
        display: flex;
        flex-direction: column;
        width: 100%;
        min-height: auto;
        border-radius: 7px;
        overflow: hidden;
    }

    .book::before {
        display: none;
    }

    .page {
        width: 100%;
        min-height: auto;
        padding: 25px 23px 45px;
        overflow: visible;
    }

    .left-page {
        border-right: none;
        border-bottom: 1px solid rgba(104,70,35,.35);
        box-shadow: inset 0 -8px 15px rgba(74,48,23,.07);
    }

    .right-page {
        box-shadow: inset 0 8px 15px rgba(74,48,23,.05);
    }

    .page::after {
        inset: 9px;
    }

    .ornament {
        font-size: 12px;
        margin-bottom: 12px;
    }

    .illustration-frame {
        height: clamp(250px, 75vw, 390px);
        width: 100%;
        border-width: 4px;
    }

    .illustration-frame img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .image-caption {
        font-size: 25px;
        margin-top: 14px;
    }

    .chapter-label {
        font-size: 10px;
        letter-spacing: 2px;
    }

    .chapter-title {
        font-size: 23px;
        line-height: 1.35;
        margin-bottom: 20px;
    }

    .story-text {
        font-size: 19px;
        line-height: 1.7;
        text-align: left;
        overflow-wrap: anywhere;
        hyphens: auto;
    }

    .story-text::first-letter {
        font-size: 3.6em;
        padding-right: 7px;
    }

    .page-number {
        bottom: 12px;
        font-size: 12px;
    }

    /* PORTADA */

    .cover {
        min-height: 540px;
        padding: 35px 23px;
    }

    .cover::before {
        inset: 11px;
        outline-offset: 4px;
    }

    .cover-ornament {
        font-size: 10px;
        letter-spacing: 3px;
    }

    .cover h2 {
        font-size: clamp(25px, 8vw, 36px);
        line-height: 1.3;
    }

    .cover-image {
        width: 100%;
        max-width: 340px;
        height: clamp(190px, 58vw, 260px);
        object-fit: cover;
    }

    .cover-genre {
        font-size: 19px;
    }

    .start-button {
        width: 100%;
        max-width: 290px;
        padding: 15px 16px;
        font-size: 12px;
    }

    /* PÁGINA FINAL */

    .end-page {
        min-height: 480px;
        padding: 35px 20px;
    }

    .end-page h2 {
        font-size: 68px;
    }

    .end-page p {
        font-size: 21px;
    }

    /* NAVEGACIÓN */

    .nav-area {
        gap: 15px;
        margin-top: 12px;
    }

    .nav-button {
        width: 47px;
        height: 47px;
        min-width: 47px;
        font-size: 25px;
    }

    .page-indicator {
        font-size: 10px;
        letter-spacing: 1px;
        min-width: 115px;
    }

    /* AUDIO */

    .audio-panel {
        grid-template-columns: 1fr;
        gap: 9px;
        margin-top: 18px;
        padding: 0 5px;
    }

    .audio-card {
        padding: 13px 15px;
    }

    .audio-card strong {
        font-size: 11px;
    }

    .audio-card span {
        font-size: 15px;
    }

    .audio-status {
        font-size: 13px;
        padding: 0 8px;
    }
}

/* ==========================================
   CELULARES PEQUEÑOS
========================================== */

@media (max-width: 380px) {

    .page {
        padding: 22px 17px 42px;
    }

    .illustration-frame {
        height: 245px;
    }

    .story-text {
        font-size: 17px;
        line-height: 1.65;
    }

    .chapter-title {
        font-size: 20px;
    }

    .nav-area {
        gap: 9px;
    }

    .nav-button {
        width: 43px;
        height: 43px;
        min-width: 43px;
    }

    .page-indicator {
        min-width: 105px;
        font-size: 9px;
    }
}

/* ==========================================
   TABLETS
========================================== */

@media (min-width: 701px) and (max-width: 1000px) {

    .book {
        min-height: 560px;
    }

    .page {
        padding: 23px 19px;
    }

    .illustration-frame {
        height: 390px;
    }

    .story-text {
        font-size: 18px;
        line-height: 1.55;
    }

    .chapter-title {
        font-size: 21px;
    }
}

</style>
</head>

<body>

<div class="book-shell">

    <header class="book-heading">
        <div class="small-label">Una historia creada para ti</div>
        <h1>__BOOK_TITLE__</h1>
        <p>__BOOK_GENRE__ · Storybook AI</p>
    </header>

    <main class="book-stage">
        <div class="book" id="book"></div>
    </main>

    <div class="nav-area">
        <button class="nav-button" id="previous" aria-label="Página anterior">‹</button>
        <div class="page-indicator" id="indicator">PORTADA</div>
        <button class="nav-button" id="next" aria-label="Página siguiente">›</button>
    </div>

    <div class="audio-panel">
        <div class="audio-card">
            <strong>✦ NARRACIÓN</strong>
            <span id="voice-status">Lista para comenzar</span>
        </div>
        <div class="audio-card">
            <strong>♫ AMBIENTE SONORO</strong>
            <span id="music-status">Lista para comenzar</span>
        </div>
    </div>

    <div class="audio-status" id="audio-message">
        Pulsa «Comenzar a leer» para activar el sonido.
    </div>

</div>

<script>
const scenes = __BOOK_DATA__;

const title = __TITLE_JS__;
let currentPage = -1;
let readingStarted = false;

let voiceAudio = null;
let musicAudio = null;

const book = document.getElementById("book");
const indicator = document.getElementById("indicator");
const previous = document.getElementById("previous");
const next = document.getElementById("next");

function stopAudio() {
    if (voiceAudio) {
        voiceAudio.pause();
        voiceAudio.currentTime = 0;
        voiceAudio.src = "";
        voiceAudio = null;
    }

    if (musicAudio) {
        musicAudio.pause();
        musicAudio.currentTime = 0;
        musicAudio.src = "";
        musicAudio = null;
    }

    document.getElementById("voice-status").textContent = "Detenida";
    document.getElementById("music-status").textContent = "Detenida";
}

function playChapterAudio(index) {
    stopAudio();

    if (!readingStarted || index < 0 || index >= scenes.length) {
        return;
    }

    const scene = scenes[index];

    if (scene.voice) {
        voiceAudio = new Audio(scene.voice);
        voiceAudio.preload = "auto";

        voiceAudio.play()
            .then(() => {
                document.getElementById("voice-status").textContent =
                    "Reproduciendo capítulo " + (index + 1);
            })
            .catch(() => {
                document.getElementById("voice-status").textContent =
                    "Pulsa continuar para reproducir";
            });

        voiceAudio.onended = () => {
            document.getElementById("voice-status").textContent =
                "Narración finalizada";
        };
    } else {
        document.getElementById("voice-status").textContent =
            "No disponible";
    }

    if (scene.sound) {
        musicAudio = new Audio(scene.sound);
        musicAudio.loop = true;
        musicAudio.volume = 0.30;

        musicAudio.play()
            .then(() => {
                document.getElementById("music-status").textContent =
                    "Ambiente reproduciéndose";
            })
            .catch(() => {
                document.getElementById("music-status").textContent =
                    "No se pudo iniciar";
            });
    } else {
        document.getElementById("music-status").textContent =
            "No disponible";
    }
}

function startReading() {
    readingStarted = true;

    document.getElementById("audio-message").textContent =
        "La aventura ha comenzado. Disfruta tu lectura.";

    if (currentPage === -1) {
        goToPage(0);
    } else {
        playChapterAudio(currentPage);
    }

    renderBook();
}

function createCover() {
    const firstImage = scenes[0] && scenes[0].image
        ? `<img class="cover-image" src="${scenes[0].image}" alt="Portada del cuento">`
        : "";

    return `
        <section class="cover fade-page">
            <div class="cover-inner">
                <div class="cover-ornament">✦ CUENTOS DE FANTASÍA ✦</div>
                <div class="cover-decoration">❦</div>
                <h2>${escapeHTML(title)}</h2>
                ${firstImage}
                <div class="cover-genre">Una aventura extraordinaria</div>
                <div class="cover-decoration">❧</div>
                <button class="start-button" id="start-reading">
                    ✦ COMENZAR A LEER ✦
                </button>
            </div>
        </section>
    `;
}

function createChapter(index) {
    const scene = scenes[index];

    const image = scene.image
        ? `<img src="${scene.image}" alt="Ilustración del capítulo ${index + 1}">`
        : `<div class="no-image"><span>✧</span>La ilustración de este capítulo no está disponible</div>`;

    return `
        <section class="page left-page fade-page">
            <div class="page-content">
                <div class="ornament">❦ ✦ ❦</div>
                <div class="illustration-frame">
                    ${image}
                </div>
                <div class="image-caption">${escapeHTML(scene.heading)}</div>
                <div class="page-number">${index * 2 + 1}</div>
            </div>
        </section>

        <section class="page right-page fade-page">
            <div class="page-content">
                <div class="ornament">✧ ❦ ✧</div>
                <div class="chapter-label">Capítulo ${index + 1}</div>
                <h2 class="chapter-title">${escapeHTML(scene.heading)}</h2>
                <div class="story-text">${escapeHTML(scene.text)}</div>
                <div class="page-number">${index * 2 + 2}</div>
            </div>
        </section>
    `;
}

function createEnding() {
    return `
        <section class="end-page fade-page">
            <div>
                <div class="ornament">❦ ✦ ❦</div>
                <h2>Fin</h2>
                <p>Toda gran aventura deja una historia que recordar.</p>
                <div class="ornament">✧ ❦ ✧</div>
                <button class="start-button" id="back-to-cover">
                    VOLVER A LA PORTADA
                </button>
            </div>
        </section>
    `;
}

function renderBook() {
    if (currentPage === -1) {
        book.innerHTML = createCover();

        document.getElementById("start-reading")
            .addEventListener("click", startReading);

        indicator.textContent = "PORTADA";
    } else if (currentPage >= scenes.length) {
        book.innerHTML = createEnding();

        document.getElementById("back-to-cover")
            .addEventListener("click", () => {
                stopAudio();
                currentPage = -1;
                renderBook();
            });

        indicator.textContent = "FINAL";
    } else {
        book.innerHTML = createChapter(currentPage);

        indicator.textContent =
            `CAPÍTULO ${currentPage + 1} DE ${scenes.length}`;
    }

    previous.disabled = currentPage <= -1;
    next.disabled = currentPage >= scenes.length;

    if (currentPage === -1) {
        previous.disabled = true;
    }
}

function goToPage(newPage) {
    const target = Math.max(-1, Math.min(scenes.length, newPage));

    if (target === currentPage) return;

    const oldPage = currentPage;
    currentPage = target;

    if (oldPage >= 0 && oldPage < scenes.length) {
        stopAudio();
    }

    renderBook();

    if (currentPage >= 0 && currentPage < scenes.length) {
        playChapterAudio(currentPage);
    } else {
        stopAudio();
    }
}

previous.addEventListener("click", () => {
    goToPage(currentPage - 1);
});

next.addEventListener("click", () => {
    if (currentPage === -1) {
        startReading();
    } else {
        goToPage(currentPage + 1);
    }
});

document.addEventListener("keydown", (event) => {
    if (event.key === "ArrowRight") {
        if (currentPage < scenes.length) {
            if (currentPage === -1) {
                startReading();
            } else {
                goToPage(currentPage + 1);
            }
        }
    }

    if (event.key === "ArrowLeft" && currentPage > -1) {
        goToPage(currentPage - 1);
    }
});

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}

renderBook();

// Ajusta automáticamente la altura del componente
// según el contenido de cada capítulo.
function updateFrameHeight() {
    const height = Math.max(
        document.body.scrollHeight,
        document.documentElement.scrollHeight
    );

    window.parent.postMessage({
        isStreamlitMessage: true,
        type: "streamlit:setFrameHeight",
        height: height
    }, "*");
}

// Detecta cuando cambia el tamaño del libro.
const resizeObserver = new ResizeObserver(() => {
    updateFrameHeight();
});

resizeObserver.observe(document.body);

window.addEventListener("load", updateFrameHeight);
window.addEventListener("resize", updateFrameHeight);

updateFrameHeight();
</script>

</body>
</html>
"""

    document = (
        document
        .replace("__BOOK_TITLE__", title)
        .replace("__BOOK_GENRE__", genre_safe)
        .replace("__BOOK_DATA__", payload)
        .replace("__TITLE_JS__", json.dumps(
            str(story.get("title", "Un cuento maravilloso")),
            ensure_ascii=False
        ))
    )

    components.html(
        document,
        height=1400,
        scrolling=False
    )
