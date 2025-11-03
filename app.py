import streamlit as st
import pandas as pd
from textblob import TextBlob
import re
from deep_translator import GoogleTranslator  # ✅ reemplazo moderno y 100 % compatible

# Configuración de la página
st.set_page_config(
    page_title="Taylor Text Analyzer 💌",
    page_icon="🎶",
    layout="wide"
)

# Título y descripción
st.title("🎤 Taylor Text Analyzer")
st.markdown("""
Convierte tus textos o letras en emociones al estilo de Taylor Swift ✨  
Esta aplicación analiza sentimientos, subjetividad y palabras clave —  
como si fueran versos de *All Too Well* o *Lover*. 💫
""")

# Barra lateral
st.sidebar.title("Opciones de análisis")
modo = st.sidebar.selectbox(
    "Selecciona cómo quieres analizar tu texto:",
    ["Texto directo", "Archivo de texto"]
)

# Función para contar palabras
def contar_palabras(texto):
    stop_words = set([
        "a","al","de","del","la","las","lo","los","y","o","el","ella","ellos",
        "como","en","por","para","the","and","is","to","of","in","that","it","with",
        "on","this","was","for","as","be","are","at","by","from"
    ])
    palabras = re.findall(r'\b\w+\b', texto.lower())
    palabras_filtradas = [p for p in palabras if p not in stop_words and len(p) > 2]
    contador = {}
    for palabra in palabras_filtradas:
        contador[palabra] = contador.get(palabra, 0) + 1
    contador_ordenado = dict(sorted(contador.items(), key=lambda x: x[1], reverse=True))
    return contador_ordenado, palabras_filtradas

# ✅ Traductor actualizado
def traducir_texto(texto):
    try:
        return GoogleTranslator(source='auto', target='en').translate(texto)
    except Exception as e:
        st.error(f"Error al traducir: {e}")
        return texto

# Procesar texto con TextBlob
def procesar_texto(texto):
    texto_original = texto
    texto_ingles = traducir_texto(texto)
    blob = TextBlob(texto_ingles)
    sentimiento = blob.sentiment.polarity
    subjetividad = blob.sentiment.subjectivity
    frases_originales = [f.strip() for f in re.split(r'[.!?]+', texto_original) if f.strip()]
    frases_traducidas = [f.strip() for f in re.split(r'[.!?]+', texto_ingles) if f.strip()]

    frases_combinadas = []
    for i in range(min(len(frases_originales), len(frases_traducidas))):
        frases_combinadas.append({
            "original": frases_originales[i],
            "traducido": frases_traducidas[i]
        })

    contador_palabras, palabras = contar_palabras(texto_ingles)
    return {
        "sentimiento": sentimiento,
        "subjetividad": subjetividad,
        "frases": frases_combinadas,
        "contador_palabras": contador_palabras,
        "palabras": palabras,
        "texto_original": texto_original,
        "texto_traducido": texto_ingles
    }

# Visualizaciones
def crear_visualizaciones(resultados):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💖 Emociones al estilo Taylor")
        sentimiento_norm = (resultados["sentimiento"] + 1) / 2
        st.write("**Sentimiento:**")
        st.progress(sentimiento_norm)
        if resultados["sentimiento"] > 0.05:
            st.success(f"✨ Positivo ({resultados['sentimiento']:.2f}) — vibra *Lover* 💕")
        elif resultados["sentimiento"] < -0.05:
            st.error(f"💔 Negativo ({resultados['sentimiento']:.2f}) — tono *All Too Well* 🥀")
        else:
            st.info(f"😐 Neutral ({resultados['sentimiento']:.2f}) — *Blank Space* vibes")

        st.write("**Subjetividad:**")
        st.progress(resultados["subjetividad"])
        if resultados["subjetividad"] > 0.5:
            st.warning(f"💭 Alta subjetividad ({resultados['subjetividad']:.2f}) — muy personal 📝")
        else:
            st.info(f"📋 Objetivo ({resultados['subjetividad']:.2f}) — más analítico 🎯")

    with col2:
        st.subheader("🎶 Palabras más usadas en tu letra")
        if resultados["contador_palabras"]:
            top_palabras = dict(list(resultados["contador_palabras"].items())[:10])
            st.bar_chart(top_palabras)

    st.subheader("🪞 Traducción de tu letra")
    with st.expander("Ver traducción completa"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Versión Original:**")
            st.text(resultados["texto_original"])
        with col2:
            st.markdown("**Versión en Inglés:**")
            st.text(resultados["texto_traducido"])

    st.subheader("✨ Versos detectados")
    for i, frase_dict in enumerate(resultados["frases"][:8], 1):
        frase_original = frase_dict["original"]
        frase_traducida = frase_dict["traducido"]
        blob_frase = TextBlob(frase_traducida)
        sent = blob_frase.sentiment.polarity
        emoji = "💗" if sent > 0.05 else ("💔" if sent < -0.05 else "😶")
        st.write(f"{i}. {emoji} **Original:** *\"{frase_original}\"*")
        st.write(f"   **Traducción:** *\"{frase_traducida}\"* (Sentimiento: {sent:.2f})")
        st.write("---")

# Modo principal
if modo == "Texto directo":
    st.subheader("✏️ Escribe tu texto o letra")
    texto = st.text_area("", height=200, placeholder="Escribe algo como si fuera una canción de Taylor...")
    if st.button("Analizar texto"):
        if texto.strip():
            with st.spinner("Analizando tu letra..."):
                resultados = procesar_texto(texto)
                crear_visualizaciones(resultados)
        else:
            st.warning("Por favor, escribe algo para analizar.")
else:
    st.subheader("📂 Carga un archivo de texto (letra o historia)")
    archivo = st.file_uploader("", type=["txt", "csv", "md"])
    if archivo is not None:
        try:
            contenido = archivo.getvalue().decode("utf-8")
            with st.expander("Vista previa del archivo"):
                st.text(contenido[:1000] + ("..." if len(contenido) > 1000 else ""))
            if st.button("Analizar archivo"):
                with st.spinner("Analizando contenido..."):
                    resultados = procesar_texto(contenido)
                    crear_visualizaciones(resultados)
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")

# Información
with st.expander("📚 Acerca del análisis"):
    st.markdown("""
    ### Cómo interpreta Taylor tus letras:
    - **Sentimiento:** desde 💔 triste hasta 💖 feliz.
    - **Subjetividad:** cuánta emoción personal hay en tus versos.
    - **Frecuencia de palabras:** las más repetidas suelen ser las más sentidas.
    """)

st.markdown("---")
st.caption("Desarrollado con 💌 por Migue — inspirado en la magia de Taylor Swift 🎶")
