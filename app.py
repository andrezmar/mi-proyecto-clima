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

# --- ESTILOS ---
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

# --- CONEXIÓN Y DATOS REALES ---
def get_connection():
    """Establece la conexión con MySQL en Railway usando Secrets"""
    try:
        return mysql.connector.connect(
            host=st.secrets["DB_HOST"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_NAME"],
            port=int(st.secrets["DB_PORT"])
        )
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return None

@st.cache_data(ttl=600) # El caché se limpia cada 10 min
def load_data_from_db():
    """Carga los datos de la vista creada en MySQL"""
    conn = get_connection()
    if conn:
        try:
            # Reemplaza 'nombre_de_tu_vista' por el nombre real de tu vista en MySQL
            query = "SELECT * FROM vista_municipios_clima" 
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Error al ejecutar la consulta: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# --- CARGA DE DATOS ---
df_municipios = load_data_from_db()

# Si la base de datos está vacía o falla, mostramos un mensaje
if df_municipios.empty:
    st.warning("No se pudieron cargar datos reales. Verifique la conexión o el nombre de la vista.")
    # Datos de respaldo para que la app no se rompa mientras pruebas
    df_municipios = pd.DataFrame({
        'municipio': ["Ejemplo"], 'lat': [4.6], 'lon': [-74.0], 
        'temp_avg': [20], 'precip_anual': [1000]
    })

# --- LÓGICA DE NAVEGACIÓN ---
st.sidebar.title("📌 Navegación")
page = st.sidebar.radio("Ir a:", ["Inicio", "Explorador Climático", "Análisis Agrícola"])

# --- PÁGINA 1: LANDING PAGE ---
if page == "Inicio":
    st.markdown("""
        <div class="hero-section">
            <h1>Bienvenido a GeoClima Avanzatec</h1>
            <p style="font-size: 1.2rem;">Plataforma de análisis climático municipal conectada a MySQL en Railway.</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="feature-card"><h3>📊 Visualización</h3><p>Análisis de temperaturas y precipitaciones basado en registros diarios.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="feature-card"><h3>📍 Geolocalización</h3><p>Mapas interactivos utilizando las coordenadas de tu base de datos.</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="feature-card"><h3>🌾 Agro-Inteligencia</h3><p>Recomendaciones de cultivos según el histórico de lluvias y sol.</p></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📍 Ubicación de Municipios Monitoreados")
    # Mostramos todos los municipios en el mapa
    st.map(df_municipios[['lat', 'lon']])

# --- PÁGINA 2: DASHBOARD ---
elif page == "Explorador Climático":
    st.title("📊 Análisis Detallado por Municipio")
    
    municipio_sel = st.sidebar.selectbox("Seleccione el Municipio", df_municipios['municipio'].unique())
    datos_mun = df_municipios[df_municipios['municipio'] == municipio_sel].iloc[0]

    col_stats, col_map = st.columns([1, 1])
    
    with col_stats:
        st.write(f"### Indicadores para {municipio_sel}")
        st.metric("Temperatura Promedio", f"{datos_mun.get('temp_avg', 0):.1f} °C")
        st.metric("Precipitación Total", f"{datos_mun.get('precip_anual', 0):.1f} mm")
        
        # VALOR AGREGADO: Sensación Térmica
        # Si tienes una columna de brillo solar, úsala aquí. Si no, usamos un estimado.
        brillo = datos_mun.get('brillo_solar', 5) 
        sensacion = datos_mun.get('temp_avg', 0) + (0.3 * brillo)
        st.metric("Sensación Térmica Est.", f"{sensacion:.1f} °C")

    with col_map:
        st.write("### Vista en Mapa")
        map_data = pd.DataFrame({'lat': [datos_mun['lat']], 'lon': [datos_mun['lon']]})
        st.map(map_data, zoom=11)

# --- PÁGINA 3: ANÁLISIS AGRÍCOLA ---
elif page == "Análisis Agrícola":
    st.title("🌾 Inteligencia para el Campo")
    
    municipio_sel = st.selectbox("Seleccione municipio para recomendación:", df_municipios['municipio'].unique())
    datos_mun = df_municipios[df_municipios['municipio'] == municipio_sel].iloc[0]
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Análisis de Idoneidad")
        precip = datos_mun.get('precip_anual', 0)
        temp = datos_mun.get('temp_avg', 0)
        
        if precip > 1500:
            st.success("✅ Idóneo para: Arroz o Caña (Requieren mucha agua)")
        elif 18 <= temp <= 24:
            st.success("✅ Idóneo para: Café de alta calidad")
        elif temp > 25:
            st.success("✅ Idóneo para: Cacao o Frutas Tropicales")
        else:
            st.info("ℹ️ Idóneo para: Cultivos de clima frío (Papa, hortalizas)")
            
    with col_b:
        fig = px.scatter(df_municipios, x="temp_avg", y="precip_anual", 
                         hover_name="municipio", text="municipio",
                         title="Comparativa: Temperatura vs Lluvias")
        st.plotly_chart(fig)

st.sidebar.markdown("---")
st.sidebar.caption("Proyecto 2026 | Creado: Andres Martinez")
