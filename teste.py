# acai_app.py

import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

# --- Banco de dados ---
try:
    from banco import inserir_cliente, inserir_pedido, inserir_produtos
    DB_ATIVO = True
except ImportError:
    DB_ATIVO = False

# --- Configurações Globais ---
USUARIO_PROPRIETARIO = "admin"
SENHA_PROPRIETARIO = "1234"
NUMERO_TELEFONE = "5511999998888"

# --- Função: Dashboard ---
def exibir_dashboard():
    st.title("\U0001F4CA Dashboard de Vendas")
    st.markdown("Bem-vindo ao painel de controle da **Doces Lalumare**!")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Vendas", "R$ 1.250,00")
    col2.metric("Pedidos no Mês", "42")
    col3.metric("Ticket Médio", "R$ 29,76")

    st.subheader("\U0001F4C8 Vendas da Semana")
    df_vendas = pd.DataFrame({
        "Dia": ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"],
        "Vendas (R$)": [120, 150, 90, 180, 200, 240, 210]
    })
    st.bar_chart(df_vendas.set_index("Dia"))

    st.subheader("\U0001F944 Adicionais Mais Pedidos")
    df_adicionais = pd.DataFrame({
        "Adicional": ["Morango", "Leite Condensado", "Granola Tradicional", "Mousse Ninho", "Paçoca", "Kit Kat", "Bis", "Trento"],
        "Quantidade de Pedidos": [28, 25, 18, 32, 20, 15, 12, 10]
    })
    st.bar_chart(df_adicionais.set_index("Adicional"))

    st.subheader("\U0001F4CB Últimos Pedidos")
    st.table(pd.DataFrame({
        "Cliente": ["Ana", "Carlos", "Beatriz"],
        "Data": ["20/04", "20/04", "19/04"],
        "Valor": ["R$ 18,00", "R$ 20,00", "R$ 21,50"]
    }))

