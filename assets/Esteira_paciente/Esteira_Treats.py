import pandas as pd
import datetime

# Primeiro checkpoint - Elegibilidade
def check_eleg(row):
    if row['Potencial Elegível (Sim/Não)'] == "Não":
        pot_elegivel_idx = row.index.get_loc('Potencial Elegível (Sim/Não)')
        
        for col in row.index[pot_elegivel_idx+3:]:
            row[col] = "Não se aplica"
    
    return row

# Segundo checkpoint - Tem interesse em participar
def check_interesse(row):
    if row['Tem interesse em participar?'] == "Não":
        pot_elegivel_idx = row.index.get_loc('Tem interesse em participar?')
        
        for col in row.index[pot_elegivel_idx+2:]:
            row[col] = "Não se aplica"
    
    return row

# Terceiro checkpoint - Foi consentido
def check_consent(row):
    if row['Consentido (Sim/Não)'] == "Não":
        pot_elegivel_idx = row.index.get_loc('Consentido (Sim/Não)')
        
        for col in row.index[pot_elegivel_idx+1:]:
            if col not in ['Categoria de não consentimento', 'Motivo de não consentimento']:
                row[col] = "Não se aplica"
    
    return row

# Quarto checkpoint - Foi randomizado
def check_rando(row):
    if row['Status Final (Randomizado/Falha)'] == "Randomizado":
        pot_elegivel_idx = row.index.get_loc('Status Final (Randomizado/Falha)')
        
        for col in row.index[pot_elegivel_idx+1:]:
            if col in ['Quem identificou a falha?', 'Categoria (da falha)', 'Motivo (da falha)']:
                row[col] = "Não se aplica"
    
    return row

# Quinto checkpoint - Extensão de screening
def check_extensao(row):
    if row['Houve extensão ou re-screening deste paciente? (Sim/Não)'] == "Não":
        pot_elegivel_idx = row.index.get_loc('Houve extensão ou re-screening deste paciente? (Sim/Não)')
        
        for col in row.index[pot_elegivel_idx+1:]:
            row[col] = "Não se aplica"
    
    return row

# Aplicar a função em cada linha do DataFrame, preenchendo com "Não se aplica"
def aplicar_checkpoints(data_frame, funcoes):
    df_final = data_frame.copy()
    for funcao in funcoes:
        df_final = df_final.apply(funcao, axis=1)

    return df_final

# Aplica as funções acima
def tratar_dados_upload(upload):
    '''Aqui deve ser feito o upload do arquivo Excel, pelo file `st.file_uploader` e aplica o tratamento'''
    df_inicial = pd.read_excel(upload, sheet_name=None)
    df = df_inicial['TCLE'].copy()

    funcoes=[check_eleg, check_interesse, check_consent, check_rando, check_extensao]

    df_preenchido = aplicar_checkpoints(df, funcoes)
    df_preenchido = df_preenchido.replace('-', 'Não se aplica')
    df_preenchido = df_preenchido.drop(columns='Tempo real de SCR', axis=0)

    return df_preenchido

# Retorna Df_tempos - média do processo
def dataframe_para_calculo_tempos(data_frame):
    """
    Recebe um DataFrame contendo datas relacionadas ao processo clínico e calcula tempos relativos entre eventos.

    Este DataFrame é geralmente o resultado da função `tratar_dados.df_preenchido`, contendo colunas de datas.
    A função calcula o número de dias entre a data de recebimento e outras datas relevantes.

    Returns:
        pd.DataFrame: DataFrame contendo as mesmas colunas de datas (convertidas para datetime)
                      e colunas adicionais com a diferença em dias entre os eventos.
    """
    colunas = ['Data de Recebimento (início/encaminhamento)',
                      'Data de Avaliação Elegibilidade', 'Data do contato', 'Data Consentimento', 'Data randomização/falha']
    
    df_tempos = data_frame[colunas].copy()

    # Convertendo para datetime    
    for data in colunas:
        df_tempos[data] = pd.to_datetime(df_tempos[data], errors='coerce', dayfirst=True, format='%d/%m/%Y')

    # Cálculo dos tempos
    df_tempos['Tempo Eligibilidade - Recebimento'] = (df_tempos['Data de Avaliação Elegibilidade'] - df_tempos['Data de Recebimento (início/encaminhamento)']).dt.days
    df_tempos['Tempo Contato - Recebimento'] = (df_tempos['Data do contato'] - df_tempos['Data de Recebimento (início/encaminhamento)']).dt.days
    df_tempos['Tempo TCLE - Recebimento'] = (df_tempos['Data Consentimento'] - df_tempos['Data de Recebimento (início/encaminhamento)']).dt.days
    df_tempos['Tempo Randomização/Falha - Recebimento'] = (df_tempos['Data randomização/falha'] - df_tempos['Data de Recebimento (início/encaminhamento)']).dt.days


    return df_tempos

