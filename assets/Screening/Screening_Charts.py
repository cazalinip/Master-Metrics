import pandas as pd
import plotly.express as px
import assets.Screening.Screening_Treatments as SCR_Treats


def pie_chart_motivos(dataframe, estudo=None, medico=None, anos=None, meses=None, show_value_label=False):
    '''
    Esta função apenas encapsula a criação do gráfico com os dados utilizados em SCR_Charts.ipynb.\n
    Aqui é criado o gráfico de rosca/donuts para uma análise de quantos "motivos" cada "categoria" possui.\n
    Dataframe esperado = Compilado_Motivos_Categoria (Screening_Treatments.Compilado_Motivos_Categoria)    
    Retorna uma fig com estes dados.
    '''
    df = dataframe.copy()

    if estudo:
        df = df[df['Estudo'].isin(estudo)]
        if df.empty:
            return None
        
    if medico:
        df = df[df['Médico que assinou'] == medico]
        if df.empty:
            return None

    if anos:
        df = df[df['Data da falha'].dt.year.isin(anos)]
        if df.empty:
            return None

    if meses:
        df = df[df['Data da falha'].dt.month.isin(meses)]
        if df.empty:
            return None
    
    # Contando os motivos por categoria
    cat_count = df['Categoria'].value_counts()

    # Criando o gráfico de rosca/donut com Plotly
    fig = px.pie(names=cat_count.index, values=cat_count.values, hole=0.5,
                 color_discrete_sequence=px.colors.qualitative.Prism,
                 opacity=0.8)
    
    fig.update_traces(
        insidetextfont_color='white'
    )

    if show_value_label:
        fig.update_traces(
            textinfo='percent+value+label',
            insidetextfont_color='white'
        )

        fig.update_layout(
            showlegend=False,
        )

    return fig


def bar_chart_contagem_motivo_estudos(dataframe, anos=None, meses=None):
    '''
    Aqui é criado o gráfico de barras sobre quantos erros cada estudo possui, no total.
    Dataframe esperado = Compilado_Motivos_Categoria (Screening_Treatments.Compilado_Motivos_Categoria)
    Retorna uma fig com estes dados.
    '''

    df = dataframe.copy()
    df['Data da falha'] = pd.to_datetime(df['Data da falha'], dayfirst=True)

    if anos:
        df = df[df['Data da falha'].dt.year.isin(anos)]
        if df.empty:
            return None

    if meses:
        df = df[df['Data da falha'].dt.month.isin(meses)]
        if df.empty:
            return None

    estudo_count = df.groupby('Estudo', observed=False)['Motivo'].count().reset_index()
    estudo_count = estudo_count.sort_values(by='Motivo', ascending=False)

# Criando o gráfico de barras com Plotly Express
    fig = px.bar(estudo_count, x='Estudo', y='Motivo',
                 labels={'Estudo': 'Estudo', 'Motivo': 'Número de Motivos'},
                 color='Estudo', color_discrete_sequence=px.colors.qualitative.Dark24_r,
                 category_orders={'Estudo': estudo_count['Estudo'].tolist()},
                 text_auto=True, opacity=0.85)
    
    fig.update_traces(
        textfont_color='white')

    return fig


def bar_chart_motivo_em_estudo(dataframe, categoria_especifica=None, anos=None, meses=None):
    '''
    Aqui é criado o gráfico de barras sobre quais estudos aquela categoria existe.\n
    Dataframe esperado = Compilado_Motivos_Categoria (Screening_Treatments.Compilado_Motivos_Categoria)
    Retorna uma fig com estes dados.
    '''
    # Copiar o dataframe para evitar modificações no original
    df = dataframe.copy()

    # Filtrar por categoria específico
    if categoria_especifica:
        df = df[df['Categoria'] == categoria_especifica]
        if df.empty:
            return None

    # Filtrar por anos, se fornecido
    if anos:
        df = df[df['Data da falha'].dt.year.isin(anos)]
        if df.empty:
            return None

    # Filtrar por meses, se fornecido
    if meses:
        df = df[df['Data da falha'].dt.month.isin(meses)]
        if df.empty:
            return None
    
    # Contar falhas por estudo
    df_count = df.groupby('Estudo', observed=False).size().reset_index(name='Contagem')

    df_count = df_count.sort_values(by='Contagem', ascending=False)
    
    # Criar gráfico de barras
    fig = px.bar(df_count, x='Estudo', y='Contagem',
                 labels={'Estudo': 'Estudo', 'Contagem': 'Número de Falhas'},
                 color='Estudo', text='Contagem',
                 opacity=0.85,
                 color_discrete_sequence=px.colors.qualitative.Prism)  # Usar a paleta de cores Prism

    # Mostrar gráfico
    return fig


