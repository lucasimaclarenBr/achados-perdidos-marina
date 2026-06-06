import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def iniciar_conexao() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = iniciar_conexao()