import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="GeoClima Avanzatec",
    page_icon="🌍",
    layout="wide"
)

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .hero-section {
        padding: 40px;
        text-align: center;
        background: linear-gradient(135deg, #0f172a, #1e3a8a);
        color: white;
        border-radius: 15px;
        margin-bottom: 30px;
    }
    .stMetric {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A BASE DE DATOS ---
def get_connection():
    try:
        return mysql.connector.connect(
            host=st.secrets["DB_HOST"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_NAME"],
            port=int(st.secrets["DB_PORT"])
        )
    except Exception as e:
        st.error(f"Error conectando a la base de datos: {e}")
        return None

@st.cache_data(ttl=600)
def load_comprehensive_data():
    conn = get_connection()
    if conn:
        try:
            # Query actualizada: Se usan latitud y longitud de la tabla 'municipios'
            # Se relaciona m.id con municipio_id de las otras tablas
            query = """
            SELECT 
                m.id as municipio_id, 
                m.Municipio, 
                m.latitud, 
                m.longitud,
                p.`Valor_num` as precip_valor, 
                p.fecha_nueva as fecha,
                t.`Valor_num` as temp_valor,
                b.`Valor_num` as brillo_valor,
                c.año, 
                c.nombre_mes, 
                c.mes, 
                c.trimestre, 
                c.dia_semana
            FROM municipios m
            LEFT JOIN precipitacion p ON m.id = p.municipio_id
            LEFT JOIN temperaturas t ON m.id = t.Municipio_id AND p.fecha_nueva = t.fecha_nueva
            LEFT JOIN brillo_solar b ON m.id = b.municipio_id AND p.fecha_nueva = b.fecha_nueva
            LEFT JOIN calendario c ON p.fecha_nueva = c.fecha_nueva
            """
            df = pd.read_sql(query, conn)
            conn.close()
            
            if not df.empty:
                # Limpieza de nombres de columnas y conversión de fechas
                df.columns = df.columns.str.strip()
                df['fecha'] = pd.to_datetime(df['fecha'])
                
                # Asegurar que latitud y longitud sean numéricos
                df['latitud'] = pd.to_numeric(df['latitud'], errors='coerce')
                df['longitud'] = pd.to_numeric(df['longitud'], errors='coerce')
                
            # Eliminar columnas duplicadas por los JOINs
            df = df.loc[:, ~df.columns.duplicated()]
            return df
        except Exception as e:
            st.error(f"Error en la consulta SQL con tabla municipios: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# --- CARGA DE DATOS ---
df_master = load_comprehensive_data()

if df_master.empty:
    st.warning("No se encontraron datos. Verifique que las columnas 'latitud' y 'longitud' existan en la tabla 'municipios'.")
    st.stop()

# --- BARRA LATERAL: SEGMENTADORES (CALENDARIO) ---
st.sidebar.title("🔍 Filtros de Calendario")
meses_orden = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# Obtener opciones de filtrado
años_disp = sorted(df_master['año'].dropna().unique().astype(int)) if 'año' in df_master.columns else []
meses_presentes = df_master['nombre_mes'].dropna().unique() if 'nombre_mes' in df_master.columns else []
meses_disp = [m for m in meses_orden if m in meses_presentes]

año_sel = st.sidebar.multiselect("Seleccione Año(s)", años_disp, default=años_disp[-1:] if años_disp else [])
meses_sel = st.sidebar.multiselect("Seleccione Mes(es)", meses_disp, default=meses_disp)

# Aplicación de filtros
df_filtered = df_master.copy()
if 'año' in df_filtered.columns and año_sel:
    df_filtered = df_filtered[df_filtered['año'].isin(año_sel)]
if 'nombre_mes' in df_filtered.columns and meses_sel:
    df_filtered = df_filtered[df_filtered['nombre_mes'].isin(meses_sel)]

# --- NAVEGACIÓN ---
page = st.sidebar.radio("Navegación:", ["Dashboard General", "Mapa de Georeferenciación", "Tendencias Temporales"])

# --- PÁGINA 1: DASHBOARD GENERAL ---
if page == "Dashboard General":
    st.markdown("<div class='hero-section'><h1>Dashboard Climático Unificado</h1><p>Datos vinculados mediante ID de Municipios</p></div>", unsafe_allow_html=True)
    
    if not df_filtered.empty:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Promedio Temp.", f"{df_filtered['temp_valor'].mean():.1f} °C" if 'temp_valor' in df_filtered else "N/A")
        col2.metric("Total Lluvia", f"{df_filtered['precip_valor'].sum():.1f} mm" if 'precip_valor' in df_filtered else "N/A")
        col3.metric("Brillo Solar", f"{df_filtered['brillo_valor'].mean():.1f} h" if 'brillo_valor' in df_filtered else "N/A")
        col4.metric("Municipios", len(df_filtered['Municipio'].unique()))

        st.markdown("---")
        
        # Análisis de variables
        col_sel, col_graph = st.columns([1, 2])
        with col_sel:
            st.subheader("Configuración")
            var = st.radio("Métrica:", ["precip_valor", "temp_valor", "brillo_valor"], 
                           format_func=lambda x: "Precipitación" if "precip" in x else ("Temperatura" if "temp" in x else "Brillo Solar"))
            agrupar = st.selectbox("Agrupar por:", ["nombre_mes", "año", "trimestre"])

        with col_graph:
            df_grouped = df_filtered.groupby(agrupar)[var].mean().reset_index()
            if agrupar == "nombre_mes":
                df_grouped[agrupar] = pd.Categorical(df_grouped[agrupar], categories=meses_orden, ordered=True)
                df_grouped = df_grouped.sort_values(agrupar)
            
            fig = px.bar(df_grouped, x=agrupar, y=var, color=var, color_continuous_scale="Blues" if "precip" in var else "OrRd")
            st.plotly_chart(fig, use_container_width=True)

# --- PÁGINA 2: MAPA DE GEOREFERENCIACIÓN ---
elif page == "Mapa de Georeferenciación":
    st.title("📍 Georeferenciación de Municipios")
    st.write("Visualización basada en las coordenadas latitud/longitud de la tabla municipios.")
    
    # Filtrar solo registros con coordenadas válidas
    df_geo = df_filtered.dropna(subset=['latitud', 'longitud'])
    
    if not df_geo.empty:
        # Agrupar por municipio para el mapa (promedio del periodo seleccionado)
        df_map = df_geo.groupby(['Municipio', 'latitud', 'longitud']).agg({
            'precip_valor': 'sum',
            'temp_valor': 'mean',
            'brillo_valor': 'mean'
        }).reset_index()
        
        # Selector de capa para el mapa
        capa = st.selectbox("Mostrar en el mapa:", ["precip_valor", "temp_valor", "brillo_valor"],
                           format_func=lambda x: "Precipitación Acumulada" if "precip" in x else ("Temperatura Promedio" if "temp" in x else "Brillo Solar Promedio"))

        fig_map = px.scatter_mapbox(df_map, 
                                   lat="latitud", lon="longitud", 
                                   hover_name="Municipio", 
                                   color=capa,
                                   size=capa if df_map[capa].min() >= 0 else None,
                                   color_continuous_scale="Viridis", 
                                   zoom=6, 
                                   mapbox_style="carto-positron",
                                   height=600)
        
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.error("No se pueden mostrar mapas: Faltan coordenadas en la tabla 'municipios' para los filtros seleccionados.")

# --- PÁGINA 3: TENDENCIAS ---
elif page == "Tendencias Temporales":
    st.title("📈 Análisis de Tendencia")
    if not df_filtered.empty:
        df_trend = df_filtered.groupby(['fecha', 'Municipio'])['temp_valor'].mean().reset_index()
        fig_trend = px.line(df_trend, x='fecha', y='temp_valor', color='Municipio', title="Evolución de Temperatura por Municipio")
        st.plotly_chart(fig_trend, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info(f"Registros georeferenciados: {len(df_filtered.dropna(subset=['latitud']))}")
st.sidebar.caption("Proyecto 2026 | Creado: Andres Martinez")