def bar_chart_contagem_categoria_em_estudo(dataframe, estudo_selecionado=None, anos=None, meses=None, altura=None, largura=None):
    '''
    Esta função cria o gráfico de barras com os motivos filtrados pelo estudo selecionado.
    A galera preferiu este gráfico, de barras.
    Dataframe esperado = Compilado_Motivos_Categoria (Screening_Treatments.Compilado_Motivos_Categoria)
    '''
    df = dataframe.copy()
    df['Data da falha'] = pd.to_datetime(df['Data da falha'], dayfirst=True)

    if estudo_selecionado:
        df = df[df['Estudo'] == estudo_selecionado]
        if df.empty:
            return None

    if anos:
        df = df[df['Data da falha'].dt.year.isin(anos)]
        if df.empty:
            return None

    if meses:
        df = df[df['Data da falha'].dt.month.isin(meses)]
        if df.empty:
            return None

    contagem = df['Categoria'].value_counts()
    fig = px.bar(x=contagem.index, y=contagem.values, 
                 labels={'x': 'Categoria', 'y': 'Número de Ocorrências'},
                 color=contagem.index,
                 color_discrete_sequence=px.colors.qualitative.Dark2, opacity=0.85,
                 height=altura,
                 width=largura,
                 text_auto=True)

    fig.update_layout(xaxis={'categoryorder': 'total descending'})

    fig.update_traces(textfont_color='white')
    
    return fig


def pie_chart_meta_atingida(dataframe, estudos_tempo_scr=None, anos=None, meses=None, meta=None):
    '''
    Esta função apenas encapsula a criação do gráfico com os dados utilizados em SCR_Charts.ipynb.\n
    Aqui é criado o gráfico de rosca/donuts para uma análise da meta atingida em relação ao cumprimento de 28 dias para randomizar.
    Dataframe esperado = Espera_Total_pct (Screening_Treatments.Espera_Total_pct)    
    Retorna uma fig com estes dados.
    '''
    df = dataframe.copy()
    df['Data assinatura'] = pd.to_datetime(df['Data assinatura'], dayfirst=True)

    if estudos_tempo_scr:
        # Filtrar estudos que possuam o tempo de Scr específico
        df = df[df['Tempo de SCR (dias)'].isin(estudos_tempo_scr)]
        if df.empty:
            return None

    if anos:
        df = df[df['Data assinatura'].dt.year.isin(anos)]
        if df.empty:
            return None

    if meses:
        df = df[df['Data assinatura'].dt.month.isin(meses)]
        if df.empty:
            return None


    df.loc[:,'Meta'] = df.loc[:,'Tempo corrido'].apply(lambda tempo: 'Meta atingida' if tempo <=meta else 'Não atingiram a meta')
    count_meta = df['Meta'].value_counts().reset_index()
    count_meta.columns = ['Meta', 'Quantidade']
    
    colors = ['#4169e1', '#ef8035']

    fig = px.pie(count_meta, values='Quantidade', names='Meta',
                color_discrete_sequence=colors, opacity=0.8,
                width=450, height=325)

    fig.update_layout(
        showlegend=False
    )

    fig.update_traces(
        textinfo='percent+value+label',
        hole = 0.5,
        insidetextfont_color='white'
    )

    return fig


