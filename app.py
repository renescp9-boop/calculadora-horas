import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import io

# Importações para gerar PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

st.set_page_config(
    page_title="Gestão de Ponto & Vencimento", 
    page_icon="🏦",
    layout="centered"
)

# --- VALORES BASE REAIS (Triangle / Gotflow) ---
SALARIO_BASE_MES = 920.00
SALARIO_HORA_BRUTO = 5.31
TAXA_SS = 0.11
SA_CARTAO_DIA = 10.20

# --- ESTADO DE SESSÃO ---
if "registos_diarios" not in st.session_state:
    st.session_state.registos_diarios = [
        {"Data": "15/06/2026", "Dia": "Segunda-feira", "Entrada": "08:00", "Almoço Início": "13:00", "Almoço Fim": "14:00", "Saída": "17:00", "Horas Extra": 0.0, "Refeição": "Sim"},
        {"Data": "04/07/2026", "Dia": "Sábado", "Entrada": "08:00", "Almoço Início": "14:00", "Almoço Fim": "15:00", "Saída": "17:00", "Horas Extra": 8.0, "Refeição": "Não"},
        {"Data": "06/07/2026", "Dia": "Segunda-feira", "Entrada": "08:00", "Almoço Início": "13:00", "Almoço Fim": "14:00", "Saída": "19:00", "Horas Extra": 2.0, "Refeição": "Sim"},
    ]

