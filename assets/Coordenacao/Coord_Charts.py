import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.io as pio
import datetime
import os
import zipfile
import kaleido


chrome_path = st.secrets["chrome_path"]["CHROME_PATH"]

# instala o chromium + dependências
os.system("playwright install chromium")

pio.defaults = [
    "--headless",
    "--no-sandbox",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--single-process",
]

def bar_chart_desvios(dataframe: pd.DataFrame, anos: None, meses: None, estudos: None, categoria_selecionada: None, setor_selecionado: None):
    """
    Cria e exibe um gráfico de barras mostrando a quantidade de categorias por setor.

    Esta função agrupa o DataFrame fornecido por setor, conta o número de categorias em cada setor e cria um
    gráfico de barras usando Plotly Express. O gráfico é exibido interativamente.

    Args:
        df (pd.DataFrame): O DataFrame a ser usado para criar o gráfico, que deve conter a coluna 'Setor' e
                           'Categoria'.

    Returns:
        None: A função exibe o gráfico diretamente e não retorna nenhum valor.
    """
    
    df = dataframe.copy()
        
    if categoria_selecionada:
        df = df[df['Categoria'].isin(categoria_selecionada)]
        if df.empty:
            return None
        
    if setor_selecionado:
        df = df[df['Setor'].isin(setor_selecionado)]
        if df.empty:
            return None
    
    if anos:
        df = df[df['Data da submissão'].dt.year.isin(anos)]
        if df.empty:
            return None
        
    if meses:
        df = df[df['Data da submissão'].dt.month.isin(meses)]
        if df.empty:
            return None
    
    if estudos:
        df = df[df['Estudo'].isin(estudos)]
        if df.empty:
            return None
        

    # Agrupar e contar o número de categorias por setor
    sector_category_count = df.groupby('Setor', observed=False).size().reset_index(name='Número de Categorias')
    sector_category_count = sector_category_count.sort_values(by='Número de Categorias', ascending=False)

    # Criar o gráfico de barras
    fig = px.bar(sector_category_count, x='Setor', y='Número de Categorias',
                 text_auto=True, color='Setor',
                 color_discrete_sequence=px.colors.qualitative.Prism, opacity=0.8,
                 labels={'Setor': 'Setor', 'Número de Categorias': 'Número de Desvios'})

    # Mostrar o gráfico
    return fig


def donut_chart_prejuizos(dataframe: pd.DataFrame, anos: None, meses: None, estudos: None, categoria_selecionada: None, setor_selecionado: None):
    """
    Cria e exibe um gráfico de rosca mostrando a distribuição dos valores na coluna 'Houve prejuízos para o participante?'.

    Esta função conta o número de ocorrências dos valores 'Sim' e 'Não' na coluna fornecida e cria um
    gráfico de rosca usando Plotly Express. O gráfico é exibido interativamente.

    Args:
        df (pd.DataFrame): O DataFrame a ser usado para criar o gráfico, que deve conter a coluna 'Houve prejuízos para o participante?'.

    Returns:
        None: A função exibe o gráfico diretamente e não retorna nenhum valor.
    """
    
    df = dataframe.copy()
    
    if categoria_selecionada:
        df = df[df['Categoria'].isin(categoria_selecionada)]
        if df.empty:
            return None
            
    if setor_selecionado:
        df = df[df['Setor'].isin(setor_selecionado)]
        if df.empty:
            return None
    
    if anos:
        df = df[df['Data da submissão'].dt.year.isin(anos)]
        if df.empty:
            return None
        
    if meses:
        df = df[df['Data da submissão'].dt.month.isin(meses)]
        if df.empty:
            return None
        
    if estudos:
        df = df[df['Estudo'].isin(estudos)]
        if df.empty:
            return None

    # Agrupar e contar o número de ocorrências de cada valor na coluna 'Houve prejuízos para o participante?'
    prejuizos_count = df['Houve prejuízos para o participante?'].value_counts().reset_index()
    prejuizos_count.columns = ['Resposta', 'Número de Ocorrências']

    # Criar o gráfico de rosca
    fig = px.pie(prejuizos_count, names='Resposta', values='Número de Ocorrências', 
                 color='Resposta', 
                 color_discrete_sequence=px.colors.qualitative.Prism, opacity=0.8,
                 hole=0.5)  # Define o gráfico como rosca com um buraco no meio

    # Mostrar o gráfico
    return fig