def bar_chart_tempo_medio(dataframe, estudos_tempo_scr=None, anos=None, meses=None, meta=None):
    '''
    Esta função cria um gráfico de barras com média de tempo corrido por estudo,
    adicionando desvio padrão de cada barra e uma linha de meta.
    Dataframe esperado = Espera_Total_pct (Screening_Treatments.Espera_Total_pct)
    Retorna a figura (fig) com esses dados.
    '''
    df = dataframe.copy()
    df['Data assinatura'] = pd.to_datetime(df['Data assinatura'], dayfirst=True)
    
    if estudos_tempo_scr:
        # Filtrar estudos que possuam o tempo de Scr específico
        df = df[df['Tempo de SCR (dias)'].isin(estudos_tempo_scr)]
        if df.empty:
            return None

    if anos:
        # Filtrar pelo ano específico
        df = df[df['Data assinatura'].dt.year.isin(anos)]
        if df.empty:
            return None

    if meses:
        # Filtrar pelo ano específico
        df = df[df['Data assinatura'].dt.month.isin(meses)]
        if df.empty:
            return None


    # Calcular média e desvio padrão de tempo corrido por estudo
    df_final = round(df.groupby('Estudo', observed=False)['Tempo corrido'].agg(['mean', 'std']).reset_index(), 0)
    df_final = df_final.rename(columns={'mean':'Média', 'std':'Desvio Padrão'})

    # Organizar os valores para ficar de forma decrescente (maior-menor)
    df_final = df_final.sort_values(by='Média', ascending=False)

    # Escala de cores personalizada
    colorscale = [(0, '#4169e1'),
                  (0.5, '#86299d'),
                  (1, '#ef8035')]

    # Plotar gráfico de barras com plotly.express
    fig = px.bar(df_final, x='Estudo', y='Média',
                 error_y='Desvio Padrão',  # Mostrar desvio padrão como erro vertical
                 labels={'Estudo': 'Estudo', 'Média': 'Tempo corrido médio'},
                 hover_data={'Desvio Padrão': ':.2f'},  # Informação de sobreposição ao passar o mouse (desvio padrão formatado)
                 text='Média',  # Mostrar média como texto nas barras
                 color='Média',  # Colore as barras com base na média
                 color_continuous_scale=colorscale, opacity=0.85,
                 range_color=[df_final['Média'].min(), df_final['Média'].max()],
                 width=1000, height=480)

    if meta:
        meta = int(round(meta,0))
    # Adicionar linha horizontal para a meta
        fig.add_hline(y=meta, line_dash='dash', line_color='gray', annotation_text=f'Meta: menos que {meta} dias',
                    annotation_position='top right')
    
    # Personalizar layout do gráfico
    fig.update_layout(
        xaxis_title='Estudo',
        yaxis_title='Tempo corrido médio (dias)',
        xaxis_tickangle=-45,
        yaxis=dict(tickformat='d')
    )

    fig.update_traces(textfont_color='white')

    return fig


def pie_chart_porcentagem_status_pcts(dataframe, estudo=None, anos=None, meses=None, altura=None, largura=None):
    '''
    Esta função cria um gráfico de rosca com os status dos pacientes,
    sendo possível filtrar por estudo, ano e mês.\n
    Dataframe esperado = TCLE_agrupado (Screening_Treatments.TCLE_agrupado),
    ou Pre_TCLE_sheet_2024 (Screening_Treatments.Pre_TCLE_sheet_2024)\n
    Retorna a figura (fig) com esses dados.
    '''

    # Copia o dataframe original para não modificar o original
    df = dataframe.copy()

    if 'Data limite - Rando' in df.columns:
        df = df.rename(columns={'Data limite - Rando': 'Datas'})

    elif 'Data assinatura' in df.columns:
        df = df.rename(columns={'Data assinatura': 'Datas'})

    df['Datas'] = pd.to_datetime(df['Datas'])
    
    df['Status'] = df['Status'].str.title()

    if estudo:
        df = df[df['Estudo'] == estudo]
        if df.empty:
            return None
        
    # Filtra por anos, se especificados
    if anos:
        df = df[df['Datas'].dt.year.isin(anos)]
        if df.empty:
            return None
    
    # Filtra por meses, se especificados
    if meses:
        df = df[df['Datas'].dt.month.isin(meses)]
        if df.empty:
            return None

    # Contagem de pacientes por status ('randomizado' e 'falha')
    contagem_status = df['Status'].value_counts()
    
    # Verifica se há 'randomizado' e 'falha' na contagem
    if 'Randomizado' not in contagem_status.index:
        contagem_status['Randomizado'] = None
    if 'Falha' not in contagem_status.index:
        contagem_status['Falha'] = None
    if 'Andamento' not in contagem_status.index:
        contagem_status['Andamento'] = None
    if 'Segue Tcle Principal' not in contagem_status.index:
        contagem_status['Segue Tcle Principal'] = None
    
    # Obtém os valores para o gráfico de rosca
    labels = contagem_status.index
    values = contagem_status.values
    
    # Define as cores personalizadas
    cores = ['#ef8035', '#4169e1', '#86299d', '#ffdf40']

    # Cria o gráfico de rosca com Plotly Express
    fig = px.pie(names=labels,
                 color_discrete_sequence=cores, opacity=0.8,
                 values=values,  # Define os valores do gráfico
                 hole=0.5,
                 height=altura,
                 width=largura
                 )
    
    fig.update_layout(
        showlegend = False
    )

    # Coloca a descrição dos valores fora do gráfico
    fig.update_traces(textposition='outside',
                        textinfo='percent+value+label',
                        insidetextfont_color='white'
                     )
    
    return fig


