import streamlit as st
import pandas as pd
import urllib.parse
import io
from banco import *
from datetime import datetime

# PDF generation
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    # Higher-level platypus API for nicer layouts
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.utils import ImageReader
except Exception:
    # reportlab may not be installed in the environment; the app will show an error if user tries to generate PDF
    A4 = None
    canvas = None
    mm = None
    SimpleDocTemplate = None
    Paragraph = None
    Spacer = None
    RLImage = None
    Table = None
    TableStyle = None
    colors = None
    getSampleStyleSheet = None
    ImageReader = None

# -----------------------------------
# LÓGICA DO ZOOM (ACESSIBILIDADE)
# -----------------------------------
# Tamanho da fonte normal e do zoom
FONT_NORMAL = 18    # Tamanho base em pixels
FONT_ZOOM = 28      # Aumento de 2 unidades (pixels)

if 'font_size' not in st.session_state:
    st.session_state['font_size'] = FONT_NORMAL
if 'zoom_status' not in st.session_state:
    st.session_state['zoom_status'] = 'normal' # pode ser 'normal', 'aumentado', ou 'diminuido'

def aumentar_fonte():
    """Aumenta a fonte uma única vez."""
    if st.session_state['zoom_status'] == 'normal':
        st.session_state['font_size'] = FONT_ZOOM
        st.session_state['zoom_status'] = 'aumentado'
    elif st.session_state['zoom_status'] == 'diminuido':
        st.session_state['font_size'] = FONT_NORMAL
        st.session_state['zoom_status'] = 'normal'

def diminuir_fonte():
    """Diminui a fonte uma única vez."""
    if st.session_state['zoom_status'] == 'normal':
        st.session_state['font_size'] = FONT_NORMAL - 6 # 14px
        st.session_state['zoom_status'] = 'diminuido'
    elif st.session_state['zoom_status'] == 'aumentado':
        st.session_state['font_size'] = FONT_NORMAL
        st.session_state['zoom_status'] = 'normal'


def request_remove_item(index: int) -> None:
    """Marca um item para remoção (mostra diálogo de confirmação)."""
    st.session_state['confirm_remove_index'] = index


def confirm_remove_item() -> None:
    """Remove o item previamente marcado e atualiza a UI."""
    idx = st.session_state.get('confirm_remove_index')
    try:
        if idx is not None and 0 <= idx < len(st.session_state.carrinho):
            st.session_state.carrinho.pop(idx)
            st.success("Item removido do carrinho.")
    except Exception:
        pass
    finally:
        # Limpa a solicitação de confirmação; não chamamos st.rerun() aqui porque
        # chamar st.rerun() dentro de callbacks é um no-op e gera um aviso.
        st.session_state['confirm_remove_index'] = None


def cancel_remove_item() -> None:
    """Cancela a solicitação de remoção de item."""
    # Apenas limpar o flag; o Streamlit fará o rerun automaticamente após o callback
    st.session_state['confirm_remove_index'] = None

# -----------------------------------
# Variáveis Globais
# -----------------------------------
USUARIO_PROPRIETARIO = "admin"
SENHA_PROPRIETARIO = "1234" # Trocar por uma senha segura depois
NUMERO_TELEFONE = "5519998661470"

# -----------------------------------
# CUSTOMIZAÇÃO DA PÁGINA (CSS)
# -----------------------------------
CURRENT_FONT_SIZE = st.session_state['font_size']

# Variáveis de cor removidas, valores codificados diretamente no CSS

