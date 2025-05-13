import pandas as pd
import streamlit as st
from progress_bar import ProgressBar


def gerar_mot_cat(sheet_df, nome_dt_falha):
    if 'Motivo' in sheet_df.columns and 'Categoria' in sheet_df.columns:
        try:
            nome_tcle_ou_pre = 'Data TCLE' if 'Data TCLE' in sheet_df.columns else 'Data pré-TCLE'
            nome_dt_falha = 'Data da falha' if nome_tcle_ou_pre == 'Data pré-TCLE' else nome_dt_falha

            cols = ['Médico que assinou','Motivo', 'Categoria', 'Estudo', nome_tcle_ou_pre, nome_dt_falha]
            if 'Onco/multi' in sheet_df.columns:
                cols.insert(4, 'Onco/multi')

            mot_cat = sheet_df[sheet_df['Status'].str.lower() == 'falha'][cols].copy()
            mot_cat[nome_dt_falha] = mot_cat[nome_dt_falha].fillna(mot_cat[nome_tcle_ou_pre])
            
            mot_cat['Processo'] = 'TCLE' if nome_tcle_ou_pre == 'Data TCLE' else 'Pré-TCLE'
            
            if not 'Data da falha' in mot_cat.columns:
                mot_cat = mot_cat.rename(columns={nome_dt_falha: 'Data da falha', nome_tcle_ou_pre: 'Data assinatura'})
            else:
                mot_cat = mot_cat.rename(columns={nome_tcle_ou_pre: 'Data assinatura'})
            
            
            mot_cat['Data da falha'] = pd.to_datetime(mot_cat['Data da falha'], errors='coerce')
            mot_cat['Data assinatura'] = pd.to_datetime(mot_cat['Data assinatura'], errors='coerce')

            mot_cat['Médico que assinou'] = mot_cat['Médico que assinou'].str.title()
            mot_cat['Estudo'] = mot_cat['Estudo'].str.upper()

            return mot_cat
        except Exception as e:
            st.error('Erro ao agrupar os dados de falha. Verifique se o arquivo enviado está correto.')
            print(f'[ERRO gerar_mot_cat] - {e}')
            return None


def agrupar_info(sheet_df, nome_dt_falha):
    try:
        nome_tcle_ou_pre = 'Data TCLE' if 'Data TCLE' in sheet_df.columns else 'Data pré-TCLE'
        nome_dt_falha = 'Data da falha' if nome_tcle_ou_pre == 'Data pré-TCLE' else nome_dt_falha
        
        if 'Status' not in sheet_df.columns:
              return None, None
        
        cols = ['Estudo', 'Status', nome_tcle_ou_pre, 'Médico que assinou', nome_dt_falha]
        if 'Onco/multi' in sheet_df.columns:
            cols.insert(1, 'Onco/multi')

        if nome_tcle_ou_pre == 'Data pré-TCLE':
            tcle_agrupado = sheet_df[cols].copy()
        else:
            cols.append('Tempo de SCR (dias)')
            tcle_agrupado = sheet_df[cols].copy()
            tcle_agrupado['Tempo de SCR (dias)'] = tcle_agrupado['Tempo de SCR (dias)'].fillna(28).astype(int)
            tcle_agrupado['Data limite - Rando'] = tcle_agrupado['Data TCLE'] + pd.to_timedelta(tcle_agrupado['Tempo de SCR (dias)'], unit='D')

        
        tcle_agrupado = tcle_agrupado.dropna(subset=nome_tcle_ou_pre)

        tcle_agrupado['Médico que assinou'] = tcle_agrupado['Médico que assinou'].fillna('Não especificado')

        tcle_agrupado['Médico que assinou'] = tcle_agrupado['Médico que assinou'].str.title()
        tcle_agrupado['Estudo'] = tcle_agrupado['Estudo'].str.upper()


        cols_to_datetime = [nome_tcle_ou_pre, nome_dt_falha]
        for column in cols_to_datetime:
            tcle_agrupado[column] = pd.to_datetime(tcle_agrupado[column], dayfirst=True, errors='coerce')

        if not 'Data da falha' in tcle_agrupado.columns:
            tcle_agrupado = tcle_agrupado.rename(columns={nome_dt_falha: 'Data da falha', nome_tcle_ou_pre: 'Data assinatura'})
        else:
            tcle_agrupado = tcle_agrupado.rename(columns={nome_tcle_ou_pre: 'Data assinatura'})

        
        return nome_tcle_ou_pre, tcle_agrupado
    
    except Exception as e:
        st.error('Erro ao agrupar os dados. Verifique se o arquivo enviado está correto.')
        print(f'[ERRO agrupar_info] - {e}')
        return None, None


