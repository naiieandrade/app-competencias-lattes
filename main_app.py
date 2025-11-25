# main_app.py — Portal principal do painel CGEE INCT
import streamlit as st
import pandas as pd
from pathlib import Path
import app_inct
import app_area


def do_rerun():
    """Compatível com Streamlit novas e antigas."""
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()


# ==========================
# ESTÁGIOS: home -> login -> app
# ==========================

def pagina_inicial():
    st.title("📊 Painel CGEE INCT")
    st.markdown("""
    Bem-vindo(a) ao **Painel de Competências Lattes** do CGEE.

    Aqui você poderá explorar:
    - Redes de colaboração entre pesquisadores
    - Produção científica por INCT e por Área
    - Distribuição geográfica e formações
    """)

    st.info("O acesso é restrito a usuários autorizados do CGEE.")

    if st.button("Prosseguir para login"):
        st.session_state["stage"] = "login"
        do_rerun()


def tela_login():
    st.header("🔐 Acesso restrito")

    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        # pegue essas credenciais de st.secrets ou hard-code por enquanto
        user_ok = username == st.secrets["username"]
        pass_ok = password == st.secrets["password"]

        if user_ok and pass_ok:
            st.session_state["logged_in"] = True
            st.session_state["stage"] = "app"
            do_rerun()
        else:
            st.error("Usuário ou senha incorretos.")


# --------- Controle de fluxo ---------
if "stage" not in st.session_state:
    st.session_state["stage"] = "home"

if st.session_state["stage"] == "home":
    pagina_inicial()
    st.stop()

if not st.session_state.get("logged_in", False):
    tela_login()
    st.stop()


# ==================== REMOVER BARRA DO STREAMLIT (PRODUÇÃO) ====================
st.set_page_config(
    page_title="Painel de Competências",# page_icon="🧬",
    layout="wide",
    menu_items={
        "Get help": None,
        "Report a bug": None,
        "About": None,
    }
)

HIDE_STREAMLIT_STYLE = """
<style>
/* Remove toolbar superior (inclui botão Deploy) */
[data-testid="stToolbar"] {
    visibility: hidden !important;
    height: 0 !important;
    position: fixed;
    top: -100px;
}

/* Remove menu hambúrguer */
#MainMenu {visibility: hidden !important;}

/* Remove footer "Made with Streamlit" */
footer {visibility: hidden !important;}

/* Remove header padrão */
header {visibility: hidden !important;}
</style>
"""
st.markdown(HIDE_STREAMLIT_STYLE, unsafe_allow_html=True)
# ============================================================================== 


# Header visual
for _p in [Path("header_cgee.png"), Path("imgs/header_cgee.png"), Path("/mnt/data/header_cgee.png")]:
    if _p.exists():
        st.image(str(_p), width="stretch")
        break
st.markdown("<style>.block-container{padding-top:0.5rem;}</style>", unsafe_allow_html=True)

def gap(px=24):
    st.markdown(f"<div style='height:{px}px'></div>", unsafe_allow_html=True)

# ========== LEITURA DAS BASES ==========
@st.cache_data(show_spinner=False)
def load_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

CATALOGO_PATH = "bases/select_incts_areas_coord_sexo.csv"
catalogo = load_csv(CATALOGO_PATH)

# ========== CABEÇALHO ==========
#st.title("Rede de Competências Lattes")
#st.markdown("### 🔍 Escolha o tipo de painel que deseja explorar")

st.markdown(
    """
    <h1 style="text-align:center; margin-top:0.25rem;">
        Rede de Competências Lattes
    </h1>
    """,
    #  <h3 style="text-align:center; font-weight:400; margin-top:0.5rem;">
    #     🔍 Escolha o tipo de painel que deseja explorar
    # </h3>
    unsafe_allow_html=True,
)
st.markdown("#### 🔍 Escolha o tipo de painel que deseja explorar")


# ======== FILTRO PRINCIPAL (no topo) ========
c1, c2 = st.columns([2, 7])

with c1:
    filtro_tipo = st.radio(
        "Filtrar por:",
        ["INCT", "Área"],
        horizontal=True,
        label_visibility="collapsed",
        key="tipo_painel"
    )

with c2:
    if filtro_tipo == "INCT":
        inct_sel = st.selectbox(
            "Selecione o INCT",
            sorted(catalogo["nome_inct"].unique()),
            index=None,
            placeholder="Escolha um INCT..."
        )
        df_filtrado = catalogo[catalogo["nome_inct"] == inct_sel]

    else:  # filtro por área
        area_sel = st.selectbox(
            "Selecione a Área",
            sorted(catalogo["area"].unique()),
            index=None,
            placeholder="Escolha uma Área..."
        )
        df_filtrado = catalogo[catalogo["area"] == area_sel]

if df_filtrado.empty:
    st.info("👆 Escolha um INCT ou uma Área para visualizar os dados.")
    st.stop()

# uso
#st.plotly_chart(fig1, width='stretch')
gap(16)
#st.plotly_chart(fig2, width='stretch')


# ========== DIRECIONAMENTO ==========
if filtro_tipo == "INCT" and inct_sel:
    app_inct.run(inct_sel, df_filtrado)
elif filtro_tipo == "Área" and area_sel:
    app_area.run(area_sel, df_filtrado)
