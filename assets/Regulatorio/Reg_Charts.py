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

    return fig


def bar_chart_dossie_tec(dataframe):
    df = dataframe[['PI', 'CAAE', 'Estudo', 'Patrocinador', 'Centro Coordenador?',
                     'Tipo de Submissão', 'Implementação?', 'Data de Solicitação', 'Dias úteis - Data de Solicitação → Data de Submissão']].copy()
    
    df['mes'] = df['Data de Solicitação'].dt.month_name(locale='pt_BR')

    media_mes = df.groupby('mes')['Dias úteis - Data de Solicitação → Data de Submissão'].mean().reset_index(name='Média')
    media_mes['label'] = media_mes['Média'].apply(lambda row: f'{row:.2f}')

    ordem_meses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]

    media_mes['mes'] = pd.Categorical(media_mes['mes'], categories=ordem_meses, ordered=True)
    media_mes = media_mes.sort_values('mes')

    if media_mes.empty:
        return None

    fig = px.bar(data_frame=media_mes, x='mes', y='Média', text='label',
                color='mes', title='Tempo médio para preparo do Dossiê Técnico',
                color_discrete_sequence=px.colors.qualitative.Prism, opacity=0.85,
                labels={'Média': 'Média (dias)', 'mes':'Meses'})
    
    fig.update_layout(
        title_font = dict(size=24)
    )

    return fig