def line_chart_assinaturas_randomizados_por_mes(dataframe, estudos=None, meses=None, anos=None):
    '''
    Esta função cria um gráfico de linhas preenchido com as assinaturas x randomizações por mês,
    sendo possível filtrar por ano e mês.\n
    Dataframe esperado = TCLE_agrupado (Screening_Treatments.TCLE_agrupado),
    ou Pre_TCLE_sheet_2024 (Screening_Treatments.Pre_TCLE_sheet_2024).\n
    Retorna a figura (fig) com esses dados.
    '''

    df = dataframe.copy()


    tcle_principal = False
    pre_tcle = False

    if 'Data limite - Rando' in df.columns:
        df = df.rename(columns={'Data limite - Rando': 'Datas'})
        tcle_principal = True

    elif 'Data pré-TCLE' in df.columns:
        df = df.rename(columns={'Data pré-TCLE': 'Datas'})
        pre_tcle = True

    df['Status'] = df['Status'].str.title()
    df['Datas'] = pd.to_datetime(df['Datas'], dayfirst=True)

    if estudos:
        df = df[df['Estudo'].isin(estudos)]
        if df.empty:
            return None, None
        
    if meses:
        df = df[df['Datas'].dt.month.isin(meses)]
        if df.empty:
            return None, None
        
    if anos:
        df = df[df['Datas'].dt.year.isin(anos)]
        if df.empty:
            return None, None

    if tcle_principal:
        df['Randomizado'] = df['Status'].apply(lambda status: status == 'Randomizado')
    
        # Agrupar por mês e contar o número de assinaturas e randomizados por mês
        df_agregado = df.resample('ME', on='Datas').agg({
            'Status': 'size',         # Conta o número de eventos por mês (assinaturas)
            'Randomizado': 'sum'         # Soma dos valores booleanos, contando quantos são True (randomizados)
        }).reset_index()

        df_agregado['Mês'] = df_agregado['Datas'].dt.strftime('%b')
        df_agregado = df_agregado.rename(columns={'Status':'Assinaturas', 'Randomizado':'Randomizados'})

        labels = {'value':'Quantidade', 'Mês': 'Mês', 'variable': 'Variável'}
        fig = px.line(df_agregado, x='Mês', y=['Randomizados', 'Assinaturas'],
                    labels=labels, text='value',
                    color_discrete_sequence=['#4169e1', '#86299d'],
                    markers=True)
    
        fig.update_traces(fill='tonexty')

        # fig.update_layout(
        #     font=dict(color='black')
        # )

        # Calcular a média de randomizados por mês
        media_randomizados = round(df_agregado['Randomizados'].mean(), 2)

        return fig, media_randomizados


    elif pre_tcle:
        df['Segue Tcle Principal'] = df['Status'].apply(lambda status: status == 'Segue Tcle Principal')

        # Agrupar por mês e contar o número de assinaturas e randomizados por mês
        df_agregado = df.resample('ME', on='Datas').agg({
            'Status': 'size',         # Conta o número de eventos por mês (assinaturas)
            'Segue Tcle Principal': 'sum'         # Soma dos valores booleanos, contando quantos são True (randomizados)
        }).reset_index()

        df_agregado['Mês'] = df_agregado['Datas'].dt.strftime('%b')
        df_agregado = df_agregado.rename(columns={'Status':'Assinaturas', 'Segue Tcle Principal':'Seguiram p/ TCLE Principal'})

        labels = {'value':'Quantidade', 'Mês': 'Mês', 'variable': 'Variável'}
        fig = px.line(df_agregado, x='Mês', y=['Seguiram p/ TCLE Principal', 'Assinaturas'],
                    labels=labels, text='value',
                    color_discrete_sequence=['#4169e1', '#86299d'],
                    markers=True)

        fig.update_traces(fill='tonexty')

        # fig.update_layout(
        #     font=dict(color='black')
        # )

        # Calcular a média de randomizados por mês
        media_randomizados = round(df_agregado['Seguiram p/ TCLE Principal'].mean(), 2)

        return fig, media_randomizados


