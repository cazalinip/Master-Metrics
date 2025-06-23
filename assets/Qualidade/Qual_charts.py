import plotly.express as px
import pandas as pd
import zipfile
import os


def bar_chart_achados_protocolo(dataframe: pd.DataFrame, anos: list=None, meses: list=None, estudos: list=None, responsavel: list=None):
    df = dataframe.copy()

    if anos:
        df = df[df['Data da Verificação'].dt.year.isin(anos)]
        if df.empty:
            return None
        
    if meses:
        df = df[df['Data da Verificação'].dt.month.isin(meses)]
        if df.empty:
            return None
        
    if estudos:
        df = df[df['Protocolo'].isin(estudos)]
        if df.empty:
            return None
        
    if responsavel:
        df = df[df['Responsável'].isin(responsavel)]
        if df.empty:
            return None
        
    data = df.groupby('Protocolo', observed=False).count()['Achados'].reset_index(name='Contagem de Achados')
    data = data.sort_values(by='Contagem de Achados', ascending=False)

    fig = px.bar(data_frame=data, x='Protocolo', y='Contagem de Achados', 
             color='Protocolo', color_discrete_sequence=px.colors.qualitative.Prism,
             opacity=0.85, text_auto=True)

    fig.update_layout(
        showlegend=False,
        title={
            'text': 'Distribuição dos achados nos protocolos',
            'font': {
                'family': 'Arial',
                'size': 24
            }
        }
    )

    return fig


def bar_chart_resp_achados(dataframe: pd.DataFrame, anos: list=None, meses: list=None, estudos: list=None, responsavel: list=None):
    df = dataframe.copy()

    if anos:
        df = df[df['Data da Verificação'].dt.year.isin(anos)]
        if df.empty:
            return None
        
    if meses:
        df = df[df['Data da Verificação'].dt.month.isin(meses)]
        if df.empty:
            return None
        
    if estudos:
        df = df[df['Protocolo'].isin(estudos)]
        if df.empty:
            return None
        
    if responsavel:
        df = df[df['Responsável'].isin(responsavel)]
        if df.empty:
            return None
        
    resps = df.groupby('Responsável', observed=False).count()['Achados'].reset_index(name='Contagem de Achados')
    resps = resps.sort_values(by='Contagem de Achados', ascending=False)
    contagem_total = resps['Contagem de Achados'].sum()

    fig = px.bar(data_frame=resps, x='Responsável', y='Contagem de Achados', 
             color='Responsável', color_discrete_sequence=px.colors.qualitative.Prism,
             opacity=0.85, text_auto=True)
    
    fig.add_annotation(
        text=f'Total de achados nesta visualização: {contagem_total}',
        xref='paper', yref='paper',
        x=0, y=1.06,
        showarrow=False,
        font=dict(size=14, color='gray'),
        align='center'
    )

    fig.update_layout(
        showlegend=False,
        title={
            'text': 'Distribuição dos Responsáveis vs Achados',
            'font': {
                'family': 'Arial',
                'size': 24
            }
        }
    )

    return fig


def bar_chart_achados_frequentes(dataframe: pd.DataFrame, anos: list=None, meses: list=None, estudos: list=None, responsavel: list=None, tamanho: dict={'w':1280, 'h':720}):
    df = dataframe.copy()

    if anos:
        df = df[df['Data da Verificação'].dt.year.isin(anos)]
        if df.empty:
            return None
        
    if meses:
        df = df[df['Data da Verificação'].dt.month.isin(meses)]
        if df.empty:
            return None
        
    if estudos:
        df = df[df['Protocolo'].isin(estudos)]
        if df.empty:
            return None
        
    if responsavel:
        df = df[df['Responsável'].isin(responsavel)]
        if df.empty:
            return None
        
    if tamanho:
        width = tamanho['w']
        height = tamanho['h']

        
    comum = df['Achados'].value_counts().reset_index(name='Contagem de Achados')
    comum = comum.sort_values(by='Contagem de Achados', ascending=False)

    fig = px.bar(data_frame=comum, y='Achados', x='Contagem de Achados', 
             color='Achados', color_discrete_sequence=px.colors.qualitative.Prism,
             opacity=0.85, text_auto=True, width=width, height=height)

    fig.update_layout(
        showlegend=False,
        title={
            'text': 'Distribuição dos achados mais frequentes das visitas',
            'font': {
                'family': 'Arial',
                'size': 24,
                'color': 'white'
            }
        },
        margin=dict(l=500),
        yaxis_title=None,
        plot_bgcolor='#0E1117',
        paper_bgcolor='#0E1117',
        font=dict(color='white')
    )

    return fig


def gerar_grafico_por_responsavel(dataframe: pd.DataFrame, anos: list=None, meses: list=None, responsavel: str=None):
    responsavel = [responsavel]
    tamanho_imagem = {'w':1600, 'h':900}

    fig = bar_chart_achados_frequentes(dataframe=dataframe, anos=anos, meses=meses, responsavel=responsavel, tamanho=tamanho_imagem)

    if fig:
        temp_dir = os.path.join(os.getcwd(), 'temp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        file_name = f"{responsavel[0]}.png"
        file_path = os.path.join(temp_dir, file_name)
        fig.write_image(file_path)
        

        return file_path
    
    return None


def gerar_arquivo_zip(arquivos):
    zip_filename = os.path.join(os.getcwd(), 'graficos_responsaveis.zip')

    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for arquivo in arquivos:
            zipf.write(arquivo, os.path.basename(arquivo))
        
    return zip_filename

