# Importando a biblioteca Streamlit
import streamlit as st

# Função para carregar o CSS externo
def load_css():
    try:
        with open("style.css", "r") as f:
            css = f.read()  # Lê o conteúdo do arquivo CSS
        # Aplica o CSS diretamente ao HTML da página
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
      #  st.write("CSS carregado corretamente!")  # Mensagem para confirmar o carregamento
    except FileNotFoundError:
        st.error("Arquivo CSS não encontrado! Verifique se o arquivo 'style.css' está na mesma pasta que o seu código Python.")

# Carregando o CSS
load_css()

# Título do site
st.markdown('<h1 class="titulo">Doces Lalumare 🍨</h1>', unsafe_allow_html=True)

# Criando um menu lateral
st.sidebar.header("Escolha seu Açaí")
tamanho = st.sidebar.selectbox("Tamanho:", ["Pequeno", "Médio", "Grande"])
adicionais = st.sidebar.multiselect(
    "Adicionais:", 
    ["Leite em pó", "Granola", "Paçoca", "Banana", "Morango", "Leite condensado"]
)

preco_base = {"Pequeno": 10, "Médio": 15, "Grande": 20}
preco_final = preco_base[tamanho] + len(adicionais) * 2

# Exibindo o pedido com um bloco estilizado
st.markdown('<div class="pedido">', unsafe_allow_html=True)
st.write(f"**Você escolheu um açaí {tamanho} com:**")
for adicional in adicionais:
    st.write(f"✔️ {adicional}")
st.write(f"**Preço total: R$ {preco_final},00**")
st.markdown('</div>', unsafe_allow_html=True)

# Botão de confirmação
if st.button("Confirmar Pedido"):
    st.success("Pedido realizado com sucesso! 🍨")