def bar_chart_desvios_por_estudo(dataframe: pd.DataFrame, anos: None, meses: None, estudos: None, categoria_selecionada: None, setor_selecionado: None):
    """
    Cria e exibe um gráfico de barras mostrando a quantidade de desvios por estudo.

    Esta função conta o número de desvios para cada estudo e cria um gráfico de barras usando Plotly Express.
    O gráfico é exibido interativamente.

    Args:
        df (pd.DataFrame): O DataFrame a ser usado para criar o gráfico, que deve conter a coluna 'estudo' e 'Data do desvio'.

    Returns:
        None: A função exibe o gráfico diretamente e não retorna nenhum valor.
    """
    
    df = dataframe.copy()
    
    if categoria_selecionada:
        df = df[df['Categoria'].isin(categoria_selecionada)]
        if df.empty:
            return None
        
    if setor_selecionado:
        df = df[df['Setor'].isin(setor_selecionado)]
        if df.empty:
            return None
    
    if anos:
        df = df[df['Data da submissão'].dt.year.isin(anos)]
        if df.empty:
            return None
        
    if meses:
        df = df[df['Data da submissão'].dt.month.isin(meses)]
        if df.empty:
            return None
    
    if estudos:
        df = df[df['Estudo'].isin(estudos)]
        if df.empty:
            return None
    
    # Agrupar e contar o número de desvios por estudo
    desvios_count = df.groupby('Estudo', observed=False).size().reset_index(name='Número de Desvios')
    desvios_count = desvios_count.sort_values(by='Número de Desvios', ascending=False)

    # Criar o gráfico de barras
    fig = px.bar(desvios_count, x='Estudo', y='Número de Desvios',
                 text_auto=True, color='Estudo',
                 color_discrete_sequence=px.colors.qualitative.Prism, opacity=0.8,
                 labels={'estudo': 'Estudo', 'Número de Desvios': 'Número de Desvios'})

    # Mostrar o gráfico
    return fig


def bar_chart_count_por_categoria(dataframe: pd.DataFrame, anos: None, meses: None, estudos: None, categoria_selecionada: None, setor_selecionado: None):
    """
    Cria e exibe um gráfico de barras mostrando a contagem de desvios por categoria.

    Esta função conta o número de ocorrências de cada categoria no DataFrame e cria um gráfico de barras
    usando Plotly Express. O gráfico é exibido interativamente.

    Args:
        df (pd.DataFrame): O DataFrame a ser usado para criar o gráfico, que deve conter a coluna 'Categoria'.

    Returns:
        None: A função exibe o gráfico diretamente e não retorna nenhum valor.
    """
    
    df = dataframe.copy()
        
    if categoria_selecionada:
        df = df[df['Categoria'].isin(categoria_selecionada)]
        if df.empty:
            return None
            
    if setor_selecionado:
        df = df[df['Setor'].isin(setor_selecionado)]
        if df.empty:
            return None
    
    if anos:
        df = df[df['Data da submissão'].dt.year.isin(anos)]
        if df.empty:
            return None
        
    if meses:
        df = df[df['Data da submissão'].dt.month.isin(meses)]
        if df.empty:
            return None
    
    if estudos:
        df = df[df['Estudo'].isin(estudos)]
        if df.empty:
            return None
        
    # Agrupar e contar o número de ocorrências de cada categoria
    categorias_count = df['Categoria'].value_counts().reset_index()
    categorias_count.columns = ['Categoria', 'Número de Ocorrências']

    # Criar o gráfico de barras
    fig = px.bar(categorias_count, x='Categoria', y='Número de Ocorrências',
                 text_auto=True, color='Categoria',
                 color_discrete_sequence=px.colors.qualitative.Prism, opacity=0.8,
                 labels={'Categoria': 'Categoria', 'Número de Ocorrências': 'Número de Ocorrências'})

    # Mostrar o gráfico
    return fig

