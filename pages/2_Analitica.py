import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go
import plotly.express as px  # Agregado para el gráfico de torta
import unicodedata 

st.set_page_config(page_title="Análisis de Matrículas", layout="wide")

# CSS personalizado para hacer los selectores más atractivos con colores y barras
st.markdown("""
<style>
    .filter-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        color: white;
    }
    .filter-title {
        font-size: 1.2em;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .stSelectbox > div > div > div > select {
        background-color: #f0f2f6;
        border-radius: 5px;
        border: 2px solid #667eea;
        padding: 0.5rem;
        font-weight: bold;
    }
    .stSelectbox > label {
        color: #333;
        font-weight: bold;
    }https://neonix.streamlit.app/Analiticahttps://neonix.streamlit.app/Analitica
    .emoji-filter {
        font-size: 1.5em;
        margin-right: 0.5rem;
    }
    .plotly-chart {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

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

st.title("Evolución de la educación superior en Colombia: Análisis de matrículas 2015-2020")

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
        
        # Gráfico de Línea Embellecido con Plotly (sugerencia más bonita para tendencias temporales)
        fig_line = px.line(por_año_filtrado, 
                           x='Año', 
                           y='Total Matriculados', 
                           title='Evolución de Matrículas Totales por Año',
                           markers=True,  # Puntos en la línea para resaltar datos
                           line_shape='spline',  # Curva suave para belleza
                           color_discrete_sequence=['#636EFA'])  # Color azul moderno
        
        fig_line.update_traces(line=dict(width=4), marker=dict(size=8))  # Grosor y tamaño
        fig_line.update_layout(
            xaxis_title='Año',
            yaxis_title='Total Matriculados',
            font=dict(size=12, family='Arial'),
            title_font_size=20,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            hovermode='x unified',  # Hover unificado
            showlegend=False  # Sin leyenda para simplicidad
        )
        st.plotly_chart(fig_line, use_container_width=True)
        
        # Gráfico de torta agregado en posición 2 (debajo del bar chart)
        st.subheader("Porcentaje total de Matrículas por Año.")
        fig_torta = px.pie(por_año_filtrado, 
                           values='Total Matriculados', 
                           names='Año', 
                           color_discrete_sequence=px.colors.qualitative.Set3)  # Colores diferentes
        
        fig_torta.update_traces(textposition='inside', textinfo='percent+label')
        fig_torta.update_layout(width=800, height=600, font=dict(size=14))
        st.plotly_chart(fig_torta, use_container_width=True)
    
    with tab2:
        st.dataframe(por_año_filtrado)
else:
    st.warning("No hay datos en el rango de años seleccionado.")

# Sección de Filtros Mejorada con Estilo Visual
st.header("🔍 Filtros Generales")
# Contenedor principal con gradiente colorido
with st.container():
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.markdown('<p class="filter-title">Selecciona tus criterios para filtrar los datos</p>', unsafe_allow_html=True)
    
    # Fila 1: Institución, Programa, Departamento
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<span class="emoji-filter">🏫</span>', unsafe_allow_html=True)
        instituciones = sorted(df['Institución de Educación Superior (IES)'].unique().tolist())
        institucion = st.selectbox("Institución", ["Todas"] + instituciones, index=0, help="Selecciona una universidad específica")
    
    with col2:
        st.markdown('<span class="emoji-filter">📚</span>', unsafe_allow_html=True)
        programas = sorted(df['Programa Académico'].unique().tolist())
        programa = st.selectbox("Programa Académico", ["Todos"] + programas, index=0, help="Elige un programa de estudio")
    
    with col3:
        st.markdown('<span class="emoji-filter">🗺️</span>', unsafe_allow_html=True)
        departamentos = sorted(df['Departamento de oferta del programa'].unique().tolist())
        departamento = st.selectbox("Departamento", ["Todos"] + departamentos, index=0, help="Filtra por región del país")
    
    # Fila 2: Año, Género, Municipio
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown('<span class="emoji-filter">📅</span>', unsafe_allow_html=True)
        años = sorted(df['Año'].unique().tolist(), reverse=True)
        año = st.selectbox("Año", ["Todos"] + años, index=0, help="Año académico específico")
    
    with col5:
        st.markdown('<span class="emoji-filter">👥</span>', unsafe_allow_html=True)
        generos = [{'id': 1, 'label': 'Hombres'}, {'id': 2, 'label': 'Mujeres'}]
        genero_options = ["Todos"] + [g['label'] for g in generos]
        genero = st.selectbox("Género", genero_options, index=0, help="Filtrar análisis por género de forma independiente (no afecta filtros principales)")
    
    with col6:
        st.markdown('<span class="emoji-filter">🏙️</span>', unsafe_allow_html=True)
        municipios = sorted(df['Municipio de oferta del programa'].unique().tolist())
        municipio = st.selectbox("Municipio", ["Todos"] + municipios, index=0, help="Ciudad o municipio exacto")
    
    # Selector de Agrupación con estilo
    st.markdown('<span class="emoji-filter">📊</span>', unsafe_allow_html=True)
    group_by = st.selectbox("Agrupar por", ["Año", "Institución de Educación Superior (IES)", "Programa Académico", "Departamento de oferta del programa", "Municipio de oferta del programa"], index=0, help="Cómo agrupar los resultados")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Barra de progreso visual para filtros aplicados (ejemplo simple basado en cuántos filtros no son "Todos")
filtros_aplicados = sum([institucion != "Todas", programa != "Todos", departamento != "Todos", año != "Todos", municipio != "Todos"])  # Género independiente, no cuenta aquí
progreso = filtros_aplicados / 5 * 100
st.progress(progreso / 100)

# Filtrado principal SIN género para independencia
filtered_df = df.copy()
if institucion != "Todas":
    filtered_df = filtered_df[filtered_df['Institución de Educación Superior (IES)'] == institucion]
if programa != "Todos":
    filtered_df = filtered_df[filtered_df['Programa Académico'] == programa]
if departamento != "Todos":
    filtered_df = filtered_df[filtered_df['Departamento de oferta del programa'] == departamento]
if año != "Todos":
    filtered_df = filtered_df[filtered_df['Año'] == int(año)]
if municipio != "Todos":
    filtered_df = filtered_df[filtered_df['Municipio de oferta del programa'] == municipio]

# Filtrado para género (aplicado a filtered_df para contexto, pero sección independiente)
filtered_df_genero = filtered_df.copy()
if genero != "Todos":
    genero_id = next(g['id'] for g in generos if g['label'] == genero)
    filtered_df_genero = filtered_df_genero[filtered_df_genero['Id Género'] == genero_id]

if not filtered_df.empty:
    agrupado = filtered_df.groupby(group_by)['Total Matriculados'].sum().reset_index()
    tab3, tab4 = st.tabs(["📈 Gráfico", "🗃 Datos"])
    
    with tab3:
        
        # Gráfico de Barras Embellecido con Plotly
        fig_bar = px.bar(agrupado, 
                         x=group_by, 
                         y='Total Matriculados', 
                         title=f'Acorde a los filtros realizados anteriormente, los resultados son:',
                         color='Total Matriculados',  # Gradiente de colores basado en valores
                         color_continuous_scale='Viridis',  # Escala colorida y llamativa
                         text='Total Matriculados')  # Etiquetas en las barras
        
        fig_bar.update_traces(texttemplate='%{text:,}', textposition='outside')  # Formato de números y posición
        fig_bar.update_layout(
            xaxis_title=f'{group_by}',
            yaxis_title='Total Matriculados',
            font=dict(size=12, family='Arial'),
            title_font_size=20,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            bargap=0.2,  # Espacio entre barras
            hovermode='x unified'  # Hover mejorado
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab4:
        st.dataframe(filtered_df)
else:
    st.warning("No hay datos que cumplan con los filtros seleccionados.")

# Sección autónoma para análisis por Género
st.header("Análisis por Género")
st.write(f"**Total de Registros en Análisis por Género:** {len(filtered_df_genero):,}")

if not filtered_df_genero.empty:
    if genero == "Todos":
        # Para "Todos", usar filtered_df completo para pirámide y datos con género
        gender_analysis_df = filtered_df.copy()
        gender_analysis_df['Género'] = gender_analysis_df['Id Género'].map({1: 'Hombres', 2: 'Mujeres'})
        tab_gender1, tab_gender2 = st.tabs(["📈 Gráfico", "🗃 Datos"])
        
        with tab_gender1:
            # Pirámide usando filtered_df
            pyramid_data = filtered_df.groupby(['Año', 'Id Género'])['Total Matriculados'].sum().reset_index()
            pyramid_data['Género'] = pyramid_data['Id Género'].map({1: 'Hombres', 2: 'Mujeres'})
            
            if len(filtered_df['Año'].unique()) > 1:
                # Hombres negativos para espejo (pirámide)
                pyramid_data['Matriculados_Piramide'] = pyramid_data.apply(
                    lambda row: -row['Total Matriculados'] if row['Género'] == 'Hombres' else row['Total Matriculados'], axis=1
                )
                
                # Crear figura de pirámide
                fig_pyramid = px.bar(pyramid_data, 
                                     x='Matriculados_Piramide', 
                                     y='Año', 
                                     color='Género',
                                     orientation='h',  # Horizontal para pirámide
                                     title='Matrículas por Género y Año',
                                     color_discrete_map={'Hombres': '#1f77b4', 'Mujeres': '#ff7f0e'},  # Azul y naranja
                                     text='Total Matriculados')
                
                fig_pyramid.update_traces(texttemplate='%{text:,}', textposition='outside')
                fig_pyramid.update_layout(
                    yaxis_title='Año',
                    font=dict(size=12, family='Arial'),
                    title_font_size=16,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    bargap=0.1,
                    hovermode='y unified',
                    xaxis=dict(zeroline=True, zerolinecolor='black', zerolinewidth=2)  # Línea central
                )
                
                # Invertir orden de años para que sea de mayor a menor (como pirámide tradicional)
                fig_pyramid.update_yaxes(categoryorder='total ascending')
                
                st.plotly_chart(fig_pyramid, use_container_width=True)
            else:
                st.info("Selecciona un rango de años mayor para ver la pirámide.")
        
        with tab_gender2:
            # Resumen total: Agrupar por Género y group_by, sumando Total Matriculados (sin desglose por año)
            gender_summary = gender_analysis_df.groupby(['Género', group_by])['Total Matriculados'].sum().reset_index()
            gender_summary.columns = ['Género', group_by, 'Total Matriculados']  # Renombrar para claridad
            st.dataframe(gender_summary)
    else:
        # Para género específico
        genero_id = next(g['id'] for g in generos if g['label'] == genero)
        tab_gender1, tab_gender2 = st.tabs([f"📈 Gráfico para {genero}", f"🗃 Resumen Total para {genero}"])
        
        with tab_gender1:
            st.subheader(f"Matrículas por {group_by} ({genero})")
            agrupado_genero = filtered_df_genero.groupby(group_by)['Total Matriculados'].sum().reset_index()
            
            fig_bar_genero = px.bar(agrupado_genero, 
                                    x=group_by, 
                                    y='Total Matriculados', 
                                    title=f'Distribución de Matrículas por {group_by} ({genero})',
                                    color='Total Matriculados',  
                                    color_continuous_scale='Plasma',  
                                    text='Total Matriculados')  
            
            fig_bar_genero.update_traces(texttemplate='%{text:,}', textposition='outside')  
            fig_bar_genero.update_layout(
                xaxis_title=f'{group_by}',
                yaxis_title=f'Total Matriculados ({genero})',
                font=dict(size=12, family='Arial'),
                title_font_size=16,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                bargap=0.2,  
                hovermode='x unified'  
            )
            st.plotly_chart(fig_bar_genero, use_container_width=True)
            
            # Gráfico adicional por Año para género
            st.subheader(f"Matrículas por Año ({genero})")
            gender_by_year = filtered_df_genero.groupby('Año')['Total Matriculados'].sum().reset_index()
            fig_year = px.line(gender_by_year, 
                               x='Año', 
                               y='Total Matriculados', 
                               title=f'Evolución de Matrículas por Año ({genero})',
                               markers=True,
                               color_discrete_sequence=['#1f77b4' if genero == 'Hombres' else '#ff7f0e'])
            fig_year.update_layout(
                xaxis_title='Año',
                yaxis_title=f'Total Matriculados ({genero})',
                font=dict(size=12, family='Arial'),
                title_font_size=16,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                hovermode='x unified',
                showlegend=False
            )
            st.plotly_chart(fig_year, use_container_width=True)
        
        with tab_gender2:
            # Resumen total: Agrupar por group_by, sumando Total Matriculados (sin desglose por año)
            gender_summary = filtered_df_genero.groupby(group_by)['Total Matriculados'].sum().reset_index()
            gender_summary.columns = [group_by, 'Total Matriculados']  # Renombrar para claridad
            st.dataframe(gender_summary)
else:
    st.warning("No hay datos para el análisis por género seleccionado.")

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
            title="Colocar descripción ojo ",
        )

        st.plotly_chart(fig_mapa, use_container_width=True)
        
        st.info(f"Mostrando {len(map_data)} universidades. Total IES filtradas: {len(ies_total)}")