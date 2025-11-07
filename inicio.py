import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px


# Configuración de la página
st.set_page_config(
    page_title="Neonix",
    page_icon="",
    layout="wide"
)

# Página de Inicio con información interactiva (sin navegación)
st.title("Equipo Neonix")

# Descripción breve
st.markdown("""

""")

# Secciones laterales para mejor organización
col1, col2 = st.columns(2)

with col1:
    st.header("🔍 ¿Qué vas a encontrar?")
    st.markdown("""
    - **Proyecto integrador**: Vas a interactuar con información y datos de la tienda Neonix.
    - **Análisis de datos**: Conocerás sobre la evolución de la educación superior en Colombia: Análisis de matrículas 2015-2020.
    - **Pregúntale a la IA**: Por medio de la IA podrás preguntarlr acerca de Neonix y su historia.
    """)

with col2:
    st.header("🚀 Consejo:")
    st.info("¡Puedes darle clic a cualquiera de los títulos para poder ir directamente a la páginas y explorar las secciones a profundida!")

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



# --- Recuperar los datos guardados en sesión desde 2_Analitica.py ---
if "filtered_df" in st.session_state:
    filtered_df = st.session_state["filtered_df"]
else:
    st.warning("⚠️ No se encontró el DataFrame filtrado. Ve primero a la página 'Análisis de Matrículas' para generar los filtros.")
    st.stop()

# También intentamos recuperar el DataFrame completo si lo guardaste
df = st.session_state.get("df", filtered_df)


# Sección 2: Analítica
st.markdown("---")
st.markdown(
    """
    <h2>
        <a href="/Analitica" target="_self" style="text-decoration: none; color: inherit;">
            📊 Educación superior en Colombia: 2015–2020.
        </a>
    </h2>
    """,
    unsafe_allow_html=True
)
st.markdown("La base de datos utilizada corresponde al registro de matrículas en educación superior en Colombia entre los años 2015 y 2020, recopilando información detallada sobre las instituciones de educación superior (IES), los programas académicos, los núcleos de conocimiento, la ubicación geográfica y las características demográficas de los estudiantes. Entre las variables principales se incluyen el año, el nivel académico, la modalidad de estudio, el departamento y municipio de la IES, el programa académico y el género del estudiante.")
st.markdown("El presente programa fue desarrollado con Streamlit y Plotly para ofrecer un entorno interactivo que permite analizar la evolución de la matrícula a lo largo del tiempo. A través de distintos módulos, el usuario puede visualizar y comparar las tendencias de matrícula por género, identificar los programas o instituciones con mayor participación estudiantil, y explorar patrones regionales y académicos. De esta forma, la aplicación facilita la comprensión de los cambios en el acceso a la educación superior en Colombia, aportando una herramienta visual e intuitiva para la toma de decisiones y el análisis educativo.")
st.markdown(
    'A continuación, se compara la participación de hombres y mujeres en la educación superior. '
    'Este análisis permite visualizar cómo ha variado la matrícula por género a lo largo del tiempo.'
)
df = pd.read_csv("data/datos_limpio.csv")
filtered_df_genero = df.copy()



# --- Garantizar que filtered_df exista (si no, usar df)
if 'filtered_df' not in globals():
    filtered_df = df.copy()

filtered_df_genero = filtered_df.copy()

# --- Asegurar tipos correctos ---
for col in ['Id Género', 'Año', 'Total Matriculados']:
    if col in filtered_df_genero.columns:
        filtered_df_genero[col] = pd.to_numeric(filtered_df_genero[col], errors='coerce').fillna(0).astype(int)

# --- Agrupar por año y género ---
line_data = (
    filtered_df_genero
    .groupby(['Año', 'Id Género'], as_index=False)['Total Matriculados']
    .sum()
)

# --- Mapear etiquetas ---
line_data['Género'] = line_data['Id Género'].map({1: 'Hombres', 2: 'Mujeres'})
line_data = line_data.sort_values('Año')

# --- Crear tabla pivote para pestaña Datos ---
pivot_table = line_data.pivot(index='Año', columns='Género', values='Total Matriculados').fillna(0).reset_index()
cols_order = ['Año', 'Hombres', 'Mujeres']
pivot_table = pivot_table[[c for c in cols_order if c in pivot_table.columns]]

