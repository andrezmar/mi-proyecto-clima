from sqlalchemy import create_engine

@st.cache_resource
def get_engine():
    return create_engine(
        f"mysql+pymysql://{st.secrets['DB_USER']}:{st.secrets['DB_PASSWORD']}"
        f"@{st.secrets['DB_HOST']}:{st.secrets['DB_PORT']}/{st.secrets['DB_NAME']}"
    )

@st.cache_data(ttl=600)
def load_comprehensive_data():
    engine = get_engine()
    query = """..."""  # tu query actual, sin cambios
    return pd.read_sql(query, engine)
