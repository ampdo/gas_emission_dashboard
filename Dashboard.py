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
# SIDEBAR
# ----------------------------------------
st.sidebar.title("Filtros")
# check box para selecionar todos os estados
with st.sidebar.expander('Ano'):
    ano_min = dados['Ano'].min()
    ano_max = dados['Ano'].max()
    todos_anos = st.checkbox('Todos Anos', value=True)
    if todos_anos:
        f_ano = (ano_min, ano_max)
    else:
        # Slider para selecionar o ano
        f_ano = st.slider('Selecione o Ano', ano_min,
                          ano_max, (ano_min, ano_max))


# multiselect para selecionar os setores
with st.sidebar.expander('Setor_emissao'):
    setores = dados['Setor_emissao'].unique()
    f_setor = st.multiselect('Selecione os Setores', setores, default=setores)

with st.sidebar.expander('Gás'):
    gases = dados['Gás'].unique()
    f_gas = st.multiselect('Selecione os Gases', gases, default=gases)

with st.sidebar.expander('Estados ou Regiões'):
    filtro_regiao = st.checkbox('Filtrar por Região')
    estados = dados['Estado'].unique()

    if filtro_regiao:
        regioes = ['Brasil', 'Sudeste', 'Sul']
        regioes = st.selectbox('Selecione a Região', regioes)

        if regioes == 'Brasil':
            f_estado = estados
        elif regioes == 'Sudeste':
            f_estado = ['SP', 'RJ', 'MG', 'ES']
        elif regioes == 'Sul':
            f_estado = ['PR', 'SC', 'RS']
    else:
        f_estado = st.multiselect(
            'Selecione os Estados', estados, default=estados)

# APLICAÇÃO DOS FILTRO DE DADOS
query = '''@f_ano[0] <= Ano <= @f_ano[1] and \
            Setor_emissao in @f_setor and \
            Gás in @f_gas and \
            Estado in @f_estado
        '''
dados = dados.query(query)


# ----------------------------------------
# TABELAS
# ----------------------------------------
# emissoes_estados = dados.groupby('Estado')[['Emissão']].sum().ressset_index()
# emissoes_estados = dados.drop_duplicates(subset='Estado')[['Estado','lat','long']].merge(emissoes_estados, on='Estado').reset_index()
# emissoes_estados.drop('index', axis=1, inplace=True)

# ESTADOS
emissoes_estados = dados.groupby('Estado')[['Emissão']].sum().reset_index()
emissoes_estados = dados.drop_duplicates(subset='Estado')[
    ['Estado', 'lat', 'long']].merge(emissoes_estados, on='Estado').reset_index()
emissoes_estados.drop('index', axis=1, inplace=True)

# SETORES
emissoes_setores = dados.groupby('Setor_emissao')[
    ['Emissão']].sum().reset_index()

# ANOS
emissoes_anos = dados.groupby(
    'Ano')[['Emissão']].sum().sort_values(by='Ano').reset_index()

# GÁS
emissoes_gas = dados.groupby('Gás')[['Emissão']].sum().reset_index()
emissoes_gas['Percentual'] = (
    (emissoes_gas['Emissão'] / emissoes_gas['Emissão'].sum()) * 100).apply(lambda x: f'{x:.2f}%')

emissoes_gas_ano = dados.groupby(['Ano', 'Gás'])[
    ['Emissão']].mean().reset_index()
emissoes_gas_ano = emissoes_gas_ano.pivot(
    index='Ano', columns='Gás', values='Emissão').reset_index()

emissoes_estado_gas = dados.groupby(['Estado', 'Gás'])[
    ['Emissão']].sum().reset_index()


# emissoes_gas_ano['Percentual'] = ((emissoes_gas_ano['Emissão'] / emissoes_gas_ano.groupby('Ano')['Emissão'].transform('sum')) * 100).apply(lambda x: f'{x:.2f}%')
#

# ----------------------------------------
#  GRAFICOS
# ----------------------------------------

fig_emissoes_estado_gas = px.sunburst(emissoes_estado_gas,
                                      path=['Estado', 'Gás'],
                                      values='Emissão',
                                      title='Gás mais emitido por Estado',
                                      color='Gás',
                                      hover_data=['Emissão'])

# ESTADOS
fig_mapa_emissoes = px.scatter_geo(emissoes_estados,
                                   lat='lat',
                                   lon='long',
                                   scope='south america',
                                   size='Emissão',
                                   hover_name='Estado',
                                   hover_data={'lat': False, 'long': False},
                                   color='Estado',
                                   text='Estado',
                                   title='Total de Emissão por Estado')


# SETORES
fig_emissoes_setores = px.bar(emissoes_setores,
                              x='Emissão',
                              y='Setor_emissao',
                              color='Setor_emissao',
                              title='Emissão por Setores')

fig_emissoes_setores.update_layout(yaxis_title='', showlegend=False)

# ANOS
fig_emissoes_anos = px.line(emissoes_anos,
                            x='Ano',
                            y='Emissão',
                            title='Total Emissão por Ano')


