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
        ('Data de Solicitação', 'Data de Submissão'),
        ('Data de Solicitação', 'Parecer CEP'),
        ('Data de Solicitação', 'Parecer CONEP'),
        ('Data de Solicitação', 'Data de Implementação'),
        ('Data de Solicitação', 'SIV'),
        ('Data de Solicitação', 'ATIVAÇÃO'),
        ('Data de Submissão', 'Parecer CEP'),
        ('Data de Submissão', 'Parecer CONEP'),
        ('Data de Submissão', 'Data de Implementação'),
        ('Data de Submissão', 'SIV'),
        ('Data de Submissão', 'ATIVAÇÃO'),
        ('Data de Aceite do PP', 'Parecer CEP') # O prazo limite é de 30d
    ]

    # Calcula os demais tempos úteis
    try:
        for col_ini, col_fim in pares_datas:
            nome_coluna_resultado = f"Dias úteis - {col_ini.strip()} → {col_fim.strip()}"
            df[nome_coluna_resultado] = df.apply(
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
    metricas_sol = {
        'Solicitação → Submissão': df['Dias úteis - Data de Solicitação → Data de Submissão'].mean(),
        'Solicitação → CEP': df['Dias úteis - Data de Solicitação → Parecer CEP'].mean(),
        'Solicitação → CONEP': df['Dias úteis - Data de Solicitação → Parecer CONEP'].mean(),
        'Solicitação → Implementação': df['Dias úteis - Data de Solicitação → Data de Implementação'].mean(),
        'Solicitação → SIV': df['Dias úteis - Data de Solicitação → SIV'].mean(),
        'Solicitação → Ativação': df['Dias úteis - Data de Solicitação → ATIVAÇÃO'].mean(),
    }

    # Médias da Submissão
    metricas_sub = {
        'Submissão → CEP': df['Dias úteis - Data de Submissão → Parecer CEP'].mean(),
        'Submissão → CONEP': df['Dias úteis - Data de Submissão → Parecer CONEP'].mean(),
        'Submissão → Implementação': df['Dias úteis - Data de Submissão → Data de Implementação'].mean(),
        'Submissão → SIV': df['Dias úteis - Data de Submissão → SIV'].mean(),
        'Submissão → Ativação': df['Dias úteis - Data de Submissão → ATIVAÇÃO'].mean(),
    }

    # Tempo entre aceite do PP até CEP
    tempo_pp_cep = df['Dias úteis - Data de Aceite do PP → Parecer CEP'].mean()

    return metricas_sol, metricas_sub, tempo_pp_cep

