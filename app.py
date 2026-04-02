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
            if not df.empty:
                df['fecha'] = pd.to_datetime(df['fecha'])
                # Asegurar que los nombres de columnas no tengan espacios extras
                df.columns = df.columns.str.strip()
            
            # Eliminar columnas duplicadas si existen
            df = df.loc[:, ~df.columns.duplicated()]
            return df
        except Exception as e:
            st.error(f"Error en consulta SQL: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# --- CARGA DE DATOS ---
df_master = load_comprehensive_data()

if df_master.empty:
    st.warning("No se encontraron datos en la base de datos. Por favor, revise la configuración de Railway.")
    st.stop()

# --- BARRA LATERAL: SEGMENTADORES (CALENDARIO) ---
st.sidebar.title("🔍 Filtros de Calendario")

# Lista maestra de meses para ordenamiento
meses_orden = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# Segmentadores por periodos de la tabla Calendario
años_disp = sorted(df_master['año'].dropna().unique().astype(int)) if 'año' in df_master.columns else []
año_sel = st.sidebar.multiselect("Seleccione Año(s)", años_disp, default=años_disp[-1:] if años_disp else [])

meses_disp = sorted(df_master['nombre_mes'].dropna().unique(), key=lambda x: meses_orden.index(x) if x in meses_orden else 0) if 'nombre_mes' in df_master.columns else []
meses_sel = st.sidebar.multiselect("Seleccione Mes(es)", meses_disp, default=meses_disp)

trimestres_disp = sorted(df_master['trimestre'].dropna().unique().astype(int)) if 'trimestre' in df_master.columns else []
tri_sel = st.sidebar.multiselect("Trimestre", trimestres_disp, default=trimestres_disp)

# Filtrado dinámico del DataFrame con validación de existencia de columnas
mask = pd.Series([True] * len(df_master))
if 'año' in df_master.columns and año_sel:
    mask &= df_master['año'].isin(año_sel)
if 'nombre_mes' in df_master.columns and meses_sel:
    mask &= df_master['nombre_mes'].isin(meses_sel)
if 'trimestre' in df_master.columns and tri_sel:
    mask &= df_master['trimestre'].isin(tri_sel)

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
        # Métricas de resumen con manejo de NaNs
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Promedio Temp.", f"{df_filtered['temp_valor'].mean():.1f} °C" if 'temp_valor' in df_filtered else "N/A")
        m2.metric("Total Lluvia", f"{df_filtered['precip_valor'].sum():.1f} mm" if 'precip_valor' in df_filtered else "N/A")
        m3.metric("Brillo Solar Prom.", f"{df_filtered['brillo_valor'].mean():.1f} h" if 'brillo_valor' in df_filtered else "N/A")
        m4.metric("Días Registrados", len(df_filtered['fecha'].unique()) if 'fecha' in df_filtered else 0)

        st.markdown("---")
        
        # Segmentador de Visualización
        col_view1, col_view2 = st.columns([1, 2])
        with col_view1:
            st.subheader("Configuración de Visual")
            variable = st.radio("Variable a analizar:", ["precip_valor", "temp_valor", "brillo_valor"], 
                                format_func=lambda x: "Precipitación" if "precip" in x else ("Temperatura" if "temp" in x else "Brillo Solar"))
            
            opciones_agrupar = [c for c in ["nombre_mes", "año", "trimestre", "dia_semana"] if c in df_filtered.columns]
            agrupacion = st.selectbox("Agrupar por:", opciones_agrupar, 
                                      format_func=lambda x: x.replace("_", " ").title())

        with col_view2:
            if agrupacion in df_filtered.columns:
                df_grouped = df_filtered.groupby(agrupacion)[variable].mean().reset_index()
                
                # Ordenar lógicamente si es mes
                if agrupacion == "nombre_mes":
                    df_grouped[agrupacion] = pd.Categorical(df_grouped[agrupacion], categories=meses_orden, ordered=True)
                    df_grouped = df_grouped.sort_values(agrupacion)

                fig_dyn = px.bar(df_grouped, x=agrupacion, y=variable, 
                                title=f"Promedio de {variable.split('_')[0].title()} por {agrupacion.title()}",
                                color=variable, color_continuous_scale="Viridis")
                st.plotly_chart(fig_dyn, use_container_width=True)
    else:
        st.info("No hay datos que coincidan con los filtros seleccionados.")

# --- PÁGINA 2: COMPARATIVA TEMPORAL ---
elif page == "Comparativa Temporal":
    st.title("📈 Comparativa Interanual")
    
    if not df_filtered.empty and 'nombre_mes' in df_filtered.columns and 'año' in df_filtered.columns:
        var_comp = st.selectbox("Seleccione Variable:", ["precip_valor", "temp_valor", "brillo_valor"])
        
        df_comp = df_filtered.copy()
        df_comp['nombre_mes'] = pd.Categorical(df_comp['nombre_mes'], categories=meses_orden, ordered=True)
        df_pivot = df_comp.groupby(['año', 'nombre_mes'])[var_comp].mean().reset_index()

        fig_comp = px.line(df_pivot, x='nombre_mes', y=var_comp, color='año',
                          title=f"Evolución Mensual: Comparativa por Año",
                          markers=True, line_shape="spline")
        st.plotly_chart(fig_comp, use_container_width=True)
    else:
        st.info("Se necesitan datos de varios periodos para esta comparativa.")

# --- PÁGINA 3: MAPA DE CALOR ---
elif page == "Mapa de Calor":
    st.title("🌡️ Matriz de Intensidad (Calendario)")
    
    if not df_filtered.empty and 'nombre_mes' in df_filtered.columns and 'dia_semana' in df_filtered.columns:
        var_heat = st.selectbox("Variable para el Mapa de Calor:", ["temp_valor", "precip_valor", "brillo_valor"])
        
        heat_data = df_filtered.groupby(['nombre_mes', 'dia_semana'])[var_heat].mean().reset_index()
        heat_matrix = heat_data.pivot(index="nombre_mes", columns="dia_semana", values=var_heat)
        
        # Reordenar ejes
        meses_presentes = [m for m in meses_orden if m in heat_matrix.index]
        dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        dias_presentes = [d for d in dias_orden if d in heat_matrix.columns]
        
        heat_matrix = heat_matrix.reindex(index=meses_presentes, columns=dias_presentes)

        fig_heat = px.imshow(heat_matrix, 
                            labels=dict(x="Día de la Semana", y="Mes", color="Valor"),
                            aspect="auto", color_continuous_scale="RdYlBu_r")
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("Datos insuficientes para generar la matriz de intensidad.")

st.sidebar.markdown("---")
st.sidebar.info(f"Registros activos: {len(df_filtered)}")
st.sidebar.caption("Proyecto 2026 | Creado: Andres Martinez")
