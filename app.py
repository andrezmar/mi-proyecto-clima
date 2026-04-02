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
            # Query unificada integrando todas las tablas solicitadas
            query = """
            SELECT 
                m.id as municipio_id, m.Municipio, m.latitud, m.longitud,
                p.`Valor_num` as precip_valor, p.fecha_nueva as fecha,
                t.`Valor_num` as temp_valor,
                b.`Valor_num` as brillo_valor,
                c.año, c.nombre_mes, c.mes, c.trimestre, c.dia_semana
            FROM municipios m
            LEFT JOIN precipitacion p ON m.id = p.municipio_id
            LEFT JOIN temperaturas t ON m.id = t.Municipio_id AND p.fecha_nueva = t.fecha_nueva
            LEFT JOIN brillo_solar b ON m.id = b.municipio_id AND p.fecha_nueva = b.fecha_nueva
            LEFT JOIN calendario c ON p.fecha_nueva = c.fecha_nueva
            """
            df = pd.read_sql(query, conn)
            conn.close()
            
            # Limpieza y preparación
            df['fecha'] = pd.to_datetime(df['fecha'])
            df = df.loc[:, ~df.columns.duplicated()]
            return df
        except Exception as e:
            st.error(f"Error en consulta SQL: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# --- CARGA DE DATOS ---
df_master = load_comprehensive_data()

if df_master.empty:
    st.warning("Sin datos. Verifique conexión.")
    st.stop()

# --- BARRA LATERAL: SEGMENTADORES (CALENDARIO) ---
st.sidebar.title("🔍 Filtros de Calendario")

# Segmentadores por periodos de la tabla Calendario
años_disp = sorted(df_master['año'].dropna().unique().astype(int))
año_sel = st.sidebar.multiselect("Seleccione Año(s)", años_disp, default=años_disp[-1:] if años_disp else [])

meses_disp = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
meses_sel = st.sidebar.multiselect("Seleccione Mes(es)", meses_disp, default=meses_disp)

trimestres_disp = sorted(df_master['trimestre'].dropna().unique().astype(int))
tri_sel = st.sidebar.multiselect("Trimestre", trimestres_disp, default=trimestres_disp)

# Filtrado dinámico del DataFrame
mask = (df_master['año'].isin(año_sel)) & (df_master['nombre_mes'].isin(meses_sel)) & (df_master['trimestre'].isin(tri_sel))
df_filtered = df_master.loc[mask]

# --- NAVEGACIÓN ---
page = st.sidebar.radio("Navegación:", ["Dashboard General", "Comparativa Temporal", "Mapa de Calor"])

# --- PÁGINA 1: DASHBOARD GENERAL ---
if page == "Dashboard General":
    st.markdown("""
        <div class="hero-section">
            <h1>Análisis Climático por Periodos</h1>
            <p>Visualización integrada de la tabla Calendario y registros meteorológicos.</p>
        </div>
    """, unsafe_allow_html=True)

    if not df_filtered.empty:
        # Métricas de resumen del periodo seleccionado
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Promedio Temp.", f"{df_filtered['temp_valor'].mean():.1f} °C")
        m2.metric("Total Lluvia", f"{df_filtered['precip_valor'].sum():.1f} mm")
        m3.metric("Brillo Solar Prom.", f"{df_filtered['brillo_valor'].mean():.1f} h")
        m4.metric("Días Registrados", len(df_filtered['fecha'].unique()))

        st.markdown("---")
        
        # Segmentador de Visualización (Toggle de análisis)
        col_view1, col_view2 = st.columns([1, 2])
        with col_view1:
            st.subheader("Configuración de Visual")
            variable = st.radio("Variable a analizar:", ["precip_valor", "temp_valor", "brillo_valor"], 
                                format_func=lambda x: "Precipitación" if "precip" in x else ("Temperatura" if "temp" in x else "Brillo Solar"))
            agrupacion = st.selectbox("Agrupar por:", ["nombre_mes", "año", "trimestre", "dia_semana"], 
                                      format_func=lambda x: x.replace("_", " ").title())

        with col_view2:
            # Gráfico dinámico basado en segmentadores
            df_grouped = df_filtered.groupby(agrupacion)[variable].mean().reset_index()
            # Ordenar meses correctamente si es necesario
            if agrupacion == "nombre_mes":
                df_grouped['nombre_mes'] = pd.Categorical(df_grouped['nombre_mes'], categories=meses_disp, ordered=True)
                df_grouped = df_grouped.sort_values('nombre_mes')

            fig_dyn = px.bar(df_grouped, x=agrupacion, y=variable, 
                            title=f"Análisis de {variable.split('_')[0].title()} por {agrupacion.title()}",
                            color=variable, color_continuous_scale="Viridis")
            st.plotly_chart(fig_dyn, use_container_width=True)

# --- PÁGINA 2: COMPARATIVA TEMPORAL ---
elif page == "Comparativa Temporal":
    st.title("📈 Comparativa Interanual")
    st.write("Compare el comportamiento de una variable a través de los meses entre diferentes años.")

    var_comp = st.selectbox("Seleccione Variable:", ["precip_valor", "temp_valor", "brillo_valor"])
    
    # Preparamos datos para comparar años
    df_comp = df_filtered.copy()
    df_comp['nombre_mes'] = pd.Categorical(df_comp['nombre_mes'], categories=meses_disp, ordered=True)
    df_pivot = df_comp.groupby(['año', 'nombre_mes'])[var_comp].mean().reset_index()

    fig_comp = px.line(df_pivot, x='nombre_mes', y=var_comp, color='año',
                      title=f"Evolución Mensual: Comparativa por Año",
                      markers=True, line_shape="spline")
    st.plotly_chart(fig_comp, use_container_width=True)

# --- PÁGINA 3: MAPA DE CALOR ---
elif page == "Mapa de Calor":
    st.title("🌡️ Matriz de Intensidad (Calendario)")
    st.write("Mapa de calor que cruza meses y días de la semana para identificar patrones.")

    var_heat = st.selectbox("Variable para el Mapa de Calor:", ["temp_valor", "precip_valor", "brillo_valor"])
    
    # Crear matriz
    heat_data = df_filtered.groupby(['nombre_mes', 'dia_semana'])[var_heat].mean().reset_index()
    heat_matrix = heat_data.pivot(index="nombre_mes", columns="dia_semana", values=var_heat)
    # Reordenar índices
    heat_matrix = heat_matrix.reindex(meses_disp)

    fig_heat = px.imshow(heat_matrix, 
                        labels=dict(x="Día de la Semana", y="Mes", color="Valor"),
                        x=['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'],
                        y=meses_disp,
                        aspect="auto", color_continuous_scale="RdYlBu_r")
    st.plotly_chart(fig_heat, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info(f"Datos actuales: {len(df_filtered)} registros filtrados.")
st.sidebar.caption("Proyecto 2026 | Creado: Andres Martinez")
