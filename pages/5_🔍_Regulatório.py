import streamlit as st
import assets.Regulatorio.Reg_Charts as r_charts
import assets.Regulatorio.Reg_Treats as r_treats
import datetime
import re
import pandas as pd
from progress_bar import ProgressBar
from checar_login import ChecarAutenticacao
import time

url_plan_reg = st.secrets['urls']["PLAN_REG"]


class Regulatorio():
    def __init__(self):
        ChecarAutenticacao()
        
        if 'setor' not in st.session_state:
            st.switch_page('1_🏠_Homepage.py')
        
        elif st.session_state['setor'] not in st.secrets['permissions']['PERM_REG']:
            st.warning('Você não tem acesso à esta página. Troque de conta ou converse com o administrador.')
            if st.button('Trocar de conta'):
                st.logout()
                   
        else:
            st.title('Regulatório')
            st.subheader('Distribuição de tempo entre as diversas etapas!')

            self.upload_arquivo()
            
            self.tabs = [':orange[Delta tempos]', ' ']
            tab1, tab2 = st.tabs(self.tabs)
            
            self.valor_padrao_filtros()

            with tab1:
                self.tab1()
            
            with tab2:
                st.empty()


    def upload_arquivo(self):
        arquivo = st.file_uploader(
            'Faça upload da planilha de Indicadores Regulatório aqui!',
            type='xlsx',
            key='plan_reg',
            help='Faça download da planilha e insira-a aqui!'
        )

        if not arquivo:
            st.link_button('Indicadores Regulatório', url=url_plan_reg)
            st.session_state['dados_regulatorio'] = None

        elif st.session_state['dados_regulatorio'] is None:
            try:
                st.session_state['dados_regulatorio'] = r_treats.calcular_tempos(arquivo)
            except Exception as e:
                st.error(f'Erro de processamento! Por favor, verifique se o arquivo enviado é o correto.\n\n{e}')

        # 🔁 Aqui é o ponto chave: define df e df_original sempre que houver dados válidos
        if st.session_state['dados_regulatorio'] is not None:
            self.df_original = st.session_state['dados_regulatorio'].copy()
            self.df = self.df_original.copy()
        else:
            self.df_original = pd.DataFrame()
            self.df = pd.DataFrame()
        
    def valor_padrao_filtros(self):
        '''Configurando os atributos padrão dos gráficos'''
        self.meses = list(range(1,13))

        self.df = None
        self.filtros = None

        self.today = datetime.date.today().year
        self.anos = [self.today]

        self.max_year = self.anos[0] if self.df == None else self.df['Data de Solicitação '].dt.year.max()
        self.min_year = 2024 if self.df == None else self.df['Data de Solicitação '].dt.year.min()
    
    def filtros_opcionais(self):
        if st.session_state['dados_regulatorio'] is not None:
            self.aplicar_filtro_mes_ano()
                
            opcoes_pi = self.df['PI'].unique().tolist()
            opcoes_pi.sort()
            opcoes_pi = [re.sub(r'^(Dr\.|Dra\.)\s*', '', name, flags=re.IGNORECASE) for name in opcoes_pi]

            opcoes_estudo = self.df['Estudo'].unique().tolist()
            opcoes_estudo.sort()
            
            opcoes_patrocinador = self.df['Patrocinador'].unique().tolist()
            opcoes_patrocinador.sort()
            
            opcoes_sub = ['Todos', 'Emenda', 'Sub. Inicial']
            
            opcoes_status = self.df['Status'].unique().tolist()
            opcoes_status.sort()
            opcoes_status.insert(0, 'Todos')

            if st.sidebar.toggle('Aplicar filtros', key='toggle_filter_reg'):
                self.filtros = {
                    'PI': st.sidebar.multiselect("PI", opcoes_pi),
                    'Estudo': st.sidebar.multiselect("Estudo", opcoes_estudo),
                    'Patrocinador': st.sidebar.multiselect("Patrocinador", opcoes_patrocinador),
                    'Pendências?': st.sidebar.pills("Pendências", ['Todos', 'Sim', 'Não'], default='Todos', key='pills_pend_reg'),
                    'Tipo de Submissão': st.sidebar.pills('Tipo de submissão', opcoes_sub, default='Todos'),
                    'Implementação?': st.sidebar.pills('Implementação', ['Todos', 'Sim', 'Não'], default='Todos', key='pills_impl_reg'),
                    'Status': st.sidebar.pills('Status', opcoes_status, default='Todos'),
                    'Centro Coordenador?': st.sidebar.pills('Centro Coordenador', ['Todos', 'Sim', 'Não'], default='Todos', key='pills_cent_reg')
                }
                self.df = self.aplicar_filtros_no_df(self.df, **self.filtros)

        else:
            st.empty()


    def aplicar_filtros_no_df(self, df, **filtros):
        for coluna, valor in filtros.items():
            if valor not in [None, '', 'Todos']:
                if coluna == 'PI':
                    pis = '|'.join(item for item in valor if item not in [None, '', 'Todos'])
                    df = df[df[coluna].str.contains(pis, case=False, na=False)]

                elif coluna == 'Tipo de Submissão':
                    df = df[df[coluna].str.contains(valor)]

                elif len(valor)>0:
                    if isinstance(valor, list):
                        df = df[df[coluna].isin(valor)]
                    else:
                        df = df[df[coluna] == valor]

        return df

    def aplicar_filtro_mes_ano(self):
        meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        opcoes_meses = list(range(1, 13))
        mes_format = lambda x: "Todos" if x == 0 else meses_nomes[x - 1]

        # 0 representará a opção "Todos"
        mes_opcoes_display = [0] + opcoes_meses
        default_mes = [datetime.date.today().month]

        mes_selecionados = st.sidebar.pills(
            'Mês para comparação',
            mes_opcoes_display,
            format_func=mes_format,
            default=default_mes,
            selection_mode='multi'
        )

        anos_disponiveis = sorted(self.df_original['Data de Solicitação'].dt.year.unique(), reverse=True)
        ano_selecionado = st.sidebar.selectbox('Ano para comparação', anos_disponiveis, index=0)

        # Salva os filtros de mês/ano para as métricas depois
        self.ano_esc = ano_selecionado
        self.mes_esc = opcoes_meses if 0 in mes_selecionados else mes_selecionados

        # Aplicar filtro no self.df

        self.df = self.df[self.df['Data de Solicitação'].dt.year == self.ano_esc]
        if self.mes_esc:
            self.df = self.df[self.df['Data de Solicitação'].dt.month.isin(self.mes_esc)]


    def grafico_dossie_e_tempo_total(self, dataframe):
        chart_dossie_tec, chart_tempo_total_sub = r_charts.bar_chart_dossie_tempo_total(dataframe)

        return chart_dossie_tec, chart_tempo_total_sub

    def pie_chart_pends(self, dataframe, titulo):
        pie_chart_pendencias = r_charts.pie_chart_pendencias(dataframe, titulo)
        if pie_chart_pendencias != None:
            st.plotly_chart(pie_chart_pendencias)
        else:
            st.error('Não há dados nestas condições')
            st.empty()


    def separar_df_mes_atual_e_anterior(self, df_base, meses_atual, ano_atual, filtros_laterais_opcionais=None):
        if df_base.empty:
            return pd.DataFrame(), pd.DataFrame()

        df_base = df_base.copy()
        df_base['Data de Solicitação'] = pd.to_datetime(df_base['Data de Solicitação'], errors='coerce')
        df_base['mes'] = df_base['Data de Solicitação'].dt.month
        df_base['ano'] = df_base['Data de Solicitação'].dt.year

        df_atual = df_base[(df_base['mes'].isin(meses_atual)) & (df_base['ano'] == ano_atual)]

        if len(meses_atual) == 1:
            mes_atual = meses_atual[0]
            if mes_atual == 1:
                mes_anterior = 12
                ano_anterior = ano_atual - 1
            else:
                mes_anterior = mes_atual - 1
                ano_anterior = ano_atual

            df_anterior = df_base[(df_base['mes'] == mes_anterior) & (df_base['ano'] == ano_anterior)]

        else:
            df_anterior = pd.DataFrame()  # vazio → sem delta

        if filtros_laterais_opcionais is not None:
        # Aplicar os filtros da sidebar, criados com o self.filtros_opcionais(), nos dataframes pós seleção de mes/ano
        # Caso apenas um mês selecionado → calcular delta
            df_atual = self.aplicar_filtros_no_df(df_atual, **filtros_laterais_opcionais)
            df_anterior = self.aplicar_filtros_no_df(df_anterior, **filtros_laterais_opcionais) if not df_anterior.empty else pd.DataFrame()

        return df_atual, df_anterior

    def mostrar_metricas(self, df_atual, df_anterior):
        metricas_at = r_treats.metricas_card(df_atual)
        metricas_ant = r_treats.metricas_card(df_anterior) if not df_anterior.empty else {}

        # Pares de datas para compor o help por métrica
        pares_datas = [
            ('Data de Solicitação', 'Data de Submissão', 'Tempo preparo dossiê técnico'),
            ('Data de Solicitação', 'ATIVAÇÃO', 'Tempo total de submissão inicial'), 
            ('Data de Solicitação', 'Data de Implementação', 'Tempo total de implementação de emenda'), 
            ('Data de Submissão', 'Parecer CEP', 'Tempo liberação parecer centro participante'),
            ('Data de Submissão', 'Parecer CONEP', 'Tempo liberação parecer centro coordenador'),
            ('Data de Submissão', 'Data de Aceite do PP', 'Tempo legislativo de aceitação do projeto'),
            ('Data de Aceite do PP', 'Parecer CEP', 'Tempo legislativo do parecer em centro participante'),
            ('Data de Aceite do PP', 'Parecer CONEP', 'Tempo legislativo do parecer em centro coordenador'),
            ('SIV', 'ATIVAÇÃO', 'Tempo total ativação do Estudo'), 
        ]

        # Cria um dicionário com os textos de ajuda
        explicacoes = {nome: f"{fim} - {inicio}" for inicio, fim, nome in pares_datas}

        def exibir_metricas(linhas_de_metricas):
            for linha in linhas_de_metricas:
                cols = st.columns(len(linha))
                for col, label in zip(cols, linha):
                    valor_atual = metricas_at.get(label, float('nan'))
                    valor_passado = metricas_ant.get(label, None)
                    delta = valor_atual - valor_passado if valor_passado is not None and pd.notna(valor_passado) else None

                    col.metric(
                        label=label,
                        value=f'{valor_atual:.2f} dias' if pd.notna(valor_atual) else "N/A",
                        delta=f'{delta:+.2f} dias' if delta is not None and pd.notna(delta) else None,
                        border=True,
                        delta_color='inverse',
                        help=f"Cálculo: {explicacoes.get(label, 'Fórmula não especificada')}"
                    )

        st.subheader("⏳ Médias de Tempos Importantes!")

        # Define as linhas com os nomes exatos das métricas
        linhas_de_metricas = [
            [
                'Tempo preparo dossiê técnico',
                'Tempo total de submissão inicial',
                'Tempo total de implementação de emenda'
            ],
            [
                'Tempo liberação parecer centro participante',
                'Tempo liberação parecer centro coordenador'
            ],
            [
                'Tempo legislativo do parecer em centro participante',
                'Tempo legislativo do parecer em centro coordenador'
            ],
            [
                'Tempo legislativo de aceitação do projeto',
                'Tempo total ativação do Estudo'
            ]
        ]

        exibir_metricas(linhas_de_metricas)


    def tab1(self):
        if st.session_state['dados_regulatorio'] is not None:
            self.df = st.session_state['dados_regulatorio'].copy()
            self.filtros_opcionais()
            
            dossie, tempo_total = self.grafico_dossie_e_tempo_total(self.df)
            col1, col2 = st.columns(2)

            with col1:
                if dossie is not None:
                    st.plotly_chart(dossie)
                else:
                    st.info("Não há dados nestas condições.")

            with col2:
                if tempo_total is not None:
                    st.plotly_chart(tempo_total, use_container_width=True)
                else:
                    st.info("Não há dados nestas condições.")


            self.pie_chart_pends(self.df, titulo='Distribuição de Pendências por Tipo de Centro')
            
            if self.filtros:
                df_atual, df_anterior = self.separar_df_mes_atual_e_anterior(self.df_original, self.mes_esc, self.ano_esc, self.filtros)
            else:
                df_atual, df_anterior = self.separar_df_mes_atual_e_anterior(self.df_original, self.mes_esc, self.ano_esc)
            
            if len(self.mes_esc) > 1:
                st.info('Você selecionou mais de um mês. A média será exibida, mas o delta será desativado.', icon="ℹ️")
                df_anterior = pd.DataFrame()  # zera o delta

            self.mostrar_metricas(df_atual, df_anterior)

            with st.expander('Ver planilha'):
                st.write(self.df)
                st.write(f'Registros nesta visualização: {self.df.shape[0]}')

        else:
            st.warning("Faça upload do arquivo para ver as métricas!", icon="⚠️")


if __name__ == "__main__":
    Regulatorio()
