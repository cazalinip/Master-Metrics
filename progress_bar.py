import streamlit as st
import time
import random

class ProgressBar():
    def __init__(self, sidebar=False):
        self.progress_text = 'Analisando este arquivo...'
        
        if sidebar:
            self.my_bar = st.sidebar.progress(0, self.progress_text)
        else:
            self.my_bar = st.progress(0, self.progress_text)

        # Lista de emojis que podem ser usados
        self.emojis = [
            '🕵️‍♂️', '🔍', '🤔', '💡', '📂', '📊', '🧑‍💻', '🧐', '🧩', '🚀', '⚙️', '📈'
        ]

    
    def escolher_emoji(self):
        return random.choice(self.emojis)


    def iniciar_carregamento(self, progress_text=None, emoji=None):
        
        if progress_text:
            self.progress_text = progress_text

        if not emoji:
            emoji = self.escolher_emoji()

        # Simula progresso inicial da barra
        for percent_complete in range(16):
            time.sleep(0.05)
            self.my_bar.progress(percent_complete + 1, text=f'{self.progress_text} {emoji}')
        
        time.sleep(0.5)

    
    def finalizar_carregamento(self, progress_text=None, emoji=None):

        if progress_text:
            self.progress_text = progress_text
        else:
            self.progress_text = 'Finalizado!'

        if not emoji:
            emoji = self.escolher_emoji()

        for percent_complete in range(100):
            time.sleep(0.01)
            self.my_bar.progress(percent_complete + 1, text=f'{self.progress_text} {emoji}')
        
        time.sleep(0.5)
        self.my_bar.empty()
