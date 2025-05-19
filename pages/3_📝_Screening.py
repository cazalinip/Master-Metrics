import streamlit as st
import pandas as pd
import datetime
import os
import assets.Screening.Screening_Charts as SCR_charts
import assets.Screening.Screening_Treatments as SCR_treats
from checar_login import ChecarAutenticacao


URL_2023=st.secrets['urls']['PLAN_SCR_2023']
URL_2024=st.secrets['urls']['PLAN_SCR_2024']
URL_2025=st.secrets['urls']['PLAN_SCR_2025']

class Screening():
    def __init__(self):
        ChecarAutenticacao()

        if 'setor' not in st.session_state:
            st.switch_page('1_🏠_Homepage.py')

        elif st.session_state['setor'] not in st.secrets['permissions']['PERM_SCR']:
            st.warning('Você não tem acesso à esta página. Troque de conta ou converse com o administrador.')
            if st.button('Trocar de conta'):
                st.logout()

        else:
            st.title('Screening')
            st.subheader('Veja as métricas a respeito da esteira final do paciente')
            arquivos = st.file_uploader('Faça upload de uma ou mais planilhas aqui!', 'xlsx', accept_multiple_files=True)
            st.info('Estas são as planilhas aceitas! Caso não tenha acesso, converse com o setor.')
            col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns(10)
            with col1:
                st.link_button('Dados 2023', url=URL_2023)
            with col2:
                st.link_button('Dados 2024', url=URL_2024)
            with col3:
                st.link_button('Dados 2025', url=URL_2025)

            if arquivos:
                try:
                    self.valor_padrao_filtros()
                    self.carregamento_tratamento_arquivos(arquivos) # Provavelmente a exception está na cadeia de funções daqui
                    self.carregar_dataframes()
                    self.filtros_opcionais()
                
                    self.tabs = [
                        ':orange[Indicadores de falha]',
                        ':orange[Mensurar tempo de Screening]',
                        ':orange[Panorama Assinaturas]',
                        ':orange[Relatórios]',
                        ':orange[Planilhas]'
                    ]

                    tab1, tab2, tab3, tab4, tab5 = st.tabs(tabs=self.tabs)
                    with tab1:
                        self.tab1()
                    with tab2:
                        self.tab2()
                    with tab3:
                        self.tab3()
                    with tab4:
                        self.tab4()
                    with tab5:
                        self.tab5()
                
                except Exception as e:
                    print(f'[ERRO] Processamento de arquivo SCR - {e}')
                    st.error('Erro de processamento! Por favor, verifique se o arquivo enviado é o correto.')


    def valor_padrao_filtros(self):
        '''Configurando os atributos padrão dos gráficos'''
        self.meses = list(range(1,13))

        self.today = datetime.date.today().year
        self.anos = [self.today]

        self.max_year = self.anos[0]
        self.min_year = 2022

        self.meta = 28


    def filtros_opcionais(self):
        wants_filter_month = st.sidebar.toggle('Quer filtrar por mês?')
        if wants_filter_month:
            picked_month = st.sidebar.slider('Escolha um mês', min_value=1, max_value=12, value=(1,12)) #Escolhe o mês
            self.meses = list(range(picked_month[0], picked_month[1] +1)) # Gera os números dentro do intervalo (tipo 1 até 12+1)

        wants_filter_year = st.sidebar.toggle('Quer filtrar por ano?', disabled=False)
        if wants_filter_year:
            picked_year = st.sidebar.slider('Escolha um ano', min_value=int(self.min_year), max_value=int(self.max_year), value=(int(self.min_year), int(self.max_year)), step=1) #Escolhe o ano
            self.anos = list(range(picked_year[0], picked_year[1] +1)) # Gera os números dentro do intervalo (tipo 2022 até 2024+1)


    def carregamento_tratamento_arquivos(self, arquivos):
        if 'dfs' not in st.session_state:
            st.session_state['dfs'] = {
                'mot_cat': pd.DataFrame(), 
                'tcles': {'tcle': pd.DataFrame(), 'pre_tcle': pd.DataFrame()},
                'pcts': pd.DataFrame()
            }

        if 'arquivos_processados' not in st.session_state:
            st.session_state['arquivos_processados'] = []

        if arquivos:
            arquivos_novos = [arquivo.name for arquivo in arquivos]

            arquivos_removidos = list(set(st.session_state['arquivos_processados']) - set(arquivos_novos))
            if arquivos_removidos:
                for arquivo_removido in arquivos_removidos:
                    self.remover_dados_arquivo(arquivo_removido)

            for arquivo in arquivos:
                if arquivo.name not in st.session_state['arquivos_processados']:
                    st.session_state['arquivos_processados'].append(arquivo.name)
                    temp_dfs = {
                        'mot_cat': pd.DataFrame(), 
                        'tcles': {'tcle': pd.DataFrame(), 'pre_tcle': pd.DataFrame()},
                        'pcts': pd.DataFrame()
                    }
                    temp_dfs = SCR_treats.tratamento_dados(arquivo, temp_dfs)

                # Concatenando os DataFrames ao 'st.session_state' se eles não forem vazios
                    if not temp_dfs['mot_cat'].empty:
                        st.session_state['dfs']['mot_cat'] = pd.concat([st.session_state['dfs']['mot_cat'], temp_dfs['mot_cat']], ignore_index=True)
                    if not temp_dfs['tcles']['tcle'].empty:
                        st.session_state['dfs']['tcles']['tcle'] = pd.concat([st.session_state['dfs']['tcles']['tcle'], temp_dfs['tcles']['tcle']], ignore_index=True)
                    if not temp_dfs['tcles']['pre_tcle'].empty:
                        st.session_state['dfs']['tcles']['pre_tcle'] = pd.concat([st.session_state['dfs']['tcles']['pre_tcle'], temp_dfs['tcles']['pre_tcle']], ignore_index=True)
                    if not temp_dfs['pcts'].empty:
                        st.session_state['dfs']['pcts'] = pd.concat([st.session_state['dfs']['pcts'], temp_dfs['pcts']], ignore_index=True)
                        st.session_state['dfs']['pcts'] = st.session_state['dfs']['pcts'].drop_duplicates(subset=['Nome'], keep='first')

        return st.session_state['dfs']


    def remover_dados_arquivo(self, arquivo_nome):
        """Função para remover os dados associados a um arquivo removido do session_state."""

        st.session_state['dfs']['mot_cat'] = st.session_state['dfs']['mot_cat'][st.session_state['dfs']['mot_cat']['fonte'] != arquivo_nome]
        
        st.session_state['dfs']['tcles']['tcle'] = st.session_state['dfs']['tcles']['tcle'][st.session_state['dfs']['tcles']['tcle']['fonte'] != arquivo_nome]
        st.session_state['dfs']['tcles']['pre_tcle'] = st.session_state['dfs']['tcles']['pre_tcle'][st.session_state['dfs']['tcles']['pre_tcle']['fonte'] != arquivo_nome]
        
        st.session_state['dfs']['pcts'] = st.session_state['dfs']['pcts'][st.session_state['dfs']['pcts']['fonte'] != arquivo_nome]

        if arquivo_nome in st.session_state['arquivos_processados']:
            st.session_state['arquivos_processados'].remove(arquivo_nome)


    def carregar_dataframes(self):
        '''Função para atribuir os dataframes do `st.session_state[dfs]` 
        às variáveis pra melhor legibilidade nos códigos de gráfico'''

        self.df_Mot_Cat = st.session_state['dfs']['mot_cat']
        self.df_TCLE_agrupado = st.session_state['dfs']['tcles']['tcle']
        self.df_Pré_TCLE = st.session_state['dfs']['tcles']['pre_tcle']
        self.df_Espera_Total_pcts, self.df_Dados_relatorio = SCR_treats.gerar_dataframes(st.session_state['dfs']['tcles']['tcle'])
        self.df_Pacientes = st.session_state['dfs']['pcts']

