#
import streamlit as st
import pandas as pd
import urllib.parse
from banco import inserir_cliente, inserir_pedido, inserir_produtos
from datetime import datetime

# -----------------------------------
# DASHBOARD (área do proprietário)
# -----------------------------------
def exibir_dashboard():
    st.title("📊 Dashboard de Vendas")
    st.markdown("Bem-vindo ao painel de controle da **Doces Lalumare**!")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Vendas", "R$ 1.250,00")
    col2.metric("Pedidos no Mês", "42")
    col3.metric("Ticket Médio", "R$ 29,76")

    st.subheader("📈 Vendas da Semana")
    dados = {
        "Dia": ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"],
        "Vendas (R$)": [120, 150, 90, 180, 200, 240, 210]
    }
    df = pd.DataFrame(dados)
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
# CUSTOMIZAÇÃO DA PÁGINA (CSS)
# -----------------------------------
st.markdown(
    """
    <style>
        .stApp { background-color: #F2BBC5; }
        section[data-testid="stSidebar"] { background-color: #FFFFFF; }
        h1, h2, h3 { color: #732C4D !important; }
        .stSidebar .css-1lsbznw { color: #ffffff; }
        .stTextInput label,
        .stSelectbox label,
        .stRadio label,
        .stMultiselect label { color: #ffffff; }
        p, label, .stRadio > div { color: #732C4D !important; }
        .stTextInput input,
        .stSelectbox select,
        .stRadio label,
        .stMultiselect div { color: white !important; }
        button[kind="primary"], button[kind="secondary"] {
            background-color: #4c122d !important;
            color: white !important;
            border: none;
            border-radius: 8px;
        }
        button[kind="primary"] *, button[kind="secondary"] * {
            color: white !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.image("Logo.jpg", width=300)
st.sidebar.markdown("<div style='margin-bottom: 230px;'></div>", unsafe_allow_html=True)

USUARIO_PROPRIETARIO = "admin"
SENHA_PROPRIETARIO = "1234"

if "logado" not in st.session_state:
    st.session_state.logado = False

with st.sidebar:
    st.markdown("### 👤 Área do Proprietário")

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

    adicionais_inclusos = [
        "Mousse Ninho", "Mousse Ovomaltine", "Mousse Limão", "Mousse Amendoim", "Mousse Morango", "Uva", "Banana", "Morango", "Kiwi", "Amendoim", "Granola Tradicional",
        "Leite Condensado", "Leite em Pó", "Mel", "Paçoca", "Castanha de Caju", "Cobertura Caramelo", "Cobertura Chocolate", "Cobertura Morango"
    ]

    adicionais_extras = {
        "Bis": 2.00, "Kit Kat": 2.50, "Confete": 2.00,
        "Nescau Ball": 2.00, "Trento": 2.50
    }

    opcoes_inclusos = list(adicionais_inclusos)
    opcoes_extras = [f"{nome} - R${preco:.2f}" for nome, preco in adicionais_extras.items()]

for key in ["tamanho", "adicionais_selecionados", "adicionais_extras_selecionados"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key == "tamanho" else []

if st.session_state.logado:
    exibir_dashboard()
else:
    st.title("Monte aqui o seu açaí 🍨")
    tamanho_opcao = st.selectbox("Escolha o tamanho do copo:", ["", "300ml - R$18,00", "500ml - R$20,00"],
                                  index=0 if st.session_state.tamanho == "" else ["", "300ml - R$18,00", "500ml - R$20,00"].index(st.session_state.tamanho))
    if tamanho_opcao != st.session_state.tamanho:
        st.session_state.tamanho = tamanho_opcao
        st.session_state.adicionais_selecionados = []
        st.session_state.adicionais_extras_selecionados = []

    tamanhos = {
        "300ml - R$18,00": {"min": 3, "max": 4, "preco": 18.00},
        "500ml - R$20,00": {"min": 3, "max": 6, "preco": 20.00}
    }
    regras = tamanhos.get(st.session_state.tamanho, {"min": 0, "max": 0, "preco": 0.00})
    min_adicionais = regras["min"]
    max_adicionais = regras["max"]
    valor_base = regras["preco"]

    adicionais_disabled = st.session_state.tamanho == ""
    if adicionais_disabled:
        st.warning("Selecione o tamanho do copo antes de adicionar ingredientes.")

    st.subheader("Escolha seus adicionais")
    novos_adicionais_inclusos_formatados = st.multiselect("Adicionais inclusos:", opcoes_inclusos,
                                                           default=st.session_state.adicionais_selecionados,
                                                           disabled=adicionais_disabled)
    novos_adicionais_extras_formatados = st.multiselect("Adicionais extras (custo adicional):", opcoes_extras,
                                                         default=[f"{nome} - R${adicionais_extras[nome]:.2f}" for nome in st.session_state.adicionais_extras_selecionados],
                                                         disabled=adicionais_disabled)
    st.session_state.adicionais_selecionados = [nome.split(" - ")[0] for nome in novos_adicionais_inclusos_formatados]
    st.session_state.adicionais_extras_selecionados = [nome.split(" - ")[0] for nome in novos_adicionais_extras_formatados]
    total_adicionais = len(st.session_state.adicionais_selecionados) + len(st.session_state.adicionais_extras_selecionados)
    erro_limite = not (min_adicionais <= total_adicionais <= max_adicionais)
    if erro_limite:
        st.error(f"Você precisa selecionar entre {min_adicionais} e {max_adicionais} adicionais. Selecionados: {total_adicionais}")

    st.subheader("Dados do cliente")
    nome = st.text_input("Nome completo:")
    whatsapp = st.text_input("WhatsApp (formato: (DDD) 91234-5678):")
    forma_pagamento = st.radio("Forma de pagamento:", ["Cartão", "Dinheiro", "PIX"], index=None)
    troco = st.text_input("Troco para quanto?") if forma_pagamento == "Dinheiro" else ""
    tipo_pedido = st.radio("Tipo:", ["Retirada", "Entrega"], index=None)
    if tipo_pedido == "Retirada":
        st.session_state.endereco = ""
    if tipo_pedido == "Entrega":
        st.text_input("Endereço para entrega:", key="endereco")
    valor_extras = sum(adicionais_extras[nome] for nome in st.session_state.adicionais_extras_selecionados)
    valor_total = valor_base + valor_extras

    st.markdown("## 🧾 Resumo do Pedido")
    st.markdown(f"""
    <div style='background-color: #ffffff; padding: 20px; border-radius: 12px;
         border: 1px solid #ddd; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-top: 10px; color: #000000;'>
        <p><strong>🍨 Tamanho:</strong> {st.session_state.tamanho or 'Não selecionado'}</p>
        <p><strong>✔️ Adicionais Inclusos:</strong> {'<br>'.join(st.session_state.adicionais_selecionados) or 'Nenhum'}</p>
        <p><strong>➕ Adicionais Extras:</strong> {'<br>'.join(st.session_state.adicionais_extras_selecionados) or 'Nenhum'}</p>
        <br>
        <p><strong>👤 Cliente:</strong> {nome or 'Não informado'}</p>
        <p><strong>📞 WhatsApp:</strong> {whatsapp or 'Não informado'}</p>
        <br>
        <p><strong>💳 Pagamento:</strong> {forma_pagamento}</p>
        <p><strong>💰 Troco:</strong> {troco or 'N/A'}</p>
        <p><strong>🛵 Tipo de Pedido:</strong> {tipo_pedido or 'Não informado'}</p>
        <p><strong>📌 Endereço:</strong> {st.session_state.get("endereco", "Não informado")}</p>
        <br>
        <br>
        <p><strong> 🟢 Valor Total: R$ {valor_total:.2f}</p>
    </div>
    """, unsafe_allow_html=True)

    endereco = st.session_state.get("endereco", "")
    confirmar_button_disabled = erro_limite or st.session_state.tamanho == ""

    if st.button("✅ Confirmar Pedido", disabled=confirmar_button_disabled, use_container_width=True):
        if not nome or not whatsapp or not forma_pagamento or (tipo_pedido == "Entrega" and not endereco):
            st.error("Por favor, preencha todos os dados do cliente.")
        elif erro_limite:
            st.error("Quantidade de adicionais fora do limite.")
        else:
            try:
                id_cliente = inserir_cliente(nome, whatsapp, endereco)
                numero_pedido = f"PED-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                id_pedido = inserir_pedido(
                    cliente_id=id_cliente,
                    funcionario_id=1,
                    numero=numero_pedido,
                    valor=f"{valor_total:.2f}",
                    status="Recebido",
                    forma_pagamento=forma_pagamento,
                    forma_retirada=tipo_pedido,
                    qtd_total=total_adicionais
                )
                produtos = [(nome, "1", "0.00", "un") for nome in st.session_state.adicionais_selecionados]
                produtos += [(nome, "1", f"{adicionais_extras[nome]:.2f}", "un") for nome in st.session_state.adicionais_extras_selecionados]
                inserir_produtos(id_pedido, produtos)
                st.success("Pedido salvo com sucesso no banco de dados!")
            except Exception as e:
                st.error(f"Erro ao salvar no banco: {e}")

            endereco_texto = endereco if tipo_pedido == "Entrega" else "Cliente irá retirar no local"
            mensagem = f"""
Oi! Gostaria de fazer um pedido :)