# Retorna Df_taxas - converte as variáveis binárias para 0 e 1
def dataframe_para_calculo_taxas(data_frame):
    '''Esta função recebe o `df_preenchido` de `tratar_dados`
    Este dataframe é destinado para o mapeamento das variáveis binárias para cálculos'''
    df_taxas = data_frame.copy()
    # Convertendo variáveis categóricas em binárias
    df_taxas['Potencial Elegível (Sim/Não)'] = df_taxas['Potencial Elegível (Sim/Não)'].str.strip().str.lower().map({'sim': 1, 'não': 0})
    df_taxas['Consentido (Sim/Não)'] = df_taxas['Consentido (Sim/Não)'].str.strip().str.lower().map({'sim': 1, 'não': 0})
    df_taxas['Tem interesse em participar?'] = df_taxas['Tem interesse em participar?'].str.strip().str.lower().map({'sim': 1, 'não':0})
    df_taxas['Houve extensão ou re-screening deste paciente? (Sim/Não)'] = df_taxas['Houve extensão ou re-screening deste paciente? (Sim/Não)'].str.strip().str.lower().map({'sim': 1, 'não': 0})
    df_taxas['Status Final (Randomizado/Falha)'] = df_taxas['Status Final (Randomizado/Falha)'].str.strip().str.lower().map({'randomizado': 1, 'falha': 0})


    return df_taxas

# Retorna contagem_total. Usa df_taxas - traz a contagem bruta do ano das taxas de conversão
def totais_brutos_dados(dataframe_taxas, anos=None):
    '''Esta função recebe o `df_taxas` de `dataframe_para_calculo_taxas`.
    Retorna a contagem das variáveis mapeadas e as salva em um dicionário.'''
    df_taxas = dataframe_taxas.copy()

    anos = datetime.datetime.today().year if anos == None else anos

    df_taxas = df_taxas[df_taxas['Data de Recebimento (início/encaminhamento)'].dt.year.isin(anos)]

    # Número total de pacientes encaminhados
    total_encaminhados = df_taxas['ID processo'].nunique()
    # print(f'total encaminhados: {total_encaminhados}')

    # Número de pacientes elegíveis
    elegiveis = df_taxas[df_taxas['Potencial Elegível (Sim/Não)'] == 1]['ID processo'].nunique()
    # print(f'Elegíveis: {elegiveis}')

    # Número de pacientes contatados (com interesse em participar)
    contatados = df_taxas[df_taxas['Tem interesse em participar?'] == 1]['ID processo'].nunique()
    # print(f'Contatados: {contatados}')

    # Número de pacientes que assinaram o TCLE (consentidos)
    assinaram_tcle = df_taxas[df_taxas['Consentido (Sim/Não)'] == 1]['ID processo'].nunique()
    # print(f'Assinaram tcle: {assinaram_tcle}')

    # Número de pacientes randomizados
    randomizados = df_taxas[df_taxas['Status Final (Randomizado/Falha)'] == 1]['ID processo'].nunique()
    # print(f'Randomizados: {randomizados}')

    contagem_total = {
        'total_encaminhados': total_encaminhados,
        'elegiveis': elegiveis,
        'contatados': contatados,
        'assinaram_tcle': assinaram_tcle,
        'randomizados': randomizados
    }

    return contagem_total