st.markdown(
    f"""
    <style>
        /* CSS que força o tamanho da fonte (em Pixels) em vários seletores importantes */
        
        /* Contêiner raiz principal, sidebar e seus conteúdos */
        [data-testid="stAppViewBlock"],
        [data-testid="stSidebar"],
        [data-testid="stSidebarContent"],

        /* TODOS os elementos de texto básicos */
        h1, h2, h3, h4, h5, h6, p, div, span, label, textarea, input, select, option, button, a {{
            font-size: {CURRENT_FONT_SIZE}px !important;
            /* Cor escura dos títulos e texto normal */
            color: #732C4D !important; 
        }}
        
        /* --------------------------------- */
        /* Cores da Aplicação (Rosa Claro/Branco) */
        /* --------------------------------- */
        
        /* Fundo geral do app (Rosa claro) */
        .stApp {{
            background-color: #F2BBC5 !important;
        }}

        /* Cor da sidebar (Branco) */
        section[data-testid="stSidebar"] {{
            background-color: #FFFFFF !important;
        }}
        
        /* Títulos principais (h1, h2, h3 - Cor de destaque) */
        h1, h2, h3 {{
            color: #732C4D !important;
            /* Corrigir o tamanho para os títulos serem maiores, mas baseados na nova fonte */
            font-size: {CURRENT_FONT_SIZE + 8}px !important;
        }}
        h2 {{ font-size: {CURRENT_FONT_SIZE + 4}px !important; }}
        h3 {{ font-size: {CURRENT_FONT_SIZE + 2}px !important; }}
        
        
        /* --------------------------------- */
        /* SOLUÇÃO AGRESSIVA FINAL PARA CORES DE LISTAS SUSPENSAS (POPOVER) */
        /* --------------------------------- */
        
        /* Fundo do Menu Dropdown (o pop-up que abre) */
        div[data-baseweb="popover"] {{
            background-color: #732C4D !important; /* Fundo escuro */
        }}
        
        /* Força a cor de TODOS os textos, spans e divs dentro do pop-up para BRANCO */
        div[data-baseweb="popover"] * {{
            color: white !important;
        }}
        
        /* Cor de fundo da opção ao ser selecionada/hover (para melhor UX) */
        div[data-baseweb="popover"] div[role="option"]:hover {{
            background-color: #4c122d !important; /* Fundo ainda mais escuro no hover */
        }}
        
        /* --- Cor do texto DENTRO da caixa de seleção (o valor que está selecionado) --- */
        [data-testid="stSelectbox"] div[data-baseweb="select"] div,
        [data-testid="stMultiSelect"] div[data-baseweb="select"] div {{
            color: white !important;
        }}
        
        /* Cor do ícone da seta no selectbox */
        [data-testid="stSelectbox"] svg,
        [data-testid="stMultiSelect"] svg {{
            fill: white !important;
        }}
        
        /* Rótulos dos inputs (mantendo a cor original do tema) */
        .stTextInput label,
        .stSelectbox label,
        .stRadio label,
        .stMultiselect label {{
            color: #732C4D !important;
        }}
        
        /* --------------------------------- */
        /* CORREÇÃO APRIMORADA DO CHIP/TAG DE SELEÇÃO NO MULTISELECT */
        /* --------------------------------- */
        
        /* Cor de fundo da PÍLULA/TAG selecionada (usamos o BaseUI Tag) */
        div[data-testid="stMultiSelect"] div[data-baseweb="tag"] {{
            background-color: white !important; /* Fundo branco */
            border: 1px solid #e0e0e0 !important; /* Borda clara para delimitar */
        }}

        /* Texto e fundo da PÍLULA/TAG: fundo branco com texto preto */
        div[data-testid="stMultiSelect"] div[data-baseweb="tag"] span {{
            background-color: #ffffff !important; /* Fundo branco na própria label */
            color: #000000 !important; /* Texto preto para melhor contraste */
            padding: 2px 6px !important;
            border-radius: 6px !important;
            display: inline-block !important;
            line-height: 1 !important;
        }}

        /* Cor do ícone de remover (o 'x') dentro da PÍLULA/TAG (preto) */
        div[data-testid="stMultiSelect"] div[data-baseweb="tag"] svg {{
            fill: #000000 !important; /* Ícone 'x' em preto */
        }}

            /* --------------------------------- */
            /* FORÇAR FUNDO BRANCO NA CAIXA DO MULTISELECT E TEXTOS PRETOS */
            /* Cobrir variações internas do Streamlit/BaseUI para garantir contraste */
            /* Aplica à área que mostra os valores selecionados e ao input interno */
            div[data-testid="stMultiSelect"] div[data-baseweb="select"],
            div[data-testid="stMultiSelect"] div[data-baseweb="select"] div,
            .stMultiSelect div[data-baseweb="select"],
            [data-testid="stMultiSelect"] [role="combobox"],
            [data-testid="stSelectbox"] div[data-baseweb="select"],
            [data-testid="stSelectbox"] div[data-baseweb="select"] div,
            div[data-baseweb="select"] input,
            .stMultiSelect input,
            .stSelectbox input {{
                /* Não forçar fundo branco no seletor principal para preservar a cor cinza
                   do 'campo' do select/selectbox. Apenas garantir que o texto interno
                   fique preto quando for exibido (por exemplo, dentro das tags). */
                color: #000000 !important; /* texto preto */
            }}

            /* Placeholder dentro do select/multiselect com contraste adequado (cinza claro) */
            div[data-baseweb="select"] div::placeholder,
            .stMultiSelect input::placeholder,
            .stSelectbox input::placeholder {{
                color: #9a9a9a !important;
                opacity: 1 !important;
            }}
        
        /* --------------------------------- */
        /* ESTILOS DE BOTÕES E ACESSIBILIDADE */
        /* --------------------------------- */

        /* Botões nativos (Cor de destaque) */
        button[kind="primary"], button[kind="secondary"],
        /* Os botões de zoom nativos do Streamlit */
        div[data-testid="stVerticalBlock"] button {{
            background-color: #4c122d !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
        }}
        
        /* Garante que o texto interno dos botões também fique branco */
        button[kind="primary"] *, button[kind="secondary"] *,
        div[data-testid="stVerticalBlock"] button * {{
            color: white !important;
            /* Remove a herança de font-size dos botões de zoom para que fiquem no tamanho normal */
            font-size: {FONT_NORMAL}px !important;
        }}

        /* --------------------------------- */
        /* CSS para o BOTAO de Acessibilidade na Sidebar (Apenas layout do container) */
        /* --------------------------------- */
        .sidebar-accessibility-buttons {{
              display: flex;
              justify-content: space-between;
              margin-top: 10px;
              margin-bottom: 20px;
        }}
        
        /* Ajustar a largura do st.columns na sidebar */
        [data-testid="stSidebarContent"] [data-testid="column"] {{
            width: 100% !important;
            flex: 1 1 0% !important;
        }}
        
        /* --------------------------------- */
        /* CONTRASTE: forçar texto dos campos de input para branco (acessibilidade) */
        /* Aplica a campos de texto, textarea, selects e placeholders */
        input, textarea, select, option,
        input[type="text"], input[type="password"], input[type="email"], input[type="tel"],
        .stTextInput input, .stTextArea textarea, .stNumberInput input {{
            color: #ffffff !important;
        }}

        /* Placeholder com contraste adequado */
        input::placeholder, textarea::placeholder {{
            color: #e6e6e6 !important;
            opacity: 1 !important;
        }}

        /* Em alguns widgets o texto selecionado dentro do componente é um span interno */
        [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea, [data-baseweb="select"] div {{
            color: #ffffff !important;
        }}

        /* Reforçar estilo das 'pílulas' (tags) do MultiSelect para acessibilidade
           - fundo branco e texto preto (melhor contraste)
           - aplicar selectors adicionais para cobrir variações internas do Streamlit/BaseUI */
        div[data-testid="stMultiSelect"] div[data-baseweb="tag"],
        .stMultiSelect div[data-baseweb="tag"],
        div[data-baseweb="tag"] span,
        div[data-baseweb="tag"] {{
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #e0e0e0 !important;
        }}

        /* Ícone de remover (x) nas tags em preto para contraste */
        div[data-testid="stMultiSelect"] div[data-baseweb="tag"] svg,
        div[data-baseweb="tag"] svg {{
            fill: #000000 !important;
        }}

        /* Selecionado (valor mostrado) nas caixas de select/multiselect deve ficar com texto branco
           enquanto o fundo da caixa permanece cinza (preservando o visual original) */
        [data-testid="stSelectbox"] div[data-baseweb="select"] div,
        [data-testid="stMultiSelect"] div[data-baseweb="select"] div,
        .stSelectbox [data-baseweb="select"] div,
        .stMultiSelect [data-baseweb="select"] div {{
            color: #ffffff !important;
        }}

    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------
# DASHBOARD (área do proprietário)
# -----------------------------------
def exibir_dashboard():
    st.title("📊 Dashboard de Vendas")
    st.markdown("Bem-vindo ao painel de controle da **Doces Lalumare**!")

    pedidos = get_all_pedidos()
    total_vendas = float(0)
    total_pedidos = len(pedidos)

    vendas_seg = 0
    vendas_ter = 0
    vendas_qua = 0
    vendas_qui = 0
    vendas_sex = 0
    vendas_sab = 0
    vendas_dom = 0

    if not pedidos:
        total_vendas = 0
        total_pedidos = 0
        media = 0
    else:
        for pedido in pedidos:
            total_vendas += float(pedido[0])
            dt = pedido[3]
            int_weekday = dt.weekday()

            if int_weekday == 0:
                vendas_seg += 1
            elif int_weekday == 1:
                vendas_ter += 1
            elif int_weekday == 2:
                vendas_qua += 1
            elif int_weekday == 3:
                vendas_qui += 1
            elif int_weekday == 4:
                vendas_sex += 1
            elif int_weekday == 5:
                vendas_sab += 1
            elif int_weekday == 6:
                vendas_dom += 1

        media = float(total_vendas / total_pedidos)

    col1, col2, col3 = st.columns(3)
    col1.metric(f"Total de Vendas", f"R$ {total_vendas:.2f}")
    col2.metric(f"Pedidos no Mês", f"{total_pedidos}")
    col3.metric(f"Ticket Médio", f"R$ {media:.2f}")

    st.subheader("📈 Vendas da Semana")
    dados = {
        "Dia": ["1- Seg", "2- Ter", "3- Qua", "4- Qui", "5- Sex", "6- Sáb", "7- Dom"],
        "Vendas (R$)": [vendas_seg, vendas_ter, vendas_qua, vendas_qui, vendas_sex, vendas_sab, vendas_dom]
    }
    df = pd.DataFrame(dados)
    st.bar_chart(df.set_index("Dia"))

    statistics = get_statistics_adicionais()

    all_numbers = []
    for item_tuple in statistics:
        # Each tuple contains one string at index 0
        numbers_string = item_tuple[0]

        # Split the string by comma and space, and clean up any extra whitespace
        individual_numbers = [num.strip() for num in numbers_string.split(',')]

        # Add these numbers to our collective list
        all_numbers.extend(individual_numbers)

    prd_statistics = {}

    for n in all_numbers:
        produto = get_produto(n)
        if produto in prd_statistics:
            prd_statistics[produto] += 1
        else:
            prd_statistics[produto] = 1
        

    # --- Relatório PDF: botão para gerar relatório semanal com vendas e estoque ---
    def _create_weekly_report_pdf(total_vendas: float, total_pedidos: int, vendas_by_day: dict, adicionais_stats: dict, estoque_list: list) -> bytes:
        """
        Gera um PDF com layout melhorado usando ReportLab Platypus:
        - título e timestamp
        - resumo numérico
        - gráfico de vendas por dia (matplotlib embutido)
        - tabela de adicionais mais pedidos
        - tabela de produtos em estoque
        Retorna os bytes do PDF.
        """
        if A4 is None or SimpleDocTemplate is None:
            raise RuntimeError("biblioteca reportlab não está instalada")

        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=20*mm, bottomMargin=15*mm)
        styles = getSampleStyleSheet()
        elems = []

        # Title
        elems.append(Paragraph("Relatório Semanal - Doces Lalumare", styles['Title']))
        elems.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", styles['Normal']))
        elems.append(Spacer(1, 6))

        # Summary
        elems.append(Paragraph("Resumo de Vendas", styles['Heading2']))
        elems.append(Paragraph(f"Total de vendas (R$): <b>{total_vendas:.2f}</b>", styles['Normal']))
        elems.append(Paragraph(f"Total de pedidos: <b>{total_pedidos}</b>", styles['Normal']))
        elems.append(Spacer(1, 6))

        # Gráfico de vendas por dia (matplotlib)
        try:
            import matplotlib.pyplot as plt
            dias = list(vendas_by_day.keys())
            vals = list(vendas_by_day.values())
            fig, ax = plt.subplots(figsize=(6, 2.5), dpi=150)
            ax.bar(dias, vals, color='#732C4D')
            ax.set_title('Vendas por Dia')
            ax.set_ylabel('Pedidos')
            plt.tight_layout()
            imgbuf = io.BytesIO()
            fig.savefig(imgbuf, format='png', bbox_inches='tight')
            plt.close(fig)
            imgbuf.seek(0)
            elems.append(RLImage(imgbuf, width=160*mm, height=50*mm))
            elems.append(Spacer(1, 8))
        except Exception:
            # If matplotlib missing or error, skip chart gracefully
            elems.append(Paragraph("(Gráfico indisponível)", styles['Normal']))
            elems.append(Spacer(1, 6))

        # Adicionais table
        elems.append(Paragraph("Adicionais mais pedidos", styles['Heading2']))
        adicionais_rows = [["Adicional", "Quantidade"]]
        for adicional, cont in list(adicionais_stats.items())[:30]:
            adicionais_rows.append([str(adicional), str(cont)])
        tbl = Table(adicionais_rows, colWidths=[100*mm, 30*mm])
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F2BBC5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#732C4D')),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
        ]))
        elems.append(tbl)
        elems.append(Spacer(1, 8))

        # Estoque table (ordenar alfabeticamente por nome/tipo antes de construir a tabela)
        elems.append(Paragraph("Produtos em Estoque", styles['Heading2']))
        stock_rows = [["Nome/Tipo", "Quantidade", "Valor"]]
        try:
            estoque_list = sorted(estoque_list, key=lambda p: str(p[0]).lower() if p and len(p) > 0 else "")
        except Exception:
            estoque_list = list(estoque_list)

        for prd in estoque_list:
            try:
                # Some rows have type at index 1
                tipo = prd[0] if len(prd) > 1 else ""
                qtd = prd[1] if len(prd) > 2 else (prd[1] if len(prd) > 1 else "")
                # Try to find valor and unidade in known positions
                valor = prd[2] if len(prd) > 3 else ""
                un = prd[3] if len(prd) > 4 else (prd[3] if len(prd) > 3 else "")
                # Normalize types to strings and format valor with 2 decimals
                try:
                    # try to parse numeric value (accept comma or dot as decimal separator)
                    valor_num = float(str(valor).replace(',', '.'))
                    valor_str = f'R$ {valor_num:.2f}'
                except Exception:
                    # fallback: show original value if present, otherwise empty
                    valor_str = f'R$ {valor}' if valor not in (None, '') else ''
                stock_rows.append([str(tipo), f'{str(qtd)} {str(un)}', valor_str])
            except Exception:
                stock_rows.append([str(prd), "", "", ""]) 
        tbl2 = Table(stock_rows, colWidths=[80*mm, 40*mm, 40*mm])
        tbl2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F2BBC5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#732C4D')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (2,1), (3,-1), 'RIGHT')
        ]))
        elems.append(tbl2)

        # Build PDF
        doc.build(elems)
        buf.seek(0)
        return buf.read()

    # Botão para gerar o PDF
    try:
        vendas_by_day = {
            "Segunda": vendas_seg,
            "Terça": vendas_ter,
            "Quarta": vendas_qua,
            "Quinta": vendas_qui,
            "Sexta": vendas_sex,
            "Sábado": vendas_sab,
            "Domingo": vendas_dom,
        }

        if st.button("Gerar relatório"):
            try:
                # Buscar o estoque atual do banco de dados no momento da geração do relatório
                estoque_atual = get_produto_status()
                pdf_bytes = _create_weekly_report_pdf(total_vendas, total_pedidos, vendas_by_day, prd_statistics, estoque_atual)
                filename = f"relatorio_semanal_{datetime.now().strftime('%Y%m%d')}.pdf"
                st.download_button("Download do relatório (PDF)", data=pdf_bytes, file_name=filename, mime="application/pdf")
            except Exception as e:
                st.error(f"Não foi possível gerar o PDF: {e}")
    except Exception:
        # Se algo falhar na geração do relatório, mostramos um aviso simples
        st.warning("Função de geração de relatório indisponível no momento.")

    st.subheader("🥄 Adicionais Mais Pedidos")
    dados_adicionais = prd_statistics

    df_adicionais = pd.DataFrame(list(dados_adicionais.items()), columns=["Adicional", "Quantidade de Pedidos"])
    st.bar_chart(df_adicionais.set_index("Adicional"))

    last_orders = get_last_10_pedidos()

    cliente = []
    data = []
    valor = []
    adicionais_lst = []

    for order in last_orders:
        cliente.append(str(order[0]))
        valor.append(f"{float(order[1]):.2f}")
        data.append(str(order[2].strftime('%d-%m-%Y %H:%M:%S')))
        
        add_str = ''
        for add in order[3].split(', '):
            prd = get_produto(add)
            add_str += f"{prd}, "
        adicionais_lst.append(add_str)

    st.subheader("📋 Últimos Pedidos")
    st.dataframe(pd.DataFrame({
        "Cliente": cliente,
        "Data": data,
        "Valor": valor,
        "Adicionais": adicionais_lst
    }))

    estoque = get_produto_status()

    # Ordenar o estoque alfabeticamente por nome/tipo (case-insensitive)
    try:
        estoque_sorted = sorted(estoque, key=lambda p: str(p[0]).lower() if p and len(p) > 0 and p[0] is not None else "")
    except Exception:
        estoque_sorted = list(estoque)

    produtos = []
    quantidades = []
    valores = []
    medidas = []

    for prd in estoque_sorted:
        produtos.append(str(prd[0]))
        quantidades.append(str(prd[1]))
        valores.append(str(prd[2]))
        medidas.append(f"{str(prd[4])}{str(prd[3])}")

    st.subheader("📦 Produtos em Estoque")
    st.dataframe(pd.DataFrame({
        "Produto": produtos,
        "Quantidade disponível": quantidades,
        "Valor no pedido": valores,
        "Porção por Pedido": medidas
    }))

    st.subheader("🔧 Administração de Produtos")

    with st.expander("Adicionar novo produto"):
        novo_tipo = st.text_input("Nome do produto (tipo)")
        nova_qtd = st.number_input("Quantidade inicial", min_value=0, value=1, step=1)
        novo_valor = st.number_input("Valor (R$)", min_value=0.0, value=0.0, step=0.5, format="%.2f")
        nova_un = st.text_input("Unidade de medida", value="un")
        nova_qtd_pedido = st.number_input("Quantidade no pedido (g)", min_value=0, value=0, step=1)

        if st.button("Adicionar produto"):
            # Validação: nome do produto obrigatório
            if not novo_tipo or str(novo_tipo).strip() == "":
                st.error("Informe o nome do produto antes de adicionar.")
            else:
                try:
                    # Verifica se já existe um produto com mesmo nome (case-insensitive)
                    produtos_existentes = get_all_produtos()
                    nome_limpo = str(novo_tipo).strip().lower()
                    existe = any((p[1] is not None and str(p[1]).strip().lower() == nome_limpo) for p in produtos_existentes)

                    if existe:
                        st.error("Produto já cadastrado no estoque")
                    else:
                        new_id = adicionar_produto(novo_tipo, nova_qtd, novo_valor, nova_un, nova_qtd_pedido)
                        st.success(f"Produto '{novo_tipo}' adicionado com id {new_id}")
                        # Manter usuário logado e recarregar a página para atualizar tabelas/estados
                        st.session_state.logado = True
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro ao adicionar produto: {e}")

    with st.expander("Aumentar estoque existente"):
        # Carregar todos os produtos e montar um dropdown de tipos únicos
        produtos_lista = get_all_produtos()
        tipos = []
        for p in produtos_lista:
            tipo = p[1]
            if tipo not in tipos:
                tipos.append(tipo)

        if not tipos:
            st.info("Não há produtos cadastrados para aumentar o estoque.")
        else:
            tipos_with_empty = [""] + tipos
            tipo_sel = st.selectbox("Tipo do produto:", options=tipos_with_empty, index=0)
            qtd_aumentar = st.number_input("Quantidade a adicionar", min_value=1, value=1, step=1, key="inc_tipo")
            if st.button("Aumentar estoque"):
                if not tipo_sel:
                    st.warning("Selecione um tipo antes de aumentar o estoque.")
                else:
                    try:
                        aumentar_estoque_por_tipo(tipo_sel, qtd_aumentar)
                        st.success(f"Estoque de '{tipo_sel}' aumentado em {qtd_aumentar}")
                        # Manter usuário logado e recarregar a página para atualizar tabelas/estados
                        st.session_state.logado = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao aumentar estoque por tipo: {e}")

            # Mostrar a tabela de produtos para referência
            st.markdown("---")
            st.markdown("**Produtos atuais**")
            df_prod = pd.DataFrame(produtos_lista, columns=["id_produto", "tipo_produto", "qtd_produto", "valor_produto", "un_medida_produto"]) if produtos_lista else pd.DataFrame(columns=["id_produto", "tipo_produto", "qtd_produto", "valor_produto", "un_medida_produto"]) 
            st.dataframe(df_prod)

    with st.expander("Remover produto"):
        # Usar os mesmos tipos já obtidos
        produtos_lista_remove = get_all_produtos()
        tipos_remove = []
        for p in produtos_lista_remove:
            tipo = p[1]
            if tipo not in tipos_remove:
                tipos_remove.append(tipo)

        if not tipos_remove:
            st.info("Não há produtos cadastrados para remover.")
        else:
            tipos_remove_with_empty = [""] + tipos_remove
            tipo_remove = st.selectbox("Nome do produto", options=tipos_remove_with_empty, key="remove_tipo", index=0)
            if st.button("Remover produto"):
                if not tipo_remove:
                    st.warning("Selecione um tipo antes de remover.")
                else:
                    try:
                        from banco import remover_produto_por_tipo

                        affected = remover_produto_por_tipo(tipo_remove)
                        st.success(f"Removidos {affected} item(ns) do tipo '{tipo_remove}'")
                        # Manter logado e recarregar para atualizar a lista
                        st.session_state.logado = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao remover produto: {e}")

# ------------------------------
# LOGO DO SITE E ACESSIBILIDADE NA SIDEBAR
# ------------------------------

with st.sidebar:
    
    # 1. IMAGEM DO LOGO (TOPO)
    st.image("Logo.jpg", width=300)

    st.markdown("---") # Linha separadora
    
    # 2. BOTÕES DE ACESSIBILIDADE (ZOOM)
    
    # Títulos dos botões de acessibilidade removidos para simplificar a sidebar

    # Este markdown cria o div para que os botões tenham espaço/estilo
    st.markdown(
        """
        <div class="sidebar-accessibility-buttons">
        """
        , unsafe_allow_html=True
    )
    
    # Criando os botões Streamlit nativos em colunas
    col_a_minus, col_a_plus = st.columns(2)

    with col_a_minus:
        st.button(
            "A-", 
            on_click=diminuir_fonte, 
            key="btn_zoom_out",
            use_container_width=True
        )

    with col_a_plus:
        st.button(
            "A+", 
            on_click=aumentar_fonte, 
            key="btn_zoom_in",
            use_container_width=True
        )
    
    st.markdown(
        """
        </div>
        """, unsafe_allow_html=True
    )
    
    # Remover o botão de Alto Contraste (não utilizado)

    # Espaço antes da área de login
    st.markdown("---")
    # ------------------------------
    # FIM DA INJEÇÃO DOS BOTÕES E LOGO NA SIDEBAR
    # ------------------------------

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
# O item 'tamanho' não é usado aqui, mas 'tamanho_select' é usado na interface, mantendo por segurança.
for key in ["tamanho", "adicionais_selecionados", "adicionais_extras_selecionados"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key == "tamanho" else []

# Inicializar as chaves usadas pelos widgets multiselect para evitar
# conflito entre passar `default=` ao widget e definir a chave via
# Session State logo antes da criação do widget.
for key in ["adicionais_inclusos_multiselect", "adicionais_extras_multiselect"]:
    if key not in st.session_state:
        st.session_state[key] = []

if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

# As chaves de session state para inputs são necessárias
for key in ["nome_input", "whatsapp_input", "forma_pagamento_radio", "troco_input", "tipo_pedido_radio", "endereco_input"]:
     if key not in st.session_state:
        st.session_state[key] = "" if 'input' in key else None

# Flags de confirmação para remoções/limpeza
if 'confirm_remove_index' not in st.session_state:
    st.session_state['confirm_remove_index'] = None
if 'confirm_limpar_carrinho' not in st.session_state:
    st.session_state['confirm_limpar_carrinho'] = False

if "limpar_pedido_solicitado" not in st.session_state:
    st.session_state.limpar_pedido_solicitado = False
if "limpar_carrinho_solicitado" not in st.session_state:
    st.session_state.limpar_carrinho_solicitado = False

# Verifica se a limpeza do pedido individual foi solicitada
if st.session_state.limpar_pedido_solicitado:
    st.session_state.tamanho_select = ""
    st.session_state.adicionais_inclusos_multiselect = []
    st.session_state.adicionais_extras_multiselect = []
    st.session_state.limpar_pedido_solicitado = False
    st.rerun()

# Limpar carrinho completo
if st.session_state.limpar_carrinho_solicitado:
    st.session_state.carrinho = []
    st.session_state.nome_input = ""
    st.session_state.whatsapp_input = ""
    st.session_state.forma_pagamento_radio = None
    st.session_state.troco_input = ""
    st.session_state.tipo_pedido_radio = None
    st.session_state.endereco_input = ""
    st.session_state.limpar_carrinho_solicitado = False
    st.rerun()

# ------------------------------
# INTERFACE PRINCIPAL
# ------------------------------
if st.session_state.logado:
    exibir_dashboard()
else:
    # Mapeamento de adicionais e extras do 'banco'
    inclusos = get_adicionais()
    add = []
    for a in inclusos:
        add.append(str(a[0]))

    extras = get_extras()
    ext = {}
    for e in extras:
        ext[e[0]] = float(e[1])

    adicionais_inclusos = add
    adicionais_extras = ext
    tamanhos_select = ["", "300ml - R$18,00", "500ml - R$20,00"]

    opcoes_inclusos = adicionais_inclusos
    opcoes_extras = [f"{nome} - R${preco:.2f}" for nome, preco in adicionais_extras.items()]

    tamanho_opcao = st.selectbox(
        label="Escolha o tamanho do copo:",
        options=tamanhos_select,
        index=0,
        key="tamanho_select"
    )
    
    tamanhos = {
        "300ml - R$18,00": {"min": 3, "max": 4, "preco": 18.00},
        "500ml - R$20,00": {"min": 3, "max": 6, "preco": 20.00}
    }
    regras = tamanhos.get(tamanho_opcao, {"min": 0, "max": 0, "preco": 0.00})
    min_adicionais = regras["min"]
    max_adicionais = regras["max"]
    valor_base = regras["preco"]

    adicionais_disabled = tamanho_opcao == ""
    if adicionais_disabled:
        st.warning("Selecione o tamanho do copo antes de adicionar ingredientes.")
        # Garantir que não existam seleções anteriores enquanto o seletor estiver desabilitado
        try:
            st.session_state['adicionais_inclusos_multiselect'] = []
        except Exception:
            pass
        try:
            st.session_state['adicionais_extras_multiselect'] = []
        except Exception:
            pass

    st.subheader("Escolha seus adicionais")
    
    novos_adicionais_inclusos_formatados = st.multiselect(
        label="Adicionais inclusos:",
        options=opcoes_inclusos,
        key="adicionais_inclusos_multiselect",
        placeholder="",
        disabled=adicionais_disabled
    )

    novos_adicionais_extras_formatados = st.multiselect(
        label="Adicionais extras (custo adicional):",
        options=opcoes_extras,
        key="adicionais_extras_multiselect",
        placeholder="",
        disabled=adicionais_disabled
    )

    adicionais_selecionados = novos_adicionais_inclusos_formatados
    adicionais_extras_selecionados = [nome.split(" - ")[0] for nome in novos_adicionais_extras_formatados]

    total_adicionais = len(adicionais_selecionados) + len(adicionais_extras_selecionados)
    erro_limite = not (min_adicionais <= total_adicionais <= max_adicionais)

    if erro_limite and not adicionais_disabled:
        st.error(f"Você precisa selecionar entre {min_adicionais} e {max_adicionais} adicionais. Selecionados: {total_adicionais}")

    valor_extras = sum(adicionais_extras[nome] for nome in adicionais_extras_selecionados)
    valor_total_item = valor_base + valor_extras
    
    # -----------------------------------
    # BOTÃO ADICIONAR AO CARRINHO
    # -----------------------------------
    
    add_carrinho_disabled = erro_limite or tamanho_opcao == ""

    if st.button("➕ Adicionar ao Carrinho", use_container_width=True, disabled=add_carrinho_disabled):
        item_pedido = {
            "tamanho": tamanho_opcao,
            "adicionais": adicionais_selecionados,
            "extras": adicionais_extras_selecionados,
            "valor": valor_total_item
        }
        st.session_state.carrinho.append(item_pedido)
        st.success("Item adicionado ao carrinho!")
        st.session_state.limpar_pedido_solicitado = True
        st.rerun()

    # ------------------------------
    # RESUMO DO CARRINHO
    # ------------------------------
    
    st.subheader("🛒 Itens no Carrinho")

    if not st.session_state.carrinho:
        st.info("Seu carrinho está vazio.")
    else:
        total_pedido = 0
        for i, item in enumerate(st.session_state.carrinho):
            adicionais_str = ", ".join(item['adicionais'])
            
            # Formatação robusta para os adicionais extras
            extras_list_formatada = []
            for extra_name in item['extras']:
                # Aqui o valor é lido do dicionário e formatado de forma segura
                price = adicionais_extras.get(extra_name, 0.0)
                extras_list_formatada.append(f"{extra_name} (R$ {price:.2f})")
            
            extras_str = ", ".join(extras_list_formatada)

            # Mostrar item em duas colunas: informação (col0) + botão remover (col1)
            col_info, col_action = st.columns([12, 1])
            with col_info:
                st.markdown(f"**Item {i+1}:** {item['tamanho']}")
                st.markdown(f"**Adicionais Inclusos:** {adicionais_str or 'Nenhum'}")
                st.markdown(f"**Adicionais Extras:** {extras_str or 'Nenhum'}")
                st.markdown(f"**Valor do Item:** R$ {item['valor']:.2f}")
            with col_action:
                # Botão para solicitar a remoção do item (abre confirmação)
                btn_key = f"remove_item_{i}"
                st.button("❌", key=btn_key, on_click=request_remove_item, args=(i,))
            st.markdown("---")
            total_pedido += item['valor']

        st.markdown(f"**Total do Pedido: R$ {total_pedido:.2f}**")

        # Botão para iniciar confirmação de limpar o carrinho
        if st.button("🧹 Limpar Carrinho", use_container_width=True):
            st.session_state['confirm_limpar_carrinho'] = True

        # Confirmação de remoção individual (aparece quando solicitada)
        if st.session_state.get('confirm_remove_index') is not None:
            idx = st.session_state['confirm_remove_index']
            if 0 <= idx < len(st.session_state.carrinho):
                item = st.session_state.carrinho[idx]
                st.warning(f"Confirma remoção do Item {idx+1}: {item['tamanho']} ?")
                c1, c2 = st.columns(2)
                with c1:
                    st.button("Confirmar remoção", on_click=confirm_remove_item, key="confirm_remove_confirm")
                with c2:
                    st.button("Cancelar", on_click=cancel_remove_item, key="confirm_remove_cancel")
            else:
                # índice inválido — limpar solicitação
                st.session_state['confirm_remove_index'] = None

        # Confirmação para limpar todo o carrinho
        if st.session_state.get('confirm_limpar_carrinho'):
            st.warning("Tem certeza que deseja limpar todo o carrinho? Esta ação não pode ser desfeita.")
            cc1, cc2 = st.columns(2)
            with cc1:
                def do_clear_cart():
                    st.session_state.carrinho = []
                    st.session_state.nome_input = ""
                    st.session_state.whatsapp_input = ""
                    st.session_state.forma_pagamento_radio = None
                    st.session_state.troco_input = ""
                    st.session_state.tipo_pedido_radio = None
                    st.session_state.endereco_input = ""
                    st.session_state['confirm_limpar_carrinho'] = False
                    st.success("Carrinho limpo.")
                    # Não chamar st.rerun() aqui — é um no-op dentro de callbacks.

                st.button("Confirmar limpeza", on_click=do_clear_cart, key="confirm_clear_confirm")
            with cc2:
                def cancel_clear_cart():
                    st.session_state['confirm_limpar_carrinho'] = False
                    # Apenas limpar o flag; Streamlit irá rerun automaticamente.

                st.button("Cancelar", on_click=cancel_clear_cart, key="confirm_clear_cancel")
        
        # ------------------------------
        # CAMPOS DO CLIENTE
        # ------------------------------
        st.subheader("Dados do cliente")
        nome = st.text_input("Nome completo:", key="nome_input")
        whatsapp = st.text_input("WhatsApp (formato: (xx) 91234-5678):", key="whatsapp_input")

        forma_pagamento = st.radio("Forma de pagamento:", ["Cartão", "Dinheiro", "PIX"], index=None, key="forma_pagamento_radio")
        troco = st.text_input("Troco para quanto?", key="troco_input") if forma_pagamento == "Dinheiro" else ""
        
        tipo_pedido = st.radio("Tipo:", ["Retirada", "Entrega"], index=None, key="tipo_pedido_radio")
        endereco = st.text_input("Endereço para entrega:", key="endereco_input") if tipo_pedido == "Entrega" else ""

        confirmar_disabled = not nome or not whatsapp or not forma_pagamento or (tipo_pedido == "Entrega" and not endereco)
        
        # --------------------------
        # BOTÃO DE CONFIRMAR PEDIDO FINAL
        # --------------------------
        if st.button("✅ Confirmar Pedido Completo", use_container_width=True, disabled=confirmar_disabled):
            
            troco_texto = troco if forma_pagamento == "Dinheiro" else "N/A"
            endereco_texto = endereco if tipo_pedido == "Entrega" else "Cliente irá retirar no local"

            save_ok = False
            try:
                cliente_id = get_existing_cliente(nome=nome, telefone=whatsapp)
                if cliente_id is None:
                    cliente_id = inserir_cliente(nome=nome, telefone=whatsapp, endereco=endereco_texto)
                
                # Juntando todos os adicionais de todos os itens do carrinho
                adicionais_ids = []
                for item in st.session_state.carrinho:
                    adicionais_ids.extend(get_id_produtos(item['adicionais']))

                    if len(item['extras']) > 0:
                        adicionais_ids.extend(get_id_produtos(item['extras']))
                
                # Certifique-se de que item[0] seja convertido para string
                adicionais_texto = ', '.join([str(item[0]) for item in adicionais_ids])
                
                pedido_id = inserir_pedido(
                    cliente_id=cliente_id, 
                    funcionario_id=1, 
                    numero=f"PD{datetime.now().strftime('%Y%m%d%H%M%S')}", 
                    valor=total_pedido, 
                    status="Recebido", 
                    forma_pagamento=forma_pagamento, 
                    forma_retirada=tipo_pedido, 
                    data_hora_previsao=datetime.now(), 
                    soma_qtd_produto=len(st.session_state.carrinho), 
                    adicionais=adicionais_texto
                )
                
                for prd in adicionais_ids:
                    update_qtd_produto(prd[0])
                save_ok = True
            except Exception as e:
                # Não expor o erro cru ao usuário (ex.: erro MySQL 1292 sobre conversão de DOUBLE)
                # Logamos no console para investigação e seguimos para o redirecionamento ao WhatsApp
                # para não interromper a experiência do cliente.
                print(f"Erro ao salvar pedido (detalhe no servidor): {type(e).__name__}: {e}")
                save_ok = False
                # Não usar st.error com a mensagem crua do banco para evitar mensagens técnicas na UI.
            
            # --------------------------
            # INTEGRAÇÃO COM O WHATSAPP
            # --------------------------
            
            # Preparando a mensagem do WhatsApp com todos os itens
            mensagem_itens = ""
            for i, item in enumerate(st.session_state.carrinho):
                adicionais_item = ", ".join(item['adicionais'])
                extras_item = ", ".join([f"{e}" for e in item['extras']])
                
                mensagem_itens += f"""
*Item {i+1}:*
🍨 Copo: {item['tamanho']}
✔️ Adicionais inclusos: {adicionais_item or 'Nenhum'}
➕ Adicionais extras: {extras_item or 'Nenhum'}
"""
            
            mensagem = f"""
Olá! Gostaria de fazer um pedido 😀

*Meus dados são:*
😎 Nome: {nome}
📱 WhatsApp: {whatsapp}
🏡 Endereço: {endereco_texto}
💳 Forma de pagamento: {forma_pagamento}

*Meu pedido:*
{mensagem_itens}
*Total:* R$ {total_pedido:.2f}
*Troco para:* R$ {troco_texto}

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