# --- GERADOR DE PDF ---
def gerar_pdf_recibo(dias_trabalhados, horas_extra_totais, mes_ano_str="Agosto/2026"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=11, alignment=1, spaceAfter=8)
    normal_style = ParagraphStyle('Norm', parent=styles['Normal'], fontSize=8, leading=10)

    header_data = [
        [Paragraph("<b>TRIANGLE - E.T.T. UNIPESSOAL, LDA.</b><br/>Praça de Alvalade Nº7, 12º Dto<br/>1700-036 - LISBOA", normal_style),
         Paragraph(f"<b>RECIBO DE REMUNERAÇÃO</b><br/><br/><b>{mes_ano_str}</b>", title_style)]
    ]
    t_header = Table(header_data, colWidths=[280, 240])
    t_header.setStyle(TableStyle([('BOX', (0,0), (-1,-1), 1, colors.black), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(t_header)
    story.append(Spacer(1, 10))

    val_horas_extra = horas_extra_totais * (SALARIO_HORA_BRUTO * 1.5)
    val_sa = dias_trabalhados * SA_CARTAO_DIA
    bruto_sujeito = SALARIO_BASE_MES + val_horas_extra
    desconto_ss = bruto_sujeito * TAXA_SS
    total_abonos = bruto_sujeito + val_sa
    total_descontos = desconto_ss + val_sa
    liquido = bruto_sujeito - desconto_ss

    items_data = [
        ["DESIGNAÇÃO", "HORAS QUANT.", "VALOR TAXA", "ABONOS", "DESCONTOS"],
        ["Salário Bruto Mensal", "173.33", f"{SALARIO_HORA_BRUTO:.2f}", f"{SALARIO_BASE_MES:.2f}", ""],
        ["Hora Extra 50%", f"{horas_extra_totais:.2f}", f"{SALARIO_HORA_BRUTO*1.5:.2f}", f"{val_horas_extra:.2f}", ""],
        ["Cartão de Refeição", f"{dias_trabalhados:.2f}", f"{SA_CARTAO_DIA:.2f}", f"{val_sa:.2f}", ""],
        ["Segurança Social", "", "11.00%", "", f"{desconto_ss:.2f}"],
        ["SA - Cartão Ticket", "", "", "", f"{val_sa:.2f}"]
    ]
    
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
        ["TOTAIS", f"{total_abonos:.2f} €", f"{total_descontos:.2f} €"],
        ["TOTAL LÍQUIDO A RECEBER (BANCO)", "", f"{liquido:.2f} €"],
        ["A RECEBER EM CARTÃO DE REFEIÇÃO", "", f"{val_sa:.2f} €"]
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

# --- TITULO PRINCIPAL ---
st.title("🏦 Caixadirecta / Ponto")
st.caption("Yanik René Lobo de Pina Ucha Pereira")

# --- MENUS ---
menu = st.sidebar.radio("Navegação", [
    "📅 Calendário & Estimativa", 
    "📝 Registo Diário de Ponto", 
    "📊 Movimentos da Conta", 
    "📄 Descarregar Recibos PDF"
])

# ----------------------------------------------------
# 1. CALENDÁRIO & ESTIMATIVA
# ----------------------------------------------------
if menu == "📅 Calendário & Estimativa":
    st.header("📅 Selecionar Intervalo no Calendário")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        data_inicio = st.date_input("Data de Início", value=date(2026, 8, 1))
    with col_d2:
        data_fim = st.date_input("Data do Fim", value=date(2026, 8, 31))
        
    hextra = st.number_input("Horas Extra Estimadas no Período", min_value=0.0, step=1.0, value=0.0)

    if data_inicio <= data_fim:
        dias_totais = (data_fim - data_inicio).days + 1
        dias_uteis = sum(1 for i in range(dias_totais) if (data_inicio + timedelta(days=i)).weekday() < 5)
        
        bruto_base = SALARIO_BASE_MES
        bruto_extra = hextra * (SALARIO_HORA_BRUTO * 1.5)
        subs_alimentacao = dias_uteis * SA_CARTAO_DIA
        
        bruto_sujeito = bruto_base + bruto_extra
        desconto_ss = bruto_sujeito * TAXA_SS
        liquido_banco = bruto_sujeito - desconto_ss
        total_bruto = bruto_sujeito + subs_alimentacao

        st.divider()
        st.subheader(f"Resultados para {dias_uteis} dias úteis")
        
        c1, c2 = st.columns(2)
        c1.metric("Líquido a Receber (Banco)", f"{liquido_banco:.2f} €")
        c2.metric("Cartão de Refeição", f"{subs_alimentacao:.2f} €")
        
        st.write(f"• **Salário Bruto Base:** {bruto_base:.2f} €")
        if hextra > 0:
            st.write(f"• **Horas Extra ({hextra:.1f}h):** +{bruto_extra:.2f} €")
        st.write(f"• **Total Bruto (com Subs. Alimentação):** {total_bruto:.2f} €")
        st.write(f"• **Desconto SS (11%):** -{desconto_ss:.2f} €")

# ----------------------------------------------------
# 2. REGISTO DIÁRIO DE PONTO
# ----------------------------------------------------
elif menu == "📝 Registo Diário de Ponto":
    st.header("📝 Registo Diário (Gotflow)")
    
    c1, c2 = st.columns(2)
    with c1:
        d_reg = st.date_input("Data", value=date.today())
        ent = st.time_input("Entrada", value=datetime.strptime("08:00", "%H:%M").time())
        alm_i = st.time_input("Início Almoço", value=datetime.strptime("13:00", "%H:%M").time())
    with c2:
        alm_f = st.time_input("Fim Almoço", value=datetime.strptime("14:00", "%H:%M").time())
        sai = st.time_input("Saída", value=datetime.strptime("17:00", "%H:%M").time())
        ref = st.selectbox("Refeição Paga?", ["Sim", "Não"])

    h_ex = st.number_input("Horas Extra Feitas", min_value=0.0, max_value=8.0, step=0.5, value=0.0)

    if st.button("Guardar Registo", use_container_width=True):
        dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
        st.session_state.registos_diarios.append({
            "Data": d_reg.strftime("%d/%m/%Y"),
            "Dia": dias_semana[d_reg.weekday()],
            "Entrada": ent.strftime("%H:%M"),
            "Almoço Início": alm_i.strftime("%H:%M"),
            "Almoço Fim": alm_f.strftime("%H:%M"),
            "Saída": sai.strftime("%H:%M"),
            "Horas Extra": h_ex,
            "Refeição": ref
        })
        st.success("Registo guardado com sucesso!")

    st.divider()
    st.subheader("Histórico Guardado")
    st.dataframe(pd.DataFrame(st.session_state.registos_diarios), use_container_width=True)

# ----------------------------------------------------
# 3. MOVIMENTOS
# ----------------------------------------------------
elif menu == "📊 Movimentos da Conta":
    st.header("📊 Movimentos - CaixaJovem")
    st.subheader("Saldo Atual: 904,63 €")
    st.divider()

    movs = [
        ("31 JUL", "Trf Triangle Empresa", "+904,63 €"),
        ("28 JUL", "Digi Portugal Lda", "-6,77 €"),
        ("28 JUL", "Tfi In S Filipa David", "+6,00 €"),
        ("28 JUL", "Tfi In S Filipa David", "+1,00 €"),
        ("24 JUL", "Compras C.deb A9", "-0,35 €"),
        ("23 JUL", "Trf Mbway 923xxx659", "-64,47 €"),
        ("23 JUL", "Deposito", "+63,50 €")
    ]
    
    for dt, tit, val in movs:
        col_a, col_b = st.columns([3, 1])
        col_a.write(f"**{tit}** ({dt})")
        col_b.write(f"**{val}**")

# ----------------------------------------------------
# 4. RECIBOS PDF
# ----------------------------------------------------
elif menu == "📄 Descarregar Recibos PDF":
    st.header("📄 Descarregar Recibos de Vencimento")
    
    mes = st.text_input("Mês/Ano do Recibo", value="Agosto/2026")
    dias = st.number_input("Dias de Alimentação", value=21)
    he = st.number_input("Horas Extra Feitas", value=0.0)

    pdf = gerar_pdf_recibo(dias, he, mes_ano_str=mes)
    
    st.download_button(
        label="📥 Descarregar Recibo em PDF",
        data=pdf,
        file_name=f"Recibo_{mes.replace('/', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
