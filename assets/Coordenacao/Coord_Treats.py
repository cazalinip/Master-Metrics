import pandas as pd
import streamlit as st
from progress_bar import ProgressBar

# Função para verificar se um valor pode ser convertido para datetime
def verificar_data(valor):
    try:
        pd.to_datetime(valor, dayfirst=True)
        return valor
    except ValueError:
        return pd.NA


def process_excel_file(excel_file) -> pd.DataFrame:
    """
    Processa um arquivo Excel contendo várias planilhas e combina os dados em um único DataFrame.

    Esta função lê todas as planilhas de um arquivo Excel, exceto a planilha chamada 'MODELO'. Para cada
    planilha, ela seleciona colunas específicas e adiciona uma coluna extra chamada 'estudo', que indica
    de qual planilha (estudo) os dados foram extraídos. Finalmente, todos os DataFrames são concatenados
    em um único DataFrame longo.

    Args:
        excel_file (str): O caminho para o arquivo Excel a ser processado.

    Returns:
        pd.DataFrame: Um DataFrame concatenado contendo dados de todas as planilhas, exceto a 'MODELO', com
                      uma coluna adicional 'estudo' que indica a origem dos dados.
    """
    
    # Carregar todas as planilhas do arquivo Excel
    df = pd.read_excel(excel_file, sheet_name=None).copy()

    # Inicializar uma lista para armazenar os DataFrames processados
    processed_dfs = []

    # Iterar sobre cada planilha
    for sheet_name, sheet_df in df.items():
        # Ignorar a planilha 'MODELO'
        if 'modelo' in sheet_name.lower() or 'folha' in sheet_name.lower():
            continue

        
        # Selecionar as colunas de interesse
        new_df = sheet_df[['Categoria', 'Setor', 'Houve prejuízos para o participante?', 'Data do desvio', 'Data da ciência', 'Data da submissão']].copy()
        
        # Adicionar uma coluna 'estudo' com o nome da planilha
        new_df['Estudo'] = sheet_name

        new_df = new_df[new_df['Data da submissão'] != "Em duplicata"]

        dates = ['Data do desvio', 'Data da ciência', 'Data da submissão']
        for date in dates:
            new_df[date] = new_df[date].apply(verificar_data)
            
            new_df[date] = pd.to_datetime(new_df[date], errors='coerce', dayfirst=True)

        new_df['Data da submissão'] = new_df['Data da submissão'].fillna(new_df['Data da ciência'])

        new_df['Houve prejuízos para o participante?'] = new_df['Houve prejuízos para o participante?'].str.strip().str.capitalize()

        # Adicionar o DataFrame processado à lista
        processed_dfs.append(new_df)

    # Concatenar todos os DataFrames da lista em um único DataFrame
    final_df = pd.concat(processed_dfs, ignore_index=True)

    return final_df


def dict_dataframe(excel_file):
    '''Recebe upload da planilha, pelo streamlit, para gerar o `dict_dataframe` a fim de ser utilizado em `process_tab_qual_coord`'''
    df = pd.read_excel(excel_file, sheet_name=None)
    return df


