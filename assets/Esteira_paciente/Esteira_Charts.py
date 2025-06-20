import pandas as pd
import plotly.express as px


def bar_chart_medias_tempo_processo(dataframe_tempos, anos=None, meses=None):
    """
    Gera um gráfico de barras com as médias do tempo levado em cada etapa do processo.

    A função recebe o DataFrame resultante de `dataframe_para_calculo_tempos`, calcula as médias dos tempos
    entre eventos (em dias) e exibe um gráfico de barras. É possível filtrar os dados por ano e/ou mês de início.

        Returns:
        None: A função apenas exibe o gráfico, sem retornar dados.
    """
    df_tempos = dataframe_tempos.copy()

    if anos:
        df_tempos = df_tempos[df_tempos['Data de Recebimento (início/encaminhamento)'].dt.year.isin(anos)]
        if df_tempos.empty:
            return None

    if meses:
        df_tempos = df_tempos[df_tempos['Data de Recebimento (início/encaminhamento)'].dt.month.isin(meses)]
        if df_tempos.empty:
            return None

    # Filtrando apenas os valores positivos para cada coluna, evitando erro de digitação
    media_eligibilidade = round(df_tempos.loc[df_tempos['Tempo Eligibilidade - Recebimento'] >= 0, 'Tempo Eligibilidade - Recebimento'].mean(), 2)
    media_contato = round(df_tempos.loc[df_tempos['Tempo Contato - Recebimento'] >= 0,'Tempo Contato - Recebimento'].mean(), 2)
    media_tcle = round(df_tempos.loc[df_tempos['Tempo TCLE - Recebimento'] >= 0, 'Tempo TCLE - Recebimento'].mean(), 2)
    media_processo = round(df_tempos.loc[df_tempos['Tempo Randomização/Falha - Recebimento'] >= 0,'Tempo Randomização/Falha - Recebimento'].mean(), 2)

    dados_medias = {
        'Média': [media_eligibilidade, media_contato, media_tcle, media_processo],
        'Tipo de Tempo': ['Elegibilidade', 'Contato', 'TCLE', 'Processo']
    }

    df_medias = pd.DataFrame(dados_medias)

    # Criando o gráfico de barras
    fig = px.bar(df_medias, 
                x='Tipo de Tempo', 
                y='Média', 
                title="Média em dias dos processos", 
                labels={'Tipo de Tempo': 'Processos', 'Média': 'Média (dias)'},
                color='Tipo de Tempo',  # Cores diferentes para cada barra
                text='Média',  # Mostrar as médias nas barras
                color_discrete_sequence=px.colors.qualitative.Prism,
                opacity=0.85
            )

    fig.update_layout(
        title_font = dict(size=24)
    )

    return fig


def line_chart_taxas_mensais(df, anos=None):
    '''
    Recebe o dataframe de `calcular_taxas_mensais` - `df_taxas_mensais`.

    Exibe o gráfico de linhas com a evolução das taxas de conversão mensais.
    
    Returns:
        px.line -> Gráfico de linhas do ano selecionado inteiro
    '''
    if anos:
        df = df[df['Ano'].isin(anos)]

    # Agora vamos criar o gráfico de linha para mostrar a evolução das taxas por mês
    fig = px.line(
        df,
        x="Mês", 
        y=["Taxa Elegibilidade", "Taxa Contato", "Taxa Consentimento", "Taxa Randomização"],
        title="Evolução das Taxas de Conversão por Mês",
        labels={"Mês": "Mês", "value": "Taxa (%)", "variable": "Indicador"},
        markers=True,
    )

    # Formatar o eixo Y para mostrar as taxas em porcentagem
    fig.update_layout(
        yaxis_tickformat='.2%',
        xaxis_title="Mês",
        yaxis_title="Taxa (%)",
        xaxis=dict(tickmode='linear', tick0=1, dtick=1),  # Para mostrar todos os meses
        title_font=dict(size=24)
    )

    return fig


def missing_data(dataframe):
    perc_missing = round(dataframe.isnull().sum() / len(dataframe) * 100,2)
    perc_missing = perc_missing.reset_index(name='Percentual').sort_values(by='Percentual', ascending=True)

    fig = px.bar(perc_missing, x='index', y='Percentual', text_auto=True)
    return fig

