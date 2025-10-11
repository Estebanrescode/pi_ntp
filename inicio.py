import streamlit as st
import numpy as np
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Mi Aplicación",
    page_icon="🏠",
    layout="wide"
)

# Página de Inicio con información interactiva (sin navegación)
st.title("🏠 Bienvenido a Mi Aplicación - Inicio")

# Descripción breve
st.markdown("""
Esta es la página de inicio de mi aplicación desarrollada con Streamlit. Aquí puedes explorar las funcionalidades principales de manera interactiva.
""")

# Secciones laterales para mejor organización
col1, col2 = st.columns(2)

with col1:
    st.header("🔍 ¿Qué puedes hacer?")
    st.markdown("""
    - **Explorar datos**: Analiza gráficos y estadísticas en tiempo real.
    - **Interactuar**: Usa controles personalizados para experimentar.
    - **Aprender**: Encuentra tutoriales y guías integradas.
    """)

with col2:
    st.header("🚀 Comenzar rápido")
    st.info("Explora las secciones abajo para interactuar con cada tema.")

# Sección 1: Proyecto Integrador
st.markdown("---")
st.header("📋 Proyecto Integrador")

st.markdown("""
**Descripción**: Este proyecto integra conceptos de desarrollo web, análisis de datos y IA para crear una aplicación completa. 
Es el corazón de esta app, donde se unen todas las herramientas.
""")
# Elemento interactivo: Selector para etapas del proyecto
etapa = st.selectbox("Selecciona una etapa del proyecto:", ["Planificación", "Desarrollo", "Pruebas", "Despliegue"])
if etapa == "Planificación":
    st.success("En esta etapa, definimos objetivos y recursos. ¡Interactúa para ver un checklist!")
    st.checkbox("Definir objetivos")
    st.checkbox("Asignar roles al equipo")
elif etapa == "Desarrollo":
    st.info("Aquí codificamos con Python y Streamlit. Prueba un botón de simulación.")
    if st.button("Simular commit de código"):
        st.balloons()
elif etapa == "Pruebas":
    st.warning("Realizamos pruebas unitarias y de integración. ¡Verifica el estado!")
    st.progress(75)
elif etapa == "Despliegue":
    st.success("¡Listo para producción! Simula el deploy.")
    if st.button("Simular despliegue"):
        st.success("¡Desplegado exitosamente! 🚀")

# Sección 2: Analítica
st.markdown("---")
st.header("📊 Analítica")

st.markdown("""
**Descripción**: Sección dedicada al análisis de datos con visualizaciones interactivas y métricas clave.
""")
# Elemento interactivo: Gráfico simple de ejemplo
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['A', 'B', 'C']
)
st.line_chart(chart_data)
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric("Ventas Totales", "1,234", "8%")
with col_m2:
    st.metric("Usuarios Activos", "567", "-2%")
with col_m3:
    st.metric("Tasa de Conversión", "3.2%", "1.5%")

# Sección 3: App Gemini
st.markdown("---")
st.header("🤖 App Gemini")

st.markdown("""
**Descripción**: Integración con Google Gemini para generación de texto y chat IA. (Nota: Requiere API key para funcionalidad completa).
""")
# Elemento interactivo: Input de texto simulado
prompt = st.text_input("Escribe un prompt para Gemini:")
if st.button("Generar respuesta (simulada)"):
    st.write(f"Respuesta simulada de Gemini: '¡Hola! Tu prompt sobre {prompt} es genial. En un entorno real, generaría contenido personalizado.'")
st.info("Para producción, usa la API de Google Gemini con tu clave.")

# Sección 4: App Google Sheet
st.markdown("---")
st.header("📈 App Google Sheet")

st.markdown("""
**Descripción**: Conexión con Google Sheets para importar/exportar datos en tiempo real.
""")
# Elemento interactivo: Selector de hoja simulada
hoja = st.selectbox("Selecciona una hoja de Google Sheets:", ["Ventas Q1", "Usuarios", "Inventario"])
if hoja:
    st.success(f"Datos cargados de '{hoja}'. Ejemplo de tabla:")
    st.dataframe(pd.DataFrame({
        'Columna1': [10, 20, 30],
        'Columna2': [100, 200, 300]
    }))
st.info("Usa gspread para integración real con autenticación OAuth.")

# Sección del equipo
st.markdown("---")
st.header("👥 Nuestro Equipo")

col_team1, col_team2, col_team3 = st.columns(3)

with col_team1:
    st.markdown("""
    ### Juan Pérez
    **Desarrollador Principal**
    """)
    st.image("https://via.placeholder.com/150x150?text=Juan+Pérez", use_column_width=True)
    st.markdown("""
    Experto en Python y Streamlit con más de 5 años de experiencia. Apasionado por la IA y el análisis de datos.
    """)

with col_team2:
    st.markdown("""
    ### María López
    **Diseñadora UX/UI**
    """)
    st.image("https://via.placeholder.com/150x150?text=María+López", use_column_width=True)
    st.markdown("""
    Especialista en interfaces intuitivas. Crea experiencias de usuario memorables y accesibles.
    """)

with col_team3:
    st.markdown("""
    ### Carlos García
    **Analista de Datos**
    """)
    st.image("https://via.placeholder.com/150x150?text=Carlos+García", use_column_width=True)
    st.markdown("""
    Maestro en el manejo de grandes volúmenes de datos. Transforma números en insights accionables.
    """)

# Pie de página
st.markdown("---")
st.markdown("Desarrollado con ❤️ usando Streamlit en Python.")