def bar_chart_status_estudo(dataframe, meses=None, anos=None):
    '''
    Esta função cria um gráfico de barras com os status dos pacientes por estudo.\n
    Dataframe esperado =  TCLE_agrupado (Screening_Treatments.TCLE_agrupado),
    ou Pre_TCLE_sheet_2024 (Screening_Treatments.Pre_TCLE_sheet_2024).\n
    Retorna a figura (fig) com esses dados.
    '''    
    
    df = dataframe.copy()

    if 'Data limite - Rando' in df.columns:
        df = df.rename(columns={'Data limite - Rando': 'Datas'})
        status_order = ['Falha, Andamento, Randomizado']

    elif 'Data assinatura' in df.columns:
        df = df.rename(columns={'Data assinatura': 'Datas'})
        status_order = ['Segue Tcle Principal, Andamento, Falha']

    df['Datas'] = pd.to_datetime(df['Datas'], dayfirst=True)

    df['Status'] = df['Status'].str.title()

    if meses:
        df = df[df['Datas'].dt.month.isin(meses)]
        if df.empty:
            return None
    
    if anos:
        df = df[df['Datas'].dt.year.isin(anos)]
        if df.empty:
            return None
        
    df_grouped = df.groupby(['Estudo', 'Status'], observed=False).size().reset_index(name='Contagem')

    contagem_total = df_grouped.groupby('Estudo', observed=False)['Contagem'].sum().reset_index(name='Contagem Total')

    df_grouped = pd.merge(df_grouped, contagem_total, on='Estudo')

    df_grouped = df_grouped.sort_values(by='Contagem Total', ascending=False)

    total_contagem = df_grouped['Contagem'].sum()

    # Define as cores personalizadas
    cores = ['#86299d', '#ef8035', '#4169e1']

    # Ordenar explicitamente os dados
    estudos_ordenados = df_grouped['Estudo'].unique()

    fig = px.bar(df_grouped, x='Estudo', y='Contagem', color='Status',
                 category_orders={'Estudo': estudos_ordenados, 'Status':status_order}, text_auto=True,
                 color_discrete_sequence=cores, opacity=0.85)
    
    fig.update_traces(
        textfont_color='white')
    
    # Adicionar a anotação com o total
    fig.add_annotation(
        text=f"Total de pacientes: {total_contagem}",
        xref="paper", yref="paper",
        x=0, y=1.1,  # Ajuste a posição conforme necessário
        showarrow=False,
        font=dict(size=14, color="gray"),
        align="center"
        )
    
    return fig

# Este gráfico até o atual momento está inutilizado
def bar_chart_assinaturas_medicos(dataframe, estudo=None, meses=None, anos=None, largura=None, altura=None):
    '''
    Esta função cria um gráfico de barras com o Nº assinaturas dos médicos.\n
    Dataframe esperado =  TCLE_agrupado (Screening_Treatments.TCLE_agrupado),
    ou Pre_TCLE_sheet_2024 (Screening_Treatments.Pre_TCLE_sheet_2024).\n
    Retorna a figura (fig) com esses dados.
    ''' 

    df = dataframe.copy()

    if 'Data assinatura' in df.columns:
        df = df.rename(columns={'Data assinatura': 'Datas'})
        status_order = ['Falha, Andamento, Randomizado']

    elif 'Data pré-TCLE' in df.columns:
        df = df.rename(columns={'Data pré-TCLE': 'Datas'})
        status_order = ['Segue Tcle Principal, Andamento, Falha']

    df['Datas'] = pd.to_datetime(df['Datas'], dayfirst=True)

    df['Status'] = df['Status'].str.title()

    if estudo:
        df = df[df['Estudo'] == estudo]
        if df.empty:
            return None
    
    if meses:
        df = df[df['Datas'].dt.month.isin(meses)]
        if df.empty:
            return None
    
    if anos:
        df = df[df['Datas'].dt.year.isin(anos)]
        if df.empty:
            return None
        
    df_grouped = df.groupby(['Médico que assinou'], observed=False)['Estudo'].size().reset_index(name='Contagem')
    df_grouped = df_grouped.sort_values(by='Contagem', ascending=False)


    fig = px.bar(df_grouped, x='Médico que assinou', y='Contagem', color='Médico que assinou',
                 category_orders={'Status':status_order},
                 text_auto=True, color_discrete_sequence=px.colors.qualitative.Prism,
                 opacity=0.85,
                 width=largura, height=altura)
    
    fig.update_traces(textfont_color='white')
    
    return fig

