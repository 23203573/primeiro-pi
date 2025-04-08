import streamlit as st

# ------------------------------
# ADICIONAIS COM VALORES
# ------------------------------

# Adicionais inclusos: já estão no valor base do copo
adicionais_inclusos = {
    "Mousse Ninho": 2.00, "Mousse Ovomaltine": 3.00, "Mousse Limão": 2.00,
    "Mousse Amendoim": 2.50, "Mousse Morango": 2.50, "Uva": 2.00, "Banana": 2.00,
    "Morango": 2.50, "Kiwi": 3.50, "Amendoim": 1.50, "Granola Tradicional": 2.00,
    "Leite Condensado": 2.00, "Leite em Pó": 1.50, "Mel": 2.00, "Paçoca": 1.50,
    "Castanha de Caju": 2.00, "Cobertura Caramelo": 1.00, "Cobertura Chocolate": 1.00,
    "Cobertura Morango": 1.00
}

# Adicionais extras: cobrados à parte
adicionais_extras = {
    "Bis": 2.00, "Kit Kat": 2.50, "Confete": 2.00,
    "Nescau Ball": 2.00, "Trento": 2.50
}

# ------------------------------
# FORMATAR ITENS PARA MULTISELECT
# ------------------------------

opcoes_inclusos = [f"{nome} - R${preco:.2f}" for nome, preco in adicionais_inclusos.items()]
mapa_inclusos = {f"{nome} - R${preco:.2f}": nome for nome, preco in adicionais_inclusos.items()}

opcoes_extras = [f"{nome} - R${preco:.2f}" for nome, preco in adicionais_extras.items()]
mapa_extras = {f"{nome} - R${preco:.2f}": nome for nome, preco in adicionais_extras.items()}

# ------------------------------
# INICIALIZAR VARIÁVEIS NO SESSION STATE
# ------------------------------

for key in ["tamanho", "adicionais_selecionados", "adicionais_extras_selecionados"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key == "tamanho" else []

# ------------------------------
# INTERFACE DO APLICATIVO
# ------------------------------

st.title("Monte seu Copo de Açaí 🍧")

tamanho_opcao = st.selectbox(
    "Escolha o tamanho do copo:", 
    ["", "300ml - R$18,00", "500ml - R$20,00"],
    index=0 if st.session_state.tamanho == "" else ["", "300ml - R$18,00", "500ml - R$20,00"].index(st.session_state.tamanho)
)

if tamanho_opcao != st.session_state.tamanho:
    st.session_state.tamanho = tamanho_opcao
    st.session_state.adicionais_selecionados = []
    st.session_state.adicionais_extras_selecionados = []

# Regras por tamanho
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

# Atualiza session_state com os novos selecionados
st.session_state.adicionais_selecionados = [mapa_inclusos[nome] for nome in novos_adicionais_inclusos_formatados]
st.session_state.adicionais_extras_selecionados = [mapa_extras[nome] for nome in novos_adicionais_extras_formatados]

# Validação de regras
total_adicionais = len(st.session_state.adicionais_selecionados) + len(st.session_state.adicionais_extras_selecionados)
erro_limite = not (min_adicionais <= total_adicionais <= max_adicionais)

if erro_limite:
    st.error(f"Você precisa selecionar entre {min_adicionais} e {max_adicionais} adicionais. Selecionados: {total_adicionais}")

# ------------------------------
# CAMPOS DO CLIENTE
# ------------------------------

st.subheader("Dados do Cliente")

nome = st.text_input("Nome Completo:")
endereco = st.text_input("Endereço para entrega:")

forma_pagamento = st.radio("Forma de pagamento:", ["Cartão", "Dinheiro"])
troco = st.text_input("Troco para quanto?") if forma_pagamento == "Dinheiro" else ""

tipo_pedido = st.selectbox("Tipo de pedido:", ["", "Entrega", "Retirada"])

# ------------------------------
# RESUMO DO PEDIDO
# ------------------------------

if any([st.session_state.tamanho, nome, endereco, st.session_state.adicionais_selecionados, st.session_state.adicionais_extras_selecionados]):
    st.subheader("Resumo do Pedido")

    adicionais_str = ', '.join(st.session_state.adicionais_selecionados) or "Nenhum"
    extras_str = ', '.join(st.session_state.adicionais_extras_selecionados) or "Nenhum"
    total = valor_base + sum(adicionais_extras[n] for n in st.session_state.adicionais_extras_selecionados)

    st.markdown(
        f"""
        <div style='padding: 15px; border-radius: 10px; background-color: #f5f5f5;
                    box-shadow: 2px 2px 10px #ccc; color: #000;'>
            <strong>Nome:</strong> {nome or '-'}<br>
            <strong>Endereço:</strong> {endereco or '-'}<br>
            <strong>Tipo de pedido:</strong> {tipo_pedido or '-'}<br>
            <strong>Forma de pagamento:</strong> {forma_pagamento}<br>
            {"<strong>Troco para:</strong> R$ " + troco if forma_pagamento == "Dinheiro" and troco else ""}
            <br><br>
            <strong>Tamanho:</strong> {st.session_state.tamanho or '-'}<br>
            <strong>Adicionais:</strong> {adicionais_str}<br>
            <strong>Extras:</strong> {extras_str}<br>
            <strong>Total a pagar:</strong> R$ {total:.2f}
        </div>
        """, unsafe_allow_html=True
    )
else:
    st.info("O resumo do pedido será exibido aqui quando você preencher os dados 😉")

# ------------------------------
# BOTÕES DE AÇÃO
# ------------------------------

if st.button("Limpar Pedido"):
    st.session_state.tamanho = ""
    st.session_state.adicionais_selecionados = []
    st.session_state.adicionais_extras_selecionados = []

confirmar_button_disabled = erro_limite or st.session_state.tamanho == ""
st.button("✅ Confirmar Pedido", disabled=confirmar_button_disabled, use_container_width=True)
