import streamlit as st
import re
import os
import warnings
import datetime


# Supressão de avisos conhecidas que não são um problema
def custom_warning_filter(message, category, filename, lineno, file=None, line=None):
    if "Data Validation extension is not supported" in str(message):
        return
    if "Conditional Formatting extension is not supported" in str(message):
        return
    return warnings.defaultaction

warnings.showwarning = custom_warning_filter

class HomePage():
    def __init__(self):
        self.layout = 'centered' if not self.usuario_logado() else 'wide'
        st.set_page_config(
            page_title='Master Métricas',
            page_icon= '📊',
            layout=self.layout
        )
        
        self.saudacao = st.empty()
        self.orientacao = st.empty()
        
        self.emails_permitidos = self.whitelist()
        self.autenticacao()


    def usuario_logado(self):
        '''Checar se o usuário está logado ou não'''
        if not st.user:
            return False
        return st.user['is_logged_in']
    

    def whitelist(self):
        '''Carrega e define a lista de e-mails permitidos (whitelist)'''
        try:
            emails_permitidos = st.secrets['whitelist']['emails'].split(',')
            if not emails_permitidos:
                raise ValueError('A variável de e-mails está vazia')
            return emails_permitidos
        except FileNotFoundError as e:
            print(f'[ERRO] - Whitelist não encontrada - {e}')
            st.error("Erro! E-mail não foi encontrado. Converse com o administrador.")
            return []


    def validar_email(self, email):
        '''Valida o formato do e-mail, permitindo apenas e-mails do Gmail'''
        email_regex = r'^[a-zA-Z0-9_.+-]+@gmail\.com$'
        return re.match(email_regex, email) is not None


    def verificar_email(self):
        """
        Verifica se o e-mail logado está na whitelist e se é um e-mail do Gmail.

        Esta função valida se o e-mail do usuário logado está no formato correto (somente Gmail) 
        e se está presente na lista de e-mails permitidos (whitelist).

        Args:
            Nenhum.

        Returns:
            bool: Retorna `True` se o e-mail está na whitelist e é do Gmail.
                Retorna `False` se o e-mail não estiver na whitelist ou não for do Gmail.
        
        Exemplo:
            - Se o e-mail for "usuario@gmail.com" e estiver na whitelist, retorna `True`.
            - Se o e-mail for "usuario@yahoo.com" ou não estiver na whitelist, retorna `False`.
        """
        email = st.user['email']
        if not self.validar_email(email):
            st.error('E-mail inválido.')
            return False            

        return email in self.emails_permitidos


    def resgatar_dados_usuario(self):
        '''Resgatar e formatar os dados do usuário logado através do uso da `st.user`'''
        nome = st.user['given_name']
        foto = st.user['picture']
        email = st.user['email']

        setor = email.split('@')[0].split('.')[0].capitalize()
        setor_formatado = re.match(r'^[a-zA-Z]+', setor)
        setor_final = setor_formatado.group(0)

        st.session_state['setor'] = setor_final  

        return nome, foto, email, setor_final


    def autenticacao(self):
        '''Chama todas as outras funções para autenticar o usuário, conferindo o email e resgatando seus dados.
        Após a autenticação do usuário e conferência do e-mail, o conteúdo do site é apresentado/mostrado.'''

        if self.usuario_logado() == False:
            self.saudacao.title('Bem vindo!')
            self.orientacao.subheader('Por favor, autentique-se com o botão abaixo.')

            if st.button('Autenticar'):
                st.login('google')

        elif self.verificar_email():
            self.mostrar_conteudo()
            print(f"[LOGIN] - [{datetime.datetime.today().strftime("%d-%m-%Y %H:%M:%S")}] {st.session_state['setor']}")

        else:
            self.email_nao_permitido()


    def mostrar_conteudo(self):
        '''Conteúdo da página a ser mostrado somente para os usuários permitidos e autenticados.'''
        nome, foto, email, setor = self.resgatar_dados_usuario()
        st.set_option('client.showSidebarNavigation', True)
        self.saudacao = st.empty()
        self.orientacao = st.empty()


        st.title(f'Seja bem vindo, {setor}')
        st.subheader('Aqui o sucesso começa.')

        st.divider()

        col1, col2 = st.columns([0.1, 0.9])
        with col1:
            st.image(foto)
        
        with col2:
            st.write(f'Seu nome: {nome}')
            st.write(f'Seu email: {email}')
            st.write(f'Seu setor e privilegios: {setor}')


        if st.sidebar.button('Sair da conta'):
            st.logout()

        if st.sidebar.button("Cadê as páginas?"):
            st.rerun()


    def email_nao_permitido(self):
        '''Alerta o usuário que o email não está na whitelist, oferencendo a opção de logar em outra conta'''
        st.subheader('Ops! Parece que este e-mail não está permitido na organização.')
        st.write('Isso pode acontecer se estiver com uma conta de e-mail não listada. Converse com o administrador.')
        if st.button('Tentar outra conta'):
            st.login('google')


if __name__ == "__main__":
    HomePage()
    