import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq


# === CONFIGURACIÓN DE LA PÁGINA ===
st.set_page_config(page_title="Pregúntale a Neonix", page_icon="💬", layout="centered")

st.title("💬 Pregúntale a Neonix")
st.markdown("Tu asistente virtual impulsado por IA local 🧠")
st.caption("Basado en la información del archivo `neonix_info.txt`")


# === CARGAR VARIABLES DE ENTORNO ===
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("⚠️ No se encontró la variable `GROQ_API_KEY` en el archivo `.env`.")
    st.stop()


# === RUTAS ===
data_path = "data/neonix_info.txt"
index_path = "embeddings/neonix_index.faiss"


# === VERIFICAR EXISTENCIA DEL ARCHIVO DE DATOS ===
if not os.path.exists(data_path):
    st.error(f"No se encontró `{data_path}`. Crea el archivo dentro de la carpeta `/data` con información sobre Neonix.")
    st.stop()


# === CARGAR DOCUMENTOS ===
loader = TextLoader(data_path, encoding="utf-8")
documents = loader.load()


# === DIVIDIR TEXTO EN FRAGMENTOS ===
splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
texts = splitter.split_documents(documents)


# === CREAR O CARGAR EMBEDDINGS ===
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
os.makedirs("embeddings", exist_ok=True)

if os.path.exists(index_path):
    db = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
else:
    db = FAISS.from_documents(texts, embeddings)
    db.save_local(index_path)

retriever = db.as_retriever()


# === CONFIGURAR MODELO GROQ ===
llm = ChatGroq(model="llama-3.1-8b-instant", api_key=GROQ_API_KEY)


# === FUNCIÓN DE RESPUESTA ===
def retrieve_and_answer(query):
    docs = retriever.invoke(query)
    context = "\n\n".join([d.page_content for d in docs])
    full_prompt = f"""
Eres **Neonix**, el asistente virtual oficial de la marca de ropa urbana *Neonix*.
Tu tarea es responder con precisión, usando solo la siguiente información de contexto.

Contexto:
{context}

Pregunta:
{query}

Respuesta:
"""
    response = llm.invoke(full_prompt)
    return response.content

# === INTERFAZ DE USUARIO ===
query = st.text_input("✍️ Escribe tu pregunta sobre Neonix:")

if query:
    with st.spinner("🧩 Neonix está pensando..."):
        try:
            result = retrieve_and_answer(query)
            st.success(result)
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

st.divider()
st.caption("💡 Consejo: puedes actualizar el archivo `neonix_info.txt` para entrenar a Neonix con nueva información.")
