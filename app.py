import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="GeoClima Municipios de Antioquia",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# ESTILOS CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

/* Reset y base */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Fondo principal */
.stApp {
    background-color: #0e1a14;
    color: #e8ede9;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #111f17 !important;
    border-right: 1px solid #1e3328;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stRadio label {
    color: #FFFFFF !important;
    font-size: 0.78rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* Hero */
.hero {
    background: linear-gradient(135deg, #0a2e1a 0%, #0e3d22 50%, #1a4d2e 100%);
    border: 1px solid #1e4d2e;
    border-radius: 16px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(74,222,128,0.06) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.8rem;
    color: #FFFFFF;
    margin: 0 0 0.3rem 0;
    line-height: 1.1;
}
.hero-subtitle {
    color: #6fa87e;
    font-size: 0.95rem;
    font-weight: 300;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin: 0;
}

/* Tarjetas de métricas */
.metric-card {
    background: #111f17;
    border: 1px solid #1e3328;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: #2d5c3e; }
.metric-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #2d6a4f, #52b788);
}
.metric-label {
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #FFFFFF;
    margin-bottom: 0.5rem;
}
.metric-value {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: #FFFFFF;
    line-height: 1;
}
.metric-unit {
    font-size: 0.75rem;
    color: #4a7c59;
    margin-top: 0.2rem;
}

/* Sección separadora */
.section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    color: #a8d5b5;
    margin: 0.5rem 0 1.2rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #1e3328;
}

/* Contenedor de gráfico */
.chart-container {
    background: #111f17;
    border: 1px solid #1e3328;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
}

/* Info badge */
.info-badge {
    display: inline-block;
    background: #1a3d28;
    border: 1px solid #2d5c3e;
    border-radius: 20px;
    padding: 0.25rem 0.9rem;
    font-size: 0.78rem;
    color: #74c99a;
    margin: 0.2rem;
}

/* Selectbox y multiselect */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    background-color: #1a2e20 !important;
    border-color: #2d5c3e !important;
    color: #d4f0dc !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: #111f17;
    border-bottom: 1px solid #1e3328;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    color: #6fa87e !important;
    border: none !important;
    padding: 0.7rem 1.4rem;
    font-size: 0.85rem;
    letter-spacing: 0.05em;
}
.stTabs [aria-selected="true"] {
    color: #52b788 !important;
    border-bottom: 2px solid #52b788 !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #0e1a14; }
::-webkit-scrollbar-thumb { background: #2d5c3e; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PALETA PLOTLY
# ─────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#9cbfa8", size=12),
    xaxis=dict(gridcolor="#1e3328", linecolor="#1e3328", tickcolor="#2d5c3e"),
    yaxis=dict(gridcolor="#1e3328", linecolor="#1e3328", tickcolor="#2d5c3e"),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#9cbfa8")),
    colorway=["#52b788", "#40916c", "#74c99a", "#2d6a4f", "#95d5b2", "#1b4332"],
)

def apply_layout(fig, **kwargs):
    """Aplica PLOTLY_LAYOUT + kwargs adicionales sin conflicto de claves duplicadas."""
    merged = {**PLOTLY_LAYOUT, **kwargs}
    fig.update_layout(**merged)
    return fig

COLORES_MUNICIPIOS = {
    "Alejandría": "#52b788",
    "Urrao":      "#40916c",
    "Cañasgordas":"#74c99a",
    "Arboletes":  "#95d5b2",
    "Peñol":      "#b7e4c7",
    "Turbo":      "#d8f3dc",
    "Nechí":      "#2d6a4f",
}

# ─────────────────────────────────────────────
# CONEXIÓN A BASE DE DATOS
# ─────────────────────────────────────────────
@st.cache_resource
def get_engine():
    try:
        cfg = st.secrets["mysql"]
        url = (
            f"mysql+pymysql://{cfg['DB_USER']}:{cfg['DB_PASSWORD']}"
            f"@{cfg['DB_HOST']}:{cfg['DB_PORT']}/{cfg['DB_NAME']}"
        )
        engine = create_engine(url, pool_pre_ping=True, pool_recycle=3600)
        return engine
    except Exception as e:
        st.error(f"❌ Error de conexión: {e}")
        return None

def query_db(sql: str) -> pd.DataFrame:
    engine = get_engine()
    if engine is None:
        return pd.DataFrame()
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(sql), conn)
    except Exception as e:
        st.error(f"❌ Error en consulta: {e}")
        return pd.DataFrame()

