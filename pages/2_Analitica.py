import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import unicodedata 

st.set_page_config(page_title="Análisis de Matrículas", layout="wide")

csv_path = os.path.join('data/datos_limpio.csv')

df = pd.read_csv(csv_path, encoding='utf-8', dtype=str) 
for col in ['Id Género', 'Total Matriculados', 'Año']:
    df[col] = df[col].str.replace(',', '').replace('', '0') 
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int) 
df = df[df['Total Matriculados'] > 0]  

@st.cache_data  
def load_municipios_coords():
    url = 'https://www.datos.gov.co/api/views/vafm-j2df/rows.csv?accessType=DOWNLOAD'
    try:
        mun_df = pd.read_csv(url, encoding='utf-8')
      
        mun_df['LATITUD'] = pd.to_numeric(mun_df['LATITUD'], errors='coerce')
        mun_df['LONGITUD'] = pd.to_numeric(mun_df['LONGITUD'], errors='coerce')
        mun_df = mun_df.dropna(subset=['LATITUD', 'LONGITUD'])  
        
        def normalize_name(name):
            return unicodedata.normalize('NFKD', str(name)).encode('ascii', 'ignore').decode('utf-8').upper().strip()
        
        mun_df['NOM_MPIO_norm'] = mun_df['NOM_MPIO'].apply(normalize_name)
        mun_df['NOM_DPTO_norm'] = mun_df['NOM_DPTO'].apply(normalize_name)
        mun_df['key_norm'] = mun_df['NOM_MPIO_norm'] + ' - ' + mun_df['NOM_DPTO_norm']
        
        coords_dict = dict(zip(mun_df['key_norm'], zip(mun_df['LATITUD'], mun_df['LONGITUD'])))
        
        fallback = {
            'BOGOTA - BOGOTA D.C.': (4.60971, -74.08175),
            'MEDELLIN - ANTIOQUIA': (6.25184, -75.56359),
            'CALI - VALLE DEL CAUCA': (3.43722, -76.5225),
        }
        coords_dict.update(fallback)
        
        #st.success(f"Coordenadas cargadas: {len(coords_dict)} entradas.")
        return coords_dict, mun_df  
    
    except Exception as e:
        st.error(f"Error cargando coordenadas: {e}. Usando fallback.")
        fallback = {
            'BOGOTA - BOGOTA D.C.': (4.60971, -74.08175),
            'MEDELLIN - ANTIOQUIA': (6.25184, -75.56359),
            'CALI - VALLE DEL CAUCA': (3.43722, -76.5225),
        }
        return fallback, pd.DataFrame()  

coords_dict, mun_coords_df = load_municipios_coords()

st.title("Análisis de Matrículas en Educación Superior")

st.header("Resumen General")
total_matriculas = df['Total Matriculados'].sum()
st.write(f"**Total de Matrículas:** {total_matriculas:,}")

st.subheader("Matrículas por Año")
años_min = df['Año'].min()
años_max = df['Año'].max()
año_range = st.slider("Rango de Años", min_value=años_min, max_value=años_max, value=(años_min, años_max))
por_año = df.groupby('Año')['Total Matriculados'].sum().reset_index()
por_año_filtrado = por_año[(por_año['Año'] >= año_range[0]) & (por_año['Año'] <= año_range[1])]

if not por_año_filtrado.empty:
    tab1, tab2 = st.tabs(["📈 Gráfico", "🗃 Datos"])
    
    with tab1:
        st.subheader("Matrículas Totales por Año")
        st.bar_chart(por_año_filtrado.set_index('Año'))
    
    with tab2:
        st.dataframe(por_año_filtrado)
else:
    st.warning("No hay datos en el rango de años seleccionado.")

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

group_by = st.selectbox("Agrupar por", ["Año", "Institución de Educación Superior (IES)", "Programa Académico", "Departamento de oferta del programa", "Municipio de oferta del programa"], index=0)

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

st.header("Resultados Filtrados")
st.write(f"**Total de Registros Filtrados:** {len(filtered_df):,}")
if not filtered_df.empty:
    agrupado = filtered_df.groupby(group_by)['Total Matriculados'].sum().reset_index()
    tab3, tab4 = st.tabs(["📈 Gráfico", "🗃 Datos"])
    
    with tab3:
        st.subheader(f"Matrículas por {group_by}")
        st.bar_chart(agrupado.set_index(group_by))
    
    with tab4:
        st.dataframe(filtered_df)
else:
    st.warning("No hay datos que cumplan con los filtros seleccionados.")

st.header("Mapa de Ubicaciones de Universidades")
if not filtered_df.empty and coords_dict:
   
    def normalize_name(name):
        return unicodedata.normalize('NFKD', str(name)).encode('ascii', 'ignore').decode('utf-8').upper().strip()
    
    filtered_df['key_norm'] = filtered_df['Municipio de oferta del programa'].apply(normalize_name) + ' - ' + filtered_df['Departamento de oferta del programa'].apply(normalize_name)
    
    ies_mun = filtered_df.groupby(['Institución de Educación Superior (IES)', 'key_norm'])['Total Matriculados'].sum().reset_index()
    ies_principal = ies_mun.loc[ies_mun.groupby('Institución de Educación Superior (IES)')['Total Matriculados'].idxmax()]
  
    ies_total = filtered_df.groupby('Institución de Educación Superior (IES)')['Total Matriculados'].sum().reset_index()
    
    map_data = ies_principal.merge(ies_total, on='Institución de Educación Superior (IES)')
    map_data = map_data[map_data['key_norm'].isin(coords_dict)]  
    map_data = map_data.rename(columns={'Total Matriculados_x': 'Total IES', 'Total Matriculados_y': 'Total Municipio'})
    
    if not map_data.empty:
        lats, lons, texts, sizes = [], [], [], []
        for _, row in map_data.iterrows():
            lat, lon = coords_dict[row['key_norm']]
            total = int(row['Total IES'])
            lats.append(lat)
            lons.append(lon)
            texts.append(f"{row['Institución de Educación Superior (IES)']}: {total:,} matrículas<br>(Sede principal: {row['key_norm']})")
            size = max(5, min(25, (total / map_data['Total IES'].max()) * 20 + 5))
            sizes.append(size)
        
        fig_mapa = go.Figure(go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=sizes,
                color='blue',
                opacity=0.7,
                sizeref=2 
            ),
            text=texts,
            hovertemplate='<b>%{text}</b><extra></extra>',
        ))

        fig_mapa.update_layout(
            autosize=True,
            hovermode='closest',
            mapbox=dict(
                style="open-street-map",
                bearing=0,
                center=dict(
                    lat=4.6,  
                    lon=-74
                ),
                pitch=0,
                zoom=5
            ),
            title="Ubicaciones de Universidades (tamaño = total matrículas; navega con zoom y pan)",
        )

        st.plotly_chart(fig_mapa, use_container_width=True)
        
        st.info(f"Mostrando {len(map_data)} universidades. Total IES filtradas: {len(ies_total)}")