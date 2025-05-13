import streamlit as st
from progress_bar import ProgressBar
from checar_login import ChecarAutenticacao

class Regulatorio():
    def __init__(self):
        st.title('Regulatório')
        st.subheader('Veja as aprovações da CEP/CONEP')

        st.write('Esta página ainda está sob construção.')

        

if __name__ == "__main__":
    Regulatorio()