# ─────────────────────────────────────────────
# CARGA DE DATOS
# ─────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def load_temperatura():
    sql = """
    SELECT
        m.id AS municipio_id,
        m.Municipio,
        m.latitud,
        m.longitud,
        t.fecha_nueva,
        MAX(CASE WHEN t.Parametro = 'Temperatura máxima diaria' THEN t.Valor_num END) AS temp_max,
        MIN(CASE WHEN t.Parametro = 'Temperatura mínima diaria' THEN t.Valor_num END) AS temp_min,
        c.Año AS año,
        c.Mes_Nombre AS mes_nombre,
        c.Mes_Num AS mes_num,
        c.Trimestre AS trimestre
    FROM municipios m
    JOIN temperaturas t ON m.id = t.Municipio_id
    JOIN calendario c ON t.fecha_nueva = c.fecha_nueva
    GROUP BY m.id, m.Municipio, m.latitud, m.longitud,
             t.fecha_nueva, c.Año, c.Mes_Nombre, c.Mes_Num, c.Trimestre
    """
    df = query_db(sql)
    if not df.empty:
        df['fecha_nueva'] = pd.to_datetime(df['fecha_nueva'])
        df['latitud']     = pd.to_numeric(df['latitud'], errors='coerce')
        df['longitud']    = pd.to_numeric(df['longitud'], errors='coerce')
    return df

@st.cache_data(ttl=600, show_spinner=False)
def load_precipitacion():
    sql = """
    SELECT
        m.id AS municipio_id,
        m.Municipio,
        m.latitud,
        m.longitud,
        p.fecha_nueva,
        p.Valor_num AS precipitacion_mm,
        c.Año AS año,
        c.Mes_Nombre AS mes_nombre,
        c.Mes_Num AS mes_num,
        c.Trimestre AS trimestre
    FROM municipios m
    JOIN precipitacion p ON m.id = p.municipio_id
    JOIN calendario c ON p.fecha_nueva = c.fecha_nueva
    """
    df = query_db(sql)
    if not df.empty:
        df['fecha_nueva'] = pd.to_datetime(df['fecha_nueva'])
        df['latitud']     = pd.to_numeric(df['latitud'], errors='coerce')
        df['longitud']    = pd.to_numeric(df['longitud'], errors='coerce')
    return df

@st.cache_data(ttl=600, show_spinner=False)
def load_brillo():
    sql = """
    SELECT
        m.id AS municipio_id,
        m.Municipio,
        m.latitud,
        m.longitud,
        b.fecha_nueva,
        b.Valor_num AS brillo_horas,
        c.Año AS año,
        c.Mes_Nombre AS mes_nombre,
        c.Mes_Num AS mes_num,
        c.Trimestre AS trimestre
    FROM municipios m
    JOIN brillo_solar b ON m.id = b.municipio_id
    JOIN calendario c ON b.fecha_nueva = c.fecha_nueva
    """
    df = query_db(sql)
    if not df.empty:
        df['fecha_nueva'] = pd.to_datetime(df['fecha_nueva'])
        df['latitud']     = pd.to_numeric(df['latitud'], errors='coerce')
        df['longitud']    = pd.to_numeric(df['longitud'], errors='coerce')
    return df