# Tab1 - Indicadores de Falha
    def grafs_analise_falha_tab1(self):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Gráfico de Contagem de Motivos por Categoria')

        with col2:
            st.subheader('Gráfico de Contagem de Motivos por Estudo')

        col1, col2 = st.columns(2)
        with col1:
            pie_chart_motivos_mes_ano = SCR_charts.pie_chart_motivos(dataframe=self.df_Mot_Cat, meses=self.meses, anos=self.anos)
            if pie_chart_motivos_mes_ano != None:
                st.plotly_chart(pie_chart_motivos_mes_ano)
                st.info('O filtro de data é com base na "Data de falha"')
            else:
                st.error('Não há dados no período selecionado.')

        with col2:
            bar_chart_estudos_p_motivo_mes_ano = SCR_charts.bar_chart_contagem_motivo_estudos(dataframe=self.df_Mot_Cat, meses=self.meses, anos=self.anos)
            if bar_chart_estudos_p_motivo_mes_ano != None:
                st.plotly_chart(bar_chart_estudos_p_motivo_mes_ano)
                st.info('O filtro de data é com base na "Data de falha"')
            else:
                st.error('Não há dados deste estudo no período escolhido.')

        st.divider()


    def grafs_analise_esp_tab1(self):
        lista_estudos_status_combinados = self.df_TCLE_agrupado['Estudo'].unique()
    
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            estudos_selecionados_tab1 = st.multiselect('Selecione um estudo', lista_estudos_status_combinados,max_selections=1, key='scr_tab1', placeholder='Escolha um estudo')
        
            if not estudos_selecionados_tab1:
                st.warning('Selecione um estudo para visualizar o gráfico.')
                st.empty()
            else:
                selecao_estudo_tab1 = estudos_selecionados_tab1[0]

        with col2, col3, col4:
            st.empty()

