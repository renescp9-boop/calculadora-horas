import streamlit as st
import pandas as pd
from datetime import datetime, date
import io

# Importações para gerar PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

st.set_page_config(
    page_title="Caixa | Caixadirecta", 
    page_icon="🏦",
    layout="centered"
)

# --- RECURSOS E DADOS FIXOS DE RECIBOS REAIS ---
RECIBOS_REAIS = {
    "Junho/2026": {
        "mes_str": "Junho/2026",
        "data_recibo": "30-06-2026",
        "salario_base": 920.00,
        "salario_hora": 5.31,
        "itens": [
            ["Salário Bruto Mensal", "86.67", "5.31", "460.00", ""],
            ["Subsídio de Férias", "1.00", "36.56", "36.56", ""],
            ["Cartão de Refeição", "12.00", "7.23", "86.76", ""],
            ["Segurança Social", "", "11.00%", "", "48.26"],
            ["Segurança Social Sub. Férias", "", "11.00%", "", "4.02"],
            ["Falta Just N/Remunerada", "4.00", "", "", "21.23"],
            ["SA - Cartão Ticket", "", "", "", "86.76"]
        ],
        "total_abonos": 583.32,
        "total_descontos": 160.27,
        "liquido_banco": 423.05,
        "cartao_ref": 86.76
    },
    "Julho/2026": {
        "mes_str": "Julho/2026",
        "data_recibo": "31-07-2026",
        "salario_base": 920.00,
        "salario_hora": 5.31,
        "itens": [
            ["Salário Bruto Mensal", "173.33", "5.31", "920.00", ""],
            ["Hora Extra 50%", "8.00", "7.96", "63.69", ""],
            ["Hora Extra 25%", "1.00", "6.63", "6.63", ""],
            ["Hora Extra 37.5%", "1.00", "7.30", "7.30", ""],
            ["Cartão de Refeição", "23.00", "10.20", "234.60", ""],
            ["Retroativo Cartão de Refeição", "12.00", "2.97", "35.64", ""],
            ["Segurança Social", "976.39", "11.00%", "", "107.40"],
            ["Falta Just N/Remunerada", "3.00", "", "", "15.92"],
            ["Falta Injustificada", "1.00", "", "", "5.31"],
            ["SA - Cartão Ticket", "", "", "", "234.60"]
        ],
        "total_abonos": 1267.86,
        "total_descontos": 363.23,
        "liquido_banco": 904.63,
        "cartao_ref": 234.60
    }
}

# --- FUNÇÃO PARA GERAR PDF EXATO ---
def gerar_pdf_recibo(dados):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=11, alignment=1, spaceAfter=8)
    normal_style = ParagraphStyle('Norm', parent=styles['Normal'], fontSize=8, leading=10)

    header_data = [
        [Paragraph("<b>TRIANGLE - E.T.T. UNIPESSOAL, LDA.</b><br/>Praça de Alvalade Nº7, 12º Dto<br/>1700-036 - LISBOA", normal_style),
         Paragraph(f"<b>RECIBO DE REMUNERAÇÃO</b><br/><br/><b>{dados['mes_str']}</b>", title_style)]
    ]
    t_header = Table(header_data, colWidths=[280, 240])
    t_header.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 1, colors.black), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(t_header)
    story.append(Spacer(1, 10))

    items_data = [["DESIGNAÇÃO", "HORAS QUANT.", "VALOR TAXA", "ABONOS", "DESCONTOS"]]
    items_data.extend(dados['itens'])
    
    t_items = Table(items_data, colWidths=[180, 80, 80, 90, 90])
    t_items.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ALIGN', (1,0), (-1,-1), 'CENTER')
    ]))
    story.append(t_items)
    story.append(Spacer(1, 15))

    totais_data = [
        ["TOTAIS", f"{dados['total_abonos']:.2f} €", f"{dados['total_descontos']:.2f} €"],
        ["TOTAL LÍQUIDO A RECEBER", "", f"{dados['liquido_banco']:.2f} €"],
        ["A RECEBER EM CARTÃO DE REFEIÇÃO", "", f"{dados['cartao_ref']:.2f} €"]
    ]
    t_totais = Table(totais_data, colWidths=[260, 130, 130])
    t_totais.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BACKGROUND', (0,1), (-1,1), colors.whitesmoke)
    ]))
    story.append(t_totais)

    doc.build(story)
    buffer.seek(0)
    return buffer