def tratamento_pacientes_sheet(sheet_df):
    df_pacientes_sheet = sheet_df.copy()

    for col in df_pacientes_sheet:
        if 'Nome' in col:
            df_pacientes_sheet.rename(columns={col: 'Nome'}, inplace=True)
            break

    df_pacientes_sheet['Nome'] = df_pacientes_sheet['Nome'].str.split(' ').str[0]
    return df_pacientes_sheet[['Nome', 'Ano']]


def tratamento_dados(arquivo, dicionario):
    barra = ProgressBar()
    barra.iniciar_carregamento(progress_text=f'Processando {arquivo.name}...')

    df = pd.read_excel(arquivo, sheet_name=None)

    for sheet_name, sheet_df in df.items():
        falha_rando_nome = 'Data falha/rando' if 'TCLE' in sheet_name else 'Data real falha/rando'

        if 'TCLE' in sheet_name or 'SCREENING' in sheet_name:
            mot_cat = gerar_mot_cat(sheet_df, falha_rando_nome)
            tcle_ou_pre_tcle, dados_agrupados = agrupar_info(sheet_df, falha_rando_nome)

            mot_cat['fonte'] = arquivo.name
            dados_agrupados['fonte'] = arquivo.name

            dicionario['mot_cat'] = pd.concat([dicionario['mot_cat'], mot_cat], ignore_index=True)
            if tcle_ou_pre_tcle == 'Data TCLE':
                dicionario['tcles']['tcle'] = pd.concat([dicionario['tcles']['tcle'], dados_agrupados], ignore_index=True)
            else:
                dicionario['tcles']['pre_tcle'] = pd.concat([dicionario['tcles']['pre_tcle'], dados_agrupados], ignore_index=True)
        
        if 'Pacientes' in sheet_name:
            pacientes_sheet = tratamento_pacientes_sheet(sheet_df)
            pacientes_sheet['fonte'] = arquivo.name
            dicionario['pcts'] = pd.concat([dicionario['pcts'], pacientes_sheet], ignore_index=True)

    barra.finalizar_carregamento(progress_text=f'{arquivo.name} finalizado!', emoji='🎉')

    return dicionario


def gerar_df_espera_total(df_tcle_agrupado):
    Espera_total_pct = df_tcle_agrupado[['Data assinatura', 'Data da falha', 'Estudo', 'Tempo de SCR (dias)', 'fonte']]
    Espera_total_pct = Espera_total_pct.dropna(subset=['Data assinatura', 'Data da falha'])

    Espera_total_pct['Tempo corrido'] = (Espera_total_pct['Data da falha'] - Espera_total_pct['Data assinatura']).dt.days

    Espera_total_pct['Média de tempo corrido'] = Espera_total_pct['Tempo corrido'].mean().astype(float)
    Espera_total_pct = Espera_total_pct.reset_index(drop=True)

    return Espera_total_pct


