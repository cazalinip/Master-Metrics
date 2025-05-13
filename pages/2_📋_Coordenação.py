import streamlit as st
import datetime
import assets.Coordenacao.Coord_Treats as c_treats
import assets.Coordenacao.Coord_Charts as c_charts
import os
from checar_login import ChecarAutenticacao
from progress_bar import ProgressBar


url_tabela_qual_coord = st.secrets['urls']["PLAN_QUAL_COORD"]
url_plan_desv = st.secrets['urls']["PLAN_DESV"]


class Coordenacao():
    def __init__(self):
        ChecarAutenticacao()
        
        if 'setor' not in st.session_state:
            st.switch_page('1_🏠_Homepage.py')
        
        elif st.session_state['setor'] not in st.secrets['permissions']['PERM_COORD']:
            st.warning('Você não tem acesso à esta página. Troque de conta ou converse com o administrador.')
            if st.button('Trocar de conta'):
                st.logout()
                   
        else:
            st.title('Coordenação')
            st.subheader('Aqui você conta com as informações dos desvios de protocolo!')
            
            self.valor_padrao_filtros()
            
            tabs = ['Informações Desvios', 'Tempo de Entrega Coordenação', ' ']
            tab1, tab2, tab3 = st.tabs(tabs)

            with tab1:
                self.tab1()

            with tab2:
                self.tab2()


    def valor_padrao_filtros(self):
        '''Configurando os atributos padrão dos gráficos'''
        self.meses = list(range(1,13))
        self.estudos = None
        self.categorias = None
        self.setores = None

        self.today = datetime.date.today().year
        self.anos = [self.today]

        self.max_year = self.anos[0]
        self.min_year = 2022

    
    def filtros_opcionais(self):
        wants_filter_month = st.sidebar.checkbox('Quer filtrar por mês?')
        if wants_filter_month:
            picked_month = st.sidebar.slider('Escolha um mês', min_value=1, max_value=12, value=(1,12)) #Escolhe o mês
            self.meses = list(range(picked_month[0], picked_month[1] +1)) # Gera os números dentro do intervalo (tipo 1 até 12+1)

        wants_filter_year = st.sidebar.checkbox('Quer filtrar por ano?', disabled=False)
        if wants_filter_year:
            picked_year = st.sidebar.slider('Escolha um ano', min_value=int(self.min_year), max_value=int(self.max_year), value=(int(self.min_year), int(self.max_year)), step=1) #Escolhe o ano
            self.anos = list(range(picked_year[0], picked_year[1] +1)) # Gera os números dentro do intervalo (tipo 2022 até 2024+1)

        wants_filter_study = st.sidebar.checkbox('Quer filtrar por estudo?')
        if wants_filter_study:
            list_of_studies = self.df['Estudo'].unique()
            picked_study = st.sidebar.multiselect('Veja os estudos', options=list_of_studies, placeholder='Escolha os estudos')
            self.estudos = picked_study

        wants_filter_category = st.sidebar.checkbox('Quer filtrar por categoria?')
        if wants_filter_category:
            list_of_categories = self.df['Categoria'].unique()
            picked_category = st.sidebar.multiselect('Veja as categorias', options=list_of_categories, placeholder='Escolha as categorias')
            self.categorias = picked_category

        wants_filter_sector = st.sidebar.checkbox('Quer filtrar por setor?')
        if wants_filter_sector:
            list_of_sectors = self.df['Setor'].unique()
            picked_sector = st.sidebar.multiselect('Veja os setores', options=list_of_sectors, placeholder='Escolha os setores')
            self.setores = picked_sector