def process_tab_qual_coord(dict_dataframe: dict) -> pd.DataFrame:
    df_list = []

    for sheet_name, sheet_df in dict_dataframe.items():
        if sheet_name in ['Outubro 23', 'Novembro 23', 'Agosto', 'Setembro', 'Planilha1']:
            continue

        # Renomeia as colunas para remover espaços extras
        sheet_df.columns = sheet_df.columns.str.replace(r'\s+', ' ', regex=True).str.strip().str.capitalize()

        # Remove colunas sem dados
        sheet_df = sheet_df.dropna(how='all', axis=1)

        # Remove colunas "Unnamed"
        sheet_df = sheet_df.loc[:, ~sheet_df.columns.str.contains('Unnamed')]

        mes, ano = sheet_name.split()

        sheet_df['Mês'] = mes
        sheet_df['Ano'] = ano

        df_list.append(sheet_df)


    # Concatenar todos os dataframes em um único
    df_final = pd.concat(df_list, ignore_index=True)

    # Transferir e agregar as colunas de data
    df_final['Data entrega para auditoria'] = df_final['Data entrega para auditoria'].combine_first(df_final['Data entrega para qualidade'])
    df_final['Data entrega para arquivo'] = df_final['Data entrega para arquivo'].combine_first(df_final['Data entrega supervisão para arquivo'])
    df_final['Data entrega para arquivo'] = df_final['Data entrega para arquivo'].combine_first(df_final['Data entrega qualidade para arquivo'])
    df_final['Data recebimento coordenação'] = df_final['Data recebimento coordenação'].combine_first(df_final['Data entrega qualidade para coordenação'])

    # Selecionar as colunas de interesse
    df_final = df_final[['Data consulta', 'Data recebimento coordenação', 'Data entrega para auditoria', 'Data entrega para arquivo', 'Mês', 'Ano']]


    # Dicionário para mapear os meses por extenso para números
    meses_dict = {
        'Janeiro': '01', 'Fevereiro': '02', 'Março': '03', 'Abril': '04', 'Maio': '05', 'Junho': '06',
        'Julho': '07', 'Agosto': '08', 'Setembro': '09', 'Outubro': '10', 'Novembro': '11', 'Dezembro': '12'
    }

   # Convertendo o nome do mês por extenso para número
    df_final['Mês'] = df_final['Mês'].map(meses_dict)

    # Criando a coluna 'Data Registro' com o formato '01/{mes}/{ano}'
    df_final['Data Registro'] = '01/' + df_final['Mês'] + '/' + df_final['Ano'].apply(lambda x: f'20{x}' if len(str(x)) == 2 else str(x))

    # Removendo as colunas Mês e Ano pois após a criação de Data Registro, elas são inúteis.
    df_final = df_final.drop(['Mês','Ano'], axis=1)

    # Convertendo para datetime e ignorando os erros/datas inválidas (NaT)
    for col in df_final.columns:
        df_final[col] = pd.to_datetime(df_final[col], errors='coerce', format='%d/%m/%Y')


    # Tirando todas os campos vazios após a conversão e aqueles pré-existentes
    df_final = df_final.dropna(how='any', axis=0)

    # Adicionando o cálculo de tempo
    df_final['Tempo Coordenação vs Entrega Auditoria'] = (df_final['Data entrega para auditoria'] - df_final['Data recebimento coordenação']).dt.days
    df_final['Tempo total do processo'] = (df_final['Data entrega para arquivo'] - df_final['Data consulta']).dt.days

    # Reordenando as colunas
    df_final = df_final[['Data Registro','Data consulta', 'Data recebimento coordenação', 
                         'Data entrega para auditoria', 'Data entrega para arquivo', 
                         'Tempo Coordenação vs Entrega Auditoria', 'Tempo total do processo']]
    
    df_final['Mês'] = df_final['Data Registro'].dt.month
    df_final['Ano'] = df_final['Data Registro'].dt.year


    return df_final


def gerar_calculo_tempos(dataframe_desvios):
    '''Esse é para os cálculos de tempo do processo da Coordenação
    - Planilha Desvios'''

    df = dataframe_desvios.copy()
    shape_antes = df.shape[0]
    df = df.dropna()
    shape_depois = df.shape[0]

    registros_apagados = shape_antes - shape_depois

    meses_dict = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
                 }

    ordem_meses = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]

    df['Mês'] = df['Data da ciência'].dt.month.map(meses_dict)

    # Converte a coluna 'Mes' em uma categoria com a ordem definida
    df['Mês'] = pd.Categorical(df['Mês'], categories=ordem_meses, ordered=True)

    df['Ano'] = df['Data da ciência'].dt.year


    df['Tempo Desvio_Ciencia'] = (df['Data da ciência'] - df['Data do desvio']).dt.days
    df['Tempo Ciencia_Sub'] = (df['Data da submissão'] - df['Data da ciência']).dt.days
    

    return registros_apagados, df