# ------------------- Gráfico de barras Motivos/Categorias por estudo
        col1, col2, col3 = st.columns([0.33, 0.33, 0.33])
        with col1:
            if estudos_selecionados_tab1:
                st.subheader(f'Número de Ocorrências por Categoria em :blue[{selecao_estudo_tab1}]')

                bar_chart_motivos_por_estudo_mes_ano = SCR_charts.bar_chart_contagem_categoria_em_estudo(dataframe=self.df_Mot_Cat, estudo_selecionado=selecao_estudo_tab1, anos=self.anos, meses=self.meses, altura=400, largura=600)
                if bar_chart_motivos_por_estudo_mes_ano != None:
                    st.plotly_chart(bar_chart_motivos_por_estudo_mes_ano)
                    st.info('O filtro de data é com base na "Data de falha"')
                else:
                    st.error('Não há dados deste estudo no período escolhido.')

# ------------------- Gráfico de rosca Status pacientes por estudo (Status pcts TCLE principal)
        with col2:
            if estudos_selecionados_tab1:
                st.subheader(f'Status pacientes no estudo :blue[{selecao_estudo_tab1}] - TCLE principal')

                pie_chart_porcentagem_status_pcts_mes_ano = SCR_charts.pie_chart_porcentagem_status_pcts(dataframe=self.df_TCLE_agrupado, estudo=selecao_estudo_tab1, meses=self.meses, anos=self.anos, altura=300, largura=650)
                if pie_chart_porcentagem_status_pcts_mes_ano != None:
                    st.plotly_chart(pie_chart_porcentagem_status_pcts_mes_ano)
                    st.info('O filtro de data é com base na "Data limite - Rando"')
                else:
                    st.error('Não há dados deste estudo no período escolhido.')
                    st.empty()