# Tab1
    def grafs_desvio_p_categoria(self):
        bar_chart_count_por_categoria = c_charts.bar_chart_count_por_categoria(dataframe=self.df, anos=self.anos, 
                                                                                meses=self.meses, estudos=self.estudos, 
                                                                                categoria_selecionada=self.categorias,
                                                                                setor_selecionado=self.setores)
        if bar_chart_count_por_categoria != None:
            st.plotly_chart(bar_chart_count_por_categoria)
        else:
            st.error('Não há dados nestas condições')
            st.empty()


    def grafs_desvio_p_setor(self):
        bar_chart_desvios = c_charts.bar_chart_desvios(dataframe=self.df, anos=self.anos, meses=self.meses,
                                                        estudos=self.estudos, categoria_selecionada=self.categorias, 
                                                        setor_selecionado=self.setores)
        if bar_chart_desvios != None:
            st.plotly_chart(bar_chart_desvios)
        else:
            st.error('Não há dados nestas condições')
            st.empty()


    def grafs_tempo_desv_ciencia(self):
        tempo_desv_ciencia = c_charts.bar_chart_media_tempos_desvios(self.df_tempos, self.meses, self.anos, tempo_desv_cien=True)
        if tempo_desv_ciencia != None:
            st.plotly_chart(tempo_desv_ciencia)
        else:
            st.error('Não há dados nestas condições')
            st.empty()
        
    
    def grafs_tempo_ciencia_submissao(self):
        tempo_ciencia_submissao = c_charts.bar_chart_media_tempos_desvios(self.df_tempos, self.meses, self.anos, tempo_desv_cien=False)
        if tempo_ciencia_submissao != None:
            st.plotly_chart(tempo_ciencia_submissao)
        else:
            st.error('Não há dados nestas condições')
            st.empty()


    def grafs_desvio_p_estudo(self):
        bar_chart_desvios_por_estudo = c_charts.bar_chart_desvios_por_estudo(dataframe=self.df, anos=self.anos, 
                                                                                meses=self.meses, estudos=self.estudos, 
                                                                                categoria_selecionada=self.categorias,
                                                                                setor_selecionado=self.setores)
        if bar_chart_desvios_por_estudo != None:
            st.plotly_chart(bar_chart_desvios_por_estudo)
        else:
            st.error('Não há dados nestas condições')
            st.empty()
    

    def grafs_preju_pct(self):
        donut_chart_prejuizos = c_charts.donut_chart_prejuizos(dataframe=self.df, anos=self.anos, meses=self.meses, 
                                                            estudos=self.estudos, categoria_selecionada=self.categorias,
                                                            setor_selecionado=self.setores)
        if donut_chart_prejuizos != None:
            st.plotly_chart(donut_chart_prejuizos)
        else:
            st.error('Não há dados nestas condições')
            st.empty()


# Tab2
    def grafs_tempos_coord_audit(self):
        bar_chart_control_qual_tempos = c_charts.bar_chart_control_qual_tempos(dataframe=self.df_tempos, anos=self.anos, meses=self.meses)
        if bar_chart_control_qual_tempos != None:
            st.plotly_chart(bar_chart_control_qual_tempos)
            st.info('Este gráfico é afetado por filtros de tempo, somente.')
            with st.expander('Ver planilha'):
                st.write(st.session_state['dados_tab_qual_coord'])
                st.info('Você pode fazer o download da tabela passando o mouse em cima e clicando na setinha ↓')
        else:
            st.error('Não há dados nestas condições')
            st.empty()

