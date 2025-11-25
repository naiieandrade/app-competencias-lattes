# app_area.py — Painel por Área
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import networkx as nx
from pyvis.network import Network

from wordcloud import WordCloud

# ==========================================================
# 🧠 FUNÇÕES CACHEADAS
# ==========================================================

@st.cache_data(show_spinner=False)
def load_csv_cached(path: str) -> pd.DataFrame:
    """Lê CSV e guarda em cache"""
    return pd.read_csv(path)

@st.cache_data(show_spinner=False)
def load_cached_html(html_path: str) -> str | None:
    """Carrega HTML pré-gerado do grafo (PyVis) se existir."""
    p = Path(html_path)
    if p.exists():
        return p.read_text(encoding="utf-8")
    return None

@st.cache_data(show_spinner=False)
def load_html_sankey_cached(path: str) -> str:
    """Lê e cacheia o HTML do Sankey"""
    return open(path, encoding="utf-8").read()

# ==========================================================
# 🧩 FUNÇÃO PRINCIPAL
# ==========================================================
def run(area_sel: str, df_filtrado: pd.DataFrame):
    # ======================== IO ============================    
    INST_PATH     = "bases/select_instituicoes_por_inct.csv"
    PROD_BBL_PATH = "bases/big_number_qtd_producao_bibliografica_periodo_area.csv"
    MAIOR_FORMACAO_PATH = "bases/big_number_maior_formacao.csv"
    PALAVRAS_WORDCLOUD_PATH = "bases/wordcloud_area_agg.csv"
    PATH_GRAD = "bases/grafico_maior_graduacao_area.csv"
    TEXTO_PATH = "bases/texto_descricao_area.csv"
    
    df_inst  = load_csv_cached(INST_PATH)
    prod_bbl = load_csv_cached(PROD_BBL_PATH)
    maior_formacoes = load_csv_cached(MAIOR_FORMACAO_PATH)
    df_wc_area_agg = load_csv_cached(PALAVRAS_WORDCLOUD_PATH)
    df_grad = load_csv_cached(PATH_GRAD)
    df_texto_area = load_csv_cached(TEXTO_PATH)
    
    info = df_filtrado.iloc[0]
    

    # ====== FILTRO DE PERÍODO ======
    periodos = ["2010–2015", "2015–2020", "2020–2025"]
    periodo_sel = st.radio(
        "Período:",
        options=periodos,
        index=len(periodos) - 1,  # começa no mais recente
        horizontal=True,
        key=f"periodo_{area_sel}"
    )

    st.markdown(f"## Painel — Área: {area_sel}")

    st.markdown("""**CONTEXTUALIZAÇÃO METODOLÓGICA**    
O estudo se baseia na premissa de que a estrutura das interações entre cientistas é fundamental para entender as redes de colaboração científica. Utilizando a abordagem de redes, os cientistas são representados como "nós" e as coautorias como "arestas", permitindo mapear a organização social da ciência. Conforme demonstrado por Newman (2001), essas redes formam "mundos pequenos" com alta conectividade, o que impacta diretamente a difusão de informações e a inovação.    
Para investigar o conteúdo dessa produção, a metodologia aplica a análise de redes semânticas. Esse método é usado para extrair, correlacionar e visualizar o significado das relações e conceitos na literatura científica. O objetivo é identificar insights (sinais fracos e fortes) que possam auxiliar na avaliação de políticas públicas e na tomada de decisão para os INCTs.
""")
    texto = df_texto_area.query(
        "area == @area_sel and periodo == @periodo_sel"
    )["texto_md"].iloc[0]
    
    st.markdown(texto)
    texto_coautoria = df_texto_area.query(
        "area == @area_sel and periodo == @periodo_sel"
    )["texto_coautoria"].iloc[0]
    st.markdown(texto_coautoria)

    # ==========================================================
    # 🕸️ GRAFO INTERATIVO (GEXF CACHEADO)
    # ==========================================================
    # path_gexf = info.get("path_area_gexf_html", "")
    # html_cached_path = f"gexf_html/{Path(path_gexf).stem}.html"
    # with st.container(border=True):
    #     st.markdown("#### Rede de Colaboração")
    #     html = load_cached_html(html_cached_path)
    #     if html:
    #         st.components.v1.html(
    #             #html,
    #             f"""
    #             <iframe srcdoc='{html.replace("'", "&apos;")}'
    #                     style="width:100%; height:950px; border:none; overflow:hidden;">
    #             </iframe>
    #             """,
    #             height=900,
    #             scrolling=False
    #         )
    #     else:
    #         st.info(
    #             "📁 Grafo da área ainda não foi pré-gerado. "
    #             f"Esperado: `{html_cached_path}`"
    #         )

    # ==========================================================
    # 🪢 FLUXO SANKEY (CACHEADO)
    # ==========================================================
    st.subheader("Fluxo Sankey — Palavras-chave por Período")

    sankey_path = Path(f"sankey_inct_palavra_tratada_area/sankey_inct_{info['identificador_area']}.html")

    with st.container(border=True):
        if sankey_path.exists():
            try:
                html = load_html_sankey_cached(sankey_path)
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
                        width: max-content;
                    ">
                    {html}</div>
                </div>
                """
                st.components.v1.html(sankey_html, height=1000, scrolling=False)
            except Exception as e:
                st.warning(f"⚠️ Erro ao carregar o gráfico Sankey: {e}")
        else:
            st.info("Nenhum gráfico Sankey disponível para esta área.")

    # ==========================================================
    # 📊 KPIs iniciais
    # ==========================================================
    st.divider()
    n_incts = len(df_filtrado)
    total_pesquisadores = int(df_filtrado["n_pesquisadores"].sum())
    fem = int(df_filtrado["n_feminino"].sum())
    masc = int(df_filtrado["n_masculino"].sum())
    pct_fem = (fem / total_pesquisadores * 100) if total_pesquisadores else 0.0
    pct_masc = (masc / total_pesquisadores * 100) if total_pesquisadores else 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("INCTs nesta área", n_incts)
    col2.metric("Pesquisadores totais", total_pesquisadores)
    col3.metric("Feminino (%)", f"{pct_fem:.1f}%")
    col4.metric("Masculino (%)", f"{pct_masc:.1f}%")

    # ==========================================================
    # 📄 TABELA DE INFORMAÇÕES POR ÁREA
    # ==========================================================
    st.divider()
    st.subheader("Informações dos INCTs desta Área")
    
    
    # Tooltip explicativo
    st.markdown(
        """
        <span style='font-size: 13px; color: gray;'>
        ℹ️ <strong>Atenção:</strong> A soma entre pesquisadores do sexo feminino e masculino 
        pode não corresponder exatamente ao total de pesquisadores, 
        pois alguns currículos não possuem o campo de sexo preenchido.
        </span>
        """,
        unsafe_allow_html=True
    )
    
    # Seleção das colunas necessárias
    df_tabela = df_filtrado[[
        "nome_inct",
        "n_pesquisadores",
        "n_feminino",
        "n_masculino"
    ]].rename(columns={
        "nome_inct": "INCT",
        "n_pesquisadores": "Quantidade de Pesquisadores",
        "n_feminino": "Feminino",
        "n_masculino": "Masculino",
    })
    
    # Ordenação opcional (maior → menor)
    df_tabela = df_tabela.sort_values("Quantidade de Pesquisadores", ascending=False)
    
    # Estilo da tabela (mais bonita)
    st.dataframe(
        df_tabela,
        width="stretch",
        hide_index=True
    )

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
        prod_bbl[prod_bbl["area"] == area_sel].copy()
        if "area" in prod_bbl.columns
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
    
    # # ==========================================================
    # # ☁️ NUVEM DE PALAVRAS
    # # ==========================================================
    # st.divider()
    # st.subheader("Nuvem de Palavras — Produção Científica da Área")
    

    # try:
    #     # df_wc = load_csv_cached("bases/wordcloud.csv")
    #     df_wc_area = df_wc[df_wc["area"] == area_sel]
    #     if not df_wc_area.empty:
    #         top_words = df_wc_area["palavra"].value_counts().head(100)
    #         st.bar_chart(top_words)
    #     else:
    #         st.info("Sem palavras disponíveis para esta área.")
    # except Exception as e:
    #     st.warning(f"Erro ao carregar wordcloud: {e}")
    # ==========================================================
    # ☁️ NUVEM DE PALAVRAS
    # ==========================================================
    # ==========================================================
    # ☁️ NUVEM DE PALAVRAS — GRÁFICO DE BARRAS
    # ==========================================================
    st.divider()
    st.subheader("Distribuição de Palavras-Chave")
    
    try:
        # 🔹 Seleciona períodos da base agregada
        periodos_wc = sorted(df_wc_area_agg["periodo"].unique())
    
        # 🔹 Multiselect
        periodos_sel = st.multiselect(
            "Filtrar por período:",
            options=periodos_wc,
            default=periodos_wc
        )
    
        # 🔹 Filtra pela área selecionada
        df_area_sel = df_wc_area_agg[df_wc_area_agg["area"] == area_sel]
    
        # 🔹 Filtra períodos
        if periodos_sel:
            df_area_sel = df_area_sel[df_area_sel["periodo"].isin(periodos_sel)]
    
        # 🔹 Gráfico
        if not df_area_sel.empty:
            top_words = (
                df_area_sel.groupby("palavra")["freq"]
                .sum()
                .sort_values(ascending=False)
                .head(100)
            )
            st.bar_chart(top_words, width="stretch")
        else:
            st.info("Sem palavras disponíveis para esta área e período selecionado.")
    
    except Exception as e:
        st.warning(f"Erro ao carregar wordcloud: {e}")



    # ====================== CARDS: WORDCLOUD | MAIOR FORMAÇÃO ======================
    # ====================== CARDS: WORDCLOUD | MAIOR FORMAÇÃO ======================
    import matplotlib
    matplotlib.use("Agg")
    
    col_wc, col_form = st.columns(2, gap="medium")
    
    with col_wc:
        with st.container(border=True):
            st.markdown("#### Nuvem de Palavras")
    
            # 🔹 Filtra pela área
            wc_sel = df_wc_area_agg[df_wc_area_agg["area"] == area_sel]
    
            # 🔹 Filtrar períodos selecionados
            if periodos_sel:
                wc_sel = wc_sel[wc_sel["periodo"].isin(periodos_sel)]
    
            if wc_sel.empty:
                st.warning("Nenhuma frase disponível para gerar a nuvem com os filtros atuais.")
            else:
                s = wc_sel["palavra"].astype(str)
    
                # stopwords básicas
                STOPWORDS_ONEWORD = {
                    "de","da","do","das","dos","em","no","na","nas","nos","para","por",
                    "e","a","o","os","as","um","uma","com","ao","aos","se","que",
                    "sobre","entre","ou","como"
                }
    
                # remove palavras isoladas muito comuns
                mascara_um_termo = ~s.str.contains(r"\s", regex=True)
                palavras_validas = s[~(mascara_um_termo & s.isin(STOPWORDS_ONEWORD))]
    
                # alinhar com a base original
                wc_filtrado = wc_sel.loc[palavras_validas.index]
    
                # dicionário de frequências diretamenre da base
                freqs = dict(
                    zip(
                        wc_filtrado["palavra"],
                        wc_filtrado["freq"]
                    )
                )
    
                if not freqs:
                    st.warning("Nenhuma frase disponível após filtragem.")
                else:
                    top_n = st.slider(
                        "Número de expressões exibidas",
                        min_value=10,
                        max_value=300,
                        value=30,
                        step=10,
                        key=f"slider_wc_{area_sel}",
                    )
    
                    # top n ordenado
                    freqs_top = dict(
                        sorted(freqs.items(), key=lambda x: x[1], reverse=True)[:top_n]
                    )
    
                    # gerar wordcloud
                    wc_img = WordCloud(
                        width=900,
                        height=500,
                        background_color="white",
                        colormap="Blues",
                        collocations=False,
                    ).generate_from_frequencies(freqs_top)
    
                    st.image(wc_img.to_array(), width="content")
    

    # ---------- CARD 2: MAIOR FORMAÇÃO ----------
    with col_form:
        with st.container(border=True):
            st.markdown(f"#### Maior Formação por Área")
    
            df_plot = (
                maior_formacoes[maior_formacoes["area"] == area_sel]
                #.sort_values("qtd", ascending=False)
                # maior_formacoes
                   .groupby(["area", "area_de_maior_formacao"], as_index=False)["count"]
                   .sum()
                   .sort_values("count", ascending=False)
            )
    
            if df_plot.empty:
                st.warning("Nenhuma informação de formação disponível para esta Área.")
            else:
                fig_bar = px.bar(
                    df_plot,
                    x="count",
                    # y="area_de_maior_formacao",
                    y="area_de_maior_formacao",
                    orientation="h",
                    color="count",
                    color_continuous_scale="Blues",
                    text="count",
                    labels={
                        "count": "Quantidade",
                        "area_de_maior_formacao": "Área"
                    },
                )
                fig_bar.update_layout(
                    xaxis_title="Número de Pesquisadores",
                    yaxis_title="Área de Formação",
                    #height=420,
                    height=530,
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

    # ======================== MAPA + TOP INSTITUIÇÕES ===================
    col_uf, col_form = st.columns(2, gap="medium")
    with col_uf:
        with st.container(border=True):
            #st.markdown("#### 🗺️ Distribuição Geográfica — Pesquisadores por UF")
            st.markdown("#### Distribuição do Endereço Profissional por UF")
            
    
            info_instituicao = df_inst[df_inst["area"] == area_sel].copy()
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
                #hover_data={"qtd": "Quantidade de Instituições/Empresas"},
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


    # ---------- CARD 2: MAIOR FORMAÇÃO ----------
    with col_form:
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
                st.warning("Nenhuma instituição registrada para esta Área.")


    # --- CARD: Gráfico de barras verticais (abaixo) ---   
    with st.container(border=True):
        st.markdown("#### Distribuição das Formações Mais Altas")
    
        if Path(PATH_GRAD).exists():
            df_plot = (
                df_grad[df_grad["area"] == area_sel]
                .sort_values("qtd", ascending=False)
            )
    
            if df_plot.empty:
                st.warning("Nenhuma informação de formação disponível para esta Área.")
            else:
                fig_bar_vert = px.bar(
                    df_plot,
                    x="formacao_mais_alta",
                    y="qtd",
                    color="qtd",
                    color_continuous_scale="Blues",
                    text="qtd",
                    #title=f"Distribuição das Formações Mais Altas — {inct_sel}",
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
            st.warning("Base 'grafico_maior_graduacao_area.csv' não encontrada.")
