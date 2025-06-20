import streamlit as st
import pandas as pd
import datetime
import os
import assets.Esteira_paciente.Esteira_Treats as est_treats
import assets.Esteira_paciente.Esteira_Charts as est_charts
from checar_login import ChecarAutenticacao
from progress_bar import ProgressBar


URL_SCR_REC = st.secrets['urls']['PLAN_SCR_REC']

class Esteira_Paciente():
    def __init__(self):
        ChecarAutenticacao()

        if 'setor' not in st.session_state:
            st.switch_page('1_🏠_Homepage.py')

        elif st.session_state['setor'] not in st.secrets['permissions']['PERM_REC_SCR']:
            st.warning('Você não tem acesso à esta página. Troque de conta ou converse com o administrador.')
            if st.button('Trocar de conta'):
                st.logout()

        else:
            st.title('Indicadores centralizados - Recrutamento e Screening')
            st.subheader('Acompanhe a esteira completa dos pacientes, do começo ao fim')
            self.tab1()


    def valor_padrao_filtros(self):
        '''Configurando os atributos padrão dos gráficos'''
        self.meses = list(range(1,13))

        self.today = datetime.date.today().year
        self.anos = [self.today]

        self.max_year = self.anos[0]
        self.min_year = 2024


    def filtros_opcionais(self):
        wants_filter_month = st.sidebar.toggle('Quer filtrar por mês?')
        if wants_filter_month:
            picked_month = st.sidebar.slider('Escolha um mês', min_value=1, max_value=12, value=(1,12)) #Escolhe o mês
            self.meses = list(range(picked_month[0], picked_month[1] +1)) # Gera os números dentro do intervalo (tipo 1 até 12+1)

        wants_filter_year = st.sidebar.toggle('Quer filtrar por ano?', disabled=False)
        if wants_filter_year:
            picked_year = st.sidebar.slider('Escolha um ano', min_value=int(self.min_year), max_value=int(self.max_year), value=(int(self.min_year), int(self.max_year)), step=1) #Escolhe o ano
            self.anos = list(range(picked_year[0], picked_year[1] +1)) # Gera os números dentro do intervalo (tipo 2022 até 2024+1)


    def tratar_planilha(self, arquivo):
        if st.session_state['dados_esteira'] is None:
            try:
                barra = ProgressBar()
                barra.iniciar_carregamento()
                st.session_state['dados_esteira'] = est_treats.tratar_dados_upload(arquivo)
                st.session_state['df_tempos'] = est_treats.dataframe_para_calculo_tempos(st.session_state['dados_esteira'])
                st.session_state['df_taxas'] = est_treats.dataframe_para_calculo_taxas(st.session_state['dados_esteira'])
                barra.finalizar_carregamento(emoji='🎉')
            except Exception as e:
                st.error('Erro de processamento! Por favor, verifique se o arquivo enviado é o correto.')
                st.error(f'Erro: {e}')
            

    def calculos_cards_e_graf_linhas(self, mes):
        self.contagem_total = est_treats.totais_brutos_dados(self.df_taxas, anos=self.anos)
        taxas_conversao_total = est_treats.taxas_conversao_total(self.contagem_total)

        self.taxa_elegibilidade_geral = taxas_conversao_total['taxa_elegibilidade'] 
        self.taxa_contato_geral = taxas_conversao_total['taxa_contato'] 
        self.taxa_consentimento_geral = taxas_conversao_total['taxa_consentimento']
        self.taxa_randomizacao_geral = taxas_conversao_total['taxa_randomizacao']
        
        self.df_taxas_mensais = est_treats.calcular_taxas_mensais(self.df_taxas, anos=self.anos)
        taxas_cards, diffs_cards = est_treats.taxas_cards(self.df_taxas_mensais, ano=self.anos, mes=mes)
        
        if taxas_cards is not None and diffs_cards is not None:
            self.taxa_elegibilidade_card = taxas_cards['Taxa Elegibilidade'] 
            self.taxa_contato_card = taxas_cards['Taxa Contato'] 
            self.taxa_consentimento_card = taxas_cards['Taxa Consentimento'] 
            self.taxa_randomizacao_card = taxas_cards['Taxa Randomização'] 

            self.diff_elegibilidade_card = diffs_cards['Dif_Taxa_Elegibilidade']
            self.diff_contato_card = diffs_cards['Dif_Taxa_Contato']
            self.diff_consentimento_card = diffs_cards['Dif_Taxa_Consentimento']
            self.diff_randomizacao_card = diffs_cards['Dif_Taxa_Randomizacao']


    def mostrar_cards_geral(self):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric('Taxa Elegibilidade', f'{self.taxa_elegibilidade_geral:.2%}', border=True)
        
        with col2:
            st.metric('Taxa Contato', f'{self.taxa_contato_geral:.2%}', border=True)

        with col3:
            st.metric('Taxa Consentimentos', f'{self.taxa_consentimento_geral:.2%}', border=True)

        with col4:
            st.metric('Taxa Randomizados', f'{self.taxa_randomizacao_geral:.2%}', border=True)


    def mostrar_cards_delta(self):
        try:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric('Taxa Elegibilidade', f'{self.taxa_elegibilidade_card:.2%}', delta=f'{self.diff_elegibilidade_card}', border=True)
            
            with col2:
                st.metric('Taxa Contato', f'{self.taxa_contato_card:.2%}', delta=f'{self.diff_contato_card}', border=True)

            with col3:
                st.metric('Taxa Consentimentos', f'{self.taxa_consentimento_card:.2%}', delta=f'{self.diff_consentimento_card}', border=True)

            with col4:
                st.metric('Taxa Randomizados', f'{self.taxa_randomizacao_card:.2%}', delta=f'{self.diff_randomizacao_card}', border=True)
        except:
            st.warning('Selecione somente um mês para ver os cards comparado ao mês anterior!', icon='🚨')


    def mostrar_line_chart_taxas_mensais(self):
        line_chart_taxas_mensais = est_charts.line_chart_taxas_mensais(self.df_taxas_mensais, anos=self.anos)
        if line_chart_taxas_mensais != None:
            st.plotly_chart(line_chart_taxas_mensais)
        else:
            st.error('Não há dados no período selecionado.')

    
    def mostrar_bar_chart_tempo_processo(self):
        bar_chart_medias_tempo_processo = est_charts.bar_chart_medias_tempo_processo(self.df_tempos, anos=self.anos, meses=self.meses)
        if bar_chart_medias_tempo_processo != None:
            st.plotly_chart(bar_chart_medias_tempo_processo)
        else:
            st.error('Não há dados no período selecionado.')


    def tab1(self):
        arquivo = st.file_uploader('Faça upload do excel Esteira aqui', 'xlsx')
        if not arquivo:
            st.session_state['dados_esteira'] = None
            st.session_state['df_tempos'] = None
            st.session_state['df_taxas'] = None

        elif arquivo and st.session_state['df_taxas'] is None:
            self.tratar_planilha(arquivo)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.link_button('Esteira REC-SCR', url=URL_SCR_REC)

        if st.session_state['df_taxas'] is not None:
            self.valor_padrao_filtros()
            self.filtros_opcionais()
            self.df_preenchido = st.session_state['dados_esteira']
            self.df_tempos = st.session_state['df_tempos']
            self.df_taxas = st.session_state['df_taxas']

            mes = st.pills('Selecione um mês para ver a taxa de conversão', list(range(1,13)), default=datetime.datetime.today().month)
            self.calculos_cards_e_graf_linhas(mes)
            
            st.subheader('Taxas de conversão geral do ano')
            self.mostrar_cards_geral()
            st.info('Inclua o ano anterior no filtro à esquerda, caso queira comparar os dados de janeiro')
            
            st.subheader('Taxas de conversão do mês comparado ao mês anterior')
            self.mostrar_cards_delta()
            st.info('"inf" ou "nan" significa que não há dados para aquele período, resultando em cálculo inválido, trazendo um valor inexistente. Ao atualizar a planilha, isso deve se resolver.')
            
            st.divider()
            self.mostrar_line_chart_taxas_mensais()
            st.info('Este gráfico utiliza das mesmas informações do card acima 👆')

            st.divider()
            self.mostrar_bar_chart_tempo_processo()
            st.info('O ponto de partida de todos os dados é o registro na planilha: Data Recebimento/Encaminhamento.')
            st.info('Desta forma, Elegibilidade é o tempo entre recebimento e classificação daquele paciente. O contato é o tempo entre o recebimento até o contato, e assim sucessivamente.')

            


if __name__ == "__main__":
    Esteira_Paciente()
