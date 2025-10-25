import streamlit as st
import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings

# --- Configuración de la página ---
st.set_page_config(page_title="Pregúntale a Neonix", page_icon="💬", layout="centered")

st.title("💬 Pregúntale a Neonix")
st.markdown("Tu asistente virtual impulsado por IA ⚡ con tecnología Groq (Llama 3)")
st.caption("Basado en la información del archivo `neonix_info.txt`")

# --- Cargar clave desde secrets o entorno ---
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))

if not GROQ_API_KEY:
    st.error("⚠️ No se encontró la clave de API de Groq. Agrégala en `.streamlit/secrets.toml`.")
    st.stop()

# --- Rutas ---
data_path = "data/neonix_info.txt"
index_path = "embeddings/neonix_index.faiss"

# --- Verificar archivo de datos ---
if not os.path.exists(data_path):
    st.error(f"No se encontró `{data_path}`. Asegúrate de crearlo dentro de `/data`.")
    st.stop()

# --- Cargar documentos ---
loader = TextLoader(data_path, encoding="utf-8")
documents = loader.load()

# --- Dividir texto ---
splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
texts = splitter.split_documents(documents)

# --- Crear embeddings con modelo gratuito de HuggingFace ---
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
os.makedirs("embeddings", exist_ok=True)

# --- Cargar o crear índice FAISS ---
if os.path.exists(index_path):
    db = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
else:
    db = FAISS.from_documents(texts, embeddings)
    db.save_local(index_path)

retriever = db.as_retriever()

# --- LLM con Groq (usa modelo Llama3) ---
llm = ChatGroq(model="llama-3.1-8b-instant", api_key=GROQ_API_KEY)

# --- Función de respuesta ---
def retrieve_and_answer(query):
    docs = retriever.invoke(query)
    context = "\n\n".join([d.page_content for d in docs])
    full_prompt = f"""
Eres **Neonix**, el asistente virtual de la marca de ropa urbana *Neonix*.
Responde con precisión y naturalidad, basándote solo en el siguiente contexto:

Contexto:
{context}

Pregunta:
{query}

Respuesta:
"""
    response = llm.invoke(full_prompt)
    return response.content

# --- Interfaz Streamlit ---
query = st.text_input("✍️ Escribe tu pregunta sobre Neonix:")

if query:
    with st.spinner("🧩 Neonix está pensando..."):
        try:
            result = retrieve_and_answer(query)
            st.success(result)
        except Exception as e:
            import traceback
            st.error(f"Ocurrió un error: {e}")
            st.code(traceback.format_exc())


st.divider()
st.caption("💡 Consejo: actualiza el archivo `neonix_info.txt` para entrenar a Neonix con nueva información.")