# --- CSS PERSONALIZADO APLICADO AO ESTILO CAIXA REAL ---
st.markdown("""
    <style>
    .stApp { background-color: #061626; color: #ffffff; }
    
    /* Ecrã de Conta / Topo */
    .cgd-account-card {
        background-color: #0d2238;
        padding: 16px;
        border-radius: 14px;
        margin-bottom: 15px;
        border: 1px solid #1c3d5a;
    }
    
    /* Item de Movimento */
    .cgd-mov-card {
        background-color: #0a1b2b;
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 8px;
        border-left: 3px solid #1f2937;
    }
    .cgd-mov-card.green { border-left: 3px solid #10b981; }
    .cgd-mov-card.red { border-left: 3px solid #ef4444; }
    
    .cgd-date-header {
        color: #9ca3af;
        font-size: 11px;
        font-weight: 700;
        margin-top: 15px;
        margin-bottom: 5px;
        text-transform: uppercase;
    }
    .cgd-title { font-weight: 600; font-size: 14px; color: #ffffff; }
    .cgd-val-pos { font-weight: 700; font-size: 15px; color: #34d399; float: right; }
    .cgd-val-neg { font-weight: 700; font-size: 15px; color: #f87171; float: right; }
    .cgd-sub { font-size: 11px; color: #6b7280; margin-top: 2px; }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- MENU DE NAVEGAÇÃO INFERIOR ---
aba = st.radio(
    "",
    ["🏠 Início", "📊 Movimentos", "🔮 Simular / Estimativa", "📄 Recibos Guardados"],
    horizontal=True
)
st.markdown("<hr style='margin-top:0; border-color:#1c3d5a;'>", unsafe_allow_html=True)

# ----------------------------------------------------
# 1. INÍCIO
# ----------------------------------------------------
if aba == "🏠 Início":
    st.markdown("""
        <div class="cgd-account-card">
            <div style="font-size:12px; color:#8ab4f8;">CaixaJovem Extracto</div>
            <div style="font-size:11px; color:#9ca3af;">0824668149130</div>
            <div style="font-size:28px; font-weight:700; margin-top:5px;">901,87 €</div>
        </div>
    """, unsafe_allow_html=True)
    st.info("💡 Podes consultar os teus movimentos e descarregar os recibos de Julho e Junho na aba 'Movimentos' ou 'Recibos Guardados'.")

# ----------------------------------------------------
# 2. MOVIMENTOS (IDÊNTICO À FOTO DA CAIXA)
# ----------------------------------------------------
elif aba == "📊 Movimentos":
    st.title("Movimentos")
    
    # Seletor de Meses estilo Caixa
    mes_selecionado = st.select_slider(
        "",
        options=["Março", "Abril", "Maio", "Junho", "Julho", "Agosto"],
        value="Julho"
    )
    
    if mes_selecionado == "Julho":
        st.markdown('<div class="cgd-date-header">31 DE JUL</div>', unsafe_allow_html=True)
        st.markdown("""
            <div class="cgd-mov-card green">
                <span class="cgd-val-pos">+904,63 €</span>
                <div class="cgd-title">Trf Triangle Empresa</div>
                <div class="cgd-sub">Saldo: 904,86 €</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Botão para gerar o recibo de Julho diretamente dos Movimentos
        pdf_jul = gerar_pdf_recibo(RECIBOS_REAIS["Julho/2026"])
        st.download_button("📄 Descarregar Recibo de Julho (PDF)", pdf_jul, "Recibo_Julho_2026.pdf", "application/pdf")

        st.markdown('<div class="cgd-date-header">28 DE JUL</div>', unsafe_allow_html=True)
        st.markdown("""
            <div class="cgd-mov-card red">
                <span class="cgd-val-neg">-6,77 €</span>
                <div class="cgd-title">Digi Portugal Lda</div>
                <div class="cgd-sub">Saldo: 0,23 €</div>
            </div>
            <div class="cgd-mov-card green">
                <span class="cgd-val-pos">+6,00 €</span>
                <div class="cgd-title">Tfi In S Filipa David</div>
                <div class="cgd-sub">Saldo: 7,00 €</div>
            </div>
            <div class="cgd-mov-card green">
                <span class="cgd-val-pos">+1,00 €</span>
                <div class="cgd-title">Tfi In S Filipa David</div>
                <div class="cgd-sub">Saldo: 1,00 €</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="cgd-date-header">24 DE JUL</div>', unsafe_allow_html=True)
        st.markdown("""
            <div class="cgd-mov-card red">
                <span class="cgd-val-neg">-0,35 €</span>
                <div class="cgd-title">Compras C.deb A9</div>
                <div class="cgd-sub">Saldo: 0,00 €</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="cgd-date-header">23 DE JUL</div>', unsafe_allow_html=True)
        st.markdown("""
            <div class="cgd-mov-card red">
                <span class="cgd-val-neg">-64,47 €</span>
                <div class="cgd-title">Trf Mbway 923xxx659</div>
                <div class="cgd-sub">Saldo: 0,35 €</div>
            </div>
            <div class="cgd-mov-card green">
                <span class="cgd-val-pos">+63,50 €</span>
                <div class="cgd-title">Deposito</div>
                <div class="cgd-sub">Saldo: 64,82 €</div>
            </div>
        """, unsafe_allow_html=True)

    elif mes_selecionado == "Junho":
        st.markdown('<div class="cgd-date-header">30 DE JUN</div>', unsafe_allow_html=True)
        st.markdown("""
            <div class="cgd-mov-card green">
                <span class="cgd-val-pos">+423,05 €</span>
                <div class="cgd-title">Trf Triangle Empresa</div>
                <div class="cgd-sub">Recibo Vencimento Junho</div>
            </div>
        """, unsafe_allow_html=True)
        
        pdf_jun = gerar_pdf_recibo(RECIBOS_REAIS["Junho/2026"])
        st.download_button("📄 Descarregar Recibo de Junho (PDF)", pdf_jun, "Recibo_Junho_2026.pdf", "application/pdf")
        
    else:
        st.write("Sem movimentos registados para este mês.")

# ----------------------------------------------------
# 3. SIMULAÇÃO E ESTIMATIVAS
# ----------------------------------------------------
elif aba == "🔮 Simular / Estimativa":
    st.subheader("🔮 Estimativa de Ordenado Futuro")
    dias = st.number_input("Dias Úteis Trabalhados", value=22)
    hextra = st.number_input("Horas Extra Feitas", value=0.0)
    
    bruto = (dias * 8 * 5.31) + (hextra * 5.31 * 1.5) + (dias * 10.20)
    ss = ((dias * 8 * 5.31) + (hextra * 5.31 * 1.5)) * 0.11
    liquido_banco = bruto - ss - (dias * 10.20)
    
    st.write(f"**Total Bruto:** {bruto:.2f} €")
    st.write(f"**Desconto SS (11%):** -{ss:.2f} €")
    st.write(f"**Líquido a receber no Banco:** {liquido_banco:.2f} €")
    st.write(f"**Cartão de Refeição:** {dias * 10.20:.2f} €")

# ----------------------------------------------------
# 4. RECIBOS GUARDADOS (JUNHO E JULHO)
# ----------------------------------------------------
elif aba == "📄 Recibos Guardados":
    st.subheader("📁 Histórico de Recibos de Vencimento")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📄 Junho / 2026")
        st.write("**Líquido Banco:** 423,05 €")
        st.write("**Cartão Refeição:** 86,76 €")
        pdf_j = gerar_pdf_recibo(RECIBOS_REAIS["Junho/2026"])
        st.download_button("📥 Baixar PDF Junho", pdf_j, "Recibo_Junho_2026.pdf", key="jun_btn")
        
    with col2:
        st.markdown("### 📄 Julho / 2026")
        st.write("**Líquido Banco:** 904,63 €")
        st.write("**Cartão Refeição:** 234,60 €")
        pdf_jul = gerar_pdf_recibo(RECIBOS_REAIS["Julho/2026"])
        st.download_button("📥 Baixar PDF Julho", pdf_jul, "Recibo_Julho_2026.pdf", key="jul_btn")