def get_andamentos(dataframe, anos, meses):
    df = dataframe.copy()

    final_df = df[(df['Data assinatura'].dt.month.isin(meses)) & 
                  (df['Data assinatura'].dt.year.isin(anos))]

    final_df = final_df[final_df['Status'].str.capitalize() == 'Andamento']
    final_df['Mes TCLE'] = final_df['Data assinatura'].dt.month_name()
    final_df['Ano TCLE'] = final_df['Data assinatura'].dt.year

    return final_df


def get_randomizados(dataframe, anos, meses):
    df = dataframe.copy()

    final_df = df[(df['Data da falha'].dt.month.isin(meses)) &
                  (df['Data da falha'].dt.year.isin(anos))]
    
    final_df = final_df[final_df['Status'].str.capitalize() == 'Randomizado']
    final_df['Mes TCLE'] = final_df['Data assinatura'].dt.month_name()
    final_df['Ano TCLE'] = final_df['Data assinatura'].dt.year

    return final_df


def get_falhas(dataframe, anos, meses):
    df = dataframe.copy()

    final_df = df[(df['Data da falha'].dt.month.isin(meses)) &
                  (df['Data da falha'].dt.year.isin(anos))]
    
    final_df = final_df[final_df['Status'].str.capitalize() == 'Falha']
    final_df['Mes TCLE'] = final_df['Data assinatura'].dt.month_name()
    final_df['Ano TCLE'] = final_df['Data assinatura'].dt.year

    return final_df


def gerar_dados_rel_completo(dados_relatorio, anos, meses):
    '''Essa função gera as contagens a partir do dataframe principal `Dados Relatório` para ser passado aos gráficos'''
    df = dados_relatorio.copy()

    ordem_meses = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    ordem_meses_invertida = ordem_meses[::-1]

    if len(meses) > 1:
        andamento = get_andamentos(dataframe=df, anos=anos, meses=meses)
        
        contagem_final = andamento.groupby(by=['Ano TCLE', 'Mes TCLE', 'Status'], observed=False).size().reset_index(name='Contagem')
        contagem_final['Mes'] = pd.Categorical(contagem_final['Mes TCLE'], categories=ordem_meses, ordered=True)

        return contagem_final
        
    else:
        andamento = get_andamentos(dataframe=df, anos=anos, meses=meses)
        randomizados = get_randomizados(dataframe=df, anos=anos, meses=meses)
        falhas = get_falhas(dataframe=df, anos=anos, meses=meses)

        final_df = pd.concat([andamento, randomizados, falhas], ignore_index=True)

        contagem_final = final_df.groupby(by=['Ano TCLE', 'Mes TCLE', 'Status'], observed=False).size().reset_index(name='Contagem')

        contagem_final['Mes'] = pd.Categorical(contagem_final['Mes TCLE'], categories=ordem_meses_invertida, ordered=True)

        return contagem_final


def get_inicio_triagem(dataframe, anos, meses):
    df = dataframe

    final_df = df[(df['Data assinatura'].dt.month.isin(meses)) & 
                   (df['Data assinatura'].dt.year.isin(anos))].copy()
    
    final_df['Mes'] = final_df['Data assinatura'].dt.month_name()
    final_df['Ano'] = final_df['Data assinatura'].dt.year

    ordem_meses = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    # Converte a coluna 'Mes' em uma categoria com a ordem definida
    final_df['Mes'] = pd.Categorical(final_df['Mes'], categories=ordem_meses, ordered=True)

    contagem_assinaturas = final_df.groupby(by=['Mes', 'Ano'], observed=False).count()['Status'].reset_index(name='Contagem')

    return contagem_assinaturas


def gerar_dataframes(df_tcle_agrupado):
    '''Produz os dataframes restantes que são um fragmento do TCLE agrupado'''

    df_Espera_Total_pcts = gerar_df_espera_total(df_tcle_agrupado)
    df_Dados_relatorio = df_tcle_agrupado[['Status', 'Estudo', 'Data assinatura', 'Data da falha', 'Data limite - Rando', 'Tempo de SCR (dias)', 'fonte']].copy()
    
    return df_Espera_Total_pcts, df_Dados_relatorio


