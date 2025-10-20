import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os
from datetime import datetime

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Pregúntale a Neonix", page_icon="🧢", layout="centered")

# --- CARGA DEL MODELO (LIGERO) ---
@st.cache_resource
def load_model():
    model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # Modelo liviano y gratuito (~500 MB)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float32)
    model.to("cpu")
    return tokenizer, model

tokenizer, model = load_model()

# --- CARGAR INFORMACIÓN DE LA MARCA ---
ruta_datos = os.path.join("data", "neonix_info.txt")

if not os.path.exists(ruta_datos):
    st.error(f"No se encontró el archivo de información en {ruta_datos}")
    st.stop()

with open(ruta_datos, "r", encoding="utf-8") as f:
    neonix_info = f.read()

# --- INTERFAZ ---
st.markdown("📁 **Información de marca actualizada por última vez:** " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
st.title("🧢 Pregúntale a Neonix")
st.write("Tu asistente virtual de la marca **Neonix**. Pregunta lo que quieras sobre nuestros productos, estilo o filosofía urbana.")

# --- HISTORIAL ---
if "history" not in st.session_state:
    st.session_state["history"] = []

# --- ENTRADA DEL USUARIO ---
user_input = st.text_input("🗣️ Escribe tu pregunta aquí:", "")

# --- PROCESAMIENTO ---
if user_input:
    with st.spinner("🌀 Neonix está pensando..."):
        prompt = f"""
Eres Neonix, el asistente virtual de la marca de ropa urbana "Neonix".
Usa la siguiente información para responder las preguntas de los usuarios:

{neonix_info}

Pregunta del usuario: {user_input}
Respuesta:
"""
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
        outputs = model.generate(**inputs, max_new_tokens=150)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Limpiar respuesta (solo mostrar parte final)
        if "Respuesta:" in response:
            response = response.split("Respuesta:")[-1].strip()

        st.session_state["history"].append({"usuario": user_input, "neonix": response})
        st.success(response)

# --- HISTORIAL DE CONVERSACIÓN ---
if st.session_state["history"]:
    st.markdown("### 💬 Conversaciones anteriores")
    for chat in reversed(st.session_state["history"]):
        st.markdown(f"**Tú:** {chat['usuario']}")
        st.markdown(f"**🧢 Neonix:** {chat['neonix']}")
        st.markdown("---")