# Não usado
def bar_chart_desvios_por_setor_categoria(dataframe: pd.DataFrame, anos: None, meses: None, estudos: None, categoria_selecionada: None, setor_selecionado: None):
    """
    Cria e exibe um gráfico de barras agrupadas mostrando a contagem de desvios por setor e categoria.

    Esta função conta o número de desvios para cada combinação de setor e categoria e cria um gráfico de barras
    agrupadas usando Plotly Express. O gráfico é exibido interativamente.

    Args:
        df (pd.DataFrame): O DataFrame a ser usado para criar o gráfico, que deve conter as colunas 'Setor' e 'Categoria'.

    Returns:
        None: A função exibe o gráfico diretamente e não retorna nenhum valor.
    """
    
    df = dataframe.copy()
        
    if categoria_selecionada:
        df = df[df['Categoria'].isin(categoria_selecionada)]
        if df.empty:
            return None
            
    if setor_selecionado:
        df = df[df['Setor'].isin(setor_selecionado)]
        if df.empty:
            return None
    
    if anos:
        df = df[df['Data da submissão'].dt.year.isin(anos)]
        if df.empty:
            return None
        
    if meses:
        df = df[df['Data da submissão'].dt.month.isin(meses)]
        if df.empty:
            return None
    
    if estudos:
        df = df[df['Estudo'].isin(estudos)]
        if df.empty:
            return None
    
    # Agrupar e contar o número de ocorrências de cada combinação de setor e categoria
    setor_categoria_count = df.groupby(['Setor', 'Categoria'], observed=False).size().reset_index(name='Número de Desvios')

    # Criar o gráfico de barras agrupadas
    fig = px.bar(setor_categoria_count, x='Categoria', y='Número de Desvios', color='Setor',
                 text_auto=True, color_discrete_sequence=px.colors.qualitative.Prism, opacity=0.8,
                 labels={'Categoria': 'Categoria', 'Número de Desvios': 'Número de Desvios', 'Setor': 'Setor'},
                 barmode='group')  # Agrupar as barras por categoria

    # Mostrar o gráfico
    return fig


def bar_chart_media_tempos_desvios(dataframe, meses, anos, tempo_desv_cien):
    '''Retorna o gráfico/fig do cálculo de tempos agrupados por Mes e Ano da Coordenação.
    - Planilha Desvios.
    
    `tempo_desv_cien` serve para filtrar qual cálculo mostrar no gráfico. True mostra ciencia - desvio, False mostra submissão - ciencia.   
    
    Args:
        tempo_desv_cien: True/False'''
    
    df = dataframe.copy()

    if anos:
        df = df[df['Data da ciência'].dt.year.isin(anos)]
        if df.empty:
            return None
    
    if meses:
        df = df[df['Data da ciência'].dt.month.isin(meses)]
        if df.empty:
            return None
        
    cols = ['Tempo Desvio_Ciencia'] if tempo_desv_cien else ['Tempo Ciencia_Sub']

    
    media_por_mes = round(df.groupby(['Mês', 'Ano'], observed=True)[cols].mean(),2).reset_index(names=['Mes', 'Ano'])
    media_por_mes['Ano'] = media_por_mes['Ano'].astype(str)
        
    fig = px.bar(
        media_por_mes,
        x='Mes',
        y=cols[0],
        color='Ano',
        barmode='group',
        color_discrete_sequence=px.colors.qualitative.Prism, opacity=0.8,
        text_auto=True,
        title='Tempo entre Desvio e Ciência do desvio por Mês' if tempo_desv_cien else 'Tempo entre Ciência e Submissão do desvio por Mês'
    )

    return fig