Meus dados são:
- Nome: {nome}
- WhatsApp: {whatsapp}
- Endereço: {endereco_texto}
- Forma de pagamento: {forma_pagamento}

E quero um açaí com:
- Copo: {st.session_state.tamanho}
- Adicionais inclusos: {', '.join(st.session_state.adicionais_selecionados)}
- Adicionais extras: {', '.join(st.session_state.adicionais_extras_selecionados)}

Total: R$ {valor_total:.2f}

Obrigado(a)!
"""
            msg_encoded = urllib.parse.quote(mensagem)
            numero_proprietario = "5511999998888"
            link_whatsapp = f"https://wa.me/{numero_proprietario}?text={msg_encoded}"
            st.success("Estamos te redirecionando para o WhatsApp...")
            redirecionamento_html = f"""
            <meta http-equiv='refresh' content='1;url={link_whatsapp}'>
            <script>window.location.href = "{link_whatsapp}";</script>
            """
            st.markdown(redirecionamento_html, unsafe_allow_html=True)

    if st.button("Limpar Pedido"):
        for key in ["tamanho", "adicionais_selecionados", "adicionais_extras_selecionados", "nome", "forma_pagamento", "troco", "tipo_pedido", "endereco"]:
            st.session_state[key] = "" if key == "tamanho" else [] if "adicionais" in key else ""
        st.rerun()