# ------------------- Gráfico de rosca Status pacientes por estudo (Status pcts PRÉ-TCLE)
        with col3:
            if estudos_selecionados_tab1:  
                st.subheader(f'Status pacientes no estudo :blue[{selecao_estudo_tab1}] - Pré-TCLE')

                pré_pie_chart_porcentagem_status_pcts_mes_ano = SCR_charts.pie_chart_porcentagem_status_pcts(dataframe=self.df_Pré_TCLE, estudo=selecao_estudo_tab1, meses=self.meses, anos=self.anos, altura=300, largura=650)
                if pré_pie_chart_porcentagem_status_pcts_mes_ano != None:
                    st.plotly_chart(pré_pie_chart_porcentagem_status_pcts_mes_ano)
                    st.info('O filtro de data é com base na "Data assinatura"')
                else:
                    st.error('Não há dados deste estudo no período escolhido.')
                    st.empty()

        st.divider()                    


    def grafs_cat_falha_no_estudo_tab1(self):
        lista_categoria_selecionada = self.df_Mot_Cat['Categoria'].unique()

        col1, col2 = st.columns([0.22, 0.68])
        with col1:
            categoria_selecionada = st.multiselect('Selecione uma categoria', lista_categoria_selecionada, max_selections=1, placeholder='Escolha uma categoria', key='SCR_Mot_Cat')
            if not categoria_selecionada:
                st.warning('Selecione uma categoria para visualizar o gráfico')
                st.empty()
            else:
                selecao_categoria_tab1 = categoria_selecionada[0]

        with col2:
            st.empty()

        if categoria_selecionada:
            bar_chart_motivo_em_estudo_mes_ano = SCR_charts.bar_chart_motivo_em_estudo(dataframe=self.df_Mot_Cat, categoria_especifica=selecao_categoria_tab1, anos=self.anos, meses=self.meses)
            if bar_chart_motivo_em_estudo_mes_ano != None:
                st.plotly_chart(bar_chart_motivo_em_estudo_mes_ano)
            else:
                st.error('Não há dados deste estudo nas condições escolhidas')
                st.empty()

# Tab2 - Mensurar Tempo de Screening
    def grafs_pizza_meta_tab2(self):
        pie_chart_meta_atingida_mes_ano = SCR_charts.pie_chart_meta_atingida(
            dataframe=self.df_Espera_Total_pcts, 
            estudos_tempo_scr=self.selecao_tempo_de_scr, 
            anos=self.anos, meses=self.meses, meta=self.meta_selecionada
        )

        if pie_chart_meta_atingida_mes_ano != None:
            st.plotly_chart(pie_chart_meta_atingida_mes_ano)
            st.info('O filtro de data é com base na "Data Assinatura"')
        else:
            st.error('Não há dados deste estudo no período escolhido.')

        
        if not self.selecao_tempo_de_scr or not pie_chart_meta_atingida_mes_ano:
            st.empty() # Para evitar de aparecer texto quando não há seleção alguma

        else:            
            st.write('Pacientes que atingiram a meta são aqueles que randomizaram em um tempo menor ou igual a meta.')
            st.info(f'Meta aplicada atualmente: {self.meta_selecionada} dias.')


    def grafs_tempo_corrido_estudo_tab2(self):
        bar_chart_tempo_medio = SCR_charts.bar_chart_tempo_medio(
            dataframe=self.df_Espera_Total_pcts,
            estudos_tempo_scr=self.selecao_tempo_de_scr,
            anos=self.anos, meses=self.meses, meta=self.meta_selecionada
        )
        
        if bar_chart_tempo_medio != None:
            st.plotly_chart(bar_chart_tempo_medio, use_container_width=False)
            st.info('O filtro de data é com base na "Data assinatura"')
        else:
            st.error('Não há dados deste estudo no período escolhido.')

