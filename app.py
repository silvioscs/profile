import streamlit as st
import requests
from pypdf import PdfReader
import os

# 1. Configurações e Segurança
try:
    # Carrega a chave do arquivo .streamlit/secrets.toml
    API_KEY = st.secrets["GEMINI_API_KEY"]
    # Imprime no terminal para verificação (pode apagar esta linha depois)
    print(f"Chave carregada: {API_KEY[:5]}...{API_KEY[-5:]}")
except KeyError:
    st.error("Chave de API não encontrada. Configure o arquivo .streamlit/secrets.toml com a variável GEMINI_API_KEY.")
    st.stop()

# URL atualizada para o modelo 2.5 Flash
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

st.set_page_config(page_title="Silvio AI", page_icon="📊")

# 2. Leitura do PDF
@st.cache_data
def get_pdf_text(file_path):
    if not os.path.exists(file_path):
        return "Arquivo perfil.pdf não encontrado."
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"Erro ao ler PDF: {e}"

pdf_context = get_pdf_text("perfil.pdf")

# 3. Interface
st.title("Silvio AI")
st.markdown("*Pergunte-me como te ajudar com FP&A. Como é uma versão gratuita de AI, faça perguntas com 4 palavras no máximo.*")
st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Chamada via API Direta
if prompt := st.chat_input("Pergunte algo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"Você é o Silvio (Head de FP&A). Responda de forma executiva e com números em negrito.\n\nContexto: {pdf_context}\n\nPergunta: {prompt}"
                    }]
                }]
            }
            
            response = requests.post(URL, json=payload)
            response_json = response.json()
            
            if response.status_code == 200:
                answer = response_json['candidates'][0]['content']['parts'][0]['text']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error(f"Erro na API: {response_json}")
                
        except Exception as e:
            st.error(f"Erro técnico: {e}")
