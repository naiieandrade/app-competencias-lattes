# app_inct.py — Painel por INCT
import streamlit as st
import io, json
import pandas as pd
from pathlib import Path
import plotly.express as px
import networkx as nx
from pyvis.network import Network
import plotly.graph_objects as go

import matplotlib.pyplot as plt
#import matplotlib
#matplotlib.use("Agg")   # garante renderização estática

from wordcloud import WordCloud

import plotly.io as pio
pio.renderers.default = "browser"

# ============================ FUNÇÕES AUXILIARES ============================

def gap(px=24):
    st.markdown(f"<div style='height:{px}px'></div>", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

@st.cache_data(show_spinner=False)
def load_cached_html(html_path: str) -> str | None:
    """Carrega HTML pré-gerado do grafo (PyVis) se existir."""
    p = Path(html_path)
    if p.exists():
        return p.read_text(encoding="utf-8")
    return None
    
def run(inct_sel: str, df_filtrado: pd.DataFrame):

    # === CSS global (adicione uma vez no topo do app) ===
    st.markdown("""
    <style>
    .card {
      background: #f9fafb;               /* fundo leve */
      padding: 16px 18px;
      border-radius: 16px;
      border: 1px solid #e9edf3;
      box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    }
    .card h4 {
      margin: 0 0 0.5rem 0;
      font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)
        
    # ======================== IO ============================    
    INST_PATH     = "bases/select_instituicoes_por_inct.csv"
    PROD_BBL_PATH = "bases/big_number_qtd_producao_bibliografica_periodo.csv"
    MAIOR_FORMACAO_PATH = "bases/big_number_maior_formacao.csv"
    PALAVRAS_WORDCLOUD_PATH = "bases/wordcloud_inct_agg.csv"
    TEXTO_PATH = "bases/texto_descricao_inct.csv"
    
    df_inst  = load_csv(INST_PATH)
    prod_bbl = load_csv(PROD_BBL_PATH)
    maior_formacoes = load_csv(MAIOR_FORMACAO_PATH)
    palavras_wc_inct = load_csv(PALAVRAS_WORDCLOUD_PATH)
    df_texto_inct = load_csv(TEXTO_PATH)

    info = df_filtrado.iloc[0]

    # ======================== HELPERS KPI ===================
    def safe_int(x):
        try:
            return int(x)
        except Exception:
            return 0
    
    def get_val(df, tipo, periodo):
        """Retorna n_tipos_producao para um tipo/periodo (ou 0)."""
        if df is None or df.empty:
            return 0
        sub = df[(df["tipo_producao"] == tipo) & (df["periodo"] == periodo)]["n_tipos_producao"]
        return safe_int(sub.iloc[0]) if not sub.empty else 0

    
    # ======================== INFOS INCT ===================
    """Renderiza o painel do INCT selecionado"""
    #st.markdown(f"## 🧬 Painel — {inct_sel}")
    st.markdown(f"## Painel — {inct_sel}")

    st.markdown("")
    st.markdown(f"**Área:** {info['area']}")
    st.markdown(f"**Coordenador:** {info['coordenador']}")
    #st.markdown("---")
    st.markdown("")

    left, right = st.columns([2, 2])
    with left:
        texto = df_texto_inct.loc[df_texto_inct['nome_inct']==inct_sel]['texto_descricao'].iloc[0]
        if pd.notna(texto) and texto.strip():
            st.write(texto)
        else:
            st.info("📄 Nenhuma descrição disponível para este INCT.")

        texto_estatisticas = df_texto_inct.loc[df_texto_inct['nome_inct']==inct_sel]['texto_estatisticas'].iloc[0]
        if pd.notna(texto_estatisticas) and texto_estatisticas.strip():
            st.write(texto_estatisticas)
        else:
            st.write("")

        texto_comparativos = df_texto_inct.loc[df_texto_inct['nome_inct']==inct_sel]['texto_comparativos'].iloc[0]
        if pd.notna(texto_comparativos) and texto_comparativos.strip():
            st.write(texto_comparativos)
        else:
            st.write("")

        texto_indicadores = df_texto_inct.loc[df_texto_inct['nome_inct']==inct_sel]['texto_indicadores'].iloc[0]
        if pd.notna(texto_indicadores) and texto_indicadores.strip():
            st.write(texto_indicadores)
        else:
            st.write("")

    # ====== GRAFO INTERATIVO (GEXF) ======
    with right:

        path_gexf = info.get("path_gexf_html", "")
        html_cached_path = f"gexf_html/{Path(path_gexf).stem}.html"
    
        html = load_cached_html(html_cached_path)
    
        if html:
            st.components.v1.html(
                f"""
                <iframe srcdoc='{html.replace("'", "&apos;")}'
                        style="width:100%; height:950px; border:none; overflow:hidden;">
                </iframe>
                """,
                height=960,
                scrolling=False
            )
        else:
            st.info(f"📁 Grafo ainda não foi pré-gerado. Arquivo esperado: `{html_cached_path}`")


    # ====== SANKEY (pré-gerado, centralizado e em card) ======
    # st.divider()
    st.subheader("Fluxo Sankey — Palavras-chave por Período")

    
    sankey_path = Path(f"sankey_inct_palavra_tratada/sankey_inct_{info['Identificador']}.html")
    
    with st.container(border=True):
        if sankey_path.exists():
            try:
                # Lê o HTML do Sankey
                html = open(sankey_path, encoding="utf-8").read()
    
                # Centraliza o gráfico com um container interno
                sankey_html = f"""
                <div style="
                    width: 100%;
                    overflow-x: auto;
                    padding: 10px;
                    background-color: #fff;
                    text-align: center;
                ">
                    <div style="
                        display: inline-block;
                        min-width: 900px;
                        width: max-content;    /* largura = largura real do gráfico */
                    ">
                        {html}
                    </div>
                </div>
                """
    
                # Exibe dentro do card
                st.components.v1.html(
                    sankey_html,
                    height=1000,  # altura padrão ajustada
                    scrolling=False,  # rolagem interna automática
                )
            except Exception as e:
                st.warning(f"⚠️ Erro ao carregar o gráfico Sankey: {e}")
        else:
            st.info("Nenhum gráfico Sankey disponível para este INCT.")

    # ====================== CARDS: WORDCLOUD | MAIOR FORMAÇÃO ======================
    # ====================== CARDS: WORDCLOUD | MAIOR FORMAÇÃO ======================
    import matplotlib
    matplotlib.use("Agg")  # garante renderização estática
    
    # ---------- CARD 1: WORDCLOUD ----------
    col_wc, col_form = st.columns(2, gap="medium")
    
    with col_wc:
        with st.container(border=True):
            st.markdown("#### Nuvem de Palavras")
    
            # ---------------------------------------------
            # 🔹 FILTRO DIRETO NA BASE AGREGADA
            # ---------------------------------------------
            wc_sel = palavras_wc_inct[palavras_wc_inct["nome_inct"] == inct_sel]
    
            if wc_sel.empty:
                st.warning("Nenhuma palavra encontrada para este INCT.")
            else:
                # Remove stopwords simples
                STOPWORDS_ONEWORD = {
                    "de","da","do","das","dos","em","no","na","nas","nos","para","por",
                    "e","a","o","os","as","um","uma","com","ao","aos","se","que",
                    "sobre","entre","ou","como"
                }
    
                # Mantém as palavras + remove conectivos isolados
                s = wc_sel["palavra"].astype(str)
                mascara_um_termo = ~s.str.contains(r"\s")
                palavras_validas = s[~(mascara_um_termo & s.isin(STOPWORDS_ONEWORD))]
    
                # Juntar novamente com df original para manter a coluna freq
                wc_filtrado = wc_sel.loc[palavras_validas.index]
    
                # ---------------------------------------------
                # 🔹 Freq já vem pronta (coluna `freq`)
                # ---------------------------------------------
                freqs = dict(
                    zip(
                        wc_filtrado["palavra"],
                        wc_filtrado["freq"]
                    )
                )
    
                if not freqs:
                    st.warning("Nenhuma palavra disponível após filtragem.")
                else:
    
                    top_n = st.slider(
                        "Número de expressões exibidas",
                        min_value=10,
                        max_value=300,
                        value=30,
                        step=10,
                        key=f"slider_wc_{inct_sel}",
                    )
    
                    # Ordena e pega o top_n
                    freqs_top = dict(
                        sorted(freqs.items(), key=lambda x: x[1], reverse=True)[:top_n]
                    )
    
                    # === Gera a wordcloud diretamente das frequências ===
                    wc = WordCloud(
                        width=900,
                        height=500,
                        background_color="white",
                        colormap="Blues",
                        collocations=False,
                    ).generate_from_frequencies(freqs_top)
    
                    img_array = wc.to_array()
    
                    st.image(img_array, width="content")

    # ---------- CARD 2: MAIOR FORMAÇÃO ----------
    with col_form:
        with st.container(border=True):
            st.markdown(f"#### Maior Formação por INCT")
    
            df_plot = (
                maior_formacoes[maior_formacoes["nome_inct"] == inct_sel]
                .sort_values("count", ascending=False)
            )
    
            if df_plot.empty:
                st.warning("Nenhuma informação de formação disponível para este INCT.")
            else:
                fig_bar = px.bar(
                    df_plot,
                    x="count", y="area_de_maior_formacao",
                    orientation="h",
                    color="count",
                    color_continuous_scale="Blues",
                    text="count",
                    #title="Maior Formação por INCT",
                    labels={
                        "count": "Quantidade",
                        "area_de_maior_formacao": "Área"
                    },
                )
                fig_bar.update_layout(
                    xaxis_title="Número de Pesquisadores",
                    yaxis_title="Área de Formação",
                    height=420,
                    margin=dict(l=10, r=10, t=30, b=0),
                )
                fig_bar.update_traces(textposition="outside")
    
                # Somente config (nada de kwargs antigos) -> sem avisos
                st.plotly_chart(
                    fig_bar,
                    config={
                        "displayModeBar": True,
                        "displaylogo": False,
                        "responsive": True,
                        #"scrollZoom": True,
                        "scrollZoom": False,
                        "doubleClick": "reset",  # padrão seguro
                        "modeBarButtonsToRemove": [
                                    "zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d",
                                    "zoomOut2d", "resetScale2d" #"autoScale2d",
                                ],
                    },
                )

    # ====== KPIs ======
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.subheader("Valores em destaque")
    
    def safe_int(x):
        try:
            return int(x)
        except Exception:
            return 0
    
    total = safe_int(info.get("n_pesquisadores"))
    fem   = safe_int(info.get("n_feminino"))
    masc  = safe_int(info.get("n_masculino"))
    
    pct_fem = (fem / total * 100) if total else 0.0
    pct_mas = (masc / total * 100) if total else 0.0
    
    # Linha de cards
    c1, c2, c3 = st.columns(3, gap="medium")
    
    with c1:
        with st.container(border=True):
            st.metric("Total de Pesquisadores", f"{total:,}".replace(",", "."))
    
    with c2:
        with st.container(border=True):
            st.metric("Feminino (%)", f"{pct_fem:.1f}%")
    
    with c3:
        with st.container(border=True):
            st.metric("Masculino (%)", f"{pct_mas:.1f}%")
    
    if total == 0:
        st.warning("Sem dados de pesquisadores para este INCT.")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


    # ======================== KPIs: PRODUÇÃO BIBLIOGRÁFICA ===================
    st.divider()
    st.markdown("### Produção Bibliográfica por Período")
    
    import unicodedata
    
    def normalize_text(text):
        """Remove acentos, normaliza hífen e deixa em minúsculas."""
        if pd.isna(text):
            return ""
        text = str(text).strip().lower()
        text = unicodedata.normalize("NFKC", text)
        text = text.replace("–", "-")  # troca hífen especial por simples
        return text
    
    def get_val(df, tipo, periodo):
        """Busca o valor de produção de forma robusta (tolerante a variações)."""
        if df.empty:
            return 0
        tipo_norm = normalize_text(tipo)
        periodo_norm = normalize_text(periodo)
        df["tipo_norm"] = df["tipo_producao"].apply(normalize_text)
        df["periodo_norm"] = df["periodo"].apply(normalize_text)
        val = df.query("tipo_norm == @tipo_norm and periodo_norm == @periodo_norm")["n_tipos_producao"]
        return int(val.iloc[0]) if not val.empty else 0
    
    
    tipos = [
        ("Artigos Publicados",               "Artigo Publicado"),
        ("Trabalhos em Eventos",             "Trabalho Em Eventos"),
        ("Capítulos de Livros",              "Capitulo De Livro Publicado"),
        ("Livros Publicados/Organizados",    "Livro Publicado Ou Organizado"),
        ("Textos em Jornais/Revistas",       "Texto Em Jornal Ou Revista"),
        ("Outras Produções Bibliográficas",  "Outra Producao Bibliografica"),
        ("Artigos Aceitos",                  "Artigo Aceito Para Publicacao"),
        ("Prefácios/Pósfácios",              "Prefacio Posfacio"),
        ("Traduções",                        "Traducao"),
        ("Partituras Musicais",              "Partitura Musical"),
    ]
    
    periodos = ["2010-2015", "2015-2020", "2020-2025"]
    
    df_prod_bbl = (
        prod_bbl[prod_bbl["nome_inct"] == inct_sel].copy()
        if "nome_inct" in prod_bbl.columns
        else pd.DataFrame()
    )
    
    # === Layout responsivo: 2 linhas (5 métricas cada) ===
    for periodo in periodos:
        st.markdown(f"### {periodo}")
        
    
        # Divide os 10 tipos em 2 linhas de 5
        for linha in range(0, len(tipos), 5):
            subset = tipos[linha:linha+5]
    
            with st.container(horizontal=True, gap="medium"):
                cols = st.columns(len(subset), gap="medium")
    
                for i, (titulo, tipo) in enumerate(subset):
                    val = get_val(df_prod_bbl, tipo, periodo)
    
                    with cols[i]:
                        st.metric(
                            label=titulo,
                            value=f"{val:,}".replace(",", "."),
                            label_visibility="visible",
                            width="content",
                        )
                        
        # pequeno espaçamento entre blocos de período
        st.markdown("<br>", unsafe_allow_html=True)


    # ======================== MAPA + TOP INSTITUIÇÕES ===================    
    col1, col2 = st.columns(2, gap="medium")
    
    # --- CARD 1: MAPA ---
    with col1:
        with st.container(border=True):
            st.markdown("#### Distribuição do Endereço Profissional por UF")
            
    
            info_instituicao = df_inst[df_inst["nome_inct"] == inct_sel].copy()
            ufs = [
                "AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT",
                "PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"
            ]
            uf_base = pd.DataFrame({"uf": ufs})
    
            if not info_instituicao.empty:
                uf_counts = (
                    info_instituicao.groupby("uf")["nome_instituicao_empresa"]
                    .count()
                    .reset_index(name="qtd")
                )
            else:
                uf_counts = pd.DataFrame(columns=["uf", "qtd"])
    
            uf_counts = uf_base.merge(uf_counts, on="uf", how="left").fillna(0)
    
            geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    
            fig_mapa = px.choropleth(
                uf_counts,
                geojson=geojson_url,
                locations="uf",
                featureidkey="properties.sigla",
                color="qtd",
                hover_name="uf",
                hover_data={"qtd": True},
                color_continuous_scale="Blues",
                range_color=(0, int(uf_counts["qtd"].max()) if len(uf_counts) else 0),
                #title="Distribuição do Endereço Profissional por UF",
                labels={
                        "uf": "UF",
                        "qtd": "Quantidade de Instituições/Empresas"
                    },
            )
            fig_mapa.update_geos(fitbounds="locations", visible=False, scope="south america")
            fig_mapa.update_layout(
                height=500,
                margin=dict(l=0, r=0, t=40, b=0),
                coloraxis_colorbar=dict(title="Instituições"),
                dragmode=False,
            )
    
            # ✅ NENHUM argumento solto — tudo via config
            st.plotly_chart(
                fig_mapa,
                config={
                    "displayModeBar": True,
                    "scrollZoom": False,
                    "doubleClick": False,
                    "staticPlot": False,  # mantém hover ativo
                    "responsive": True,
                    "plotlyServerURL": "",  # silencia o aviso de kwargs
                },
            )
    
    # --- CARD 2: TOP INSTITUIÇÕES ---
    with col2:
        with st.container(border=True):
            st.markdown("#### Principais Instituições Participantes")
            
    
            if not info_instituicao.empty:
                top_inst = (
                    info_instituicao.groupby("nome_instituicao_empresa")["n_pesquisadores"]
                    .sum()
                    .reset_index()
                    .sort_values("n_pesquisadores", ascending=False)
                    .head(10)
                )
                fig_bar = px.bar(
                    top_inst,
                    x="n_pesquisadores",
                    y="nome_instituicao_empresa",
                    orientation="h",
                    color="n_pesquisadores",
                    color_continuous_scale="Blues",
                    title="Top 10 Instituições",
                    #title="Top Instituições Participantes",
                    text="n_pesquisadores",
                    labels={
                        "nome_instituicao_empresa": "Nome Instituição/Empresa",
                        "n_pesquisadores": "Quantidade de Pesquisadores"
                    },
                )
                fig_bar.update_layout(
                    yaxis=dict(title=""),
                    xaxis_title="Número de Pesquisadores",
                    height=500,
                    margin=dict(l=0, r=0, t=40, b=0),
                )
    
                st.plotly_chart(
                    fig_bar,
                    config={
                        "displayModeBar": True,
                        "displaylogo": False,
                        "modeBarButtonsToRemove": [
                                    "zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d",
                                    "zoomOut2d", "resetScale2d" #"autoScale2d",
                                ],
                        "responsive": True,
                        "scrollZoom": False,
                        "plotlyServerURL": "",
                    },
                )
            else:
                st.warning("Nenhuma instituição registrada para este INCT.")

    # --- CARD - MAIOR GRADUAÇÃO: Gráfico de barras verticais ---    
    with st.container(border=True):
        st.markdown("#### Distribuição das Formações Mais Altas")
        path_grad = "bases/grafico_maior_graduacao_inct.csv"
    
        if Path(path_grad).exists():
            df_grad = pd.read_csv(path_grad)
            df_plot = (
                df_grad[df_grad["nome_inct"] == inct_sel]
                .sort_values("qtd", ascending=False)
            )
    
            if df_plot.empty:
                st.warning("Nenhuma informação de formação disponível para este INCT.")
            else:
                fig_bar_vert = px.bar(
                    df_plot,
                    x="formacao_mais_alta",
                    y="qtd",
                    color="qtd",
                    color_continuous_scale="Blues",
                    text="qtd",
                    labels={
                        "formacao_mais_alta": "Formação mais alta",
                        "qtd": "Pesquisadores"
                    },
                )
                fig_bar_vert.update_layout(
                    xaxis_title="Formação Mais Alta",
                    yaxis_title="Número de Pesquisadores",
                    height=350,
                    margin=dict(l=20, r=20, t=60, b=80),
                )
                fig_bar_vert.update_traces(textposition="outside", cliponaxis=False)
    
                st.plotly_chart(
                    fig_bar_vert,
                    config={
                        "displayModeBar": True,
                        "scrollZoom": False,
                        "displaylogo": False,
                        "responsive": True,
                        "modeBarButtonsToRemove": [
                                    "zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d",
                                    "zoomOut2d", "resetScale2d" #"autoScale2d",
                                ],
                        
                    },
                )
        else:
            st.warning("Base 'grafico_maior_graduacao_inct.csv' não encontrada.")


