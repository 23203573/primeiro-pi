import streamlit as st

st.markdown(
    """
    <style>
        /* Fundo geral do app */
        .stApp {
            background-color: #F2BBC5;
        }

        /* Cor da sidebar (lateral onde fica login/senha) */
        section[data-testid="stSidebar"] {
            background-color: #732C4D;
        }

        /* Títulos principais (h1, h2, h3) */
        h1, h2, h3 {
            color: #732C4D !important;
        }

        /* Título "Área do Usuário" */
        .stSidebar .css-1lsbznw {
            color: #ffffff;
        }

        /* Labels dos inputs ("Usuário", "Senha", etc) */
        .stTextInput label,
        .stSelectbox label,
        .stRadio label,
        .stMultiselect label {
            color: #ffffff;
        }

        /* Ajusta cor de parágrafos e texto em geral */
        p, label, .stRadio > div {
            color: #732C4D !important;
        }

        /* Área do usuário e texto branco */
        .stTextInput input,
        .stSelectbox select,
        .stRadio label,
        .stMultiselect div {
            color: white !important;
        }

        /* Botões personalizados */
        button[kind="primary"], button[kind="secondary"] {
            background-color: #4c122d !important;
            color: white !important;
            border: none;
            border-radius: 8px;
        }

        /* Garante que o texto interno dos botões também fique branco */
        button[kind="primary"] *, button[kind="secondary"] * {
            color: white !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ------------------------------
# CONFIG LOGIN DO PROPRIETÁRIO
# ------------------------------
USUARIO_PROPRIETARIO = "admin"
SENHA_PROPRIETARIO = "1234"  # Troque para uma senha segura depois

if "logado" not in st.session_state:
    st.session_state.logado = False

with st.sidebar:
    st.markdown("### 👤 Área do Proprietário")
    if not st.session_state.logado:
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if usuario == USUARIO_PROPRIETARIO and senha == SENHA_PROPRIETARIO:
                st.success("Login realizado com sucesso!")
                st.session_state.logado = True
            else:
                st.error("Usuário ou senha incorretos.")
    else:
        st.success("Você está logado como proprietário.")
        if st.button("Sair"):
            st.session_state.logado = False

# ------------------------------------
# SISTEMA DE PEDIDOS (visível a todos)
# ------------------------------------
# ------------------------------
# ADICIONAIS COM VALORES
# ------------------------------

adicionais_inclusos = {
    "Mousse Ninho": 2.00, "Mousse Ovomaltine": 3.00, "Mousse Limão": 2.00,
    "Mousse Amendoim": 2.50, "Mousse Morango": 2.50, "Uva": 2.00, "Banana": 2.00,
    "Morango": 2.50, "Kiwi": 3.50, "Amendoim": 1.50, "Granola Tradicional": 2.00,
    "Leite Condensado": 2.00, "Leite em Pó": 1.50, "Mel": 2.00, "Paçoca": 1.50,
    "Castanha de Caju": 2.00, "Cobertura Caramelo": 1.00, "Cobertura Chocolate": 1.00,
    "Cobertura Morango": 1.00
}

adicionais_extras = {
    "Bis": 2.00, "Kit Kat": 2.50, "Confete": 2.00,
    "Nescau Ball": 2.00, "Trento": 2.50
}

opcoes_inclusos = [f"{nome} - R${preco:.2f}" for nome, preco in adicionais_inclusos.items()]
mapa_inclusos = {f"{nome} - R${preco:.2f}": nome for nome, preco in adicionais_inclusos.items()}

opcoes_extras = [f"{nome} - R${preco:.2f}" for nome, preco in adicionais_extras.items()]
mapa_extras = {f"{nome} - R${preco:.2f}": nome for nome, preco in adicionais_extras.items()}

for key in ["tamanho", "adicionais_selecionados", "adicionais_extras_selecionados"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key == "tamanho" else []

# ------------------------------
# INTERFACE PRINCIPAL
# ------------------------------

st.title("Doces Lalumare 🍧")

tamanho_opcao = st.selectbox(
    "Escolha o tamanho do copo:", 
    ["", "300ml - R$18,00", "500ml - R$20,00"],
    index=0 if st.session_state.tamanho == "" else ["", "300ml - R$18,00", "500ml - R$20,00"].index(st.session_state.tamanho)
)

if tamanho_opcao != st.session_state.tamanho:
    st.session_state.tamanho = tamanho_opcao
    st.session_state.adicionais_selecionados = []
    st.session_state.adicionais_extras_selecionados = []

tamanhos = {
    "300ml - R$18,00": {"min": 3, "max": 4, "preco": 18.00},
    "500ml - R$20,00": {"min": 3, "max": 6, "preco": 20.00}
}
regras = tamanhos.get(st.session_state.tamanho, {"min": 0, "max": 0, "preco": 0.00})
min_adicionais, max_adicionais, valor_base = regras["min"], regras["max"], regras["preco"]

adicionais_disabled = st.session_state.tamanho == ""
if adicionais_disabled:
    st.warning("Selecione o tamanho do copo antes de adicionar ingredientes.")

st.subheader("Escolha seus adicionais")

novos_adicionais_inclusos_formatados = st.multiselect(
    "Adicionais inclusos:", opcoes_inclusos,
    default=[f"{nome} - R${adicionais_inclusos[nome]:.2f}" for nome in st.session_state.adicionais_selecionados],
    disabled=adicionais_disabled
)

novos_adicionais_extras_formatados = st.multiselect(
    "Adicionais extras (custo adicional):", opcoes_extras,
    default=[f"{nome} - R${adicionais_extras[nome]:.2f}" for nome in st.session_state.adicionais_extras_selecionados],
    disabled=adicionais_disabled
)

st.session_state.adicionais_selecionados = [mapa_inclusos[nome] for nome in novos_adicionais_inclusos_formatados]
st.session_state.adicionais_extras_selecionados = [mapa_extras[nome] for nome in novos_adicionais_extras_formatados]

total_adicionais = len(st.session_state.adicionais_selecionados) + len(st.session_state.adicionais_extras_selecionados)
erro_limite = not (min_adicionais <= total_adicionais <= max_adicionais)

if erro_limite:
    st.error(f"Você precisa selecionar entre {min_adicionais} e {max_adicionais} adicionais. Selecionados: {total_adicionais}")

# ------------------------------
# CAMPOS DO CLIENTe
# ------------------------------

st.subheader("Dados do cliente")
nome = st.text_input("Nome completo:")
endereco = st.text_input("Endereço para entrega:")
forma_pagamento = st.radio("Forma de pagamento:", ["Cartão", "Dinheiro"])
troco = st.text_input("Troco para quanto?") if forma_pagamento == "Dinheiro" else ""
tipo_pedido = st.selectbox("Tipo de pedido:", ["", "Entrega", "Retirada"])

# ------------------------------
# RESUMO DO PEDIDO
# ------------------------------

st.markdown("## 🧾 Resumo do Pedido")

resumo_html = f"""
<div style="background-color: #ffffff; padding: 20px; border-radius: 12px;
     border: 1px solid #ddd; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-top: 10px; color: #000000;">
    <p><strong>🍧 Tamanho:</strong> {st.session_state.tamanho or 'Não selecionado'}</p>
    <p><strong>✅ Adicionais Inclusos:</strong> {"<br>".join(st.session_state.adicionais_selecionados) or 'Nenhum'}</p>
    <p><strong>➕ Adicionais Extras:</strong> {"<br>".join(st.session_state.adicionais_extras_selecionados) or 'Nenhum'}</p>
    <p><strong>👤 Cliente:</strong> {nome or 'Não informado'}</p>
    <p><strong>📍 Endereço:</strong> {endereco or 'Não informado'}</p>
    <p><strong>💳 Pagamento:</strong> {forma_pagamento}</p>
    <p><strong>💰 Troco:</strong> {troco or 'N/A'}</p>
    <p><strong>🚚 Tipo de Pedido:</strong> {tipo_pedido or 'Não informado'}</p>
</div>
"""

st.markdown(resumo_html, unsafe_allow_html=True)

# ------------------------------
# BOTÃO DE CONFIRMAR
# ------------------------------

# Botão de limpar pedido
if st.button("Limpar Pedido"):
    # Limpa as variáveis do estado da sessão
    st.session_state.tamanho = ""  # Limpa a seleção do tamanho
    st.session_state.adicionais_selecionados = []  # Limpa os adicionais selecionados
    st.session_state.adicionais_extras_selecionados = []  # Limpa os adicionais extras selecionados
    st.session_state.nome = ""  # Limpa o nome do cliente
    st.session_state.endereco = ""  # Limpa o endereço do cliente
    st.session_state.forma_pagamento = ""  # Limpa a forma de pagamento
    st.session_state.troco = ""  # Limpa o campo de troco
    st.session_state.tipo_pedido = ""  # Limpa o tipo de pedido

    # Recarrega a aplicação para limpar o estado e os campos da interface
    st.rerun()  # Usando a função correta para reiniciar a aplicação

confirmar_button_disabled = erro_limite or st.session_state.tamanho == ""
st.button("✅ Confirmar Pedido", disabled=confirmar_button_disabled, use_container_width=True)

# -----------------------------------
# ÁREA DO PROPRIETÁRIO (requer login)
# -----------------------------------
if st.session_state.logado:
    st.markdown("---")
    st.markdown("## 🔐 Painel do Proprietário")
    st.info("Aqui você pode visualizar os pedidos, gerenciar ingredientes, ver relatórios, etc.")
    # Aqui você pode futuramente adicionar funcionalidades como:
    # - visualização de pedidos feitos
    # - exportação para Excel
    # - gestão de estoque
    # - controle de vendas por dia

    # Exemplo básico
    st.write("👷‍♂️ Área em construção...")

