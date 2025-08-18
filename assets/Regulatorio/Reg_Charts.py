import plotly.express as px
import pandas as pd


def dist_pend(dataframe):
    df = dataframe.copy()
    df['Pendências?'] = df['Pendências?'].str.strip().str.capitalize()
    df_direto = df.groupby('Pendências?').size().reset_index(name='Contagem')
    
    return df_direto


def pie_chart_pendencias(dataframe, titulo=None):
    df = dataframe.copy()

    pendencias = dist_pend(df)
    titulo = titulo if titulo else None
    fig = px.pie(pendencias, names='Pendências?', values='Contagem', color='Pendências?', title=titulo, color_discrete_map={'Sim': '#4169e1','Não': "#823fb1"})

    fig.update_layout(
        title_font = dict(size=24)
    )

    return fig


def bar_chart_dossie_tempo_total(dataframe):
    df = dataframe[['PI', 'CAAE', 'Estudo', 'Patrocinador', 'Centro Coordenador?',
                     'Tipo de Submissão', 'Implementação?', 'Data de Solicitação', 'Tempo preparo dossiê técnico', 'Tempo total de submissão inicial']].copy()
    
    df['mes'] = df['Data de Solicitação'].dt.month_name()

    media_mes_dossie = df.groupby('mes')['Tempo preparo dossiê técnico'].mean().reset_index(name='Média')
    media_mes_dossie['label'] = media_mes_dossie['Média'].apply(lambda row: f'{row:.2f}')

    media_mes_total = df.groupby('mes')['Tempo total de submissão inicial'].mean().reset_index(name='Média')
    media_mes_total['label'] = media_mes_total['Média'].apply(lambda row: f'{row:.2f}')

    ordem_meses = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    media_mes_dossie['mes'] = pd.Categorical(media_mes_dossie['mes'], categories=ordem_meses, ordered=True)
    media_mes_dossie = media_mes_dossie.sort_values('mes')

    media_mes_total['mes'] = pd.Categorical(media_mes_total['mes'], categories=ordem_meses, ordered=True)
    media_mes_total = media_mes_total.sort_values('mes')

    fig = None
    fig2 = None

    if not media_mes_dossie.empty:
        fig = px.bar(
            data_frame=media_mes_dossie, x='mes', y='Média', text='label',
            color='mes', title='Tempo médio para preparo do Dossiê Técnico',
            color_discrete_sequence=px.colors.qualitative.Prism, opacity=0.85,
            labels={'Média': 'Média (dias)', 'mes':'Meses'}
        )
        fig.update_layout(title_font=dict(size=24))

    if not media_mes_total.empty:
        fig2 = px.bar(
            data_frame=media_mes_total, x='mes', y='Média', text='label',
            color='mes', title='Tempo total médio de submissão inicial',
            color_discrete_sequence=px.colors.qualitative.Prism, opacity=0.85,
            labels={'Média': 'Média (dias)', 'mes':'Meses'}
        )
        fig2.update_layout(title_font=dict(size=24))


    return fig, fig2

