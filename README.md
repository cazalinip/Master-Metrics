# Descrição
Este é um dashboard interativo desenvolvido com Streamlit que permite a visualização de métricas importantes da instituição. A aplicação permite aos usuários fazer upload de planilhas específicas (somente arquivos da instituição) e gerar gráficos dinâmicos com base nos dados carregados. Além disso, o sistema de autenticação via Google garante que apenas usuários autenticados e autorizados possam acessar as informações sensíveis, com a possibilidade de download de relatórios específicos.
- Atenção: Este repositório e a aplicação são privados e destinados apenas a usuários autorizados.


# Funcionalidades
- Autenticação via Google: Login seguro com a conta do Google, utilizando a API de autenticação do Streamlit.
- Whitelist de e-mails: Apenas e-mails autorizados têm acesso à aplicação.
- Upload de arquivos: Possibilidade de fazer upload de arquivos .xlsx contendo dados específicos da instituição.
- Visualização de gráficos dinâmicos: Geração de gráficos interativos com Plotly Express baseados nos dados carregados.
- Download de relatórios: Funcionalidade de download de gráficos específicos que são frequentemente requisitados.


# Como rodar o projeto localmente
**Pré-requisitos**
- Python 3.8+
- Streamlit
- Plotly (para criação dos gráficos dinâmicos)
- Pandas (para manipulação de dados)
- Outras dependências listadas no arquivo requirements.txt


# Como usar o aplicativo
- 1. Ao acessar a página inicial, faça login com sua conta do Google. Apenas e-mails na whitelist terão acesso ao conteúdo.
- 2. Após a autenticação, você será redirecionado para a página onde pode fazer o upload de um arquivo .xlsx contendo os dados da instituição.
- 3. O aplicativo gerará gráficos dinâmicos baseados nesses dados, utilizando o Plotly Express.


# Segurança
- **Autenticação via Google:** Apenas usuários com e-mails autorizados (na whitelist) podem acessar o aplicativo.
- **Validação de e-mails:** Somente e-mails do Gmail são permitidos para login.
- **Proteção contra upload de arquivos maliciosos:** O sistema valida os arquivos carregados para garantir que eles sejam seguros e no formato esperado.


# Contribuindo
**Este projeto é privado**, e não há contribuições externas planejadas por enquanto.

# Licença
Este projeto é de **uso exclusivo do Núcleo de Pesquisa e Ensino IBCC e não é open-source. Licença privada**.