# Este gráfico mostra o que o de cima mostra + os Status dos pacientes.
def bar_chart_assinaturas_medicos_estudo_status(dataframe, estudos=None, meses=None, anos=None, largura=None, altura=None):
    '''
    Esta função cria um gráfico de barras com o Nº assinaturas dos 
    médicos geral ou em determinado estudo e o status daqueles pacientes.\n
    Dataframe esperado =  TCLE_agrupado (Screening_Treatments.TCLE_agrupado),
    ou Pre_TCLE_sheet_2024 (Screening_Treatments.Pre_TCLE_sheet_2024).\n
    Retorna a figura (fig) com esses dados.
    '''    

    df = dataframe.copy()

    if 'Data limite - Rando' in df.columns:
        df = df.rename(columns={'Data limite - Rando': 'Datas'})
        status_order = ['Falha', 'Randomizado', 'Andamento']

    elif 'Data assinatura' in df.columns:
        df = df.rename(columns={'Data assinatura': 'Datas'})
        status_order = ['Falha', 'Segue Tcle Principal', 'Andamento']


    if estudos:
        df = df[df['Estudo'].isin(estudos)]
        if df.empty:
            return None
        
    
    df['Datas'] = pd.to_datetime(df['Datas'], dayfirst=True)
    if meses:
        df = df[df['Datas'].dt.month.isin(meses)]
        if df.empty:
            return None
    
    if anos:
        df = df[df['Datas'].dt.year.isin(anos)]
        if df.empty:
            return None

    # Agrupar por Médico e Status e contar as ocorrências
    contagem_status = df.groupby(['Médico que assinou', 'Status'], observed=False).size().reset_index(name='Contagem')

    # Calcular a contagem total por médico
    contagem_total = contagem_status.groupby('Médico que assinou', observed=False)['Contagem'].sum().reset_index(name='Contagem Total')

    # Mesclar a contagem total de volta ao DataFrame original
    contagem_status = pd.merge(contagem_status, contagem_total, on='Médico que assinou')

    # Ordenar por contagem total em ordem decrescente
    contagem_status = contagem_status.sort_values(by='Contagem Total', ascending=False)

    fig = px.bar(contagem_status, x='Médico que assinou', y='Contagem', color='Status',
                category_orders={'Status':status_order}, text_auto=True,
                labels={'Médico que assinou': 'Médico', 'Contagem': 'Número de Pacientes'},
                width=largura, height=altura,
                color_discrete_sequence=px.colors.qualitative.Prism, opacity=0.85)
    
    fig.update_traces(textfont_color='white')

    return fig


def bar_chart_falha_estudo_medico(dataframe, medico, meses=None, anos=None, largura=None, altura=None):
    '''
    Aqui é criado o gráfico de barras para uma análise de quantas falhas "o médico" possui.\n
    A fim de cruzar os dados entre os motivos de falha do paciente e os estudos do médico.\n
    Dataframe esperado = Compilado_Motivos_Categoria (Screening_Treatments.Compilado_Motivos_Categoria)    
    Retorna uma fig com estes dados.
    '''
    df = dataframe.copy()

    df = df[df['Médico que assinou'] == medico]
    if df.empty:
        return None
    
    if meses:
        df = df[df['Data da falha'].dt.month.isin(meses)]
        if df.empty:
            return None
    
    if anos:
        df = df[df['Data da falha'].dt.year.isin(anos)]
        if df.empty:
            return None


    estudo_count = df['Estudo'].value_counts().reset_index()
    estudo_count.columns = ['Estudo', 'Contagem']

    fig = px.bar(estudo_count, x='Estudo', y='Contagem', 
                 text='Contagem', color='Estudo',
                 labels={'Estudo': 'Estudo', 'Contagem': 'Contagem de Falhas'},
                 text_auto=True,
                 width=largura, height=altura,
                 opacity=0.85, color_discrete_sequence=px.colors.qualitative.Dark2)

    fig.update_traces(textfont_color='white')
    
    return fig