# --- Estilo CSS ---
st.markdown("""
    <style>
        .stApp { background-color: #F2BBC5; }
        section[data-testid="stSidebar"] { background-color: #FFFFFF; }
        h1, h2, h3 { color: #732C4D !important; }
        .stTextInput label,
        .stSelectbox label,
        .stRadio label,
        .stMultiselect label,
        p, label, .stRadio > div {
            color: #732C4D !important;
        }
        .stTextInput input,
        .stSelectbox select,
        .stMultiselect div {
            color: white !important;
        }
        button[kind="primary"], button[kind="secondary"] {
            background-color: #4c122d !important;
            color: white !important;
            border-radius: 8px;
        }
        button[kind="primary"] *, button[kind="secondary"] * {
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar: Login ---
st.sidebar.image("Logo.jpg", width=300)
st.sidebar.markdown("<div style='margin-bottom: 230px;'></div>", unsafe_allow_html=True)

if "logado" not in st.session_state:
    st.session_state.logado = False

with st.sidebar:
    st.markdown("### \U0001F464 Área do Proprietário")
    if not st.session_state.logado:
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if usuario == USUARIO_PROPRIETARIO and senha == SENHA_PROPRIETARIO:
                st.session_state.logado = True
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
    else:
        st.success("Você está logado como proprietário.")
        if st.button("Sair"):
            st.session_state.logado = False
            st.rerun()

# --- Se logado, exibir dashboard ---
if st.session_state.logado:
    exibir_dashboard()
    st.stop()

# --- Parte do Cliente: Pedido ---
st.title("Monte aqui o seu açaí \U0001F368")

adicionais_inclusos = [
    "Mousse Ninho", "Mousse Ovomaltine", "Mousse Limão", "Mousse Amendoim",
    "Mousse Morango", "Uva", "Banana", "Morango", "Kiwi", "Amendoim",
    "Granola Tradicional", "Leite Condensado", "Leite em Pó", "Mel",
    "Paçoca", "Castanha de Caju", "Cobertura Caramelo",
    "Cobertura Chocolate", "Cobertura Morango"
]
adicionais_extras = {
    "Bis": 2.00, "Kit Kat": 2.50, "Confete": 2.00,
    "Nescau Ball": 2.00, "Trento": 2.50
}
tamanhos = {
    "300ml - R$18,00": {"min": 3, "max": 4, "preco": 18.00},
    "500ml - R$20,00": {"min": 3, "max": 6, "preco": 20.00}
}

# --- Sessão inicial ---
for key in ["tamanho", "adicionais_selecionados", "adicionais_extras_selecionados"]:
    if key not in st.session_state:
        st.session_state[key] = [] if "adicionais" in key else ""

# --- Interface do Pedido ---
tamanho = st.selectbox("Escolha o tamanho do copo:", [""] + list(tamanhos.keys()), index=0)
regras = tamanhos.get(tamanho, {"min": 0, "max": 0, "preco": 0.0})

adicionais_disabled = tamanho == ""
if adicionais_disabled:
    st.warning("Selecione o tamanho do copo antes de adicionar ingredientes.")

incl = st.multiselect("Adicionais inclusos:", adicionais_inclusos, disabled=adicionais_disabled)
ext = st.multiselect("Adicionais extras:", [f"{k} - R${v:.2f}" for k,v in adicionais_extras.items()], disabled=adicionais_disabled)

st.session_state.tamanho = tamanho
st.session_state.adicionais_selecionados = incl
st.session_state.adicionais_extras_selecionados = [s.split(" - ")[0] for s in ext]

# --- Dados do Cliente ---
nome = st.text_input("Nome completo:")
whatsapp = st.text_input("WhatsApp (formato: (DDD) 91234-5678):")
forma_pagamento = st.radio("Forma de pagamento:", ["Cartão", "Dinheiro", "PIX"], index=None)
troco = st.text_input("Troco para quanto?") if forma_pagamento == "Dinheiro" else "N/A"
tipo_pedido = st.radio("Tipo:", ["Retirada", "Entrega"], index=None)
endereco = st.text_input("Endereço para entrega:") if tipo_pedido == "Entrega" else "Cliente irá retirar no local"

# --- Validações ---
min_add, max_add = regras["min"], regras["max"]
total_add = len(incl) + len(st.session_state.adicionais_extras_selecionados)
erro_limite = not (min_add <= total_add <= max_add)
valor_total = regras["preco"] + sum(adicionais_extras[n] for n in st.session_state.adicionais_extras_selecionados)

# --- Resumo ---
st.markdown("## \U0001F9FE Resumo do Pedido")

st.markdown(f"""
<div style='background-color: #fff; padding: 20px; border-radius: 12px; color: #000;'>
<p><strong>Copo:</strong> {tamanho}</p>
<p><strong>Adicionais:</strong> {'<br>'.join(incl)}</p>
<p><strong>Extras:</strong> {'<br>'.join(st.session_state.adicionais_extras_selecionados)}</p>
<p><strong>Nome:</strong> {nome}</p>
<p><strong>WhatsApp:</strong> {whatsapp}</p>
<p><strong>Forma de pagamento:</strong> {forma_pagamento}</p>
<p><strong>Troco:</strong> {troco}</p>
<p><strong>Tipo:</strong> {tipo_pedido}</p>
<p><strong>Endereço:</strong> {endereco}</p>
<p><strong>Valor Total:</strong> R$ {valor_total:.2f}</p>
</div>
""", unsafe_allow_html=True)

# --- Confirmação ---
if st.button("✅ Confirmar Pedido", disabled=erro_limite or not tamanho):
    if not nome or not whatsapp or not forma_pagamento or not tipo_pedido or (tipo_pedido == "Entrega" and not endereco):
        st.error("Preencha todos os campos obrigatórios.")
    else:
        if DB_ATIVO:
            try:
                id_cliente = inserir_cliente(nome, whatsapp, endereco)
                numero_pedido = f"PED-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                id_pedido = inserir_pedido(id_cliente, 1, numero_pedido, f"{valor_total:.2f}", "Recebido", forma_pagamento, tipo_pedido, total_add)
                produtos = [(a, 1, 0.0, 'un') for a in incl] + [(e, 1, adicionais_extras[e], 'un') for e in st.session_state.adicionais_extras_selecionados]
                inserir_produtos(id_pedido, produtos)
                st.success("Pedido salvo no banco de dados!")
            except Exception as e:
                st.error(f"Erro ao salvar no banco: {e}")

        mensagem = f"""
Oi! Gostaria de fazer um pedido :)
Nome: {nome}
WhatsApp: {whatsapp}
Endereço: {endereco}
Forma de pagamento: {forma_pagamento}
Copo: {tamanho}
Adicionais: {', '.join(incl)}
Extras: {', '.join(st.session_state.adicionais_extras_selecionados)}
Total: R$ {valor_total:.2f}
Troco: {troco}
"""
        url = f"https://wa.me/{NUMERO_TELEFONE}?text={urllib.parse.quote(mensagem)}"
        st.success("Redirecionando para o WhatsApp...")
        st.markdown(f"<meta http-equiv='refresh' content='1;url={url}'>", unsafe_allow_html=True)

if st.button("Limpar Pedido"):
    for k in ["tamanho", "adicionais_selecionados", "adicionais_extras_selecionados"]:
        st.session_state[k] = [] if "adicionais" in k else ""
    st.rerun()
