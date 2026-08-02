import streamlit as st

st.set_page_config(
    page_title="Caixa - Calculadora de Horas & Ganhos", 
    page_icon="🏦",
    layout="centered"
)

# --- ESTILO VISUAL / LAYOUT DA CAIXA GERAL DE DEPÓSITOS (CGD) ---
st.markdown("""
    <style>
    /* Fundo geral e cores base da CGD */
    .stApp {
        background-color: #0b1a30;
        color: #ffffff;
    }
    
    /* Cabeçalho / Banner do Banco */
    .cgd-header {
        background: linear-gradient(135deg, #0f2b48 0%, #00529b 100%);
        padding: 20px;
        border-radius: 12px;
        border-bottom: 4px solid #00a3e0;
        margin-bottom: 25px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    .cgd-header h1 {
        color: #ffffff !important;
        font-family: 'Arial', sans-serif;
        font-weight: 700;
        margin: 0;
        font-size: 24px;
    }
    
    .cgd-header p {
        color: #00a3e0 !important;
        margin-top: 5px;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 1px;
    }

    /* Cartões de resultado no estilo das caixas da app CGD */
    div[data-testid="stMetric"], .stSuccess, .stInfo, .stWarning {
        background-color: #132743 !important;
        border: 1px solid #1d3b66 !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }
    
    /* Destaque para o valor ganho */
    .cgd-card-total {
        background: linear-gradient(90deg, #00529b 0%, #0072ce 100%);
        padding: 18px;
        border-radius: 10px;
        text-align: center;
        margin-top: 15px;
        box-shadow: 0 4px 10px rgba(0,82,155,0.4);
    }
    
    .cgd-card-total h2 {
        color: #ffffff !important;
        margin: 0;
        font-size: 22px;
    }

    /* Ajuste da barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #081220 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABEÇALHO COM ESTILO CGD ---
st.markdown("""
    <div class="cgd-header">
        <h1>🏦 Caixagest | Simulador de Horas</h1>
        <p>CAIXA GERAL DE DEPÓSITOS</p>
    </div>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÃO DE SUBSÍDIO ---
st.sidebar.header("⚙️ Definir Subsídio")
opcao_sa = st.sidebar.radio(
    "Modalidade do Subsídio de Alimentação:",
    ["Cartão de Refeição (10.20€)", "Em Dinheiro / Salário (8.81€)"]
)

sa_dia = 10.20 if "Cartão" in opcao_sa else 8.81

# VALORES BASE E HORAS EXTRA (COM 11% SS)
BASE_HORA_LIQ = 5.31 * 0.89   # ~4.73€
EXTRA_HORA_LIQ = (5.31 * 1.5) * 0.89 # ~7.09€
GANHO_8H_BASE = 8 * BASE_HORA_LIQ    # ~37.81€

# --- SEÇÃO 1: SIMULADOR DIÁRIO ---
st.subheader("1. Simular Movimento do Dia")

col1, col2 = st.columns(2)

with col1:
    tipo_dia = st.selectbox("Tipo de Dia", ["Dia Útil (Segunda a Sexta)", "Sábado"])

with col2:
    horas_extra = st.number_input(
        "Horas Extra",
        min_value=0.0,
        max_value=14.0,
        value=0.0,
        step=0.5
    )

if tipo_dia == "Dia Útil (Segunda a Sexta)":
    ganho_base_dia = GANHO_8H_BASE + sa_dia
    ganho_extra = horas_extra * EXTRA_HORA_LIQ
    total_dia = ganho_base_dia + ganho_extra
    
    st.info(f"🔹 **Dia Normal (8h + SA):** {ganho_base_dia:.2f} €")
    if horas_extra > 0:
        st.info(f"⚡ **Acréscimo Extra ({horas_extra}h):** +{ganho_extra:.2f} €")
else:
    ganho_extra = horas_extra * EXTRA_HORA_LIQ
    total_dia = ganho_extra + sa_dia
    
    st.info(f"⚡ **Trabalho ao Sábado ({horas_extra}h):** {ganho_extra:.2f} €")
    st.info(f"🍲 **Subsídio de Alimentação:** +{sa_dia:.2f} €")

# Cartão de Resultado estilo CGD
st.markdown(f"""
    <div class="cgd-card-total">
        <span style="font-size: 14px; opacity: 0.9;">CRÉDITO ESTIMADO DO DIA</span>
        <h2>+ {total_dia:.2f} €</h2>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br><hr>", unsafe_allow_html=True)

# --- SEÇÃO 2: OBJETIVO MENSAAL ---
st.subheader("2. Planeamento de Objetivos Mensais")

meta_mensal = st.number_input("Objetivo Líquido Mensal (€)", value=1090.0, step=10.0)
dias_trabalho_mes = st.number_input("Dias Úteis Trabalhados", value=22, min_value=1)
acumulado_atual = st.number_input("Saldo Acumulado no Mês (€)", value=0.0, step=10.0)

base_mes_garantido = (dias_trabalho_mes * (GANHO_8H_BASE + sa_dia)) + acumulado_atual
falta_para_meta = meta_mensal - base_mes_garantido

st.write(f"💳 **Garantido em Dias Úteis ({dias_trabalho_mes} dias):** {base_mes_garantido:.2f} €")

if falta_para_meta <= 0:
    st.balloons()
    st.success("🎉 Objetivo atingido! O valor garantido dos dias normais cumpre a tua meta mensal.")
else:
    horas_extra_totais = falta_para_meta / EXTRA_HORA_LIQ
    horas_extra_por_dia = horas_extra_totais / dias_trabalho_mes
    
    st.warning(f"Faltam **{falta_para_meta:.2f} €** para cumprir o objetivo de {meta_mensal:.0f}€.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric(label="Horas Extra Necessárias", value=f"{horas_extra_totais:.1f} h")
    with c2:
        st.metric(label="Média p/ Dia Útil", value=f"{horas_extra_por_dia:.1f} h/dia")