# --- Calcular métricas del último año disponible ---
last_year = pivot_table['Año'].max()
last_data = pivot_table[pivot_table['Año'] == last_year].iloc[0]
total_last_year = last_data.get('Hombres', 0) + last_data.get('Mujeres', 0)
pct_women = (last_data.get('Mujeres', 0) / total_last_year * 100) if total_last_year > 0 else 0
pct_men = (last_data.get('Hombres', 0) / total_last_year * 100) if total_last_year > 0 else 0

# --- Mostrar métricas resumen ---
col1, col2, col3 = st.columns(3)
col1.metric("Año más reciente", int(last_year))
col2.metric("Porcentaje Mujeres", f"{pct_women:.1f}%")
col3.metric("Porcentaje Hombres", f"{pct_men:.1f}%")

# --- Formateo legible para tabla ---
display_table = pivot_table.copy()
for c in display_table.columns:
    if c != 'Año':
        display_table[c] = display_table[c].apply(lambda x: f"{int(x):,}")

# --- Pestañas: Gráfico / Datos ---
tab_gender1, tab_gender2 = st.tabs(["Gráfico", "Datos"])

with tab_gender1:

        if "Id Género" not in filtered_df_genero.columns:
            st.warning("No se encontró la columna 'Id Género' en el DataFrame.")
        else:
            df_genero_plot = filtered_df_genero.copy()
            df_genero_plot["Género"] = df_genero_plot["Id Género"].map({1: "Hombres", 2: "Mujeres"})

            line_data = (
                df_genero_plot.groupby(["Año", "Género"], as_index=False)["Total Matriculados"]
                .sum()
                .sort_values("Año")
            )

            fig = px.line(
                line_data,
                x="Año",
                y="Total Matriculados",
                color="Género",
                markers=True,
                title="",
                labels={
                    "Total Matriculados": "Total de Matrículas",
                    "Año": "Año"
                }
            )

            fig.update_layout(
                yaxis_title="Total de Matrículas",
                xaxis_title="Año",
                legend_title="Género",
                hovermode="x unified"
            )

            st.plotly_chart(fig, use_container_width=True)



with tab_gender2:
    st.subheader("Tabla: Matrículas por género y año")
    st.dataframe(display_table, use_container_width=True)



            







# Sección 3: App Gemini
st.markdown("---")
st.header("Interectúa con Neonix.")

st.markdown("La aplicación Pregúntale a Neonix ofrece a los usuarios un asistente virtual con el que pueden interactuar directamente para resolver dudas o conocer más sobre la marca de ropa urbana Neonix. A través de una interfaz sencilla y amigable, el usuario solo debe escribir su pregunta en el campo de texto para recibir una respuesta clara y precisa, basada en la información oficial de la marca. De esta forma, la aplicación actúa como un canal informativo automatizado que facilita la consulta de datos relevantes sin necesidad de navegar por diferentes páginas o documentos.")

st.markdown("Al ingresar, el visitante encontrará una experiencia conversacional dinámica donde Neonix responde de manera contextual y coherente sobre distintos aspectos de la marca, como su historia, productos, filosofía o servicios. Además, la aplicación se actualiza fácilmente al modificar su fuente de información, lo que permite mantener las respuestas al día. En conjunto, Pregúntale a Neonix funciona como una herramienta práctica e intuitiva para mejorar la comunicación entre la marca y sus usuarios, combinando accesibilidad y tecnología de inteligencia artificial.")




# Sección del equipo
st.markdown("---")
st.header("👥 Nuestro Equipo")

col_team1, col_team2, col_team3 = st.columns(3)

with col_team1:
    st.markdown("""
    ### Santiago Díaz
    **Desarrollador**
    """)


with col_team2:
    st.markdown("""
    ### Leandro Acevedo
    **Desarrollador**
    """)

with col_team3:
    st.markdown("""
    ### Mateo González
    **Desarrollador**
    """)

with col_team1:
    st.markdown("""
    ### Javier Restrepo
    **Desarrollador**
    """)


with col_team2:
    st.markdown("""
    ### Luis Miranda
    **Desarrollador**
    """)