# Usa contagem_total - traz a porcentagem das taxas de conversão
def taxas_conversao_total(totais_dict):
    '''Esta função recebe o `contagem_total` de `totais_brutos_dados`, que é um dicionário.
    Retorna as taxas de conversão e as salva em um dicionário.
    Para filtrar por tempo (no caso, ano), `totais_brutos_dados`aceita o parâmetro.'''
    total_encaminhados = totais_dict['total_encaminhados']
    elegiveis = totais_dict['elegiveis']
    contatados = totais_dict['contatados']
    assinaram_tcle = totais_dict['assinaram_tcle']
    randomizados = totais_dict['randomizados']

    # Taxa de elegibilidade
    taxa_elegibilidade = elegiveis / total_encaminhados

    # Taxa de contato
    taxa_contato = contatados / elegiveis

    # Taxa de consentimento
    taxa_consentimento = assinaram_tcle / contatados

    # Taxa de randomização
    taxa_randomizacao = randomizados / assinaram_tcle

    taxas = {
        'taxa_elegibilidade': taxa_elegibilidade,
        'taxa_contato': taxa_contato,
        'taxa_consentimento': taxa_consentimento,
        'taxa_randomizacao': taxa_randomizacao
    }

    return taxas

# Retorna df_taxas_mensais. Usa df_taxas - calcula as taxas em porcentagem de cada mês
def calcular_taxas_mensais(dataframe_taxas, anos=None):
    '''Esta função recebe o `df_taxas` de `dataframe_para_calculo_taxas`.
    Retorna as taxas de conversão mensais, a fim de criar o gráfico de linhas.
    '''

    dataframe_taxas = dataframe_taxas.copy()
    dataframe_taxas['Data de Recebimento (início/encaminhamento)'] = pd.to_datetime(dataframe_taxas['Data de Recebimento (início/encaminhamento)'], errors='coerce', dayfirst=True, format='%d/%m/%Y')

    # Extraímos o ano e mês da coluna 'Data de Recebimento (início/encaminhamento)'
    dataframe_taxas['Ano'] = dataframe_taxas['Data de Recebimento (início/encaminhamento)'].dt.year
    dataframe_taxas['Mês'] = dataframe_taxas['Data de Recebimento (início/encaminhamento)'].dt.month

    if anos:
        dataframe_taxas = dataframe_taxas[dataframe_taxas['Ano'].isin(anos)]

    # Lista para armazenar as taxas mensais
    taxas_mensais = []

    for ano in dataframe_taxas['Ano'].unique():
        for mes in range(1, 13):  # Para cada mês de 1 a 12
            # Filtra os dados para o ano e mês atual
            dados_mes = dataframe_taxas[(dataframe_taxas['Ano'] == ano) & (dataframe_taxas['Mês'] == mes)]

            # Total de encaminhados (todos os pacientes no mês)
            total_encaminhados = dados_mes['ID processo'].nunique()

            # Calcular as taxas de acordo com as etapas
            if total_encaminhados > 0:
                # Elegíveis (pacientes com 'Potencial Elegível' == 1)
                elegiveis = dados_mes[dados_mes['Potencial Elegível (Sim/Não)'] == 1]['ID processo'].nunique()
                
                # Contatados (pacientes com 'Tem interesse em participar?' == 1)
                contatados = dados_mes[dados_mes['Tem interesse em participar?'] == 1]['ID processo'].nunique()
                
                # Consentidos (pacientes que assinaram o TCLE)
                assinaram_tcle = dados_mes[dados_mes['Consentido (Sim/Não)'] == 1]['ID processo'].nunique()
                
                # Randomizados (pacientes com 'Status Final (Randomizado/Falha)' == 1)
                randomizados = dados_mes[dados_mes['Status Final (Randomizado/Falha)'] == 1]['ID processo'].nunique()

                # Calcular as taxas
                taxa_elegibilidade = elegiveis / total_encaminhados if total_encaminhados else 0
                taxa_contato = contatados / elegiveis if elegiveis else 0
                taxa_consentimento = assinaram_tcle / contatados if contatados else 0
                taxa_randomizacao = randomizados / assinaram_tcle if assinaram_tcle else 0

                # Adicionar os dados calculados para esse mês
                taxas_mensais.append({
                    'Ano': ano,
                    'Mês': mes,
                    'Taxa Elegibilidade': taxa_elegibilidade,
                    'Taxa Contato': taxa_contato,
                    'Taxa Consentimento': taxa_consentimento,
                    'Taxa Randomização': taxa_randomizacao
                })

    # Retorna o DataFrame com as taxas mensais
    return pd.DataFrame(taxas_mensais)

