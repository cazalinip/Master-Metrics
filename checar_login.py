import streamlit as st


class ChecarAutenticacao():
    def __init__(self):
        if not self.usuario_logado():
            st.set_option('client.showSidebarNavigation', False)
            st.switch_page('1_🏠_Homepage.py')
        else:
            st.set_option('client.showSidebarNavigation', True)
            st.set_page_config(layout='wide')

    def usuario_logado(self):
        '''Checar se o usuário está logado ou não'''
        return st.user['is_logged_in']
    

    def resgatar_setor(self):
        if 'setor' not in st.session_state or st.session_state['setor'] == None:
            return False
        
        return True