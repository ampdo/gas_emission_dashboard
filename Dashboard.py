import streamlit as st
import pandas as pd
import plotly.express as px
# -------- CONFIGURAÇÃO DE PAGINA --------
st.set_page_config(layout="wide")
# ----------------------------------------
#              FUNÇÕES
# ----------------------------------------


def formataNumero(valor):
    if valor >= 1_000_000_000:
        return f'{valor / 1_000_000_000:.1f} bi'
    if valor >= 1_000_000:
        return f'{valor / 1_000_000:.1f} mi'
    if valor >= 1000:
        return f'{valor / 1000:.1f} k'

    return str(valor)


# ----------------------------------------
# DADOS
# ----------------------------------------
dados = pd.read_csv('emissoes.csv')

# ----------------------------------------
# TABELAS
# ----------------------------------------
# emissoes_estados = dados.groupby('Estado')[['Emissão']].sum().ressset_index()
# emissoes_estados = dados.drop_duplicates(subset='Estado')[['Estado','lat','long']].merge(emissoes_estados, on='Estado').reset_index()
# emissoes_estados.drop('index', axis=1, inplace=True)

##ESTADOS
emissoes_estados = dados.groupby('Estado')[['Emissão']].sum().reset_index()
emissoes_estados = dados.drop_duplicates(subset='Estado')[
    ['Estado', 'lat', 'long']].merge(emissoes_estados, on='Estado').reset_index()
emissoes_estados.drop('index', axis=1, inplace=True)

## SETORES
emissoes_setores = dados.groupby('Setor_emissao')[['Emissão']].sum().reset_index()

## ANOS
emissoes_anos = dados.groupby('Ano')[['Emissão']].sum().sort_values(by='Ano').reset_index()

# ----------------------------------------
#  GRAFICOS
# ----------------------------------------
## ESTADOS
fig_mapa_emissoes = px.scatter_geo(emissoes_estados,
                                   lat='lat',
                                   lon='long',
                                   scope='south america',
                                   size='Emissão',
                                   hover_name='Estado',
                                   hover_data={'lat':False,'long':False},
                                   color='Estado',
                                   text='Estado',
                                   title='Total de Emissão por Estado')



##SETORES
fig_emissoes_setores = px.bar(emissoes_setores,
                              x='Emissão',
                              y='Setor_emissao',
                              color='Setor_emissao',
                              title='Emissão por Setores')

fig_emissoes_setores.update_layout(yaxis_title='', showlegend=False)

#ANOS
fig_emissoes_anos = px.line(emissoes_anos,
                           x='Ano',
                           y='Emissão',
                           title='Total Emissão por Ano')


# ----------------------------------------
# DASHBOARD
# ----------------------------------------
# ---------- TITULO
st.header("EMISSÕES DE GASES DE EFEITO ESTUFA")

tab_home, tab_gas, tabela_Geral = st.tabs(["Home", "Gas","Tabela"])
with tab_home:
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Emissoes", formataNumero(dados['Emissão'].sum()) + ' de toneladas')
        st.plotly_chart(fig_mapa_emissoes)

    with col2:
        idx_maior_emissao = emissoes_anos.index[emissoes_anos['Emissão'] == emissoes_anos['Emissão'].max()]
        ano_mais_poluente = emissoes_anos.iloc[idx_maior_emissao[0]]['Ano']
        emissoes_ano_mais_poluente = emissoes_anos.iloc[idx_maior_emissao[0]]['Emissão']
        st.metric(f'Ano mais poluente: {ano_mais_poluente}', formataNumero(emissoes_ano_mais_poluente) + ' de toneladas')
        st.plotly_chart(fig_emissoes_setores)
        
        st.plotly_chart(fig_emissoes_anos)
        
 #   #st.metric("Total Estados", len(dados['Estado'].unique()))
 #   idx_maior_emissao = emissoes_anos.index[emissoes_anos['Emissão']== emissoes_anos['Emissão'].max()]
 #   anos_mais_poluentes = emissoes_anos.iloc[idx_maior_emissao[0]]['Ano'].astype(int)
 #   emissao_ano_mais_poluente = emissoes_anos.iloc[idx_maior_emissao[0]]['Emissão']
 #   st.metric("Ano mais poluente", {anos_mais_poluentes}, formataNumero(emissao_ano_mais_poluente) + ' de toneladas')
                                        


with tab_gas:
    col1, col2 = st.columns(2)

    with col1:
        ##gas com mais emissões
        idx_maior_emissao = dados.index[dados['Emissão'] == dados['Emissão'].max()]
        st.metric("Gás com Mais Emissões", idx_maior_emissao.iloc[idx_maior_emissao]]['Gás'])
        
        
        
        #gas_com_mais_emissoes = dados.groupby('Gás')[['Emissão']].sum().reset_index()
        #st.metric("Gás com Mais Emissões", gas_com_mais_emissoes['Gás'][gas_com_mais_emissoes['Emissão'].idxmax()])
       

    with col2:
        ##gas com menos emissões
        idx_menor_emissao = dados.index[dados['Emissão'] == dados['Emissão'].min()]
        st.metric("Gás com Menos Emissões", idx_menor_emissao.iloc[idx_menor_emissao]['Gás'])
        
        #gas_com_menos_emissoes = dados.groupby('Gás')[['Emissão']].sum().reset_index()  
        #st.metric("Gás com Menos Emissões", gas_com_menos_emissoes['Gás'][gas_com_menos_emissoes['Emissão'].idxmin()])
        ##total de gases
        
with tabela_Geral:       
    st.dataframe(dados)






