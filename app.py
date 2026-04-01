import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="GeoClima Avanzatec",
    page_icon="🌍",
    layout="wide"
)

# --- STYLES ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .hero-section {
        padding: 60px;
        text-align: center;
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        color: white;
        border-radius: 15px;
        margin-bottom: 30px;
    }
    .feature-card {
        padding: 20px;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        height: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE CONNECTION ---
def get_connection():
    """Establishes connection with MySQL on Railway using Secrets"""
    try:
        return mysql.connector.connect(
            host=st.secrets["DB_HOST"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_NAME"],
            port=int(st.secrets["DB_PORT"])
        )
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None

@st.cache_data(ttl=600)
def load_data_from_db():
    """Loads data from the MySQL view"""
    conn = get_connection()
    if conn:
        try:
            # IMPORTANT: Ensure 'vista_municipios_clima' exists in your DB
            query = "SELECT * FROM vista_municipios_geo" 
            df = pd.read_sql(query, conn)
            conn.close()
            
            # Standardize column names to lowercase to avoid case-sensitivity issues
            df.columns = [c.lower() for c in df.columns]
            return df
        except Exception as e:
            st.error(f"Error executing query: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# --- DATA LOADING ---
df_municipios = load_data_from_db()

# Fallback data if database is empty or connection fails
if df_municipios.empty:
    st.warning("No data detected in MySQL view. Using sample data.")
    df_municipios = pd.DataFrame({
        'municipio': ["Bogotá", "Medellín"], 
        'latitud': [4.6097, 6.2442], 
        'longitud': [-74.0817, -75.5812], 
        'temp_avg': [14.5, 22.0], 
        'precip_anual': [850, 1500]
    })

# COLUMN SEARCH LOGIC (Flexible for 'latitud', 'lat', 'longitud', 'lon', etc.)
lat_col = next((c for c in df_municipios.columns if c in ['latitud', 'lat', 'latitude']), None)
lon_col = next((c for c in df_municipios.columns if c in ['longitud', 'lon', 'longitude']), None)

# --- NAVIGATION LOGIC ---
st.sidebar.title("📌 Navegación")
page = st.sidebar.radio("Ir a:", ["Inicio", "Explorador Climático", "Análisis Agrícola"])

# --- PAGE 1: LANDING PAGE ---
if page == "Inicio":
    st.markdown("""
        <div class="hero-section">
            <h1>Bienvenido a GeoClima Avanzatec</h1>
            <p style="font-size: 1.2rem;">Análisis climático municipal de precisión en tiempo real.</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="feature-card"><h3>📊 Visualización</h3><p>Gráficos dinámicos de temperatura y precipitación diaria.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="feature-card"><h3>📍 Geolocalización</h3><p>Mapas interactivos con coordenadas de precisión (Railway).</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="feature-card"><h3>🌾 Agro-Inteligencia</h3><p>Recomendaciones de siembra basadas en históricos de lluvia.</p></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📍 Municipios en el Sistema")
    
    if lat_col and lon_col:
        # We ensure the columns are named 'lat' and 'lon' only for the st.map function
        map_df = df_municipios[[lat_col, lon_col]].copy()
        map_df.columns = ['lat', 'lon']
        st.map(map_df)
    else:
        st.error("No se encontraron columnas de coordenadas (latitud/longitud) en los datos.")

# --- PAGE 2: DASHBOARD ---
elif page == "Explorador Climático":
    st.title("📊 Análisis Detallado")
    
    if 'municipio' in df_municipios.columns:
        municipio_sel = st.sidebar.selectbox("Seleccione el Municipio", df_municipios['municipio'].unique())
        datos_mun = df_municipios[df_municipios['municipio'] == municipio_sel].iloc[0]

        col_stats, col_map = st.columns([1, 1])
        
        with col_stats:
            st.write(f"### Indicadores: {municipio_sel}")
            st.metric("Temperatura Promedio", f"{datos_mun.get('temp_avg', 0):.1f} °C")
            st.metric("Precipitación Total", f"{datos_mun.get('precip_anual', 0):.1f} mm")
            
            # Value Added: Estimated Thermal Sensation
            # Using a simplified formula: Temp + (0.2 * solar_brightness)
            sensacion = datos_mun.get('temp_avg', 0) + (0.2 * datos_mun.get('brillo_solar', 5))
            st.metric("Sensación Térmica Est.", f"{sensacion:.1f} °C")

        with col_map:
            if lat_col and lon_col:
                st.write("### Ubicación Localizada")
                map_data = pd.DataFrame({
                    'lat': [datos_mun[lat_col]], 
                    'lon': [datos_mun[lon_col]]
                })
                st.map(map_data, zoom=10)
    else:
        st.error("La columna 'municipio' no fue encontrada en la base de datos.")

# --- PAGE 3: AGRICULTURAL ANALYSIS ---
elif page == "Análisis Agrícola":
    st.title("🌾 Recomendaciones Técnicas de Siembra")
    
    if 'municipio' in df_municipios.columns:
        municipio_sel = st.selectbox("Analizar municipio para recomendación:", df_municipios['municipio'].unique())
        datos_mun = df_municipios[df_municipios['municipio'] == municipio_sel].iloc[0]
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.subheader("Idoneidad de Cultivo")
            precip = datos_mun.get('precip_anual', 0)
            
            if precip > 1800:
                st.success("✅ Recomendado: Arroz o Plátano (Requieren alta humedad)")
            elif 1000 <= precip <= 1800:
                st.success("✅ Recomendado: Café o Maíz (Humedad moderada)")
            else:
                st.info("ℹ️ Recomendado: Cultivos de secano o riego tecnificado")
                
        with col_b:
            fig = px.bar(df_municipios, x="municipio", y="precip_anual", 
                         title="Comparativa Regional de Lluvias",
                         color="precip_anual", color_continuous_scale="Viridis")
            st.plotly_chart(fig)
    else:
        st.error("No se pueden generar recomendaciones sin datos de municipios.")

st.sidebar.markdown("---")
st.sidebar.caption("Proyecto 2026 | Creado: Andres Martinez")