def relatorio_randomizados_do_mes(dataframe, df_pacientes, meses, anos, download=False):
    '''
    Esta função cria um gráfico de barras com os randomizados por estudo.\n
    Dataframe esperado =  TCLE_agrupado (Screening_Treatments.TCLE_agrupado).\n
    Retorna a figura (fig) com esses dados (para exibição) e o PGN temporário para download.
    '''
    df = dataframe.copy()

    df = df[df['Status'] == 'Randomizado'][['Estudo','Data da falha']]

    df = df.rename(columns={'Data da falha':'Data da Randomização'})
    
    df = df[df['Data da Randomização'].dt.year.isin(anos)]
    if df.empty:
        return None
    
    df = df[df['Data da Randomização'].dt.month.isin(meses)]
    if df.empty:
        return None

    contagem_estudos = df['Estudo'].value_counts().reset_index()
    contagem_estudos.columns = ['Estudo', 'Contagem']

    total_contagem = contagem_estudos['Contagem'].sum()

    pacientes = df_pacientes
    anos_int = [int(ano) for ano in anos]
    pacientes = pacientes[pacientes['Ano'].isin(anos_int)]

    if pacientes.empty:
        total_pacientes = "Contagem indisponível"
    else:
        total_pacientes = pacientes['Nome'].count()
    

    meses_dict = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
                 }

    nomes_meses = [meses_dict[mes] for mes in meses]
    anos_separados = [f'{ano}' for ano in anos]
    if len(meses) == 1:
        title_graph = f"Randomizados do mês de {nomes_meses[0]}"

    elif len(meses) == 12:
        if len(anos) == 1:
            title_graph = f"Randomizados do ano de {anos[0]}"
        elif len(anos) >1:
            title_graph = f"Randomizados dos anos de {', '.join(anos_separados)}"

    elif len(meses) >1 and len(meses) <12:
        title_graph = f"Randomizados dos meses de {', '.join(nomes_meses)}"

    fig = px.bar(contagem_estudos, x='Estudo', y='Contagem', text='Contagem',
                labels={'Estudo':'Estudo', 'Contagem':'Randomizados'},
                title=title_graph, text_auto=True, opacity=0.85,
                color_discrete_sequence=px.colors.qualitative.Plotly)
    
    fig.update_traces(textfont_color='white')

    # Ajustes no layout do gráfico para esconder os títulos dos eixos X e Y
    fig.update_layout(
        xaxis=dict(
            title=None,  # Define o título do eixo X como None para escondê-lo
            title_standoff=30  # Distância do título em relação à área do gráfico
        ),
        yaxis=dict(
            title=None,  # Define o título do eixo Y como None para escondê-lo
            title_standoff=30  # Distância do título em relação à área do gráfico
        ),
        showlegend=False,  # Esconde a legenda
        title={
            'text': title_graph,
            'font': {
                'family': 'Arial',
                'size': 24
            }
        }
    )

    # Adicionar a anotação com os totais
    fig.add_annotation(
        text=f"""Total de pacientes do ano: {total_pacientes}
                 Total de randomizados: {total_contagem}""",
        xref="paper", yref="paper",
        x=0.01, y=1.1,  # Ajuste a posição conforme necessário
        showarrow=False,
        font=dict(size=14, color="gray"),
        align="center"
        )


    if download:
        # Salva o gráfico como um arquivo PNG temporário
        file_path = "temp_fig.png"
        fig.write_image(file_path)

        return file_path
    else:
        return fig
    

def panorama_randomizados_do_mes(dataframe: pd.DataFrame, meses: None, anos: None):
    df = dataframe.copy()

    df = df[df['Status'] == 'Randomizado'][['Estudo','Data da falha']]
    df = df.rename(columns={'Data da falha':'Data da Randomização'})

    df['Mes'] = df['Data da Randomização'].dt.month_name()
    
    if anos:
        df = df[df['Data da Randomização'].dt.year.isin(anos)]
        if df.empty:
            return None
    
    if meses:
        df = df[df['Data da Randomização'].dt.month.isin(meses)]
        if df.empty:
            return None
    
    ordem_meses = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    # Converte a coluna 'Mes' em uma categoria com a ordem definida
    df['Mes'] = pd.Categorical(df['Mes'], categories=ordem_meses, ordered=True)

    # Agrupa e conta os meses
    new_df = df.groupby('Mes', observed=False).size().reset_index(name='Randomizados')
    soma = new_df['Randomizados'].sum()

    fig = px.line(data_frame=new_df, x='Mes', y='Randomizados', text='Randomizados',
                color_discrete_sequence=['#86299d'], markers=True)
        
    fig.update_traces(fill='tonexty')
    fig.update_traces(textfont_color='white')
    fig.update_layout(
    title={
            'text': 'Randomizados de cada mês',
            'font': {
                'family': 'Arial',
                'size': 24
            }
        }
    )

    # Adicionar a anotação com os totais
    fig.add_annotation(
        text=f"Total de randomizados: {soma}",
        xref="paper", yref="paper",
        x=0.01, y=1.05,  # Ajuste a posição conforme necessário
        showarrow=False,
        font=dict(size=14, color="gray"),
        align="center"
        )
    
    return fig