@st.cache_data(ttl=600, show_spinner=False)
def load_municipios():
    sql = "SELECT id, Municipio, latitud, longitud FROM municipios"
    df = query_db(sql)
    if not df.empty:
        df['latitud']  = pd.to_numeric(df['latitud'], errors='coerce')
        df['longitud'] = pd.to_numeric(df['longitud'], errors='coerce')
    return df

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem 0 1.5rem 0;">
        <div style="font-family:'DM Serif Display',serif;font-size:2.8rem;color:#a8d5b5;">GeoClima</div>
        <div style="font-size:1.0rem;color:#4a7c59;letter-spacing:0.15em;text-transform:uppercase;">Antioquia · Colombia</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<style>div[role="radiogroup"] p {color: #FFFFFF !important; font-weight: 500;}</style>', unsafe_allow_html=True)
    st.markdown("**Navegación**")
    pagina = st.radio(
        "",
        ["📊 Resumen general", "🗺️ Mapa georreferenciado",
         "📈 Tendencias temporales", "⚖️ Comparativo"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("**Filtros de tiempo**")

    # Años disponibles: cargamos desde datos de temperatura (más amplio)
    df_temp_raw = load_temperatura()
    años_disp = []
    if not df_temp_raw.empty and 'año' in df_temp_raw.columns:
        años_disp = sorted(df_temp_raw['año'].dropna().unique().astype(int).tolist())

    if años_disp:
        año_min, año_max = min(años_disp), max(años_disp)
        rango_años = st.slider(
            "Rango de años",
            min_value=año_min,
            max_value=año_max,
            value=(año_max - 4 if año_max - 4 >= año_min else año_min, año_max),
            step=1
        )
    else:
        rango_años = (2000, 2022)

    MESES_ES = {
        "January": "Enero", "February": "Febrero", "March": "Marzo",
        "April": "Abril", "May": "Mayo", "June": "Junio",
        "July": "Julio", "August": "Agosto", "September": "Septiembre",
        "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
    }
    MESES_ORDEN = list(MESES_ES.values())

    meses_sel_es = st.multiselect(
        "Meses",
        options=MESES_ORDEN,
        default=MESES_ORDEN,
        placeholder="Todos los meses"
    )
    if not meses_sel_es:
        meses_sel_es = MESES_ORDEN

    # Traducción inversa para filtrar
    meses_sel_en = [k for k, v in MESES_ES.items() if v in meses_sel_es]

    st.markdown("---")
    st.markdown(
        '<div style="font-size:0.8rem;color:#2d5c3e;text-align:center;">Análisis de datos Integrador</div>',
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────
# FUNCIÓN DE FILTRADO
# ─────────────────────────────────────────────
def filtrar(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    if 'año' in df.columns:
        df = df[df['año'].between(rango_años[0], rango_años[1])]
    if 'mes_nombre' in df.columns and meses_sel_en:
        df = df[df['mes_nombre'].isin(meses_sel_en)]
    return df

# ─────────────────────────────────────────────
# CARGA Y FILTRADO
# ─────────────────────────────────────────────
with st.spinner("Cargando datos climáticos..."):
    df_temp   = filtrar(load_temperatura())
    df_precip = filtrar(load_precipitacion())
    df_brillo = filtrar(load_brillo())
    df_muni   = load_municipios()

# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
    <p class="hero-subtitle">Dashboard climático · Antioquia, Colombia</p>
    <h1 class="hero-title">GeoClima Municipios de Antioquia</h1>
    <div style="margin-top:1rem;display:flex;flex-wrap:wrap;gap:0.4rem;">
        <span class="info-badge">📅 {rango_años[0]} – {rango_años[1]}</span>
        <span class="info-badge">🌡️ Temperatura diaria</span>
        <span class="info-badge">🌧️ Precipitación mensual</span>
        <span class="info-badge">☀️ Brillo solar diario</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PÁGINA 1: RESUMEN GENERAL
# ─────────────────────────────────────────────
if pagina == "📊 Resumen general":
    # KPIs
    c1, c2, c3, c4, c5 = st.columns(5)

    temp_max_prom = df_temp['temp_max'].mean() if not df_temp.empty else None
    temp_min_prom = df_temp['temp_min'].mean() if not df_temp.empty else None
    precip_total  = df_precip['precipitacion_mm'].sum() if not df_precip.empty else None
    brillo_prom   = df_brillo['brillo_horas'].mean() if not df_brillo.empty else None
    n_municipios  = df_muni.shape[0] if not df_muni.empty else 0

    def kpi(col, label, value, unit, fmt=".1f"):
        with col:
            val_str = f"{value:{fmt}}" if value is not None else "N/D"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{val_str}</div>
                <div class="metric-unit">{unit}</div>
            </div>
            """, unsafe_allow_html=True)

    kpi(c1, "Temp. Máx. Prom.", temp_max_prom, "°C promedio")
    kpi(c2, "Temp. Mín. Prom.", temp_min_prom, "°C promedio")
    kpi(c3, "Precipitación acumulada", precip_total, "mm totales", fmt=",.0f")
    kpi(c4, "Brillo solar prom.", brillo_prom, "horas/sol diarias")
    kpi(c5, "Municipios", n_municipios, "estaciones activas", fmt=".0f")

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Temperatura por municipio
    st.markdown('<div class="section-title">Temperatura promedio por municipio</div>', unsafe_allow_html=True)

    if not df_temp.empty:
        temp_muni = df_temp.groupby('Municipio').agg(
            temp_max=('temp_max', 'mean'),
            temp_min=('temp_min', 'mean')
        ).reset_index().sort_values('temp_max', ascending=False)

        fig_temp = go.Figure()
        fig_temp.add_bar(
            x=temp_muni['Municipio'],
            y=temp_muni['temp_max'],
            name="Máxima prom.",
            marker_color=[COLORES_MUNICIPIOS.get(m, "#52b788") for m in temp_muni['Municipio']],
            opacity=0.9
        )
        fig_temp.add_bar(
            x=temp_muni['Municipio'],
            y=temp_muni['temp_min'],
            name="Mínima prom.",
            marker_color=[COLORES_MUNICIPIOS.get(m, "#2d6a4f") for m in temp_muni['Municipio']],
            opacity=0.5
        )
        apply_layout(
            fig_temp,
            barmode='group',
            title=dict(text="°C promedio por municipio", font=dict(color="#6fa87e", size=13)),
            yaxis_title="°C",
            height=320,
            legend=dict(orientation="h", y=1.1, bgcolor="rgba(0,0,0,0)", font=dict(color="#9cbfa8"))
        )
        st.plotly_chart(fig_temp, use_container_width=True)

    col_a, col_b = st.columns(2)

    # ── Precipitación anual
    with col_a:
        st.markdown('<div class="section-title">Precipitación total anual</div>', unsafe_allow_html=True)
        if not df_precip.empty:
            precip_anual = df_precip.groupby(['año', 'Municipio'])['precipitacion_mm'].sum().reset_index()
            precip_anual_tot = precip_anual.groupby('año')['precipitacion_mm'].sum().reset_index()

            fig_p = px.area(
                precip_anual_tot, x='año', y='precipitacion_mm',
                color_discrete_sequence=["#52b788"]
            )
            fig_p.update_traces(
                fillcolor="rgba(82,183,136,0.15)",
                line=dict(color="#52b788", width=2)
            )
            apply_layout(
                fig_p,
                title=dict(text="mm totales anuales (todos los municipios)", font=dict(color="#6fa87e", size=12)),
                yaxis_title="mm",
                xaxis_title="",
                height=280,
                showlegend=False
            )
            st.plotly_chart(fig_p, use_container_width=True)

    # ── Brillo solar mensual promedio
    with col_b:
        st.markdown('<div class="section-title">Brillo solar por mes</div>', unsafe_allow_html=True)
        if not df_brillo.empty:
            # Orden de meses
            mes_order_en = list(MESES_ES.keys())
            brillo_mes = df_brillo.groupby('mes_nombre')['brillo_horas'].mean().reset_index()
            brillo_mes['mes_orden'] = brillo_mes['mes_nombre'].map(
                {m: i for i, m in enumerate(mes_order_en)}
            )
            brillo_mes = brillo_mes.sort_values('mes_orden')
            brillo_mes['mes_es'] = brillo_mes['mes_nombre'].map(MESES_ES)

            fig_b = px.bar(
                brillo_mes, x='mes_es', y='brillo_horas',
                color='brillo_horas',
                color_continuous_scale=["#1b4332", "#52b788", "#d8f3dc"]
            )
            apply_layout(
                fig_b,
                title=dict(text="Promedio de horas de sol por mes", font=dict(color="#6fa87e", size=12)),
                yaxis_title="horas/sol",
                xaxis_title="",
                height=280,
                showlegend=False,
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_b, use_container_width=True)

# ─────────────────────────────────────────────
# PÁGINA 2: MAPA
# ─────────────────────────────────────────────
elif pagina == "🗺️ Mapa georreferenciado":
    st.markdown('<div class="section-title">Mapa de municipios · Antioquia</div>', unsafe_allow_html=True)

    col_ctrl, col_map = st.columns([1, 3])

    with col_ctrl:
        variable_mapa = st.selectbox(
            "Variable a visualizar",
            ["Temperatura máxima", "Temperatura mínima", "Precipitación acumulada", "Brillo solar"]
        )
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown("**Municipios disponibles**")
        for _, row in df_muni.iterrows():
            color = COLORES_MUNICIPIOS.get(row['Municipio'], "#52b788")
            st.markdown(f"""
            <span style="display:flex;align-items:center;gap:0.5rem;margin:0.3rem 0;">
                <span style="width:8px;height:8px;border-radius:50%;background:{color};display:inline-block;"></span>
                <span style="font-size:0.85rem;color:#9cbfa8;">{row['Municipio']}</span>
            </span>
            """, unsafe_allow_html=True)

    with col_map:
        # Construir df para el mapa
        if variable_mapa == "Temperatura máxima" and not df_temp.empty:
            df_map = df_temp.groupby(['Municipio', 'latitud', 'longitud'])['temp_max'].mean().reset_index()
            df_map.rename(columns={'temp_max': 'valor'}, inplace=True)
            etiqueta = "Temp. máx. prom. (°C)"
            escala = "YlOrRd"
        elif variable_mapa == "Temperatura mínima" and not df_temp.empty:
            df_map = df_temp.groupby(['Municipio', 'latitud', 'longitud'])['temp_min'].mean().reset_index()
            df_map.rename(columns={'temp_min': 'valor'}, inplace=True)
            etiqueta = "Temp. mín. prom. (°C)"
            escala = "Blues"
        elif variable_mapa == "Precipitación acumulada" and not df_precip.empty:
            df_map = df_precip.groupby(['Municipio', 'latitud', 'longitud'])['precipitacion_mm'].sum().reset_index()
            df_map.rename(columns={'precipitacion_mm': 'valor'}, inplace=True)
            etiqueta = "Precipitación acumulada (mm)"
            escala = "Teal"
        elif variable_mapa == "Brillo solar" and not df_brillo.empty:
            df_map = df_brillo.groupby(['Municipio', 'latitud', 'longitud'])['brillo_horas'].mean().reset_index()
            df_map.rename(columns={'brillo_horas': 'valor'}, inplace=True)
            etiqueta = "Brillo solar prom. (h/sol)"
            escala = "Oranges"
        else:
            df_map = pd.DataFrame()

        if not df_map.empty and df_map['latitud'].notna().any():
            df_map = df_map.dropna(subset=['latitud', 'longitud'])

            # Normalizar tamaño: scatter_mapbox requiere valores > 0
            v_min = df_map['valor'].min()
            df_map['tamaño'] = df_map['valor'] - v_min + 1

            fig_map = px.scatter_mapbox(
                df_map,
                lat="latitud", lon="longitud",
                hover_name="Municipio",
                color="valor",
                size="tamaño",
                size_max=40,
                color_continuous_scale=escala,
                zoom=6.5,
                center={"lat": df_map['latitud'].mean(), "lon": df_map['longitud'].mean()},
                mapbox_style="carto-darkmatter",
                height=520,
                labels={"valor": etiqueta}
            )
            fig_map.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin={"r": 0, "t": 0, "l": 0, "b": 0},
                coloraxis_colorbar=dict(
                    title=dict(text=etiqueta, font=dict(color="#9cbfa8", size=11)),
                    tickfont=dict(color="#9cbfa8"),
                    bgcolor="rgba(17,31,23,0.8)",
                    bordercolor="#1e3328"
                )
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("No hay datos disponibles para esta variable con los filtros actuales.")

# ─────────────────────────────────────────────
# PÁGINA 3: TENDENCIAS
# ─────────────────────────────────────────────
elif pagina == "📈 Tendencias temporales":
    st.markdown('<div class="section-title">Evolución histórica de variables climáticas</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🌡️ Temperatura", "🌧️ Precipitación", "☀️ Brillo solar"])

    # ── Tab Temperatura
    with tab1:
        if not df_temp.empty:
            agrup_temp = st.selectbox(
                "Agrupar por",
                ["Mes", "Año", "Trimestre"],
                key="agrup_temp"
            )
            municipios_temp = sorted(df_temp['Municipio'].unique().tolist())
            muni_sel_temp = st.multiselect(
                "Municipios",
                municipios_temp,
                default=municipios_temp[:3] if len(municipios_temp) >= 3 else municipios_temp,
                key="muni_temp"
            )

            df_t = df_temp[df_temp['Municipio'].isin(muni_sel_temp)] if muni_sel_temp else df_temp

            if agrup_temp == "Mes":
                df_t_g = df_t.groupby(['año', 'mes_num', 'mes_nombre', 'Municipio']).agg(
                    temp_max=('temp_max', 'mean'), temp_min=('temp_min', 'mean')
                ).reset_index()
                df_t_g = df_t_g.sort_values(['año', 'mes_num'])
                df_t_g['periodo'] = df_t_g['año'].astype(str) + '-' + df_t_g['mes_num'].astype(str).str.zfill(2)
                x_col = 'periodo'
            elif agrup_temp == "Trimestre":
                df_t_g = df_t.groupby(['año', 'trimestre', 'Municipio']).agg(
                    temp_max=('temp_max', 'mean'), temp_min=('temp_min', 'mean')
                ).reset_index()
                df_t_g['periodo'] = df_t_g['año'].astype(str) + ' ' + df_t_g['trimestre']
                df_t_g = df_t_g.sort_values(['año', 'trimestre'])
                x_col = 'periodo'
            else:
                df_t_g = df_t.groupby(['año', 'Municipio']).agg(
                    temp_max=('temp_max', 'mean'), temp_min=('temp_min', 'mean')
                ).reset_index()
                x_col = 'año'

            col_tmax, col_tmin = st.columns(2)
            with col_tmax:
                fig_tmax = px.line(
                    df_t_g, x=x_col, y='temp_max', color='Municipio',
                    color_discrete_map=COLORES_MUNICIPIOS,
                    title="Temperatura máxima promedio"
                )
                fig_tmax.update_traces(line=dict(width=2))
                apply_layout(fig_tmax, height=320, yaxis_title="°C",
                             title=dict(text="Temperatura máxima prom.", font=dict(color="#6fa87e", size=13)))
                st.plotly_chart(fig_tmax, use_container_width=True)

            with col_tmin:
                fig_tmin = px.line(
                    df_t_g, x=x_col, y='temp_min', color='Municipio',
                    color_discrete_map=COLORES_MUNICIPIOS,
                )
                fig_tmin.update_traces(line=dict(width=2))
                apply_layout(fig_tmin, height=320, yaxis_title="°C",
                             title=dict(text="Temperatura mínima prom.", font=dict(color="#6fa87e", size=13)))
                st.plotly_chart(fig_tmin, use_container_width=True)

            # Rango diario como ribbon
            st.markdown("**Rango diario de temperatura** (máx. y mín. por año)")
            df_rango = df_temp.groupby(['año', 'Municipio']).agg(
                t_max=('temp_max', 'mean'), t_min=('temp_min', 'mean')
            ).reset_index()
            df_rango['rango'] = df_rango['t_max'] - df_rango['t_min']
            fig_rango = px.bar(
                df_rango[df_rango['Municipio'].isin(muni_sel_temp or municipios_temp)],
                x='año', y='rango', color='Municipio',
                barmode='group',
                color_discrete_map=COLORES_MUNICIPIOS
            )
            apply_layout(fig_rango, height=260, yaxis_title="Rango °C",
                         title=dict(text="Amplitud térmica diaria promedio", font=dict(color="#6fa87e", size=13)))
            st.plotly_chart(fig_rango, use_container_width=True)
        else:
            st.info("No hay datos de temperatura para los filtros seleccionados.")

    # ── Tab Precipitación
    with tab2:
        if not df_precip.empty:
            col_pa, col_pb = st.columns([1, 3])
            with col_pa:
                agrup_p = st.selectbox("Agrupar por", ["Año", "Mes", "Trimestre"], key="agrup_p")
                municipios_p = sorted(df_precip['Municipio'].unique().tolist())
                muni_sel_p = st.multiselect(
                    "Municipios",
                    municipios_p,
                    default=municipios_p[:3] if len(municipios_p) >= 3 else municipios_p,
                    key="muni_p"
                )

            df_p = df_precip[df_precip['Municipio'].isin(muni_sel_p)] if muni_sel_p else df_precip

            with col_pb:
                if agrup_p == "Año":
                    df_p_g = df_p.groupby(['año', 'Municipio'])['precipitacion_mm'].sum().reset_index()
                    x_col_p = 'año'
                elif agrup_p == "Mes":
                    df_p_g = df_p.groupby(['mes_nombre', 'Municipio'])['precipitacion_mm'].mean().reset_index()
                    orden_meses_en = list(MESES_ES.keys())
                    df_p_g['orden'] = df_p_g['mes_nombre'].map({m: i for i, m in enumerate(orden_meses_en)})
                    df_p_g = df_p_g.sort_values('orden')
                    df_p_g['mes_es'] = df_p_g['mes_nombre'].map(MESES_ES)
                    x_col_p = 'mes_es'
                else:
                    df_p_g = df_p.groupby(['trimestre', 'Municipio'])['precipitacion_mm'].sum().reset_index()
                    x_col_p = 'trimestre'

                y_label = "mm acumulados" if agrup_p != "Mes" else "mm promedio mensual"
                fig_p = px.bar(
                    df_p_g, x=x_col_p,
                    y='precipitacion_mm' if 'precipitacion_mm' in df_p_g.columns else df_p_g.columns[-1],
                    color='Municipio',
                    barmode='group',
                    color_discrete_map=COLORES_MUNICIPIOS
                )
                apply_layout(
                    fig_p,
                    title=dict(text=f"Precipitación por {agrup_p.lower()}", font=dict(color="#6fa87e", size=13))
                )
                st.plotly_chart(fig_p, use_container_width=True)

            # Boxplot mensual
            st.markdown("**Distribución mensual de precipitación**")
            meses_en_ord = list(MESES_ES.keys())
            df_precip_box = df_precip.copy()
            df_precip_box['mes_es'] = df_precip_box['mes_nombre'].map(MESES_ES)
            df_precip_box['mes_orden'] = df_precip_box['mes_nombre'].map(
                {m: i for i, m in enumerate(meses_en_ord)}
            )
            df_precip_box = df_precip_box.sort_values('mes_orden')

            fig_box = px.box(
                df_precip_box, x='mes_es', y='precipitacion_mm',
                color_discrete_sequence=["#52b788"]
            )
            apply_layout(
                fig_box,
                title=dict(text="Variabilidad mensual (todos los municipios y años)", font=dict(color="#6fa87e", size=13)),
                showlegend=False
            )
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.info("No hay datos de precipitación para los filtros seleccionados.")

    # ── Tab Brillo solar
    with tab3:
        if not df_brillo.empty:
            agrup_b = st.selectbox("Agrupar por", ["Mes", "Año", "Trimestre"], key="agrup_b")
            municipios_b = sorted(df_brillo['Municipio'].unique().tolist())
            muni_sel_b = st.multiselect(
                "Municipios",
                municipios_b,
                default=municipios_b,
                key="muni_b"
            )
            df_b = df_brillo[df_brillo['Municipio'].isin(muni_sel_b)] if muni_sel_b else df_brillo

            meses_en_ord = list(MESES_ES.keys())
            if agrup_b == "Mes":
                df_b_g = df_b.groupby(['mes_nombre', 'Municipio'])['brillo_horas'].mean().reset_index()
                df_b_g['orden'] = df_b_g['mes_nombre'].map({m: i for i, m in enumerate(meses_en_ord)})
                df_b_g = df_b_g.sort_values('orden')
                df_b_g['mes_es'] = df_b_g['mes_nombre'].map(MESES_ES)
                x_col_b = 'mes_es'
            elif agrup_b == "Año":
                df_b_g = df_b.groupby(['año', 'Municipio'])['brillo_horas'].mean().reset_index()
                x_col_b = 'año'
            else:
                df_b_g = df_b.groupby(['trimestre', 'Municipio'])['brillo_horas'].mean().reset_index()
                x_col_b = 'trimestre'

            fig_bri = px.line(
                df_b_g, x=x_col_b, y='brillo_horas', color='Municipio',
                markers=True,
                color_discrete_map=COLORES_MUNICIPIOS
            )
            fig_bri.update_traces(line=dict(width=2), marker=dict(size=5))
            apply_layout(
                fig_bri,
                title=dict(text=f"Brillo solar promedio por {agrup_b.lower()}", font=dict(color="#6fa87e", size=13))
            )
            st.plotly_chart(fig_bri, use_container_width=True)

            # Heatmap brillo por mes y año
            st.markdown("**Mapa de calor: brillo solar por mes y año**")
            muni_hm = st.selectbox(
                "Municipio para heatmap",
                sorted(df_brillo['Municipio'].unique().tolist()),
                key="muni_hm"
            )
            df_hm = df_brillo[df_brillo['Municipio'] == muni_hm].copy()
            if not df_hm.empty:
                df_hm['mes_es']   = df_hm['mes_nombre'].map(MESES_ES)
                df_hm['mes_orden']= df_hm['mes_nombre'].map({m: i for i, m in enumerate(meses_en_ord)})
                df_pivot = df_hm.groupby(['año', 'mes_orden', 'mes_es'])['brillo_horas'].mean().reset_index()
                df_pivot = df_pivot.sort_values('mes_orden')
                pivot_table = df_pivot.pivot(index='mes_es', columns='año', values='brillo_horas')
                # Ordenar filas
                orden_es = [MESES_ES[m] for m in meses_en_ord if MESES_ES[m] in pivot_table.index]
                pivot_table = pivot_table.reindex(orden_es)

                fig_hm = px.imshow(
                    pivot_table,
                    color_continuous_scale=["#1b4332", "#40916c", "#74c99a", "#d8f3dc"],
                    aspect="auto"
                )
                apply_layout(
                    fig_hm,
                    title=dict(text=f"Horas de sol · {muni_hm}", font=dict(color="#6fa87e", size=13)),
                    xaxis_title="Año", yaxis_title="",
                    coloraxis_colorbar=dict(
                        title=dict(text="h/sol", font=dict(color="#9cbfa8", size=10)),
                        tickfont=dict(color="#9cbfa8")
                    )
                )
                st.plotly_chart(fig_hm, use_container_width=True)
        else:
            st.info("No hay datos de brillo solar para los filtros seleccionados.")

# ─────────────────────────────────────────────
# PÁGINA 4: COMPARATIVO
# ─────────────────────────────────────────────
elif pagina == "⚖️ Comparativo":
    st.markdown('<div class="section-title">Comparativo entre municipios</div>', unsafe_allow_html=True)

    col_c1, col_c2 = st.columns([1, 2])

    all_munis = sorted(set(
        list(df_temp['Municipio'].unique() if not df_temp.empty else []) +
        list(df_precip['Municipio'].unique() if not df_precip.empty else []) +
        list(df_brillo['Municipio'].unique() if not df_brillo.empty else [])
    ))

    with col_c1:
        muni_comp = st.multiselect(
            "Selecciona municipios",
            all_munis,
            default=all_munis[:3] if len(all_munis) >= 3 else all_munis
        )
        var_comp = st.selectbox(
            "Variable principal",
            ["Temperatura máxima", "Temperatura mínima", "Amplitud térmica",
             "Precipitación acumulada", "Brillo solar"]
        )
        agrupar_comp = st.selectbox("Agrupar por", ["Año", "Mes", "Trimestre"])

    with col_c2:
        meses_en_ord = list(MESES_ES.keys())

        def preparar_comp(df, col_valor, agrupar):
            if df.empty or not muni_comp:
                return pd.DataFrame()
            df = df[df['Municipio'].isin(muni_comp)]
            if agrupar == "Año":
                g = df.groupby(['año', 'Municipio'])[col_valor].mean().reset_index()
                g['eje_x'] = g['año'].astype(str)
            elif agrupar == "Mes":
                g = df.groupby(['mes_nombre', 'Municipio'])[col_valor].mean().reset_index()
                g['orden'] = g['mes_nombre'].map({m: i for i, m in enumerate(meses_en_ord)})
                g = g.sort_values('orden')
                g['eje_x'] = g['mes_nombre'].map(MESES_ES)
            else:
                g = df.groupby(['trimestre', 'Municipio'])[col_valor].mean().reset_index()
                g['eje_x'] = g['trimestre']
            return g

        if var_comp == "Temperatura máxima":
            df_c = preparar_comp(df_temp, 'temp_max', agrupar_comp)
            y_col, y_lbl = 'temp_max', 'Temp. máxima prom. (°C)'
        elif var_comp == "Temperatura mínima":
            df_c = preparar_comp(df_temp, 'temp_min', agrupar_comp)
            y_col, y_lbl = 'temp_min', 'Temp. mínima prom. (°C)'
        elif var_comp == "Amplitud térmica":
            if not df_temp.empty and muni_comp:
                df_tmp = df_temp[df_temp['Municipio'].isin(muni_comp)].copy()
                df_tmp['amplitud'] = df_tmp['temp_max'] - df_tmp['temp_min']
                df_c = preparar_comp(df_tmp, 'amplitud', agrupar_comp)
                y_col, y_lbl = 'amplitud', 'Amplitud térmica prom. (°C)'
            else:
                df_c = pd.DataFrame()
                y_col, y_lbl = '', ''
        elif var_comp == "Precipitación acumulada":
            if not df_precip.empty and muni_comp:
                df_p2 = df_precip[df_precip['Municipio'].isin(muni_comp)]
                if agrupar_comp == "Año":
                    df_c = df_p2.groupby(['año', 'Municipio'])['precipitacion_mm'].sum().reset_index()
                    df_c['eje_x'] = df_c['año'].astype(str)
                elif agrupar_comp == "Mes":
                    df_c = df_p2.groupby(['mes_nombre', 'Municipio'])['precipitacion_mm'].sum().reset_index()
                    df_c['orden'] = df_c['mes_nombre'].map({m: i for i, m in enumerate(meses_en_ord)})
                    df_c = df_c.sort_values('orden')
                    df_c['eje_x'] = df_c['mes_nombre'].map(MESES_ES)
                else:
                    df_c = df_p2.groupby(['trimestre', 'Municipio'])['precipitacion_mm'].sum().reset_index()
                    df_c['eje_x'] = df_c['trimestre']
                y_col, y_lbl = 'precipitacion_mm', 'Precipitación (mm)'
            else:
                df_c = pd.DataFrame()
                y_col, y_lbl = '', ''
        else:  # Brillo solar
            df_c = preparar_comp(df_brillo, 'brillo_horas', agrupar_comp)
            y_col, y_lbl = 'brillo_horas', 'Brillo solar prom. (h/sol)'

        if not df_c.empty and y_col in df_c.columns:
            fig_comp = px.line(
                df_c, x='eje_x', y=y_col, color='Municipio',
                markers=True,
                color_discrete_map=COLORES_MUNICIPIOS
            )
            fig_comp.update_traces(line=dict(width=2.5), marker=dict(size=6))
            apply_layout(
                fig_comp,
                xaxis_title=agrupar_comp,
                title=dict(text=f"{var_comp} · comparativo por {agrupar_comp.lower()}", font=dict(color="#6fa87e", size=13))
            )
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.info("No hay datos suficientes para la combinación seleccionada.")

    # Tabla resumen comparativo
    st.markdown('<div class="section-title">Resumen estadístico</div>', unsafe_allow_html=True)

    filas = []
    for m in (muni_comp or all_munis):
        fila = {"Municipio": m}
        if not df_temp.empty:
            sub = df_temp[df_temp['Municipio'] == m]
            fila["Temp. máx. prom. (°C)"] = round(sub['temp_max'].mean(), 1) if not sub.empty else None
            fila["Temp. mín. prom. (°C)"] = round(sub['temp_min'].mean(), 1) if not sub.empty else None
        if not df_precip.empty:
            sub = df_precip[df_precip['Municipio'] == m]
            fila["Precip. total (mm)"] = round(sub['precipitacion_mm'].sum(), 0) if not sub.empty else None
        if not df_brillo.empty:
            sub = df_brillo[df_brillo['Municipio'] == m]
            fila["Brillo prom. (h/sol)"] = round(sub['brillo_horas'].mean(), 1) if not sub.empty else None
        filas.append(fila)

    if filas:
        df_resumen = pd.DataFrame(filas).set_index("Municipio")
        st.dataframe(
            df_resumen,
            use_container_width=True,
        )

st.sidebar.caption("Proyecto 2026 | Creado: Andres Martinez")
