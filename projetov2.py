import streamlit as st
import pandas as pd
import urllib.parse
from banco import inserir_cliente, inserir_pedido, inserir_produto
from datetime import datetime

# -----------------------------------
# Variáveis Globais
# -----------------------------------
USUARIO_PROPRIETARIO = "admin"
SENHA_PROPRIETARIO = "1234"
NUMERO_TELEFONE = "5519998661470"

# -----------------------------------
# DASHBOARD DO PROPRIETÁRIO
# -----------------------------------
def exibir_dashboard():
    st.title("📊 Dashboard de Vendas")
    st.markdown("Bem-vindo ao painel de controle da **Doces Lalumare**!")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Vendas", "R$ 1.250,00")
    col2.metric("Pedidos no Mês", "42")
    col3.metric("Ticket Médio", "R$ 29,76")

    st.subheader("📈 Vendas da Semana")
    df = pd.DataFrame({
        "Dia": ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"],
        "Vendas (R$)": [120, 150, 90, 180, 200, 240, 210]
    })
    st.bar_chart(df.set_index("Dia"))

    st.subheader("🥄 Adicionais Mais Pedidos")
    dados_adicionais = {
        "Morango": 28,
        "Leite Condensado": 25,
        "Granola Tradicional": 18,
        "Mousse Ninho": 32,
        "Paçoca": 20,
        "Kit Kat": 15,
        "Bis": 12,
        "Trento": 10
    }
    df_adicionais = pd.DataFrame(list(dados_adicionais.items()), columns=["Adicional", "Quantidade de Pedidos"])
    st.bar_chart(df_adicionais.set_index("Adicional"))

    st.subheader("📋 Últimos Pedidos")
    st.table(pd.DataFrame({
        "Cliente": ["Ana", "Carlos", "Beatriz"],
        "Data": ["20/04", "20/04", "19/04"],
        "Valor": ["R$ 18,00", "R$ 20,00", "R$ 21,50"]
    }))

