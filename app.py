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
    page_title="Caixadirecta | Controlo de Ponto & Salário", 
    page_icon="🏦",
    layout="centered"
)

# --- REGRAS DE CÁLCULO BASE (Triangle Solutions / Gotflow) ---
SALARIO_BASE_MES = 920.00
SALARIO_HORA_BRUTO = 5.31
TAXA_SS = 0.11 # 11% Segurança Social
SA_CARTAO_DIA = 10.20

# --- INICIALIZAÇÃO DE ESTADO ---
if "registos_diarios" not in st.session_state:
    # Dados de exemplo pré-carregados da folha Gotflow
    st.session_state.registos_diarios = [
        {"Data": "15/06/2026", "Dia": "Segunda-feira", "Entrada": "08:00", "Almoço Início": "13:00", "Almoço Fim": "14:00", "Saída": "17:00", "Horas Normal": 8.0, "Horas Extra": 0.0, "Refeição": "Sim", "Ganho Liq": 37.70},
        {"Data": "04/07/2026", "Dia": "Sábado", "Entrada": "08:00", "Almoço Início": "14:00", "Almoço Fim": "15:00", "Saída": "17:00", "Horas Normal": 0.0, "Horas Extra": 8.0, "Refeição": "Não", "Ganho Liq": 56.68},
        {"Data": "06/07/2026", "Dia": "Segunda-feira", "Entrada": "08:00", "Almoço Início": "13:00", "Almoço Fim": "14:00", "Saída": "19:00", "Horas Normal": 8.0, "Horas Extra": 2.0, "Refeição": "Sim", "Ganho Liq": 51.87},
    ]

