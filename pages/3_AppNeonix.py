import streamlit as st
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
import os


# --- Configuración de la página ---
st.set_page_config(page_title="Pregúntale a Neonix", page_icon="💬", layout="centered")

st.title("💬 Pregúntale a Neonix")
st.markdown("Tu asistente virtual impulsado por IA local 🧠")
st.caption("Basado en la información del archivo `neonix_info.txt`")

# --- Rutas ---
data_path = "data/neonix_info.txt"
index_path = "embeddings/neonix_index.faiss"

# --- Verificar existencia del archivo ---
if not os.path.exists(data_path):
    st.error(f"No se encontró `{data_path}`. Crea el archivo dentro de la carpeta `/data` con información sobre Neonix.")
    st.stop()

# --- Cargar documentos ---
loader = TextLoader(data_path, encoding="utf-8")
documents = loader.load()

# --- Dividir texto en fragmentos ---
splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
texts = splitter.split_documents(documents)

# --- Crear embeddings ---
embeddings = OllamaEmbeddings(model="llama3")
os.makedirs("embeddings", exist_ok=True)

# --- Cargar o crear el índice FAISS ---
if os.path.exists(index_path):
    db = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
else:
    db = FAISS.from_documents(texts, embeddings)
    db.save_local(index_path)

retriever = db.as_retriever()

# --- Configurar modelo LLM ---
llm = Ollama(model="llama3")

# --- Función para obtener respuesta sin usar create_retrieval_chain ---
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
    return response

# --- Interfaz de usuario ---
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