# Usa df_taxas_mensais - Retorna o dicionario com a taxa do mes atual e o delta do mês anterior
def taxas_cards(dataframe_tx_mensal, ano=None, mes=None):
    """
    Retorna as taxas de conversão e suas variações (delta) entre o mês atual/selecionado e o mês anterior.

    A função recebe o DataFrame `df_taxas_mensais` gerado por `calcular_taxas_mensais`, filtra os dados para o
    mês e ano especificados (ou usa os valores atuais por padrão), e calcula a diferença percentual entre os meses.
    Retorna dois dicionários: um com as taxas atuais e outro com os deltas.

    Args:
        dataframe (pd.DataFrame): DataFrame contendo as taxas mensais de conversão.
        ano (int, optional): Ano a ser analisado. Se None, utiliza o ano atual.
        mes (int, optional): Mês a ser analisado. Se None, utiliza o mês atual.

    Returns:
        Tuple:
            dict: Taxas de conversão do mês selecionado.
            dict: Diferenças percentuais (deltas) em relação ao mês anterior.
    """
    df = dataframe_tx_mensal.copy()

    ano_selecionado = max(ano)
    mes_anterior = mes-1 if mes != 1 else 12
    ano_anterior = ano_selecionado-1 if mes_anterior == 12 else ano_selecionado

    df_filtrado = df[df['Ano'].isin([ano_anterior, ano_selecionado])]
    df_filtrado = df_filtrado[df_filtrado['Mês'].isin([mes_anterior, mes])]

    # Ordena por ano e mês para garantir que os dados estão na ordem certa
    df_filtrado = df_filtrado.sort_values(by=['Ano', 'Mês'])

    # Calcula a diferença percentual entre as taxas de cada mês
    df_filtrado['Dif_Taxa_Elegibilidade'] = (df_filtrado['Taxa Elegibilidade'].pct_change() * 100).round(2)
    df_filtrado['Dif_Taxa_Contato'] = (df_filtrado['Taxa Contato'].pct_change() * 100).round(2)
    df_filtrado['Dif_Taxa_Consentimento'] = (df_filtrado['Taxa Consentimento'].pct_change() * 100).round(2)
    df_filtrado['Dif_Taxa_Randomizacao'] = (df_filtrado['Taxa Randomização'].pct_change() * 100).round(2)

    # Resgata as taxas e as diferenças para o mês atual (última linha)
    df_mes_atual = df_filtrado[
        (df_filtrado['Ano'] == ano_selecionado) & 
        (df_filtrado['Mês'] == mes)
    ]
    
    if df_mes_atual.empty:
        return None, None

    df_mes_atual = df_mes_atual.iloc[0]

    taxas = {
        "Taxa Elegibilidade": df_mes_atual['Taxa Elegibilidade'],
        "Taxa Contato": df_mes_atual['Taxa Contato'],
        "Taxa Consentimento": df_mes_atual['Taxa Consentimento'],
        "Taxa Randomização": df_mes_atual['Taxa Randomização']
    }

    diffs = {
        "Dif_Taxa_Elegibilidade": df_mes_atual['Dif_Taxa_Elegibilidade'],
        "Dif_Taxa_Contato": df_mes_atual['Dif_Taxa_Contato'],
        "Dif_Taxa_Consentimento": df_mes_atual['Dif_Taxa_Consentimento'],
        "Dif_Taxa_Randomizacao": df_mes_atual['Dif_Taxa_Randomizacao']
    }

    return taxas, diffs

