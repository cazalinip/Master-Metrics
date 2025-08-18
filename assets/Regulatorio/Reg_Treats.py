import pandas as pd
import numpy as np
import holidays


def calcular_dias_uteis(data_inicial, data_final, feriados):
    # Converte para string para uso com np.busday_count
    if pd.isnull(data_inicial) or pd.isnull(data_final):
        return np.nan
    return np.busday_count(data_inicial.date(), data_final.date(), holidays=feriados)


def calcular_tempos(df):
    '''Esta é a função para carregar a planilha inicial'''
    df = pd.read_excel(df)
    df.columns = df.columns.str.strip() # Remover espaços nas colunas
    
    # Identificar intervalo de anos
    datas_colunas = [
        'Data de Solicitação',
        'Data de Submissão',
        'Data de Aceite do PP',
        'Parecer CEP',
        'Parecer CONEP',
        'SIV',
        'ATIVAÇÃO',
        'Data de Implementação'
    ]

    # Garante que são datetime
    try:
        for col in datas_colunas:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    except Exception as e:
        raise Exception(f"Não foi possível converter as colunas de data para datetime.\n{e}")

    # Define anos para o calendário de feriados
    try:
        min_year = df[datas_colunas].stack().dropna().dt.year.min()
        max_year = df[datas_colunas].stack().dropna().dt.year.max()
        feriados = holidays.country_holidays('BR', years=list(range(min_year, max_year + 1)))
        feriados_np = np.array(list(feriados.keys()), dtype='datetime64[D]')
    except Exception as e:
        raise Exception(f'Erro ao construir o calendário de feriados: {e}')

    # Exemplos de pares de colunas para calcular tempo
    pares_datas = [
        ('Data de Solicitação', 'Data de Submissão', 'Tempo preparo dossiê técnico'),
        ('Data de Solicitação', 'ATIVAÇÃO', 'Tempo total de submissão inicial'), 
        ('Data de Solicitação', 'Data de Implementação', 'Tempo total de implementação de emenda'), 
        ('Data de Submissão', 'Parecer CEP', 'Tempo liberação parecer centro participante'),
        ('Data de Submissão', 'Parecer CONEP', 'Tempo liberação parecer centro coordenador'),
        ('Data de Submissão', 'Data de Aceite do PP', 'Tempo legislativo de aceitação do projeto'),
        ('Data de Aceite do PP', 'Parecer CEP', 'Tempo legislativo do parecer em centro participante'),
        ('Data de Aceite do PP', 'Parecer CONEP', 'Tempo legislativo do parecer em centro coordenador'),
        ('SIV', 'ATIVAÇÃO', 'Tempo total ativação do Estudo'), 
    ]

    # Calcula os demais tempos úteis
    try:
        for col_ini, col_fim, nome_coluna in pares_datas:
            df[nome_coluna] = df.apply(
                lambda row: calcular_dias_uteis(row[col_ini], row[col_fim], feriados_np),
                axis=1)
    except Exception as e:
        raise Exception(f"Não foi possível calcular a diferença de dias úteis entre as datas.\n{e}")
    
    # Tratamento adicional das strings
    for col in df.select_dtypes(include=['object']).columns:  # Só nas colunas de texto (strings)
        df[col] = df[col].str.strip()

    df = df.dropna(how='any', subset=['Status', 'PI', 'Estudo', 'Patrocinador',])
    
    return df


def metricas_card(dataframe):
    df = dataframe.copy()
    
    # Médias da Solicitação
    metricas = {
        'Tempo preparo dossiê técnico': df['Tempo preparo dossiê técnico'].mean(),
        'Tempo total de submissão inicial': df['Tempo total de submissão inicial'].mean(),
        'Tempo total de implementação de emenda': df['Tempo total de implementação de emenda'].mean(),
        'Tempo liberação parecer centro participante': df['Tempo liberação parecer centro participante'].mean(),
        'Tempo liberação parecer centro coordenador': df['Tempo liberação parecer centro coordenador'].mean(),
        'Tempo legislativo de aceitação do projeto': df['Tempo legislativo de aceitação do projeto'].mean(),
        'Tempo legislativo do parecer em centro participante': df['Tempo legislativo do parecer em centro participante'].mean(),
        'Tempo legislativo do parecer em centro coordenador': df['Tempo legislativo do parecer em centro coordenador'].mean(),
        'Tempo total ativação do Estudo': df['Tempo total ativação do Estudo'].mean()
    }


    return metricas