def carregar_dados_tab_qual_coord(file):
    '''Esse é para o cálculo de tempos da Auditoria da Coordenação - O tempo que levou entre os processos da Coordenação até a Qualidade e Arquivo.
    - A tabela é a Tabela Coordenação-Qualidade'''
    
    barra = ProgressBar()
    barra.iniciar_carregamento()

    dict_df = pd.read_excel(file, sheet_name=None).copy()
    
    df_list = []

    for sheet_name, sheet_df in dict_df.items():
        if sheet_name in ['Outubro 23', 'Novembro 23', 'Agosto', 'Setembro', 'Planilha1']:
            continue

        # Renomeia as colunas para remover espaços extras
        sheet_df.columns = sheet_df.columns.str.replace(r'\s+', ' ', regex=True).str.strip().str.capitalize()

        # Remove colunas sem dados
        sheet_df = sheet_df.dropna(how='all', axis=1)

        # Remove colunas "Unnamed"
        sheet_df = sheet_df.loc[:, ~sheet_df.columns.str.contains('Unnamed')]

        mes, ano = sheet_name.split()

        sheet_df['Mês'] = mes
        sheet_df['Ano'] = ano

        df_list.append(sheet_df)


    # Concatenar todos os dataframes em um único
    df_final = pd.concat(df_list, ignore_index=True)

    # Transferir e agregar as colunas de data
    df_final['Data entrega para auditoria'] = df_final['Data entrega para auditoria'].combine_first(df_final['Data entrega para qualidade'])
    df_final['Data entrega para arquivo'] = df_final['Data entrega para arquivo'].combine_first(df_final['Data entrega supervisão para arquivo'])
    df_final['Data entrega para arquivo'] = df_final['Data entrega para arquivo'].combine_first(df_final['Data entrega qualidade para arquivo'])
    df_final['Data recebimento coordenação'] = df_final['Data recebimento coordenação'].combine_first(df_final['Data entrega qualidade para coordenação'])

    # Selecionar as colunas de interesse
    df_final = df_final[['Data consulta', 'Data recebimento coordenação', 'Data entrega para auditoria', 'Data entrega para arquivo', 'Mês', 'Ano']]


    # Dicionário para mapear os meses por extenso para números
    meses_dict = {
        'Janeiro': '01', 'Fevereiro': '02', 'Março': '03', 'Abril': '04', 'Maio': '05', 'Junho': '06',
        'Julho': '07', 'Agosto': '08', 'Setembro': '09', 'Outubro': '10', 'Novembro': '11', 'Dezembro': '12'
    }

   # Convertendo o nome do mês por extenso para número
    df_final['Mês'] = df_final['Mês'].map(meses_dict)

    # Criando a coluna 'Data Registro' com o formato '01/{mes}/{ano}'
    df_final['Data Registro'] = '01/' + df_final['Mês'] + '/' + df_final['Ano'].apply(lambda x: f'20{x}' if len(str(x)) == 2 else str(x))

    # Removendo as colunas Mês e Ano pois após a criação de Data Registro, elas são inúteis.
    df_final = df_final.drop(['Mês','Ano'], axis=1)

    # Convertendo para datetime e ignorando os erros/datas inválidas (NaT)
    for col in df_final.columns:
        df_final[col] = pd.to_datetime(df_final[col], errors='coerce', format='%d/%m/%Y')


    # Tirando todas os campos vazios após a conversão e aqueles pré-existentes
    df_final = df_final.dropna(how='any', axis=0)

    # Adicionando o cálculo de tempo
    df_final['Tempo Coordenação vs Entrega Auditoria'] = (df_final['Data entrega para auditoria'] - df_final['Data recebimento coordenação']).dt.days
    df_final['Tempo total do processo'] = (df_final['Data entrega para arquivo'] - df_final['Data recebimento coordenação']).dt.days

    # Reordenando as colunas
    df_final = df_final[['Data Registro','Data consulta', 'Data recebimento coordenação', 
                         'Data entrega para auditoria', 'Data entrega para arquivo', 
                         'Tempo Coordenação vs Entrega Auditoria', 'Tempo total do processo']]
    
    meses_dict = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
                 }

    ordem_meses = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]

    df_final['Mês'] = df_final['Data Registro'].dt.month.map(meses_dict)


    # Converte a coluna 'Mes' em uma categoria com a ordem definida
    df_final['Mês'] = pd.Categorical(df_final['Mês'], categories=ordem_meses, ordered=True)


    df_final['Ano'] = df_final['Data Registro'].dt.year

    barra.finalizar_carregamento(emoji='🎉')


    return df_final