# Tab3 - Panorama Assinaturas
    def graf_distr_inic_scr_tab3(self):
        pcts_inicio_triagem = SCR_treats.get_inicio_triagem(dataframe=self.df_Dados_relatorio, anos=self.anos, meses=self.meses)
        bar_chart_inicio_triagem = SCR_charts.bar_chart_inicio_triagem(dados=pcts_inicio_triagem)
        try:
            st.plotly_chart(bar_chart_inicio_triagem)
        except Exception as e:
            st.error(f'Ops! Alguma coisa deu errado: {e}')

    
    def graf_distr_pct_mes_escolhido_tab3(self):
        '''Este gráfico retorna os desfechos dos pacientes no mês selecionado e somente quando há um mês.
        Do contrário, retornará os pacientes em andamento atualmente e quando eles assinaram/começaram o screening'''

        relatorio_final = SCR_treats.gerar_dados_rel_completo(dados_relatorio=self.df_Dados_relatorio, anos=self.anos, meses=self.meses)
        bar_chart_acompanhamento_completo = SCR_charts.bar_chart_acompanhamento_completo(relatorio_final, anos=self.anos, meses=self.meses)
        try:
            st.plotly_chart(bar_chart_acompanhamento_completo)
            st.info('O filtro de data é com base na "Data assinatura" (andamentos) e "Data da falha" (randomizados/falhas)')
        except Exception as e:
            st.error(f'Ops! Alguma coisa deu errado: {e}')


    def graf_status_pct_x_estudo_princ_tab3(self):
        bar_chart_status_estudo_principal = SCR_charts.bar_chart_status_estudo(dataframe=self.df_TCLE_agrupado, meses=self.meses, anos=self.anos)
        if bar_chart_status_estudo_principal != None:
            st.plotly_chart(bar_chart_status_estudo_principal)
            st.info('O filtro de data é com base na "Data limite - Rando"')
        else:
            st.error('Não há dados no período selecionado.')


    def graf_status_pct_x_estudo_pre_tab3(self):
        bar_chart_status_estudo_pre = SCR_charts.bar_chart_status_estudo(dataframe=self.df_Pré_TCLE, meses=self.meses, anos=self.anos)
        if bar_chart_status_estudo_pre != None:
            st.plotly_chart(bar_chart_status_estudo_pre)
            st.info('O filtro de data é com base na "Data assinatura"')
        else:
            st.error('Não há dados no período selecionado.')


    def filtros_opcionais_tcles_tab3(self):
        self.lista_estudos_assinaturas_tcle = self.df_TCLE_agrupado['Estudo'].unique().tolist()
        self.lista_estudos_assinaturas_pre = self.df_Pré_TCLE['Estudo'].unique().tolist()

        self.estudos_princ = self.lista_estudos_assinaturas_tcle
        self.estudos_pre = self.lista_estudos_assinaturas_pre

        self.estudos_tab3_princ = None
        self.estudos_tab3_pre = None

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            wants_study = st.toggle('Quer filtrar por estudo específico?', key='AssXMedXStatusBox')
        with col2, col3, col4: 
            st.empty()
        
        if wants_study:
            col1, col2 = st.columns(2)
            with col1:
                selecao_estudos_assinaturas_princ = st.multiselect('Escolha um estudo para filtrar', self.estudos_princ, placeholder='Escolha os estudos', key='AssXMedXStatusPrinc')            
                self.estudos_tab3_princ = selecao_estudos_assinaturas_princ

            with col2:
                selecao_estudos_assinaturas_pre = st.multiselect('Escolha um estudo para filtrar', self.estudos_pre, placeholder='Escolha os estudos', key='AssXMedXStatusPre')
                self.estudos_tab3_pre = selecao_estudos_assinaturas_pre


    def graf_assinatura_x_med_x_status_pct_princ_tab3(self):
        bar_chart_assinaturas_medicos_estudo_status_principal = SCR_charts.bar_chart_assinaturas_medicos_estudo_status(dataframe=self.df_TCLE_agrupado, estudos=self.estudos_tab3_princ, meses=self.meses, anos=self.anos)
        if bar_chart_assinaturas_medicos_estudo_status_principal != None:
            st.plotly_chart(bar_chart_assinaturas_medicos_estudo_status_principal)
            st.info('O filtro de data é com base na "Data limite - Rando"')
        else:
            st.error('Não há dados nas condições selecionadas.')

    
    def graf_assinatura_x_med_x_status_pct_pre_tab3(self):
        bar_chart_assinaturas_medicos_estudo_status_pre = SCR_charts.bar_chart_assinaturas_medicos_estudo_status(dataframe=self.df_Pré_TCLE, estudos=self.estudos_tab3_pre, meses=self.meses, anos=self.anos)
        if bar_chart_assinaturas_medicos_estudo_status_pre != None:
            st.plotly_chart(bar_chart_assinaturas_medicos_estudo_status_pre)
            st.info('O filtro de data é com base na "Data assinatura"')
        else:
            st.error('Não há dados nas condições selecionadas.')


    def filtros_opcionais_ass_med_tab3(self):
        col1, col2, col3 = st.columns([0.35, 0.35, 0.65])
        with col1:
            self.selecao_estudos_assinaturas_princ = st.multiselect('Escolha estudos para filtrar', self.lista_estudos_assinaturas_tcle, placeholder='Escolha pelo menos um estudo', key='MotMedEstPrinc') 
            if self.selecao_estudos_assinaturas_princ:
                self.estudo_assinatura_princ = self.selecao_estudos_assinaturas_princ[0]
        with col2:
            self.lista_opcoes_medicos_princ = self.df_Mot_Cat['Médico que assinou'].unique().tolist()
            self.lista_medicos_princ = st.multiselect('Escolha um médico', self.lista_opcoes_medicos_princ, max_selections=1, placeholder='Selecione um médico', key='ListMedMotMedEstPrinc')
            if self.lista_medicos_princ:
                self.selecao_medico_princ = self.lista_medicos_princ[0]
        
        with col3:
            st.info('O gráfico de motivos/categorias já é um compilado tanto do Principal quanto do Pré. A fim de evitar redundância ou confusões, separá-los não é eficiente.')


    def graf_mot_cat_x_med_tab3(self):
        pie_chart_motivos_medico_estudo_princ = SCR_charts.pie_chart_motivos(dataframe=self.df_Mot_Cat, estudo=self.selecao_estudos_assinaturas_princ, medico=self.selecao_medico_princ, anos=self.anos, meses=self.meses, show_value_label=True)
        if pie_chart_motivos_medico_estudo_princ != None:
            st.plotly_chart(pie_chart_motivos_medico_estudo_princ)
            st.info('O filtro de data é com base na "Data da falha"')
            
        else:
            st.error('Não há dados nas condições selecionadas.')


    def graf_cont_falhas_x_med_x_estudo_tab3(self):
        if self.lista_medicos_princ:
            st.subheader(f'Número de falhas em estudos onde Dr(a). :violet[{self.selecao_medico_princ}] acompanhou')
            bar_chart_falha_estudo_medico = SCR_charts.bar_chart_falha_estudo_medico(dataframe=self.df_Mot_Cat, medico=self.selecao_medico_princ, anos=self.anos, meses=self.meses)
            if bar_chart_falha_estudo_medico != None:
                st.plotly_chart(bar_chart_falha_estudo_medico)
                st.info('O filtro de data é com base na "Data da falha"')
            else:
                st.error('Não há dados nas condições selecionadas.')