# Relatório
    def gerar_relatorio(self):
        # Garante que a pasta temp existe
        temp_dir = os.path.join(os.getcwd(), 'temp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        barra = ProgressBar(sidebar=True)
        barra.iniciar_carregamento(progress_text='Gerando arquivos...', emoji='⚙️')

        arquivos = c_charts.gerar_grafico_relatorio(dataframe=self.df, estudo=self.estudos, setor=self.setores, categoria=self.categorias)
        zip_path = c_charts.gerar_arquivo_zip(arquivos)

        barra.finalizar_carregamento(progress_text='Pronto!', emoji='🚀')

        zip_filename = f"Desvios_{datetime.datetime.now().strftime('%d-%m-%Y')}.zip"

        with open(zip_path, 'rb') as f:
            st.sidebar.download_button(
                label="📥 Baixar gráficos",
                data=f,
                file_name=zip_filename,
                mime='application/zip'
            )

        for arquivo in arquivos:
            os.remove(arquivo)  # Remove cada imagem gerada
        os.remove('graficos_responsaveis.zip')  # Remove o arquivo ZIP


# Conteúdo tabs
    def tab1(self):
        arquivo = st.file_uploader('Faça upload da planilha de desvios!', type='xlsx', key='plandesvio', help='Faça download da planilha e insira-a aqui!')
        if not arquivo:
            st.link_button('Planilha de desvios', url=url_plan_desv)
            st.session_state['plan_desvio'] = None
            st.session_state['plan_calc_tempos'] = None
            st.session_state['regist_apag'] = None

        elif st.session_state['plan_desvio'] is None:
            try:
                barra = ProgressBar()
                barra.iniciar_carregamento()
                st.session_state['plan_desvio'] = c_treats.process_excel_file(arquivo)
                st.session_state['regist_apag'], st.session_state['plan_calc_tempos'] = c_treats.gerar_calculo_tempos(st.session_state['plan_desvio'])
                barra.finalizar_carregamento(emoji='🚀')
            except Exception as e:
                print(f'[ERRO] Processamento de arquivo Coordenacao - {e}')
                st.error('Erro de processamento! Por favor, verifique se o arquivo enviado é o correto.')
            
        if st.session_state['plan_desvio'] is not None:
            self.df = st.session_state['plan_desvio']
            self.df_tempos = st.session_state['plan_calc_tempos']
            self.registros_apagados = st.session_state['regist_apag']
            self.filtros_opcionais()
            if st.sidebar.button('Gerar relatório mensal', help='Faça download dos gráficos de Desvios por Categoria e Setor'):
                self.gerar_relatorio()

            st.subheader('Contagem de Desvios por Categoria')
            self.grafs_desvio_p_categoria()
            
            st.subheader('Contagem de Desvios por Setor')
            self.grafs_desvio_p_setor()

            with st.expander('Ver a planilha'):
                col1, col2 = st.columns(2)
                with col1:
                    cat = st.multiselect('Categorias', options=self.df['Categoria'].unique().tolist())
                with col2:
                    sect = st.multiselect('Setores', options=self.df['Setor'].unique().tolist())
                
                if not cat:
                    cat = self.df['Categoria'].unique().tolist()
                if not sect:
                    sect = self.df['Setor'].unique().tolist()

                df_filtered = self.df[self.df['Categoria'].isin(cat) & self.df['Setor'].isin(sect)]

                st.write(df_filtered)
                st.info('Faça download da planilha passando o mouse em cima e clicando na setinha para baixo ↓')

            st.subheader('Cálculo dos tempos do processo de Coordenação')
            st.info(f'ℹ️ {self.registros_apagados} Registros foram apagados devido ao preenchimento incompleto das datas.')
            
            col1, col2 = st.columns(2)
            with col1:
                self.grafs_tempo_desv_ciencia()

            with col2:
                self.grafs_tempo_ciencia_submissao()

            st.info('A data filtrada/baseada aqui é a Data da Ciência.')

            with st.expander('Ver desvios por Estudo'):
                st.subheader('Contagem de Desvios por Estudo')
                self.grafs_desvio_p_estudo()
            
                st.subheader('Distribuição de "Prejuízo" ao participante em relação aos desvios')
                self.grafs_preju_pct()
                        

    def tab2(self):
        excel_file = st.file_uploader('Faça upload da Planilha Qualidade-Coordenação!', 'xlsx', key='excel_file_uploader_coord', 
                            help='Faça o download da planilha e insira-a aqui!')
        
        if not excel_file:
            st.link_button('Acessar Tabela Qualidade-Coordenação', url=url_tabela_qual_coord)
            st.session_state['dados_tab_qual_coord'] = None
        
        elif st.session_state['dados_tab_qual_coord'] is None:
            try:
                dados_qual_coord = c_treats.carregar_dados_tab_qual_coord(excel_file)
                st.session_state['dados_tab_qual_coord'] = dados_qual_coord
            except Exception as e:
                print(f'[ERRO] Processamento de arquivo Coordenacao - {e}')
                st.error('Erro de processamento! Por favor, verifique se o arquivo enviado é o correto.')


        if st.session_state['dados_tab_qual_coord'] is not None:
            self.df_tempos = st.session_state['dados_tab_qual_coord']

            st.subheader('Contagem de Desvios por Categoria')
            self.grafs_tempos_coord_audit()
            
    
if __name__ == "__main__":
    Coordenacao()