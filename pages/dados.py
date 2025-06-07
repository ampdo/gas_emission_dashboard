import streamlit as st
import pandas as pd
import plotly.express as px


@st.cache_data
def converte_csv(df):

    """Função para carregar os dados do CSV."""
    return df.to_csv(index=False, encoding='utf-8-sig')

# -------- CONFIGURAÇÃO DE PAGINA --------
st.set_page_config(layout="wide")

# -------- TÍTULO DA PÁGINA --------
st.title("Tabela de Dados")




# ----------------------------------------
# DADOS
# ----------------------------------------
# -------- LENDO DADOS --------
dados = pd.read_csv("emissoes.csv")

# ----------------------------------------
# DASHBOARD
# ----------------------------------------
# -------- EXIBINDO DADOS --------
st.title("Tabela de Dados")

with st.expander("Visualizar Dados"):
    colunas = st.multiselect(
        "Selecione as colunas para exibir:",
        list(dados.columns),default=list(dados.columns)
    )

dados = dados[colunas]     

st.dataframe(dados)
st.markdown(f':blue[{dados.shape[0]} linhas e {dados.shape[1]} colunas]')


# -------- DOWNLOAD DOS DADOS --------
st.download_button(
    label="Download ",
    data=converte_csv(dados),
    file_name='dados.csv',
    mime='text/csv',
    icon=":material/download:"
)   