# --- DESIGN FIDEDIGNO APP CAIXA (TEMA CLARO #F4F6F9) ---
st.markdown("""
    <style>
    /* Estilo Global Caixadirecta */
    .main {
        background-color: #f4f6f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .stApp {
        background-color: #f4f6f9;
    }
    
    /* Topo Azul Caixa */
    .cgd-header {
        background-color: #005ca9;
        color: #ffffff;
        padding: 20px;
        border-radius: 0 0 16px 16px;
        margin: -60px -20px 20px -20px;
        box-shadow: 0 4px 12px rgba(0, 92, 169, 0.2);
    }
    .cgd-header h2 { color: #ffffff; margin: 0; font-size: 20px; font-weight: 700; }
    .cgd-header p { color: #d0e4ff; margin: 4px 0 0 0; font-size: 13px; }

    /* Cartão de Saldo / Conta */
    .cgd-card {
        background-color: #ffffff;
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #e5e7eb;
    }
    .cgd-card-title { font-size: 12px; color: #6b7280; font-weight: 600; text-transform: uppercase; }
    .cgd-card-balance { font-size: 28px; color: #111827; font-weight: 800; margin: 4px 0; }
    
    /* Lista de Movimentos */
    .cgd-mov-item {
        background-color: #ffffff;
        padding: 14px 16px;
        border-radius: 12px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 4px solid #005ca9;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }
    .cgd-mov-title { font-weight: 600; font-size: 14px; color: #1f2937; }
    .cgd-mov-sub { font-size: 12px; color: #6b7280; }
    .cgd-mov-val-pos { font-weight: 700; font-size: 15px; color: #10b981; }
    .cgd-mov-val-neg { font-weight: 700; font-size: 15px; color: #ef4444; }

    /* Esconder elementos padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- CABEÇALHO DA APP CAIXA ---
st.markdown("""
    <div class="cgd-header">
        <h2>🏦 Caixadirecta</h2>
        <p>Yanik René Lobo de Pina Ucha Pereira • Gotflow / Triangle</p>
    </div>
""", unsafe_allow_html=True)

# --- FUNÇÃO GERADORA DE PDF DO RECIBO DE REMUNERAÇÃO ---
def gerar_pdf_recibo(dias_trabalhados, horas_extra_totais, mes_ano_str="Julho/2026"):
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

# --- TAB NAVEGAÇÃO PRINCIPAL ---
aba = st.tabs(["🏠 Saldo & Movimentos", "📝 Registo Diário (Gotflow)", "📅 Calendário & Estimativa", "📄 Recibos PDF"])

# ----------------------------------------------------
# 1. SALDO & MOVIMENTOS (ESTILO CAIXADIRECTA)
# ----------------------------------------------------
with aba[0]:
    st.markdown("""
        <div class="cgd-card">
            <div class="cgd-card-title">CaixaJovem Extracto • 0824668149130</div>
            <div class="cgd-card-balance">904,63 €</div>
            <div style="font-size:12px; color:#10b981; font-weight:600;">+904,63 € Recebido a 31 de Julho (Triangle)</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Últimos Movimentos")
    
    # Exibição idêntica às imagens do extrato do utilizador
    movs = [
        {"data": "31 DE JUL", "titulo": "Trf Triangle Empresa", "valor": "+904,63 €", "saldo": "904,86 €", "pos": True},
        {"data": "28 DE JUL", "titulo": "Digi Portugal Lda", "valor": "-6,77 €", "saldo": "0,23 €", "pos": False},
        {"data": "28 DE JUL", "titulo": "Tfi In S Filipa David", "valor": "+6,00 €", "saldo": "7,00 €", "pos": True},
        {"data": "28 DE JUL", "titulo": "Tfi In S Filipa David", "valor": "+1,00 €", "saldo": "1,00 €", "pos": True},
        {"data": "24 DE JUL", "titulo": "Compras C.deb A9", "valor": "-0,35 €", "saldo": "0,00 €", "pos": False},
        {"data": "23 DE JUL", "titulo": "Trf Mbway 923xxx659", "valor": "-64,47 €", "saldo": "0,35 €", "pos": False},
        {"data": "23 DE JUL", "titulo": "Deposito", "valor": "+63,50 €", "saldo": "64,82 €", "pos": True},
    ]
    
    for m in movs:
        cor_val = "cgd-mov-val-pos" if m["pos"] else "cgd-mov-val-neg"
        st.markdown(f"""
            <div style="font-size:11px; font-weight:700; color:#6b7280; margin-top:10px;">{m['data']}</div>
            <div class="cgd-mov-item">
                <div>
                    <div class="cgd-mov-title">{m['titulo']}</div>
                    <div class="cgd-mov-sub">Saldo: {m['saldo']}</div>
                </div>
                <div class="{cor_val}">{m['valor']}</div>
            </div>
        """, unsafe_allow_html=True)

# ----------------------------------------------------
# 2. REGISTO DIÁRIO (FOLHA GOTFLOW)
# ----------------------------------------------------
with aba[1]:
    st.subheader("📝 Registo Diário de Ponto (Gotflow)")
    st.caption("Preenche o teu horário igual à folha física de ponto.")
    
    col1, col2 = st.columns(2)
    with col1:
        data_reg = st.date_input("Data", value=date.today())
        entrada = st.time_input("Horário Entrada", value=datetime.strptime("08:00", "%H:%M").time())
        inicio_alm = st.time_input("Início Almoço", value=datetime.strptime("13:00", "%H:%M").time())
    with col2:
        fim_alm = st.time_input("Fim Almoço", value=datetime.strptime("14:00", "%H:%M").time())
        saida = st.time_input("Horário Saída", value=datetime.strptime("17:00", "%H:%M").time())
        ref_paga = st.selectbox("Refeição Paga pela GF?", ["Sim", "Não"])

    h_extra = st.number_input("Número de Horas Extra Feitas", min_value=0.0, max_value=8.0, step=0.5, value=0.0)
    
    # Cálculos
    dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    nome_dia = dias_semana[data_reg.weekday()]
    
    val_extra = h_extra * (SALARIO_HORA_BRUTO * 1.5)
    val_sa = SA_CARTAO_DIA if ref_paga == "Sim" else 0.0
    val_base_dia = 8.0 * SALARIO_HORA_BRUTO if data_reg.weekday() < 5 else 0.0
    
    ganho_liq_dia = ((val_base_dia + val_extra) * (1 - TAXA_SS)) + val_sa

    st.info(f"💡 **Ganho Líquido Estimado para {data_reg.strftime('%d/%m/%Y')} ({nome_dia}): {ganho_liq_dia:.2f} €**")

    if st.button("💾 Gravar Registo na App", use_container_width=True):
        st.session_state.registos_diarios.append({
            "Data": data_reg.strftime("%d/%m/%Y"),
            "Dia": nome_dia,
            "Entrada": entrada.strftime("%H:%M"),
            "Almoço Início": inicio_alm.strftime("%H:%M"),
            "Almoço Fim": fim_alm.strftime("%H:%M"),
            "Saída": saída.strftime("%H:%M"),
            "Horas Normal": 8.0 if data_reg.weekday() < 5 else 0.0,
            "Horas Extra": h_extra,
            "Refeição": ref_paga,
            "Ganho Liq": round(ganho_liq_dia, 2)
        })
        st.success("Registo guardado com sucesso!")

    st.markdown("---")
    st.subheader("📋 Histórico de Ponto Registado")
    if st.session_state.registos_diarios:
        df_reg = pd.DataFrame(st.session_state.registos_diarios)
        st.dataframe(df_reg, use_container_width=True)

# ----------------------------------------------------
# 3. CALENDÁRIO PARA ESTIMATIVA (SELEÇÃO DE DATAS)
# ----------------------------------------------------
with aba[2]:
    st.subheader("📅 Seleciona o Período no Calendário")
    st.caption("Escolhe a data de início e fim para simular exatamente quanto vais ganhar nesse intervalo.")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        data_inicio = st.date_input("De (Data Início)", value=date(2026, 8, 1))
    with col_d2:
        data_fim = st.date_input("Até (Data Fim)", value=date(2026, 8, 31))
        
    hextra_estimadas = st.number_input("Horas Extra Estimadas para o Período", value=0.0, step=1.0)

    if data_inicio <= data_fim:
        # Contagem de dias úteis (Segunda a Sexta)
        dias_totais = (data_fim - data_inicio).days + 1
        dias_uteis = 0
        for i in range(dias_totais):
            d = data_inicio + timedelta(days=i)
            if d.weekday() < 5:  # 0 a 4 é de Segunda a Sexta
                dias_uteis += 1
                
        # Cálculos de estimativa
        bruto_base = (SALARIO_BASE_MES / 22) * dias_uteis if dias_uteis <= 22 else SALARIO_BASE_MES
        bruto_extra = hextra_estimadas * (SALARIO_HORA_BRUTO * 1.5)
        subs_alimentacao = dias_uteis * SA_CARTAO_DIA
        
        bruto_sujeito_ss = bruto_base + bruto_extra
        desconto_ss = bruto_sujeito_ss * TAXA_SS
        
        liquido_banco = bruto_sujeito_ss - desconto_ss
        total_bruto_com_sa = bruto_sujeito_ss + subs_alimentacao

        st.markdown("---")
        st.subheader(f"📊 Resultado para {dias_uteis} Dias Úteis Trabalhados")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Bruto (com SA)", f"{total_bruto_com_sa:.2f} €")
        with c2:
            st.metric("Desconto SS (11%)", f"-{desconto_ss:.2f} €")
        with c3:
            st.metric("Líquido a Receber no Banco", f"{liquido_banco:.2f} €")
            
        st.success(f"💳 **A receber em Cartão de Refeição:** {subs_alimentacao:.2f} €")

# ----------------------------------------------------
# 4. GERAR RECIBO DE VENCIMENTO EM PDF
# ----------------------------------------------------
with aba[3]:
    st.subheader("📄 Emitir Recibo de Vencimento em PDF")
    st.caption("Gera uma folha de ordenado em PDF idêntica à da Triangle com base nos teus dados.")
    
    mes_pdf = st.text_input("Mês / Ano do Recibo", value="Agosto/2026")
    dias_pdf = st.number_input("Dias de Subsídio de Alimentação", value=22, min_value=1)
    hextra_pdf = st.number_input("Horas Extra Totais", value=0.0)

    pdf_bytes = gerar_pdf_recibo(dias_pdf, hextra_pdf, mes_ano_str=mes_pdf)
    
    st.download_button(
        label="📥 Descarregar Recibo de Remuneração (PDF)",
        data=pdf_bytes,
        file_name=f"Recibo_Vencimento_{mes_pdf.replace('/', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