# Tab4 - Relatorios
    def graf_rando_do_mes_tab4(self):
        randomizados_do_mes = SCR_charts.relatorio_randomizados_do_mes(dataframe=self.df_TCLE_agrupado, df_pacientes=self.df_Pacientes, meses=self.meses, anos=self.anos, download=False)
        if randomizados_do_mes != None:
            st.plotly_chart(randomizados_do_mes)
        else:
            st.error('Não há dados nestas condição')


    def graf_panorama_rando_do_mes_tab4(self):
        panorama_randomizados_do_mes = SCR_charts.panorama_randomizados_do_mes(dataframe=self.df_TCLE_agrupado, meses=self.meses, anos=self.anos)
        if panorama_randomizados_do_mes != None:
            st.plotly_chart(panorama_randomizados_do_mes)
        else:
            st.error('Não há dados nestas condição')

    
    def graf_panorama_inicio_triagem_tab4(self):
        pcts_inicio_triagem_panorama = SCR_treats.get_inicio_triagem(dataframe=self.df_Dados_relatorio, anos=self.anos, meses=self.meses)
        bar_chart_inicio_triagem_panorama = SCR_charts.bar_chart_inicio_triagem(dados=pcts_inicio_triagem_panorama)
        try:
            st.plotly_chart(bar_chart_inicio_triagem_panorama, key='triagem2')
        except Exception as e:
            st.error(f'Ops! Alguma coisa deu errado: {e}')


    def relatorio_mensal_tab4(self):
        hoje = datetime.datetime.today()
        mes_atual, ano_atual = hoje.month, hoje.year

        tipo = st.segmented_control("🔍 Selecione o tipo de estudo:", options=['Ambos', 'Onco', 'Multi'], index=0, horizontal=True, selection_mode='single')
        tipo_label = None if tipo == 'Ambos' else tipo

        resumo_tcle, resumo_pre, cat_tcle, cat_pre = SCR_treats.gerar_relatorio_mes(
            self.df_TCLE_agrupado, self.df_Pré_TCLE, self.df_Mot_Cat, [mes_atual], [ano_atual], tipo_label)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📄 Resumo TCLE")
            st.dataframe(resumo_tcle)

        with col2:
            st.subheader("📄 Resumo Pré-TCLE")
            st.dataframe(resumo_pre)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("❌ Categorias de Falha - TCLE")
            with st.expander('Ver tabela'):
                st.dataframe(cat_tcle)

        with col2:
            st.subheader("❌ Categorias de Falha - Pré-TCLE")
            with st.expander('Ver tabela'):
                st.dataframe(cat_pre)

        st.info('Com exceção dos pacientes :orange[em andamento], todos os outros campos da tabela são baseados na "Data da falha/rando"')
        st.info('Se a conta não está fechando, verifique se as datas foram preenchidas corretamente na planilha, pois alguns campos possui autopreenchimento para preservar filtros.')