def bar_chart_acompanhamento_completo(dados, anos, meses):
    # Agrupar os dados de forma que cada ano e mês tenha suas contagens de status separadas
    dados_pivotados = dados.pivot_table(index='Mes', columns=['Ano TCLE', 'Status'], values='Contagem', fill_value=0, observed=False)

    # Resetar o índice para manter 'Mes TCLE' como coluna
    dados_pivotados.reset_index(inplace=True)

    # Achatar o MultiIndex das colunas
    dados_pivotados.columns = [' '.join(map(str, col)).strip() for col in dados_pivotados.columns.values]

    # Criar uma lista de colunas para o gráfico
    y_columns = [col for col in dados_pivotados.columns if col != 'Mes']

    meses_dict = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto', 
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }

    nomes_meses = [meses_dict[mes] for mes in meses]
    anos_separados = [f'{ano}' for ano in anos]
    if len(meses) == 1:
        title_graph = f"Origem dos Status dos pacientes do mês de {nomes_meses[0]}"

    elif len(meses) == 12:
        if len(anos) == 1:
            title_graph = f"Origem dos Status dos pacientes do ano de {anos[0]}"
        elif len(anos) >1:
            title_graph = f"Origem Status dos pacientes dos anos de {', '.join(anos_separados)}"

    elif len(meses) >1 and len(meses) <12:
        title_graph = f"Origem Status dos pacientes dos meses de {', '.join(nomes_meses)}"

    # Criar o gráfico de barras empilhadas
    fig = px.bar(dados_pivotados, x='Mes', 
                 y=y_columns,  # Usar as colunas achatadas
                 text_auto=True, 
                 title=title_graph,
                 labels={'value': 'Contagem', 'variable': 'Status'},
                 opacity=0.85,
                 color_discrete_sequence=px.colors.qualitative.Prism)

    # Atualizar layout para incluir legenda e personalizar
    fig.update_layout(
        barmode='group',  # Modo empilhado
        xaxis_title='Mês',
        yaxis_title='Contagem',
        title_font=dict(size=24),
        xaxis_tickangle=-45,
    )

    return fig


def bar_chart_inicio_triagem(dados):
    dados['Ano'] = dados['Ano'].astype(str)

    fig = px.bar(data_frame=dados, x='Mes', y='Contagem', text_auto=True,
                 color_discrete_sequence=px.colors.qualitative.Prism,
                 color='Ano', opacity=0.85,
                 title='N de pacientes que iniciaram triagem por mês')
    
    total_contagem = dados['Contagem'].sum()
    
    # Atualizar layout para incluir legenda e personalizar
    fig.update_layout(
        xaxis_title='Mês',
        yaxis_title='Contagem',
        title_font=dict(size=24),
        xaxis_tickangle=-45,
        showlegend=False
    )
    
    # Remover a legenda, pois "ano" é considerada variável contínua, assim a legenda fica por range de valor (2023,5, 2024, 2024,5...)

    # Adicionar a anotação com o total
    fig.add_annotation(
        text=f"Total de pacientes: {total_contagem}. Pacientes Pré-TCLE não estão nesta contagem*",
        xref="paper", yref="paper",
        x=0, y=1.1,  # Ajuste a posição conforme necessário
        showarrow=False,
        font=dict(size=14, color="gray"),
        align="center"
        )
    

    return fig

# Gera a tabela para download do SCR
def gerar_dados_e_excel(dataframe, meses, anos):
    df = dataframe.copy()

    df = df[df['Status'] == 'Randomizado'][['Nome do Paciente', 'Estudo','Data falha/rando']]
    df = df.rename(columns={'Data falha/rando':'Data da Randomização'})
    
    df = df[df['Data da Randomização'].dt.year.isin(anos)]
    if df.empty:
        return None, None
    
    df = df[df['Data da Randomização'].dt.month.isin(meses)]
    if df.empty:
        return None, None

    tmp_file_name = 'relatorio.xlsx'
    df_to_send = df[['Nome do Paciente', 'Estudo','Data da Randomização']]
    df_to_send.to_excel(tmp_file_name, index=False)
    
    return tmp_file_name, df_to_send