# -----------------------------------
# ESTILIZAÇÃO E LOGIN
# -----------------------------------
st.markdown("""
<style>
    .stApp { background-color: #F2BBC5; }
    section[data-testid="stSidebar"] { background-color: #FFFFFF; }
    h1, h2, h3 { color: #732C4D !important; }
    p, label, .stRadio > div { color: #732C4D !important; }
    .stTextInput input, .stSelectbox select, .stRadio label, .stMultiselect div { color: white !important; }
    button[kind="primary"], button[kind="secondary"] {
        background-color: #4c122d !important; color: white !important;
        border: none; border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.image("Logo.jpg", width=300)
st.sidebar.markdown("<div style='margin-bottom: 230px;'></div>", unsafe_allow_html=True)

if "logado" not in st.session_state:
    st.session_state.logado = False

with st.sidebar:
    st.markdown("### 👤 Área do Proprietário")
    if not st.session_state.logado:
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar") and usuario == USUARIO_PROPRIETARIO and senha == SENHA_PROPRIETARIO:
            st.session_state.logado = True
            st.success("Login realizado com sucesso!")
            st.rerun()
    else:
        st.success("Você está logado como proprietário.")
        if st.button("Sair"):
            st.session_state.logado = False
            st.rerun()

# -----------------------------------
# ÁREA PÚBLICA - PEDIDOS
# -----------------------------------
if not st.session_state.logado:
    st.title("Monte aqui o seu açaí 🍨")

    adicionais_inclusos = [
        "Mousse Ninho", "Mousse Ovomaltine", "Mousse Limão", "Mousse Amendoim",
        "Mousse Morango", "Uva", "Banana", "Morango", "Kiwi", "Amendoim",
        "Granola Tradicional", "Leite Condensado", "Leite em Pó", "Mel",
        "Paçoca", "Castanha de Caju", "Cobertura Caramelo", "Cobertura Chocolate",
        "Cobertura Morango"
    ]
    adicionais_extras = {
        "Bis": 2.00,
        "Kit Kat": 2.50,
        "Confete": 2.00,
        "Nescau Ball": 2.00,
        "Trento": 2.50
    }

    tamanhos = {
        "300ml - R$18,00": {"min": 3, "max": 4, "preco": 18.00},
        "500ml - R$20,00": {"min": 3, "max": 6, "preco": 20.00}
    }
    for key in ["tamanho_select", "nome_input", "whatsapp_input", "forma_pagamento_radio", "troco_input", "tipo_pedido_radio", "endereco_input"]:
        st.session_state.setdefault(key, "" if "radio" not in key else None)

    tamanho = st.selectbox("Escolha o tamanho do copo:", ["", *tamanhos.keys()], key="tamanho_select")
    regras = tamanhos.get(tamanho, {"min": 0, "max": 0, "preco": 0.00})
    min_ad, max_ad, valor_base = regras["min"], regras["max"], regras["preco"]

    adicionais_disabled = not tamanho
    st.subheader("Escolha seus adicionais")
    sel_inclusos = st.multiselect("Adicionais inclusos", adicionais_inclusos, disabled=adicionais_disabled)
    sel_extras = st.multiselect("Adicionais extras (pagos)", [f"{k} - R${v:.2f}" for k,v in adicionais_extras.items()], disabled=adicionais_disabled)
    st.session_state.adicionais_selecionados = sel_inclusos
    st.session_state.adicionais_extras_selecionados = [x.split(" - ")[0] for x in sel_extras]

    erro_limite = not (min_ad <= len(st.session_state.adicionais_selecionados + st.session_state.adicionais_extras_selecionados) <= max_ad)
    if erro_limite:
        st.error(f"Você deve selecionar entre {min_ad} e {max_ad} adicionais.")

    st.subheader("Dados do cliente")
    nome = st.text_input("Nome:", key="nome_input")
    whatsapp = st.text_input("WhatsApp:", key="whatsapp_input")
    forma_pagamento = st.radio("Pagamento:", ["Cartão","Dinheiro","PIX"], key="forma_pagamento_radio")
    troco = st.text_input("Troco para quanto?", key="troco_input") if forma_pagamento=="Dinheiro" else "N/A"
    tipo_pedido = st.radio("Tipo do pedido:", ["Retirada","Entrega"], key="tipo_pedido_radio")
    endereco = st.text_input("Endereço:", key="endereco_input") if tipo_pedido=="Entrega" else "N/A"

    # Cálculo valores e formatação
    valor_extras = sum(adicionais_extras[a] for a in st.session_state.adicionais_extras_selecionados)
    valor_total = valor_base + valor_extras
    adicionais_formatados = "".join([f"<br> - {a}" for a in st.session_state.adicionais_selecionados])
    extras_formatados = "".join([f"<br> - {a} (R${adicionais_extras[a]:.2f})" for a in st.session_state.adicionais_extras_selecionados])

    # ------------------------------
    # RESUMO DO PEDIDO (FORMATAÇÃO ATUALIZADA)
    # ------------------------------
    resumo_html = f"""
    <div style="background-color:#ffffff; padding:20px; border-radius:12px; border:1px solid #ddd; box-shadow:2px 2px 8px rgba(0,0,0,0.1); margin-top:10px; color:#000;">
        <p><strong>🍨 Tamanho:</strong> {tamanho or 'Não selecionado'}</p>
        <p><strong>✔️ Adicionais Inclusos:</strong><br>{adicionais_formatados or '- Nenhum'}</p>
        <p><strong>➕ Adicionais Extras:</strong><br>{extras_formatados or '- Nenhum'}</p>
        <hr style="border-top:1px solid #ccc;">
        <p><strong>😎 Cliente:</strong> {nome or 'Não informado'}</p>
        <p><strong>📱 WhatsApp:</strong> {whatsapp or 'Não informado'}</p>
        <p><strong>💳 Pagamento:</strong> {forma_pagamento or 'Não selecionado'}</p>
        <p><strong>💰 Troco:</strong> {troco or 'Não informado'}</p>
        <p><strong>🛵 Tipo de Pedido:</strong> {tipo_pedido or 'Não selecionado'}</p>
        <p><strong>📌 Endereço:</strong> {endereco or 'Não informado'}</p>
        <hr style="border-top:1px solid #ccc;">
        <p style="font-size:18px;"><strong>🟢 Valor Total:</strong> <span style="color:green;">R$ {valor_total:.2f}</span></p>
    </div>
    """
    st.markdown(resumo_html, unsafe_allow_html=True)

    # CONFIRMAR PEDIDO
    if st.button("✅ Confirmar Pedido", disabled=erro_limite or not tamanho):
        if not nome or not whatsapp or (tipo_pedido=="Entrega" and endereco=='N/A'):
            st.error("Preencha todos os campos obrigatórios.")
        else:
            try:
                cpf = '000.000.000-00'
                cliente_id = inserir_cliente(cpf, nome, whatsapp, endereco)
                pedido_id = inserir_pedido(cliente_id, 1, f"PD{datetime.now().strftime('%Y%m%d%H%M%S')}", valor_total, "Recebido", forma_pagamento, tipo_pedido, datetime.now(), 1)
                inserir_produto(pedido_id, "Açaí", 1, valor_total, "un")
            except Exception as e:
                st.error(f"Erro ao salvar pedido: {e}")
                st.stop()
            msg = f"Ola! Gostaria de fazer um pedido 😀\n..."
            url = f"https://api.whatsapp.com/send?phone={NUMERO_TELEFONE}&text={urllib.parse.quote_plus(msg)}"
            st.success("Pedido realizado! Redirecionando...")
            st.markdown(f"<meta http-equiv='refresh' content='1;url={url}'>", unsafe_allow_html=True)

    # LIMPAR
    if st.button("Limpar Pedido"):
        for k in list(st.session_state.keys()):
            if any(x in k for x in ['input','radio','select']):
                st.session_state[k] = None if 'radio' in k else ''
        st.rerun()

else:
    exibir_dashboard()