# Tab5 - Tabelas
    def mostrar_dataframes(self):
        with st.expander('Compilado Motivos/Categorias'):
            st.dataframe(self.df_Mot_Cat)
            st.info('Os filtros de data são aplicados na "Data da falha"')

        with st.expander('Dados TCLE Principal Agrupado'):
            st.dataframe(self.df_TCLE_agrupado)
            st.info('Os filtros de data são aplicados na "Data assinatura"')
    
        with st.expander('Pré-TCLE'):
            st.dataframe(self.df_Pré_TCLE)
            st.info('Os filtros de data são aplicados na "Data assinatura"')
        
        with st.expander('Espera total'):
            st.dataframe(self.df_Espera_Total_pcts)
            st.info('A média de tempo corrido aparece "repetida" por questões programáticas, mas é este valor único.')
            st.info('Os filtros de data são aplicados na "Data assinatura"')
        
        with st.expander('Dados relatorio de desfechos'):
            st.dataframe(self.df_Dados_relatorio)
            st.info('Os filtros de data são aplicados na "Data assinatura"')
        
        with st.expander('Pacientes'):
            st.dataframe(self.df_Pacientes)
            st.info('Pacientes com :orange[Nomes] iguais foram excluídos.')

# Mostrar conteúdo
    def tab1(self):
        st.header('Análise das falhas de cada estudo')
        self.grafs_analise_falha_tab1()

        st.header('Análise em estudo específico')
        self.grafs_analise_esp_tab1()

        st.header('Análise de Categoria de falha entre os estudos')
        self.grafs_cat_falha_no_estudo_tab1()


    def tab2(self):
        st.header('Tempo de Triagem e Metas')
        # Configuração das opções de seleção para o gráfico de pizza
        col1, col2, col3 = st.columns(3)
        with col1:      
            self.lista_estudos_tempo_scr = self.df_TCLE_agrupado['Tempo de SCR (dias)'].unique()
            self.selecao_tempo_de_scr = st.pills('Filtro por tempo de SCR', selection_mode='multi', options=self.lista_estudos_tempo_scr, default=self.lista_estudos_tempo_scr, key='lista_estudos_tempo_scr')
        
            if len(self.selecao_tempo_de_scr) == 1:
                self.meta_selecionada = int(round(self.selecao_tempo_de_scr[0] * 0.95, 0))
            else:
                self.meta_selecionada = int(round(self.meta * 0.95, 0))

        with col2:
            if len(self.selecao_tempo_de_scr) > 1:
                    st.warning('Para ver a linha de meta no gráfico de barras, por favor selecione somente um tempo de triagem.')

        with col3:
            st.empty()

        # Gráfico de pizza
        col1, col2 = st.columns([0.32, 0.7], gap='large')
        with col1:
            st.subheader('Meta atingida x Meta não atingida')
            
            if not self.selecao_tempo_de_scr:
                st.error('Por favor, selecione pelo menos um tempo de screening.')
            
            self.grafs_pizza_meta_tab2()

        with col2:
            st.subheader('Média de tempo corrido por estudo')

            if not self.selecao_tempo_de_scr:
                st.error('Por favor, selecione pelo menos um tempo de screening.')
            
            else:
                self.grafs_tempo_corrido_estudo_tab2()


    def tab3(self):
        st.header('Panorama geral das assinaturas, estudos e médicos')
        st.info('''Quando há :orange[somente um mês selecionado], você poderá ver os Randomizados, 
            os que Falharam e os que estão em andamento. Do :orange[contrário], será mostrado todos os :orange[pacientes em andamento atualmente].''')
        
        col1, col2 = st.columns([0.4, 0.6], gap='large')
        with col1:
            st.subheader('Distribuição do Início de Triagem')
            self.graf_distr_inic_scr_tab3()
        
        with col2:
            st.subheader('Distribuição dos pacientes na perspectiva do mês selecionado!')
            self.graf_distr_pct_mes_escolhido_tab3()

        st.divider()
