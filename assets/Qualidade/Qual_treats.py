import pandas as pd
import streamlit as st
import time
import io
from progress_bar import ProgressBar


def load_qualidade_file(file: io.BytesIO):

    barra = ProgressBar()
    barra.iniciar_carregamento()

    df = pd.read_excel(file, sheet_name=None).copy()
    
    dfs = []

    for sheet_name, sheet_df in df.items():
        if sheet_name == 'Achados':
            continue
        
        sheet_df = sheet_df.dropna(subset="Data da Verificação", how="any", axis=0).copy()

        try:
            dates = ['Data da Verificação', 'Data Consulta']
            for date in dates:
                sheet_df[date] = pd.to_datetime(sheet_df[date])
        
        except Exception as e:
            print(f'Erro ao converter as colunas de data para datetime na planilha "{sheet_name}": {e}')
            continue
                
        dfs.append(sheet_df)

    final_df = pd.concat(dfs, ignore_index=True)

    final_df = final_df.dropna(axis=1, how='all')
    final_df = final_df.dropna(subset='Protocolo')
    final_df = final_df.dropna(subset='Responsável')

    barra.finalizar_carregamento()

    return final_df

# Função para verificar a validade do arquivo
def verificar_arquivo(file):
    try:
        # Tente carregar o arquivo em um DataFrame
        df = pd.read_excel(file)
        # Verifique se o DataFrame contém colunas esperadas, por exemplo:
        colunas_esperadas = ['Data da Verificação', 'Protocolo', 'Achados']  # Atualize com suas colunas esperadas
        if all(coluna in df.columns for coluna in colunas_esperadas):
            return True, df
        else:
            return False, None
    except Exception as e:
        return False, None
    

def show_table(dataframe: pd.DataFrame, anos: None, meses: None, responsaveis: list):

    df = dataframe.copy()

    df = df[df['Data da Verificação'].dt.year.isin(anos)]
    if df.empty:
        return None

    df = df[df['Data da Verificação'].dt.month.isin(meses)]
    if df.empty:
        return None


    resp_df = df[df['Responsável'].isin(responsaveis)]
    resp_df = resp_df['Achados'].value_counts().reset_index(name='Contagem de Achados')
    resp_df.columns = ['Achados', 'Contagem de Achados']

    # Calcula o total
    total_achados = resp_df['Contagem de Achados'].sum()

    # Adiciona a coluna de percentual
    resp_df['Percentual'] = ((resp_df['Contagem de Achados'] / total_achados) * 100).round(2)

    # Cria a linha total
    total_row = pd.DataFrame({
        'Achados': ['Total'],
        'Contagem de Achados': [total_achados],
        'Percentual': [100.00]
    })

    # Concatena a linha total ao DataFrame original
    resp_df = pd.concat([resp_df, total_row], ignore_index=True)

    return resp_df


def contar_visitas_unicas(dataframe, anos, meses, respons):

    df = dataframe.copy()

    if anos:
        df = df[df['Data da Verificação'].dt.year.isin(anos)]
        if df.empty:
            return None
        
    if meses:
        df = df[df['Data da Verificação'].dt.month.isin(meses)]
        if df.empty:
            return None
        
    if respons:
        df = df[df['Responsável'].isin(respons)]
        if df.empty:
            return None
        

    # Remover "duplicatas" considerando as colunas especificadas
    registros_unicos = df.drop_duplicates(subset=['Paciente', 'Protocolo', 'Data Consulta', 'Documento']).copy()

    # Contar o número de registros únicos
    contagem = registros_unicos.shape[0]

    return contagem