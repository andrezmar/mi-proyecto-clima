import streamlit as st
from sqlalchemy import create_engine
import pandas as pd

@st.cache_resource
def get_engine():
    cfg = st.secrets["mysql"]
    url = (
        f"mysql+pymysql://{cfg['user']}:{cfg['password']}"
        f"@{cfg['host']}:{cfg['port']}/{cfg['database']}"
    )
    return create_engine(url)

def query(sql: str) -> pd.DataFrame:
    with get_engine().connect() as conn:
        return pd.read_sql(sql, conn)