import streamlit as st
import pandas as pd
import urllib.parse

# -----------------------------------
# Variáveis Globais
# -----------------------------------
USUARIO_PROPRIETARIO = "admin"
SENHA_PROPRIETARIO = "1234"  # Trocar por uma senha segura depois
NUMERO_TELEFONE = "5519998661470"

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
        /* Fundo geral do app */
        .stApp {
            background-color: #F2BBC5;
        }

        /* Cor da sidebar (lateral onde fica login/senha) */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF;
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
# LOGO DO SITE E ESPAÇAMENTO
# ------------------------------

# Imagem no topo da sidebar
st.sidebar.image("Logo.jpg", width=300)

# Espaço entre a imagem e os campos de login
st.sidebar.markdown("<div style='margin-bottom: 230px;'></div>", unsafe_allow_html=True)

# ------------------------------
# ÁREA DE LOGIN DO PROPRIETÁRIO
# ------------------------------
if "logado" not in st.session_state:
    st.session_state.logado = False

# ------------------------------------
# FORMULÁRIO DE LOGIN
# ------------------------------------
with st.sidebar:
    st.markdown("### 👤 Área do Proprietário")

    if not st.session_state.logado:
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        entrar = st.button("Entrar")

        if entrar:
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

# -------------------------------------
# SISTEMA DE PEDIDOS (visível a todos)
# -------------------------------------

    # Inicialização do estado da sessão
