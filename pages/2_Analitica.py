import streamlit as st
import pandas as pd
import os
import plotly.express as px

# Configurar página
st.set_page_config(page_title="Análisis de Matrículas", layout="wide")

# Cargar datos CSV al iniciar
csv_path = os.path.join('data', 'MEN_MATRICULA_ESTADISTICA_ES_20250916.csv')
# Leer el CSV como texto y limpiar comas antes de convertir a numérico
df = pd.read_csv(csv_path, encoding='utf-8', dtype=str)  # Leer todo como string inicialmente
for col in ['Id Género', 'Total Matriculados', 'Año']:
    df[col] = df[col].str.replace(',', '').replace('', '0')  # Eliminar comas y manejar vacíos
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)  # Convertir a entero
df = df[df['Total Matriculados'] > 0]  # Filtrar registros vacíos

# Título de la aplicación
st.title("Análisis de Matrículas en Educación Superior")

# Resumen general
st.header("Resumen General")
total_matriculas = df['Total Matriculados'].sum()
por_año = df.groupby('Año')['Total Matriculados'].sum().reset_index()
st.write(f"**Total de Matrículas:** {total_matriculas:,}")
st.subheader("Matrículas por Año")
fig_resumen = px.bar(por_año, x='Año', y='Total Matriculados', title="Matrículas Totales por Año")
st.plotly_chart(fig_resumen, use_container_width=True)

# Filtros interactivos
st.header("Filtros de Datos")
col1, col2, col3 = st.columns(3)

with col1:
    instituciones = sorted(df['Institución de Educación Superior (IES)'].unique().tolist())
    institucion = st.selectbox("Institución", ["Todas"] + instituciones, index=0)
with col2:
    programas = sorted(df['Programa Académico'].unique().tolist())
    programa = st.selectbox("Programa Académico", ["Todos"] + programas, index=0)
with col3:
    departamentos = sorted(df['Departamento de oferta del programa'].unique().tolist())
    departamento = st.selectbox("Departamento", ["Todos"] + departamentos, index=0)

col4, col5, col6 = st.columns(3)
with col4:
    años = sorted(df['Año'].unique().tolist(), reverse=True)
    año = st.selectbox("Año", ["Todos"] + años, index=0)
with col5:
    generos = [{'id': 1, 'label': 'Hombres'}, {'id': 2, 'label': 'Mujeres'}]
    genero_options = ["Todos"] + [g['label'] for g in generos]
    genero = st.selectbox("Género", genero_options, index=0)
with col6:
    municipios = sorted(df['Municipio de oferta del programa'].unique().tolist())
    municipio = st.selectbox("Municipio", ["Todos"] + municipios, index=0)

# Selección de agrupación
group_by = st.selectbox("Agrupar por", ["Año", "Institución de Educación Superior (IES)", "Programa Académico", "Departamento de oferta del programa", "Municipio de oferta del programa"], index=0)

# Filtrar datos
filtered_df = df.copy()
if institucion != "Todas":
    filtered_df = filtered_df[filtered_df['Institución de Educación Superior (IES)'] == institucion]
if programa != "Todos":
    filtered_df = filtered_df[filtered_df['Programa Académico'] == programa]
if departamento != "Todos":
    filtered_df = filtered_df[filtered_df['Departamento de oferta del programa'] == departamento]
if año != "Todos":
    filtered_df = filtered_df[filtered_df['Año'] == int(año)]
if genero != "Todos":
    genero_id = next(g['id'] for g in generos if g['label'] == genero)
    filtered_df = filtered_df[filtered_df['Id Género'] == genero_id]
if municipio != "Todos":
    filtered_df = filtered_df[filtered_df['Municipio de oferta del programa'] == municipio]

# Mostrar datos filtrados
st.header("Resultados Filtrados")
st.write(f"**Total de Registros Filtrados:** {len(filtered_df):,}")
if not filtered_df.empty:
    agrupado = filtered_df.groupby(group_by)['Total Matriculados'].sum().reset_index()
    fig_filtrado = px.bar(agrupado, x=group_by, y='Total Matriculados', title=f"Matrículas por {group_by}")
    st.plotly_chart(fig_filtrado, use_container_width=True)
else:
    st.warning("No hay datos que cumplan con los filtros seleccionados.")

# Mostrar datos crudos (opcional)
if st.checkbox("Mostrar datos filtrados"):
    st.dataframe(filtered_df)