def gerar_relatorio_mes(df_tcle_ori, df_pre_tcle_ori, df_mot_cat_ori, mes, ano, tipo=None):

    df_princ_andamentos = df_tcle_ori[df_tcle_ori['Data assinatura'].dt.year.isin(ano)].copy()
    df_pre_andamentos = df_pre_tcle_ori[df_pre_tcle_ori['Data assinatura'].dt.year.isin(ano) & df_pre_tcle_ori['Data assinatura'].dt.month.isin(mes)].copy()

    df_tcle = df_tcle_ori[df_tcle_ori['Data da falha'].dt.year.isin(ano) & df_tcle_ori['Data da falha'].dt.month.isin(mes)].copy()
    df_pre_tcle = df_pre_tcle_ori[df_pre_tcle_ori['Data da falha'].dt.year.isin(ano) & df_pre_tcle_ori['Data da falha'].dt.month.isin(mes)].copy()
    df_mot_cat = df_mot_cat_ori[df_mot_cat_ori['Data da falha'].dt.year.isin(ano) & df_mot_cat_ori['Data da falha'].dt.month.isin(mes)].copy()

    if tipo:
        df_tcle = df_tcle[df_tcle['Onco/multi'].str.lower() == tipo.lower()]
        df_pre_tcle = df_pre_tcle[df_pre_tcle['Onco/multi'].str.lower() == tipo.lower()]
        df_mot_cat = df_mot_cat[df_mot_cat['Onco/multi'].str.lower() == tipo.lower()]
        df_princ_andamentos = df_princ_andamentos[df_princ_andamentos['Onco/multi'].str.lower() == tipo.lower()]
        df_pre_andamentos = df_pre_andamentos[df_pre_andamentos['Onco/multi'].str.lower() == tipo.lower()]

    # Contagens TCLE
    num_rando_princ = df_tcle[df_tcle['Status'].str.lower() == 'randomizado'].shape[0]
    num_falha_princ = df_tcle[df_tcle['Status'].str.lower() == 'falha'].shape[0]
    num_andamento_princ = df_princ_andamentos[df_princ_andamentos['Status'].str.lower() == 'andamento'].shape[0]
    num_total_scr = num_rando_princ + num_falha_princ + num_andamento_princ

    # Contagens Pré-TCLE
    num_seguiu_tcle = df_pre_tcle[df_pre_tcle['Status'].str.lower() == 'segue tcle principal'].shape[0]
    num_falha_pre = df_pre_tcle[df_pre_tcle['Status'].str.lower() == 'falha'].shape[0]
    num_andamento_pre = df_pre_andamentos[df_pre_andamentos['Status'].str.lower() == 'andamento'].shape[0]
    num_total_pre = num_seguiu_tcle + num_falha_pre + num_andamento_pre

    # Agrupamento por Categoria de Falha
    cat_falha = df_mot_cat.groupby(['Processo', 'Categoria']).size().reset_index(name='Contagem')

    # Filtrando categorias por processo
    cat_falha_tcle = cat_falha[cat_falha['Processo'].str.lower() == 'tcle']
    cat_falha_pre = cat_falha[cat_falha['Processo'].str.lower() == 'pré-tcle']

    # Tabelas formatadas
    resumo_tcle = pd.DataFrame({
        'Status': ['Randomizados', 'Falhas', 'Andamento', 'Total'],
        'Quantidade': [num_rando_princ, num_falha_princ, num_andamento_princ, num_total_scr]
    })

    resumo_pre = pd.DataFrame({
        'Status': ['Seguiu TCLE Principal', 'Falhas', 'Andamento', 'Total'],
        'Quantidade': [num_seguiu_tcle, num_falha_pre, num_andamento_pre, num_total_pre]
    })

    return resumo_tcle, resumo_pre, cat_falha_tcle, cat_falha_pre


