import streamlit as st
import datetime
import assets.Qualidade.Qual_treats as qtreats
import assets.Qualidade.Qual_charts as qcharts
import os
import plotly.io
from checar_login import ChecarAutenticacao
from progress_bar import ProgressBar


url_plan_qual = st.secrets['urls']['PLAN_QUAL']


class Qualidade():
    def __init__(self):
        ChecarAutenticacao()
        
        if 'setor' not in st.session_state:
            st.switch_page('1_🏠_Homepage.py')

        elif st.session_state['setor'] not in st.secrets['permissions']['PERM_QUAL']:
            st.warning('Você não tem acesso à esta página. Troque de conta ou converse com o administrador.')
            if st.button('Trocar de conta'):
                st.logout()
            
        else:
            st.title('Controle de Qualidade')
            st.subheader('Onde a auditoria interna começa!')

            self.valor_padrao_filtros()

            tabs=[':orange[Achados nas visitas]', ' ', ' ']
            tab1, tab2, tab3 = st.tabs(tabs)

            with tab1:
                self.tab1()


            if st.sidebar.button('Gerar relatório mensal', help='Faça download do gráfico "Achados mais frequentes" para cada responsável'):
                self.gerar_relatorio(self.df, self.anos, self.meses)
            

    def valor_padrao_filtros(self):
        '''Configurando os atributos padrão dos gráficos'''
        self.meses = list(range(1,13))
        self.estudos = None
        self.responsavel = []

        self.today = datetime.date.today().year
        self.anos = [self.today]

        self.max_year = self.anos[0]
        self.min_year = 2022


    def filtros_opcionais(self):
        wants_filter_month = st.sidebar.toggle('Quer filtrar por mês?')
        if wants_filter_month:
            picked_month = st.sidebar.slider('Escolha um mês', min_value=1, max_value=12, value=(1,12))
            self.meses = list(range(picked_month[0], picked_month[1] +1)) # Gera os números dentro do intervalo (tipo 1 até 12+1)

        wants_filter_year = st.sidebar.toggle('Quer filtrar por ano?')
        if wants_filter_year:
            picked_year = st.sidebar.slider('Escolha um ano', min_value=self.min_year, max_value=self.max_year, value=(self.min_year, self.max_year), step=1)
            self.anos = list(range(picked_year[0], picked_year[1] +1)) # Gera os números dentro do intervalo (tipo 2022 até 2024+1)

        wants_filter_study = st.sidebar.toggle('Quer filtrar por estudo?')
        if wants_filter_study:
            list_of_studies = self.df['Protocolo'].unique()
            picked_study = st.sidebar.multiselect('Veja os estudos', options=list_of_studies, placeholder='Escolha os estudos')
            self.estudos = picked_study

        self.wants_filter_resp = st.sidebar.toggle('Quer filtrar por responsável?')
        if self.wants_filter_resp:
            list_of_responsaveis = self.df['Responsável'].unique()
            self.picked_resp = st.sidebar.multiselect('Selecione um responsável', options=list_of_responsaveis, placeholder='Escolha os responsáveis')
            self.responsavel = self.picked_resp

# Tab1
    def grafs_achados_frequentes_tab1(self):
        bar_chart_achados_frequentes = qcharts.bar_chart_achados_frequentes(dataframe=self.df, anos=self.anos, meses=self.meses, 
                                                                                    estudos=self.estudos, responsavel=self.responsavel)
        if bar_chart_achados_frequentes != None:
            st.plotly_chart(bar_chart_achados_frequentes)
        else:
            st.error('Não há dados nestas condições')
        
        exp1 = st.expander(':blue[Ver tabela]')
        with exp1:
            if not self.wants_filter_resp or not self.picked_resp:
                st.info('Para ver a tabela e detalhes, selecione pelo menos um Responsável.')
            else:
                table = qtreats.show_table(dataframe=self.df, anos=self.anos, meses=self.meses, responsaveis=self.responsavel)
                st.write(table)
                contagem = qtreats.contar_visitas_unicas(dataframe=self.df, anos=self.anos, meses=self.meses, respons=self.responsavel)
                responsavel_tab1_str = ', '.join(self.responsavel)
                st.info(f'Número de visitas únicas de {responsavel_tab1_str}: {contagem}')

        st.divider()


    def grafs_achados_protocolos_tab1(self):
        bar_chart_achados_protocolo = qcharts.bar_chart_achados_protocolo(dataframe=self.df, 
                                                                        anos=self.anos, meses=self.meses,
                                                                        estudos=self.estudos, responsavel=self.responsavel)
        if bar_chart_achados_protocolo != None:
            st.plotly_chart(bar_chart_achados_protocolo)
        else:
            st.error('Não há dados nestas condições')
        
        st.divider()


    def grafs_resps_por_achado_tab1(self):
        bar_chart_resp_achados = qcharts.bar_chart_resp_achados(dataframe=self.df, 
                                                                anos=self.anos, meses=self.meses, 
                                                                estudos=self.estudos, responsavel=self.responsavel)
        # if bar_chart_resp_achados != None:
            # st.plotly_chart(bar_chart_resp_achados)
        st.write(bar_chart_resp_achados)
        # else:
            # st.error('Não há dados nestas condições')


    def gerar_relatorio(self, df, anos, meses):
        responsaveis = df['Responsável'].str.strip().str.title().unique()

        # Garante que a pasta temp existe
        temp_dir = os.path.join(os.getcwd(), 'temp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        barra = ProgressBar(sidebar=True)
        barra.iniciar_carregamento(progress_text='Gerando arquivos...', emoji='⚙️')

        arquivos = []
        figures = []
        for responsavel in responsaveis:
            arquivos_grafico, fig = qcharts.gerar_grafico_por_responsavel(df, anos, meses, responsavel)
            if arquivos_grafico and fig:
                arquivos.append(arquivos_grafico)
                figures.append(fig)

        plotly.io.write_images(figures, arquivos)
        
        barra.finalizar_carregamento(progress_text='Pronto!', emoji='🚀')

        if arquivos:
            zip_file = qcharts.gerar_arquivo_zip(arquivos)
            zip_filename = f"Achados_{datetime.datetime.now().strftime('%d-%m-%Y')}.zip"
            
            with open((zip_file), 'rb') as f:
                st.sidebar.download_button(
                    label='📥 Baixar gráficos',
                    data=f,
                    file_name=zip_filename,
                    mime='application/zip'
                )

            # Após o download, remover arquivos temporários
            for arquivo in arquivos:
                os.remove(arquivo)  # Remove cada imagem gerada
            os.remove(zip_file)  # Remove o arquivo ZIP

# Mostrando conteúdo
    def tab1(self):
        arquivo = st.file_uploader('Faça upload da planilha de desvios aqui!', type='xlsx', key='plandesvio', help='Faça download da planilha e insira-a aqui!')
        if not arquivo:
            st.link_button('Planilha de achados', url=url_plan_qual)
            st.session_state['dados_qualidade'] = None

        elif st.session_state['dados_qualidade'] is None:
            try:
                st.session_state['dados_qualidade'] = qtreats.load_qualidade_file(arquivo)
            except:
                st.error('Erro de processamento! Por favor, verifique se o arquivo enviado é o correto.')
            
        if st.session_state['dados_qualidade'] is not None:
            self.df = st.session_state['dados_qualidade']
            self.filtros_opcionais()

            self.grafs_achados_frequentes_tab1()
            self.grafs_achados_protocolos_tab1()
            self.grafs_resps_por_achado_tab1()


if __name__ == "__main__":
    Qualidade()            