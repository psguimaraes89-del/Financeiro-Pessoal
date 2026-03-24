# ============================================================
#  DASHBOARD FINANCEIRO PESSOAL — Streamlit
#  Versão 1.0 | Março 2026
#  Deploy: streamlit.io
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, datetime
import os

# ── CONFIG DA PÁGINA ─────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Financeiro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS CUSTOM ───────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f0f1a; }
    .block-container { padding: 1.5rem 2rem; }
    .kpi-card {
        background: #16213e;
        border-radius: 12px;
        padding: 18px 16px;
        text-align: center;
        border-left: 4px solid #2980B9;
        margin-bottom: 8px;
    }
    .kpi-label { color: #A0A0B0; font-size: 13px; font-weight: 500; margin: 0; }
    .kpi-value { font-size: 22px; font-weight: 700; margin: 4px 0; }
    .kpi-sub   { color: #A0A0B0; font-size: 11px; margin: 0; }
    .verde   { color: #27AE60; }
    .vermelho{ color: #E74C3C; }
    .laranja { color: #E67E22; }
    .azul    { color: #2980B9; }
    .secao   { color: #EAEAEA; font-size: 15px; font-weight: 600;
               border-left: 3px solid #2980B9; padding-left: 10px;
               margin: 20px 0 10px 0; }
    div[data-testid="stMetricValue"] { font-size: 22px !important; }
    .stDataFrame { background: #16213e; }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTES ───────────────────────────────────────────────
ARQUIVO = "lancamentos.csv"

CATEGORIAS = [
    "Alimentação","Habitação","Cartão CC","Educação","Tabacaria",
    "Lazer","Vestuário","Refeição","Transporte","Saúde","Serviços",
    "Moto","Carro","Investimento","Presente","Streaming","Doação","Outros"
]
BANCOS = ["Inter","NBK","Dinheiro","Outro"]
FORMAS = ["Débito","Crédito","Pix","Dinheiro","TED/DOC"]
TIPOS  = ["Saída","Entrada","Transferência"]

ORCAMENTO = {
    "Alimentação":   800,
    "Habitação":    1300,
    "Cartão CC":    1000,
    "Educação":      400,
    "Tabacaria":     300,
    "Lazer":         300,
    "Vestuário":     200,
    "Refeição":      200,
    "Transporte":    150,
    "Saúde":         150,
    "Serviços":      150,
    "Moto":          100,
    "Carro":         200,
    "Investimento":  300,
    "Outros":        200,
}

VERDE    = "#27AE60"
VERMELHO = "#E74C3C"
LARANJA  = "#E67E22"
AZUL     = "#2980B9"
DARK     = "#0f0f1a"
CARD_BG  = "#16213e"
GRID     = "#2a2a4a"
TEXT     = "#EAEAEA"
SUBTEXT  = "#A0A0B0"

MESES_LABEL = {
    "2026-01":"Jan/26","2026-02":"Fev/26","2026-03":"Mar/26",
    "2026-04":"Abr/26","2026-05":"Mai/26","2026-06":"Jun/26",
    "2026-07":"Jul/26","2026-08":"Ago/26","2026-09":"Set/26",
    "2026-10":"Out/26","2026-11":"Nov/26","2026-12":"Dez/26",
}

# ── DADOS ────────────────────────────────────────────────────
@st.cache_data(ttl=5)
def carregar():
    if os.path.exists(ARQUIVO):
        df = pd.read_csv(ARQUIVO, parse_dates=["Data"])
    else:
        df = pd.DataFrame(columns=[
            "Data","Competência","Tipo","Categoria","Subcategoria",
            "Lugar","Banco","Forma","Valor","Observação"
        ])
        df.to_csv(ARQUIVO, index=False)
    return df

def salvar(df):
    df.to_csv(ARQUIVO, index=False)
    st.cache_data.clear()

# ── HELPERS ──────────────────────────────────────────────────
def cor_taxa(t):
    if t <= 80:  return VERDE
    if t <= 100: return LARANJA
    return VERMELHO

def emoji_taxa(t):
    if t <= 80:  return "🟢"
    if t <= 100: return "🟡"
    return "🔴"

def fmt_brl(v): return f"R$ {v:,.2f}"

def plot_bg():
    return dict(paper_bgcolor=CARD_BG, plot_bgcolor=DARK,
                font=dict(color=TEXT, size=12),
                margin=dict(l=8, r=8, t=38, b=8),
                xaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
                yaxis=dict(gridcolor=GRID, zerolinecolor=GRID))

# ── SIDEBAR ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💼 Financeiro Pessoal")
    st.markdown(f"*{datetime.now().strftime('%d/%m/%Y  %H:%M')}*")
    st.divider()

    st.markdown("### 🔍 Filtros")
    df_raw = carregar()

    periodos_disp = sorted(df_raw["Competência"].unique().tolist()) if len(df_raw) > 0 else []
    opcoes_periodo = ["Acumulado"] + [MESES_LABEL.get(p, p) for p in periodos_disp]
    periodo_sel = st.selectbox("Período", opcoes_periodo)

    cat_sel   = st.selectbox("Categoria", ["Todas"] + CATEGORIAS)
    banco_sel = st.selectbox("Banco/Conta", ["Todos"] + BANCOS)
    tipo_sel  = st.selectbox("Tipo", ["Todos","Entrada","Saída"])

    st.divider()
    st.markdown("### ➕ Novo Lançamento")

    with st.form("form_lancamento", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            inp_data = st.date_input("Data", value=date.today())
            inp_tipo = st.selectbox("Tipo", TIPOS)
            inp_cat  = st.selectbox("Categoria", CATEGORIAS)
        with col2:
            inp_banco = st.selectbox("Banco", BANCOS)
            inp_forma = st.selectbox("Forma Pag.", FORMAS)
            inp_valor = st.number_input("Valor (R$)", min_value=0.01, step=0.01, format="%.2f")

        inp_lugar = st.text_input("Lugar/Estabelecimento")
        inp_obs   = st.text_input("Observação (opcional)")
        submitted = st.form_submit_button("💾 Salvar Lançamento", use_container_width=True)

        if submitted:
            v = float(inp_valor)
            if inp_tipo == "Saída": v = -v
            comp = pd.to_datetime(inp_data).strftime("%Y-%m")
            novo = pd.DataFrame([{
                "Data": pd.to_datetime(inp_data),
                "Competência": comp,
                "Tipo": inp_tipo,
                "Categoria": inp_cat,
                "Subcategoria": "",
                "Lugar": inp_lugar,
                "Banco": inp_banco,
                "Forma": inp_forma,
                "Valor": v,
                "Observação": inp_obs
            }])
            df_atual = carregar()
            df_novo  = pd.concat([df_atual, novo], ignore_index=True)
            salvar(df_novo)
            st.success(f"✅ {inp_cat} — {fmt_brl(abs(v))}")

# ── FILTRAR DADOS ─────────────────────────────────────────────
df = carregar()

if periodo_sel != "Acumulado":
    comp_rev = {v:k for k,v in MESES_LABEL.items()}
    comp_key = comp_rev.get(periodo_sel, periodo_sel)
    df = df[df["Competência"] == comp_key]

if cat_sel != "Todas":
    df = df[df["Categoria"] == cat_sel]
if banco_sel != "Todos":
    df = df[df["Banco"] == banco_sel]
if tipo_sel != "Todos":
    df = df[df["Tipo"] == tipo_sel]

# ── CÁLCULO KPIs ─────────────────────────────────────────────
entradas = df[df["Valor"] > 0]["Valor"].sum()
saidas   = abs(df[df["Valor"] < 0]["Valor"].sum())
saldo    = entradas - saidas
taxa     = (saidas / entradas * 100) if entradas > 0 else 0
cc       = abs(df[(df["Valor"]<0) & (df["Categoria"]=="Cartão CC")]["Valor"].sum())
n_comp   = max(len(df[df["Valor"]<0]), 1)
ticket   = saidas / n_comp
invest   = abs(df[(df["Valor"]<0) & (df["Categoria"]=="Investimento")]["Valor"].sum())

# ── HEADER ───────────────────────────────────────────────────
st.markdown("## 💼 Dashboard Financeiro Pessoal")
st.caption(f"Período: **{periodo_sel}** · {len(df)} lançamentos · Atualizado agora")
st.divider()

# ── KPIs ─────────────────────────────────────────────────────
k1, k2, k3, k4, k5, k6 = st.columns(6)

def delta_fmt(v, ref):
    d = v - ref
    return f"{'+' if d>=0 else ''}{fmt_brl(d)}"

with k1:
    st.metric("📥 Receita", fmt_brl(entradas))
with k2:
    st.metric("📤 Saída Total", fmt_brl(saidas))
with k3:
    cor = "normal" if saldo >= 0 else "inverse"
    st.metric("💰 Saldo", fmt_brl(saldo))
with k4:
    st.metric(f"{emoji_taxa(taxa)} Comprometimento", f"{taxa:.1f}%",
              delta=f"Meta ≤80%", delta_color="off")
with k5:
    st.metric("💳 Cartão CC", fmt_brl(cc))
with k6:
    st.metric("🧾 Ticket Médio", fmt_brl(ticket))

st.divider()

# ── GRÁFICO 1 + 2 ────────────────────────────────────────────
g1, g2 = st.columns([2, 1])

with g1:
    st.markdown('<p class="secao">📈 Fluxo Mensal</p>', unsafe_allow_html=True)
    df_mes = df_raw.groupby("Competência").apply(lambda x: pd.Series({
        "Receita": x[x["Valor"]>0]["Valor"].sum(),
        "Saída":   abs(x[x["Valor"]<0]["Valor"].sum()),
    })).reset_index()
    df_mes["Saldo"]      = df_mes["Receita"] - df_mes["Saída"]
    df_mes["Saldo_acum"] = df_mes["Saldo"].cumsum()
    df_mes["Label"]      = df_mes["Competência"].map(lambda x: MESES_LABEL.get(x, x))

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(name="Receita", x=df_mes["Label"], y=df_mes["Receita"],
        marker_color=VERDE, opacity=0.85))
    fig1.add_trace(go.Bar(name="Saída", x=df_mes["Label"], y=df_mes["Saída"],
        marker_color=VERMELHO, opacity=0.85))
    fig1.add_trace(go.Scatter(name="Saldo Acum.", x=df_mes["Label"], y=df_mes["Saldo_acum"],
        mode="lines+markers", line=dict(color=AZUL, width=2, dash="dot"),
        marker=dict(size=8),
        text=[fmt_brl(v) for v in df_mes["Saldo_acum"]],
        textposition="top center"))
    fig1.update_layout(**plot_bg(), barmode="group", height=300,
        legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center",
                    bgcolor="rgba(0,0,0,0)"))
    fig1.update_yaxes(tickprefix="R$")
    st.plotly_chart(fig1, use_container_width=True)

with g2:
    st.markdown('<p class="secao">🎯 Comprometimento</p>', unsafe_allow_html=True)
    df_mes["Taxa"] = df_mes["Saída"] / df_mes["Receita"] * 100
    cores_b = [cor_taxa(t) for t in df_mes["Taxa"]]
    fig2 = go.Figure(go.Bar(
        x=df_mes["Label"], y=df_mes["Taxa"],
        marker_color=cores_b,
        text=[f"{t:.1f}%" for t in df_mes["Taxa"]],
        textposition="outside"
    ))
    fig2.add_hline(y=100, line_dash="dash", line_color=VERMELHO, line_width=1.5,
        annotation_text="100%", annotation_font_color=VERMELHO)
    fig2.add_hline(y=80, line_dash="dot", line_color=VERDE, line_width=1.5,
        annotation_text="80%", annotation_font_color=VERDE)
    fig2.update_layout(**plot_bg(), height=300)
    fig2.update_yaxes(range=[0, 135], ticksuffix="%")
    st.plotly_chart(fig2, use_container_width=True)

# ── GRÁFICO 3 + 4 ────────────────────────────────────────────
g3, g4 = st.columns([3, 2])

with g3:
    st.markdown('<p class="secao">🏷️ Gastos por Categoria</p>', unsafe_allow_html=True)
    df_cat = df[df["Valor"]<0].groupby("Categoria")["Valor"].sum().abs().sort_values()
    if len(df_cat) > 0:
        pct_s = [v/saidas*100 if saidas>0 else 0 for v in df_cat.values]
        pct_r = [v/entradas*100 if entradas>0 else 0 for v in df_cat.values]
        cores_c = [VERMELHO if p>15 else LARANJA if p>5 else AZUL for p in pct_s]
        fig3 = go.Figure(go.Bar(
            x=list(df_cat.values), y=list(df_cat.index),
            orientation="h", marker_color=cores_c,
            text=[f"R${v:,.0f}  ({ps:.1f}% saída / {pr:.1f}% renda)"
                  for v,ps,pr in zip(df_cat.values, pct_s, pct_r)],
            textposition="outside"
        ))
        fig3.update_layout(**plot_bg(), height=370)
        fig3.update_xaxes(range=[0, max(df_cat.values)*1.55], tickprefix="R$")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Sem dados de saída no período.")

with g4:
    st.markdown('<p class="secao">📊 Orçado vs Realizado</p>', unsafe_allow_html=True)
    df_orc = df[df["Valor"]<0].groupby("Categoria")["Valor"].sum().abs().reset_index()
    df_orc.columns = ["Categoria","Realizado"]
    df_orc["Orçado"] = df_orc["Categoria"].map(lambda c: ORCAMENTO.get(c, 0))
    df_orc = df_orc[df_orc["Orçado"] > 0].sort_values("Realizado")
    if len(df_orc) > 0:
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(name="Orçado", x=df_orc["Orçado"], y=df_orc["Categoria"],
            orientation="h", marker_color="#3a3a6a", opacity=0.75))
        fig4.add_trace(go.Bar(name="Realizado", x=df_orc["Realizado"], y=df_orc["Categoria"],
            orientation="h",
            marker_color=[VERMELHO if r>o else VERDE
                          for r,o in zip(df_orc["Realizado"],df_orc["Orçado"])]))
        fig4.update_layout(**plot_bg(), barmode="overlay", height=370,
            legend=dict(orientation="h", y=1.08, x=0.5, xanchor="center",
                        bgcolor="rgba(0,0,0,0)"))
        fig4.update_xaxes(tickprefix="R$")
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Sem dados para orçamento.")

# ── GRÁFICO 5 + 6 ────────────────────────────────────────────
g5, g6 = st.columns(2)

with g5:
    st.markdown('<p class="secao">📅 Gasto Diário</p>', unsafe_allow_html=True)
    df_dia = df[df["Valor"]<0].copy()
    if len(df_dia) > 0:
        df_dia["Dia"] = df_dia["Data"].dt.day
        df_dg = df_dia.groupby("Dia")["Valor"].sum().abs().reset_index()
        fig5 = go.Figure(go.Bar(
            x=df_dg["Dia"], y=df_dg["Valor"],
            marker_color=AZUL, opacity=0.8,
            text=[f"R${v:,.0f}" for v in df_dg["Valor"]],
            textposition="outside"
        ))
        fig5.update_layout(**plot_bg(), height=280)
        fig5.update_xaxes(title_text="Dia", dtick=5)
        fig5.update_yaxes(tickprefix="R$")
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("Sem saídas no período.")

with g6:
    st.markdown('<p class="secao">🏦 Saída por Banco</p>', unsafe_allow_html=True)
    df_banco = df[df["Valor"]<0].groupby("Banco")["Valor"].sum().abs()
    if len(df_banco) > 0:
        fig6 = go.Figure(go.Pie(
            labels=df_banco.index, values=df_banco.values,
            hole=0.45, textinfo="label+percent",
            marker=dict(colors=[AZUL, LARANJA, VERDE, VERMELHO, SUBTEXT])
        ))
        fig6.update_layout(paper_bgcolor=CARD_BG, plot_bgcolor=DARK,
            font=dict(color=TEXT, size=12), height=280,
            margin=dict(l=8,r=8,t=8,b=8),
            legend=dict(orientation="h", y=-0.12, x=0.5, xanchor="center",
                        bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.info("Sem dados no período.")

# ── SAÚDE FINANCEIRA ─────────────────────────────────────────
st.divider()
st.markdown('<p class="secao">🏥 Relatório de Saúde Financeira</p>', unsafe_allow_html=True)

s1, s2, s3, s4 = st.columns(4)

status_comp = "🔴 CRÍTICO" if taxa > 100 else "🟡 ATENÇÃO" if taxa > 80 else "🟢 SAUDÁVEL"
status_saldo = "🟢 POSITIVO" if saldo >= 0 else "🔴 DÉFICIT"

with s1:
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-label">Status Geral</p>
        <p class="kpi-value">{status_comp}</p>
        <p class="kpi-sub">Comprometimento: {taxa:.1f}%</p>
    </div>""", unsafe_allow_html=True)

with s2:
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-label">Saldo do Período</p>
        <p class="kpi-value {'verde' if saldo>=0 else 'vermelho'}">{fmt_brl(saldo)}</p>
        <p class="kpi-sub">{status_saldo}</p>
    </div>""", unsafe_allow_html=True)

with s3:
    sobra_meta = entradas * 0.20 - (entradas - saidas)
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-label">Distância da Meta (80%)</p>
        <p class="kpi-value laranja">{fmt_brl(abs(entradas*0.20 - saldo))}</p>
        <p class="kpi-sub">{'Acima do ideal' if taxa > 80 else 'Dentro da meta'}</p>
    </div>""", unsafe_allow_html=True)

with s4:
    maior_cat = df[df["Valor"]<0].groupby("Categoria")["Valor"].sum().abs().idxmax() if len(df[df["Valor"]<0])>0 else "—"
    maior_val = df[df["Valor"]<0].groupby("Categoria")["Valor"].sum().abs().max() if len(df[df["Valor"]<0])>0 else 0
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-label">Maior Gasto</p>
        <p class="kpi-value vermelho">{maior_cat}</p>
        <p class="kpi-sub">{fmt_brl(maior_val)}</p>
    </div>""", unsafe_allow_html=True)

# ── TABELA ───────────────────────────────────────────────────
st.divider()
st.markdown('<p class="secao">📋 Lançamentos</p>', unsafe_allow_html=True)

df_tab = df.sort_values("Data", ascending=False).copy()
df_tab["Data"]  = df_tab["Data"].dt.strftime("%d/%m/%Y")
df_tab["Valor"] = df_tab["Valor"].apply(fmt_brl)

st.dataframe(
    df_tab[["Data","Tipo","Categoria","Lugar","Banco","Forma","Valor","Observação"]],
    use_container_width=True,
    height=350,
    hide_index=True
)

# ── FOOTER ───────────────────────────────────────────────────
st.divider()
st.caption("💼 Dashboard Financeiro Pessoal · Dados em lancamentos.csv · Atualiza a cada lançamento")