def bar_chart_control_qual_tempos(dataframe: pd.DataFrame, meses: None, anos: None):
    df = dataframe.copy()

    if anos:
        df = df[df['Data Registro'].dt.year.isin(anos)]
        if df.empty:
            return None
    
    if meses:
        df = df[df['Data Registro'].dt.month.isin(meses)]
        if df.empty:
            return None
        
    media_por_mes = round(df.groupby(['Mês', 'Ano'])[['Tempo Coordenação vs Entrega Auditoria', 'Tempo total do processo']].mean(),2).reset_index(names=['Mes', 'Ano'])
    media_por_mes['Ano'] = media_por_mes['Ano'].astype(str)
        
    fig = px.bar(
        media_por_mes,
        x='Mes',
        y='Tempo Coordenação vs Entrega Auditoria',
        color='Ano',
        barmode='group',
        color_discrete_sequence=px.colors.qualitative.Prism, opacity=0.8,
        text_auto=True,
        labels={'Tempo Coordenação vs Entrega Auditoria': 'Média de Tempo em dias',
                'Ano': 'Ano'},
        title='Tempo Coordenação vs Entrega Auditoria por Mês/Ano'
    )

    fig.update_layout(
        title_font = dict(size=24)
    )

    return fig


def bar_chart_media_tot_proc(dataframe: pd.DataFrame, meses: None, anos: None):
    df = dataframe.copy()

    if anos:
        df = df[df['Data Registro'].dt.year.isin(anos)]
        if df.empty:
            return None
    
    if meses:
        df = df[df['Data Registro'].dt.month.isin(meses)]
        if df.empty:
            return None
        
    media_por_mes = round(df.groupby(['Mês', 'Ano'])[['Tempo total do processo']].mean(),2).reset_index(names=['Mes', 'Ano'])
    media_por_mes['Ano'] = media_por_mes['Ano'].astype(str)
        
    fig = px.bar(
        media_por_mes,
        x='Mes',
        y='Tempo total do processo',
        color='Ano',
        barmode='group',
        color_discrete_sequence=px.colors.qualitative.Prism, opacity=0.8,
        text_auto=True,
        labels={'Tempo total do processo': 'Média de Tempo em dias',
                'Ano': 'Ano'},
        title='Média Tempo Total Processo em dias'
    )

    fig.update_layout(
        title_font = dict(size=24)
    )

    return fig


def gerar_grafico_relatorio(dataframe: pd.DataFrame, estudo, setor, categoria):
    hoje = datetime.datetime.today()
    mes_atual, ano_atual = hoje.month, hoje.year

    desv_categ = bar_chart_count_por_categoria(dataframe=dataframe, meses=[mes_atual], anos=[ano_atual], estudos=estudo, setor_selecionado=setor, categoria_selecionada=categoria)
    desv_setor = bar_chart_desvios(dataframe=dataframe, meses=[mes_atual], anos=[ano_atual], estudos=estudo, setor_selecionado=setor, categoria_selecionada=categoria)


    if desv_categ and desv_setor:
        grafs = {'Desvios Categoria': desv_categ,
                 'Desvios Setor': desv_setor}
    else:
        return None

    temp_dir = os.path.join(os.getcwd(), 'temp')
    os.makedirs(temp_dir, exist_ok=True)

    caminhos = []
    figures = []
    for nome, graf in grafs.items():
        caminho = os.path.join(temp_dir, f"{nome}.png")
        figures.append(graf)
        caminhos.append(caminho)

    kaleido_options = {
        "path": chrome_path
    }

    pio.write_images(fig=figures, file=caminhos, kwargs="path")
    
    return caminhos


def gerar_arquivo_zip(arquivos):
    zip_filename = os.path.join(os.getcwd(), 'graficos_responsaveis.zip')

    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for arquivo in arquivos:
            zipf.write(arquivo, os.path.basename(arquivo))
        
    return zip_filename