# ------------------------------------------------------------------------------------ #
        st.header('Panorama Estudos')
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Status pacientes X Estudo - Principal')
            self.graf_status_pct_x_estudo_princ_tab3()
        
        with col2:
            st.subheader('Status pacientes X Estudo - Pré')
            self.graf_status_pct_x_estudo_pre_tab3()

        st.divider()
# ------------------------------------------------------------------------------------ #
        st.header('Panorama médicos')
        self.filtros_opcionais_tcles_tab3()

        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Assinaturas X Médico + Status pacientes - Principal')
            self.graf_assinatura_x_med_x_status_pct_princ_tab3()

        with col2:
            st.subheader('Assinaturas X Médico + Status pacientes - Pré')
            self.graf_assinatura_x_med_x_status_pct_pre_tab3()

# ------------------------------------------------------------------------------------ #
        st.subheader('Motivos falha X Médico X Estudo')
        self.filtros_opcionais_ass_med_tab3()

        col1, col2, col3 = st.columns([0.35, 0.35, 0.65])
        with col1:
            if not self.selecao_estudos_assinaturas_princ:
                st.warning('Selecione um estudo, por favor.')
        
        with col2:
            if not self.lista_medicos_princ:
                st.warning('Selecione um médico, por favor.')
        
        with col3:
            st.empty()

        col1, col2 = st.columns([0.4, 0.6])
        with col1:
            if self.selecao_estudos_assinaturas_princ and self.lista_medicos_princ:
                if len(self.selecao_estudos_assinaturas_princ) > 1:
                    estudos_separados = [f'{selecao_estudos_assinaturas_princ}' for selecao_estudos_assinaturas_princ in self.selecao_estudos_assinaturas_princ]
                    st.subheader(f'Falhas em :blue[{", ".join(estudos_separados)}] onde Dr(a). :violet[{self.selecao_medico_princ}] acompanhou')
                else:
                    st.subheader(f'Falhas em :blue[{self.estudo_assinatura_princ}] onde Dr(a). :violet[{self.selecao_medico_princ}] acompanhou')

                self.graf_mot_cat_x_med_tab3()

        with col2:
            self.graf_cont_falhas_x_med_x_estudo_tab3()


    def tab4(self):
        st.header('Baixe relatórios úteis para divulgar suas métricas 😁')

        self.relatorio_mensal_tab4()
        self.graf_rando_do_mes_tab4()
        self.graf_panorama_rando_do_mes_tab4()
        self.graf_panorama_inicio_triagem_tab4()


    def tab5(self):
        st.header('Fontes de dados')
        st.subheader('Estas são as planilhas geradas com os dados fornecidos.')
        st.write('Você pode fazer o download delas, caso queira, passando o mouse na tabela abaixo e clicando na setinha ↓')
        st.write('Os filtros :orange[não funcionam] nesta parte da página.')
        self.mostrar_dataframes()


if __name__ == "__main__":
    Screening()