for key in ["tamanho", "adicionais_selecionados", "adicionais_extras_selecionados"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key == "tamanho" else []

if "tamanho_select" not in st.session_state:
    st.session_state.tamanho_select = ""
if "adicionais_selecionados" not in st.session_state:
    st.session_state.adicionais_selecionados = []
if "adicionais_extras_selecionados" not in st.session_state:
    st.session_state.adicionais_extras_selecionados = []
if "nome_input" not in st.session_state:
    st.session_state.nome_input = ""
if "forma_pagamento" not in st.session_state:
    st.session_state.forma_pagamento = None
if "forma_pagamento_radio" not in st.session_state:
    st.session_state.forma_pagamento_radio = None
if "troco_input" not in st.session_state:
    st.session_state.troco_input = ""
if "tipo_pedido_radio" not in st.session_state:
    st.session_state.tipo_pedido_radio = None
if "endereco_input" not in st.session_state:
    st.session_state.endereco_input = ""
if "limpar_pedido_solicitado" not in st.session_state:
    st.session_state.limpar_pedido_solicitado = False

# Verifica se a limpeza foi solicitada e realiza a limpeza antes de renderizar os widgets
if st.session_state.limpar_pedido_solicitado:
    st.session_state.tamanho_select = ""
    st.session_state.adicionais_inclusos_multiselect = []
    st.session_state.adicionais_extras_multiselect = []
    st.session_state.nome_input = ""
    st.session_state.whatsapp_input = ""
    st.session_state.forma_pagamento_radio = None
    st.session_state.troco_input = ""
    st.session_state.tipo_pedido_radio = None
    st.session_state.endereco_input = ""
    st.session_state.limpar_pedido_solicitado = False
    st.rerun()

# ------------------------------
# INTERFACE PRINCIPAL
# ------------------------------
if st.session_state.logado:
    exibir_dashboard()
else:
    st.title("Monte aqui o seu açaí 🍨")

    adicionais_inclusos = [
        "Mousse Ninho", "Mousse Ovomaltine", "Mousse Limão", "Mousse Amendoim", "Mousse Morango", "Uva", "Banana", "Morango", "Kiwi", "Amendoim", "Granola Tradicional",
        "Leite Condensado", "Leite em Pó", "Mel", "Paçoca", "Castanha de Caju", "Cobertura Caramelo", "Cobertura Chocolate", "Cobertura Morango"
    ]

    adicionais_extras = {
        "Bis": 2.00, "Kit Kat": 2.50, "Confete": 2.00,
        "Nescau Ball": 2.00, "Trento": 2.50
    }

    tamanhos_select = ["", "300ml - R$18,00", "500ml - R$20,00"]

    opcoes_inclusos = adicionais_inclusos
    opcoes_extras = [f"{nome} - R${preco:.2f}" for nome, preco in adicionais_extras.items()]

    tamanho_opcao = st.selectbox(
        label="Escolha o tamanho do copo:", 
        options=tamanhos_select,
        index=0 if st.session_state.tamanho_select == "" else tamanhos_select.index(st.session_state.tamanho_select),
        key="tamanho_select"    
    )

    if tamanho_opcao != st.session_state.tamanho_select:
        st.session_state.tamanho_select = tamanho_opcao
        st.session_state.adicionais_selecionados = []
        st.session_state.adicionais_extras_selecionados = []

    tamanhos = {
        "300ml - R$18,00": {"min": 3, "max": 4, "preco": 18.00},
        "500ml - R$20,00": {"min": 3, "max": 6, "preco": 20.00}
    }
    regras = tamanhos.get(st.session_state.tamanho_select, {"min": 0, "max": 0, "preco": 0.00})

    min_adicionais = regras["min"]
    max_adicionais = regras["max"]
    valor_base = regras["preco"]

    adicionais_disabled = st.session_state.tamanho_select == ""
    if adicionais_disabled:
        st.warning("Selecione o tamanho do copo antes de adicionar ingredientes.")

    st.subheader("Escolha seus adicionais")

    novos_adicionais_inclusos_formatados = st.multiselect(
        label="Adicionais inclusos:",
        options=opcoes_inclusos,
        
        default=[],
        disabled=adicionais_disabled,
        key="adicionais_inclusos_multiselect"
    )

    novos_adicionais_extras_formatados = st.multiselect(
        label="Adicionais extras (custo adicional):",
        options=opcoes_extras,
        
        default=[],
        disabled=adicionais_disabled,
        key="adicionais_extras_multiselect"
    )

    st.session_state.adicionais_selecionados = [nome.split(" - ")[0] for nome in novos_adicionais_inclusos_formatados]
    st.session_state.adicionais_extras_selecionados = [nome.split(" - ")[0] for nome in novos_adicionais_extras_formatados]

    total_adicionais = len(st.session_state.adicionais_selecionados) + len(st.session_state.adicionais_extras_selecionados)
    erro_limite = not (min_adicionais <= total_adicionais <= max_adicionais)

    if erro_limite:
        st.error(f"Você precisa selecionar entre {min_adicionais} e {max_adicionais} adicionais. Selecionados: {total_adicionais}")

    # ------------------------------
    # CAMPOS DO CLIENTE
    # ------------------------------
    st.subheader("Dados do cliente")
    nome = st.text_input("Nome completo:", key="nome_input")
    whatsapp = st.text_input("WhatsApp (formato: (xx) 91234-5678):", key="whatsapp_input")

    # forma_pagamento = st.radio("Forma de pagamento:", ["Cartão", "Dinheiro", "PIX"], index=None, key="forma_pagamento_radio")
    forma_pagamento = st.radio("Forma de pagamento:", ["Cartão", "Dinheiro", "PIX"], index=st.session_state.forma_pagamento if st.session_state.forma_pagamento in ["Cartão", "Dinheiro", "PIX"] else None, key="forma_pagamento_radio")

    # Campo do troco só aparece se a forma for "Dinheiro"
    troco = st.text_input("Troco para quanto?", key="troco_input") if forma_pagamento == "Dinheiro" else ""

    troco = "N/A" if forma_pagamento == "Cartão" or forma_pagamento == "PIX" else troco

    # tipo_pedido = st.radio("Tipo:", ["Retirada", "Entrega"], index=None)
    tipo_pedido = st.radio("Tipo:", ["Retirada", "Entrega"], index=0 if st.session_state.tipo_pedido_radio == "Retirada" else 1 if st.session_state.tipo_pedido_radio == "Entrega" else None, key="tipo_pedido_radio")
   
    endereco = st.text_input("Endereço para entrega:", key="endereco_input") if tipo_pedido == "Entrega" else ""

    endereco = "N/A" if tipo_pedido == "Retirada" else endereco
    
    tamanho = "" if not st.session_state.get('tamanho_select') else st.session_state.get('tamanho_select')

    adicionais_formatados = ""
    for adicional in st.session_state.adicionais_selecionados:
        adicionais_formatados += f"<br> - {adicional}"

    extras_formatados = ""
    for extra in st.session_state.adicionais_extras_selecionados:
        extras_formatados += f"<br> - {extra} - (R${adicionais_extras[extra]:.2f})"

    # ------------------------------
    # CÁLCULO DO VALOR TOTAL
    # ------------------------------
    valor_extras = sum(adicionais_extras[nome] for nome in st.session_state.adicionais_extras_selecionados)
    valor_total = valor_base + valor_extras

    # ------------------------------
    # RESUMO DO PEDIDO
    # ------------------------------
    st.markdown("## 🧾 Resumo do Pedido")

    resumo_html = f"""
    <div style="background-color: #ffffff; padding: 20px; border-radius: 12px;
        border: 1px solid #ddd; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-top: 10px; color: #000000;">
        <p><strong>🍨 Tamanho:</strong> {tamanho or 'Não selecionado'}</p>
        <p><strong>✔️ Adicionais Inclusos:</strong> {adicionais_formatados or 'Nenhum'}</p>
        <p><strong>➕ Adicionais Extras:</strong> {extras_formatados or 'Nenhum'}</p>
        <br>
        <p><strong>😎 Cliente:</strong> {nome or 'Não informado'}</p>
        <p><strong>📱 WhatsApp:</strong> {whatsapp or 'Não informado'}</p>
        <br>
        <p><strong>💳 Pagamento:</strong> {forma_pagamento or 'Não selecionado'}</p>
        <p><strong>💰 Troco:</strong> {troco or 'Não informado'}</p>
        <p><strong>🛵 Tipo de Pedido:</strong> {tipo_pedido or 'Não selecionado'}</p>
        <p><strong>📌 Endereço:</strong> {endereco or 'Não informado'}</p>
        <br>
        <br>
        <p><strong> 🟢 Valor Total: R$ {valor_total:.2f}
    </div>
    """

    st.markdown(resumo_html, unsafe_allow_html=True)

    # --------------------------
    # BOTÃO DE CONFIRMAR PEDIDO 
    # --------------------------
    confirmar_button_disabled = erro_limite or st.session_state.tamanho_select == ""

    if st.button("✅ Confirmar Pedido", disabled=confirmar_button_disabled, use_container_width=True):
        # Endereço só é obrigatório se o tipo for Entrega
        if not nome:
            st.error("Preencha o nome.")
        elif not whatsapp:
            st.error("Preencha o número do Whatsapp.")
        elif not forma_pagamento:
            st.error("Escolha uma forma de pagamento.")
        elif tipo_pedido == "Entrega" and not endereco:
            st.error("Preencha o endereço para a forma de entrega escolhida.")
        elif erro_limite:
            st.error("Quantidade de adicionais fora do limite.")
        else:
            adicionais_inclusos = ', '.join(st.session_state.adicionais_selecionados)
            adicionais_extras_texto = ', '.join(st.session_state.adicionais_extras_selecionados)
            valor_extras = sum([adicionais_extras[nome] for nome in st.session_state.adicionais_extras_selecionados])
            valor_total = valor_base + valor_extras

            # Se for retirada, mostra "Cliente irá retirar"
            endereco_texto = endereco if tipo_pedido == "Entrega" else "Cliente irá retirar no local"

    # --------------------------
    # INTEGRAÇÃO COM O WHATSAPP
    # --------------------------
            mensagem = f"""
Ola! Gostaria de fazer um pedido 😀

Meus dados são:
😎 Nome: {nome}
📱 WhatsApp: {whatsapp}
🏡 Endereço: {endereco_texto}
💳 Forma de pagamento: {forma_pagamento}

E quero um açaí com:
🍨 Copo: {tamanho}
✔️ Adicionais inclusos: {adicionais_formatados.replace('<br>','\n')}
➕ Adicionais extras: {extras_formatados.replace('<br>','\n')}

Total: R$ {valor_total:.2f}
Troco para: R$ {troco}

Obrigado(a)!"""

            msg_encoded = urllib.parse.quote_plus(mensagem)
            numero_proprietario = NUMERO_TELEFONE
            link_whatsapp = f"https://api.whatsapp.com/send?phone={numero_proprietario}&text={msg_encoded}"

            st.success("Estamos te redirecionando para o WhatsApp...")

            redirecionamento_html = f"""
            <meta http-equiv="refresh" content="1;url={link_whatsapp}">
            <script>
                window.location.href = "{link_whatsapp}";
            </script>
            """
            st.markdown(redirecionamento_html, unsafe_allow_html=True)

    # ----------------
    # BOTÃO DE LIMPAR
    # ----------------
    if st.button("Limpar Pedido"):
        
        st.session_state.limpar_pedido_solicitado = True
        st.rerun()