# GÁS
# emissoes_gas = emissoes_gas.sort_values(by='Emissão', ascending=False)
fig_emissoes_gas = px.pie(emissoes_gas,
                          values='Emissão',
                          names='Gás',
                          title='Emissão por Gás',
                          color='Gás',
                          hover_data=['Percentual'],
                          labels={'Percentual': 'Percentual'},
                          hole=0.1)

# fig_emissoes_gas.update_traces(textposition='inside', textinfo='percent+label')
# fig_emissoes_gas.update_layout(showlegend=False)
fig_emissoes_gas = px.bar(emissoes_gas,
                          x='Emissão',
                          y='Gás',
                          text_auto=True,
                          color='Gás',
                          title='Emissão por Gás',
                          text='Percentual')

fig_emissoes_gas.update_layout(
    xaxis_title='',
    showlegend=False,
    xaxis=dict(tickformat=',.0f')  # Formatação de número
)
# ----------------------------------------
# DASHBOARD
# ----------------------------------------
# ---------- TITULO
st.header("EMISSÕES DE GASES DE EFEITO ESTUFA")

tab_home, tab_gas, tabela_Geral, tab_estado = st.tabs(
    ["Home", "Gas", "Tabela", "Estados"])
with tab_home:
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Emissoes", formataNumero(
            dados['Emissão'].sum()) + ' de toneladas')
        st.plotly_chart(fig_mapa_emissoes)

    with col2:
        idx_maior_emissao = emissoes_anos.index[emissoes_anos['Emissão']
                                                == emissoes_anos['Emissão'].max()]
        ano_mais_poluente = emissoes_anos.iloc[idx_maior_emissao[0]]['Ano']
        emissoes_ano_mais_poluente = emissoes_anos.iloc[idx_maior_emissao[0]]['Emissão']
        st.metric(f'Ano mais poluente: {ano_mais_poluente}', formataNumero(
            emissoes_ano_mais_poluente) + ' de toneladas')
        st.plotly_chart(fig_emissoes_setores)

    st.plotly_chart(fig_emissoes_gas)
    st.plotly_chart(fig_emissoes_anos)

with st.container(height=500):
    st.subheader("Media das Emissões por Gás por Ano")
    for gas in emissoes_gas_ano.columns:
        fig = px.line(emissoes_gas_ano, x='Ano', y=gas,
                      title=f'Emissão de {gas} por Ano')
        fig.update_layout(
            xaxis_title='Ano',
            yaxis_title='Emissão (toneladas)',
            showlegend=False)  # Formatação de número

        st.plotly_chart(fig)


with tab_gas:
    col1, col2 = st.columns(2)

    with col1:
        # gas com mais emissões
        idx_maior_emissao = emissoes_anos.index[emissoes_anos['Emissão']
                                                == emissoes_anos['Emissão'].max()]
        ano_mais_poluente = emissoes_anos.iloc[idx_maior_emissao[0]]['Ano']
        emissoes_ano_mais_poluente = emissoes_anos.iloc[idx_maior_emissao[0]]['Emissão']
        st.metric(f'Ano mais poluente: {ano_mais_poluente}', formataNumero(
            emissoes_ano_mais_poluente) + ' de toneladas')

        gas_com_mais_emissoes = dados.groupby(
            'Gás')[['Emissão']].sum().reset_index()
        st.metric("Gás com Mais Emissões",
                  gas_com_mais_emissoes['Gás'][gas_com_mais_emissoes['Emissão'].idxmax()])

    with col2:
        # gas com menos emissões
        idx_menor_emissao = emissoes_anos.index[emissoes_anos['Emissão']
                                                == emissoes_anos['Emissão'].min()]
        ano_menos_poluente = emissoes_anos.iloc[idx_menor_emissao[0]]['Ano']
        emissoes_ano_menos_poluente = emissoes_anos.iloc[idx_menor_emissao[0]]['Emissão']
        st.metric(f'Ano menos poluente: {ano_menos_poluente}', formataNumero(
            emissoes_ano_menos_poluente) + ' de toneladas')

        gas_com_menos_emissoes = dados.groupby(
            'Gás')[['Emissão']].sum().reset_index()
        st.metric("Gás com Menos Emissões",
                  gas_com_menos_emissoes['Gás'][gas_com_menos_emissoes['Emissão'].idxmin()])

        st.metric("Total Gases", len(dados['Gás'].unique()))

with tab_estado:
    col1, col2 = st.columns(2, border=True)
    with col1:
        idx_maior_emissao = emissoes_estados.index[emissoes_estados['Emissão']
                                                   == emissoes_estados['Emissão'].max()]
        st.metric("Estado com Mais Emissões",
                  emissoes_estados.iloc[idx_maior_emissao[0]]['Estado'])
    with col2:
        idx_menor_emissao = emissoes_estados.index[emissoes_estados['Emissão']
                                                   == emissoes_estados['Emissão'].min()]
        st.metric("Estado com Menos Emissões",
                  emissoes_estados.iloc[idx_menor_emissao[0]]['Estado'])
    st.plotly_chart(fig_emissoes_estado_gas)

# TABELA GERAL


# with tabela_Geral:
#    st.dataframe(dados)
