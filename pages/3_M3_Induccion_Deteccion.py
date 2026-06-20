"""
M3 — Inducción y Detección
PIE Tlaxcala · Anabel Ávalos · PRI 2027

Visita las secciones que importan.
Con el mensaje correcto. A quien puede cambiar su voto.
"""

import os
import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="M3 · Inducción y Detección · PIE Tlaxcala",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Rutas — pages/ está un nivel abajo del repo ──────────────────────────────
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

# ════════════════════════════════════════════════════════════════════════════
# ARQUETIPOS — idénticos a M1 y M2
# ════════════════════════════════════════════════════════════════════════════

ARQUETIPOS = {
    "A1": {
        "nombre":    "El Leal Institucional Tricolor",
        "color":     "#a3142b",
        "prioridad": "Mantenimiento",
        "emoji":     "🔴",
        "desc":      "Voto duro priista. No necesita convencimiento, necesita movilización.",
        "frase":     "Yo nunca he dejado al partido — el partido me hizo lo que soy.",
    },
    "A2": {
        "nombre":    "El Decepcionado del Gobierno Estatal",
        "color":     "#dc2626",
        "prioridad": "Máxima",
        "emoji":     "⚡",
        "desc":      "Sin partido fijo. Busca una alternativa que hable de resultados, no de ideología.",
        "frase":     "No soy de ningún partido, pero ya estoy cansado de que nada cambie.",
    },
    "A3": {
        "nombre":    "El Anti-Sistema Punitivo",
        "color":     "#7c2d92",
        "prioridad": "Alta",
        "emoji":     "🛑",
        "desc":      "Cree que todos los partidos son iguales. Pide ruptura y mano dura.",
        "frase":     "Aquí lo que se necesita es mano dura — ya no aguantamos la impunidad.",
    },
    "A4": {
        "nombre":    "La Guardiana del Miedo de Género",
        "color":     "#be185d",
        "prioridad": "Alta — nicho",
        "emoji":     "🚨",
        "desc":      "Alerta permanente por la seguridad de las mujeres. Exige compromisos verificables.",
        "frase":     "A mi hija no la dejo salir sola ni de día — y eso no debería ser normal.",
    },
    "A5": {
        "nombre":    "El Rural Desatendido por el Estado",
        "color":     "#15803d",
        "prioridad": "Media-alta",
        "emoji":     "🌾",
        "desc":      "Depende del campo. Siente el abandono del gobierno estatal. Pide gestión, no promesas.",
        "frase":     "El camino a mi parcela lleva años destrozado y nadie del estado lo ha visto.",
    },
    "A6": {
        "nombre":    "La Conforme con la Continuidad",
        "color":     "#0891b2",
        "prioridad": "Baja",
        "emoji":     "🔵",
        "desc":      "No asocia sus problemas con el gobierno estatal. Recibe apoyos y los valora.",
        "frase":     "A mí me ha ido bien — no tengo queja del gobierno.",
    },
    "A7": {
        "nombre":    "El Susceptible a la Ruptura",
        "color":     "#c2410c",
        "prioridad": "Alta — oportunidad y riesgo",
        "emoji":     "⚠️",
        "desc":      "El más volátil. Se va con quien prometa orden inmediato, sin importar el partido.",
        "frase":     "Ya no me importa de qué partido sea — solo quiero que alguien meta orden.",
    },
    "A8": {
        "nombre":    "El Desconectado de lo Estatal",
        "color":     "#64748b",
        "prioridad": "No prioritario",
        "emoji":     "⚪",
        "desc":      "Culpa al municipio, no al estado. Bajo retorno para gobernatura.",
        "frase":     "Aquí el problema es el ayuntamiento — eso no tiene nada que ver con el estado.",
    },
}

ARQ_PCT_CAPITAL = {
    "A1": 14, "A2": 16, "A3": 10, "A4": 7,
    "A5":  3, "A6": 22, "A7": 12, "A8": 16,
}

PRIORIDAD_COLOR = {
    "Máxima":                      "#dc2626",
    "Alta":                        "#c2410c",
    "Alta — nicho":                "#be185d",
    "Alta — oportunidad y riesgo": "#7c2d92",
    "Media-alta":                  "#0e7490",
    "Mantenimiento":               "#15803d",
    "Baja":                        "#64748b",
    "No prioritario":              "#94a3b8",
}

# Probabilidades simpatizante / indeciso / adverso por arquetipo
ARQ_POS_PROB = {
    "A1": [0.72, 0.23, 0.05],
    "A2": [0.30, 0.50, 0.20],
    "A3": [0.18, 0.35, 0.47],
    "A4": [0.33, 0.46, 0.21],
    "A5": [0.29, 0.51, 0.20],
    "A6": [0.09, 0.20, 0.71],
    "A7": [0.24, 0.51, 0.25],
    "A8": [0.14, 0.42, 0.44],
}

# Demanda principal detectada por arquetipo
ARQ_DEMANDA = {
    "A1": "Movilización y red de apoyo de base",
    "A2": "Mejora de servicios de salud y atención estatal",
    "A3": "Seguridad pública y combate a la impunidad",
    "A4": "Protección a mujeres y espacios seguros",
    "A5": "Infraestructura rural y apoyos al campo",
    "A6": "Continuidad de programas sociales",
    "A7": "Orden público y resultados inmediatos",
    "A8": "Servicios municipales básicos (bacheo, agua, luz)",
}

BRIGADAS = ["Brigada Norte", "Brigada Centro", "Brigada Sur", "Brigada Oriente"]

ESTADO_FILL = {
    "Completada":  "#0b6b46",
    "En proceso":  "#fbbf24",
    "Sin visitar": "#e2e8f0",
}
ESTADO_BORDER = {
    "Completada":  "#0b6b46",
    "En proceso":  "#d97706",
    "Sin visitar": "#94a3b8",
}


def score_color(score: float) -> str:
    if score >= 70: return "#a3142b"
    if score >= 55: return "#f97316"
    if score >= 40: return "#eab308"
    return "#94a3b8"


# ════════════════════════════════════════════════════════════════════════════
# CSS — alineado con M2
# ════════════════════════════════════════════════════════════════════════════

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

[data-testid="stSidebar"] { background-color: #5c0c18 !important; }
[data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span,
[data-testid="stSidebar"] div, [data-testid="stSidebar"] label { color: #f5e6e9 !important; }

.header-modulo {
    --accent: #5b7a9e;
    background: #14181f;
    padding: 28px 32px 24px; border-radius: 8px; margin-bottom: 22px;
    position: relative; overflow: hidden;
    border-bottom: 2px solid var(--accent);
}
.header-modulo::after {
    content: ''; position: absolute; top: -45px; right: -45px;
    width: 180px; height: 180px; border-radius: 50%; background: rgba(255,255,255,0.04);
}
.header-modulo .hm-eyebrow {
    font-family: 'JetBrains Mono', monospace; font-size: 0.66rem; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase; color: var(--accent); margin-bottom: 8px;
}
.header-modulo h1 {
    font-family: 'Barlow Condensed', sans-serif; font-weight: 800; text-transform: uppercase;
    color: #eef1f0; font-size: 1.85rem; letter-spacing: -0.005em; margin: 0 0 6px; line-height: 1.05;
}
.header-modulo p  { color: #8b95a8; font-size: 0.92rem; margin: 0; max-width: 620px; line-height: 1.5; }
.header-modulo .hm-dots { position: absolute; right: 28px; top: 26px; display: flex; gap: 6px; }
.header-modulo .hm-dots span { width: 5px; height: 5px; border-radius: 50%; background: var(--accent); opacity: 0.55; }
.header-modulo .hm-dots span:first-child { opacity: 1; }

.tag { font-family: 'JetBrains Mono', monospace; display: inline-block; font-size: 0.62rem; font-weight: 700; padding: 2px 8px;
       border-radius: 3px; margin-right: 4px; letter-spacing: 0.05em; text-transform: uppercase;
       vertical-align: middle; }
.tag.real { background: #dcfce7; color: #166534; }
.tag.demo { background: #fef3c7; color: #92400e; }

.kpi-card {
    background: #f8fafc; border-left: 4px solid #334155;
    border-radius: 0 10px 10px 0; padding: 14px 16px; height: 100%;
}
.kpi-val   { font-size: 1.75rem; font-weight: 800; color: #1e293b; line-height: 1.1; }
.kpi-label { font-size: 0.78rem; font-weight: 600; color: #1e293b; margin-top: 4px; }
.kpi-ctx   { font-size: 0.72rem; color: #64748b; margin-top: 2px; line-height: 1.3; }

.leyenda-item { display: flex; align-items: center; gap: 8px;
                margin-bottom: 6px; font-size: 0.80rem; color: #334155; }
.leyenda-dot  { width: 11px; height: 11px; border-radius: 50%; flex-shrink: 0; }

.teaser-card {
    background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
    border: 1px solid #cbd5e1; border-radius: 14px;
    padding: 36px 40px; text-align: center; margin-top: 16px;
}
.teaser-card h3 { font-size: 1.2rem; font-weight: 700; color: #1e293b; margin-bottom: 10px; }
.teaser-card p  { font-size: 0.88rem; color: #475569; line-height: 1.65; margin: 0; }
.teaser-chip {
    display: inline-block; background: #fff; border: 1px solid #cbd5e1;
    border-radius: 10px; padding: 8px 18px; font-size: 0.82rem;
    color: #334155; font-weight: 600; margin: 4px;
}
</style>
"""


# ════════════════════════════════════════════════════════════════════════════
# CARGA Y PROCESAMIENTO — misma lógica que M2 + datos M3
# ════════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_data():
    geo_path = os.path.join(DATA, "secciones_capital.geojson")
    with open(geo_path) as f:
        geo = json.load(f)
    secs_geo = [feat["properties"]["seccion"] for feat in geo["features"]]
    df = pd.DataFrame({"seccion": secs_geo})

    df_res = pd.read_csv(os.path.join(DATA, "Resultados_2024_Tlaxcala.csv"))
    df_res = df_res[df_res["ID_MUNICIPIO"] == 33][
        ["SECCION", "PRI", "MORENA", "NUM_VOTOS_VALIDOS", "TOTAL_VOTOS", "LISTA_NOMINAL"]
    ].copy()
    df_res.columns = [
        "seccion", "votos_pri", "votos_morena",
        "votos_validos", "total_votos", "lista_nominal_res",
    ]

    df_ln = pd.read_csv(os.path.join(DATA, "Lista_nominal_Tlaxcala.csv"))
    df_ln.columns = [c.replace("\n", "_").strip() for c in df_ln.columns]
    df_ln = df_ln[df_ln["CLAVE_MUNICIPIO"] == 33][
        ["SECCION", "LISTA_NOMINAL", "LISTA_HOMBRES", "LISTA_MUJERES"]
    ].copy()
    df_ln.columns = ["seccion", "lista_nominal", "lista_hombres", "lista_mujeres"]

    df = df.merge(df_res, on="seccion", how="left")
    df = df.merge(df_ln,  on="seccion", how="left")

    avg_part    = df_res["total_votos"].sum()  / df_ln["lista_nominal"].sum()
    avg_pct_pri = df_res["votos_pri"].sum()    / df_res["votos_validos"].sum()
    avg_pct_mor = df_res["votos_morena"].sum() / df_res["votos_validos"].sum()
    no_res = df["votos_validos"].isna()
    df.loc[no_res, "votos_validos"] = (df.loc[no_res, "lista_nominal"] * avg_part).round()
    df.loc[no_res, "votos_pri"]     = (df.loc[no_res, "votos_validos"] * avg_pct_pri).round()
    df.loc[no_res, "votos_morena"]  = (df.loc[no_res, "votos_validos"] * avg_pct_mor).round()
    df.loc[no_res, "total_votos"]   = df.loc[no_res, "votos_validos"]
    df["es_imputado"] = no_res.astype(bool)

    df["pct_pri"]       = (df["votos_pri"]    / df["votos_validos"] * 100).round(1)
    df["pct_morena"]    = (df["votos_morena"] / df["votos_validos"] * 100).round(1)
    df["margen"]        = (df["pct_morena"] - df["pct_pri"]).round(1)
    df["participacion"] = (df["total_votos"]  / df["lista_nominal"] * 100).round(1)
    df["pct_mujeres"]   = (df["lista_mujeres"] / df["lista_nominal"] * 100).round(1)

    # Arquetipos — Dirichlet rng(42) igual que M2
    rng = np.random.default_rng(42)
    arq_codes    = list(ARQ_PCT_CAPITAL.keys())
    base_weights = np.array([ARQ_PCT_CAPITAL[k] for k in arq_codes], dtype=float)
    base_weights /= base_weights.sum()
    mixes = rng.dirichlet(base_weights * 4, size=len(df))
    df["arquetipo_dom"] = [arq_codes[int(np.argmax(m))] for m in mixes]

    # Score — idéntico a M2
    df["s_competitividad"] = (100 - df["margen"].clip(0, 100)).clip(0, 100)
    df["s_base_pri"]       = (df["pct_pri"] / df["pct_pri"].max() * 100).clip(0, 100)
    df["s_peso"]           = (df["lista_nominal"] / df["lista_nominal"].max() * 100).clip(0, 100)
    df["score"] = (
        df["s_competitividad"] * 0.45 +
        df["s_base_pri"]       * 0.35 +
        df["s_peso"]           * 0.20
    ).clip(1, 99).round(1)

    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1

    # ── Datos M3 (semilla propia) ─────────────────────────────────────────
    rng3 = np.random.default_rng(99)

    s_norm = (df["score"] - df["score"].min()) / (
        df["score"].max() - df["score"].min() + 1e-6
    )

    estados = []
    for s in s_norm:
        r = rng3.random()
        if r < s * 0.65:
            estados.append("Completada")
        elif r < s * 0.65 + 0.18:
            estados.append("En proceso")
        else:
            estados.append("Sin visitar")
    df["estado"] = estados

    brigada_asig = rng3.choice(BRIGADAS, size=len(df))
    df["brigada"] = [b if e != "Sin visitar" else "—"
                     for b, e in zip(brigada_asig, df["estado"])]

    df["n_contactos"] = (s_norm * 14 + rng3.integers(0, 5, size=len(df))).astype(int)
    df.loc[df["estado"] == "Sin visitar", "n_contactos"] = 0

    simp_list, ind_list, adv_list = [], [], []
    for _, row in df.iterrows():
        n   = int(row["n_contactos"])
        arq = str(row["arquetipo_dom"])
        if n == 0:
            simp_list.append(0); ind_list.append(0); adv_list.append(0)
            continue
        probs  = ARQ_POS_PROB.get(arq, [0.33, 0.34, 0.33])
        counts = rng3.multinomial(n, probs)
        simp_list.append(int(counts[0]))
        ind_list.append(int(counts[1]))
        adv_list.append(int(counts[2]))
    df["n_simp"] = simp_list
    df["n_ind"]  = ind_list
    df["n_adv"]  = adv_list

    df["demanda_top"] = df["arquetipo_dom"].map(ARQ_DEMANDA)
    df["n_celular"]   = (df["n_contactos"] * rng3.uniform(0.60, 0.85, size=len(df))).round().astype(int)
    df["n_acepta"]    = (df["n_celular"]   * rng3.uniform(0.65, 0.90, size=len(df))).round().astype(int)

    # Centroides para lookup de click
    def poly_centroid(coords):
        ring = coords[0]
        lons = [p[0] for p in ring]
        lats = [p[1] for p in ring]
        return sum(lats) / len(lats), sum(lons) / len(lons)

    centroids = {}
    for feat in geo["features"]:
        sec  = feat["properties"]["seccion"]
        geom = feat["geometry"]
        if geom["type"] == "Polygon":
            clat, clng = poly_centroid(geom["coordinates"])
        else:
            best = max(geom["coordinates"], key=lambda p: len(p[0]))
            clat, clng = poly_centroid(best)
        centroids[sec] = (clat, clng)

    return geo, df, centroids


# ════════════════════════════════════════════════════════════════════════════
# MAPA FOLIUM
# ════════════════════════════════════════════════════════════════════════════

def build_map(geo: dict, df: pd.DataFrame, color_by: str = "estado",
              arq_filter: list | None = None) -> folium.Map:
    lookup = df.set_index("seccion")
    filtro_activo = bool(arq_filter)

    m = folium.Map(location=[19.308, -98.237], zoom_start=13,
                   tiles="CartoDB positron", prefer_canvas=True)

    def style_fn(feature):
        sec = feature["properties"]["seccion"]
        if sec not in lookup.index:
            return {"fillColor": "#e2e8f0", "fillOpacity": 0.15,
                    "color": "#e2e8f0", "weight": 0.5}
        row = lookup.loc[sec]
        arq = str(row["arquetipo_dom"])
        en_filtro = (not filtro_activo) or (arq in arq_filter)
        if not en_filtro:
            return {"fillColor": "#e2e8f0", "fillOpacity": 0.10,
                    "color": "#cbd5e1", "weight": 0.5}
        fill = (ESTADO_FILL.get(str(row["estado"]), "#e2e8f0")
                if color_by == "estado"
                else ARQUETIPOS[arq]["color"])
        return {"fillColor": fill, "fillOpacity": 0.80,
                "color": "#ffffff", "weight": 1.4}

    def highlight_fn(feature):
        return {"fillColor": "#fbbf24", "fillOpacity": 0.9,
                "color": "#fff", "weight": 2.5}

    geo_rich = json.loads(json.dumps(geo))
    for feat in geo_rich["features"]:
        sec = feat["properties"]["seccion"]
        if sec in lookup.index:
            r = lookup.loc[sec]
            feat["properties"].update({
                "Estado":        str(r["estado"]),
                "Arquetipo":     str(r["arquetipo_dom"]),
                "Brigada":       str(r["brigada"]),
                "Contactos":     int(r["n_contactos"]),
                "Simpatizantes": int(r["n_simp"]),
                "Indecisos":     int(r["n_ind"]),
                "Adversos":      int(r["n_adv"]),
                "Lista nominal": f"{int(r['lista_nominal']):,}",
            })

    folium.GeoJson(
        geo_rich,
        style_function=style_fn,
        highlight_function=highlight_fn,
        tooltip=folium.GeoJsonTooltip(
            fields=["seccion", "Estado", "Arquetipo", "Brigada",
                    "Contactos", "Simpatizantes", "Indecisos", "Adversos", "Lista nominal"],
            aliases=["Sección", "Estado", "Arquetipo", "Brigada",
                     "Contactos", "🟢 Simp.", "🟡 Ind.", "🔴 Adv.", "Lista nominal"],
            sticky=True, labels=True,
            style=("font-family:'DM Sans',sans-serif; font-size:13px;"
                   "background:#fff; border:1px solid #e2e8f0; border-radius:8px;"),
            max_width=260,
        ),
    ).add_to(m)
    return m


# ════════════════════════════════════════════════════════════════════════════
# FICHA DE SECCIÓN
# ════════════════════════════════════════════════════════════════════════════

def seccion_card(row: pd.Series) -> None:
    arq_code    = str(row["arquetipo_dom"])
    arq         = ARQUETIPOS[arq_code]
    badge_color = PRIORIDAD_COLOR.get(arq["prioridad"], "#64748b")
    n           = int(row["n_contactos"])
    ns          = int(row["n_simp"])
    ni          = int(row["n_ind"])
    na          = int(row["n_adv"])
    pct_s       = round(ns / max(n, 1) * 100)
    pct_i       = round(ni / max(n, 1) * 100)
    pct_a       = round(na / max(n, 1) * 100)
    visitada    = str(row["estado"]) != "Sin visitar"
    score       = float(row["score"])
    sc_color    = score_color(score)

    def barra(pct, color):
        return (f'<div style="flex:{max(pct,1)}; background:{color}; height:100%; '
                f'border-radius:3px;"></div>')

    barra_html = (
        '<div style="display:flex; gap:2px; height:10px; border-radius:4px; '
        'overflow:hidden; margin-bottom:6px;">'
        + barra(pct_s, "#0b6b46") + barra(pct_i, "#d97706") + barra(pct_a, "#a3142b")
        + '</div>'
    ) if n > 0 else ""

    if visitada and n > 0:
        result_block = f"""
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px;
                    padding:14px 16px; margin-top:0;">
            <div style="font-size:0.66rem; font-weight:700; letter-spacing:0.10em;
                        text-transform:uppercase; color:#64748b; margin-bottom:10px;">
                🗳️ Detección — {n} contactos en campo
            </div>
            {barra_html}
            <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; margin-bottom:12px;">
                <div style="background:#f0fdf4; border-radius:8px; padding:10px; text-align:center;">
                    <div style="font-size:1.55rem; font-weight:800; color:#0b6b46;">{ns}</div>
                    <div style="font-size:0.68rem; color:#166534; margin-top:2px;">🟢 Simpatizantes<br>{pct_s}%</div>
                </div>
                <div style="background:#fffbeb; border-radius:8px; padding:10px; text-align:center;">
                    <div style="font-size:1.55rem; font-weight:800; color:#d97706;">{ni}</div>
                    <div style="font-size:0.68rem; color:#92400e; margin-top:2px;">🟡 Indecisos<br>{pct_i}%</div>
                </div>
                <div style="background:#fff0f0; border-radius:8px; padding:10px; text-align:center;">
                    <div style="font-size:1.55rem; font-weight:800; color:#a3142b;">{na}</div>
                    <div style="font-size:0.68rem; color:#991b1b; margin-top:2px;">🔴 Adversos<br>{pct_a}%</div>
                </div>
            </div>
            <div style="font-size:0.80rem; color:#475569; line-height:1.5; margin-bottom:8px;">
                📋 Demanda dominante detectada:<br>
                <b style="color:#1e293b;">{row['demanda_top']}</b>
            </div>
            <div style="font-size:0.78rem; color:#475569;">
                📱 Con celular: <b>{int(row['n_celular'])}</b>
                &nbsp;·&nbsp; ✅ Acepta contacto: <b>{int(row['n_acepta'])}</b>
                &nbsp;·&nbsp; Brigada: <b>{row['brigada']}</b>
            </div>
        </div>
        """
    elif visitada:
        result_block = """
        <div style="background:#fffbeb; border:1px solid #fcd34d; border-radius:10px;
                    padding:12px 16px; margin-top:0; font-size:0.82rem; color:#92400e;">
            🟡 En proceso — aún no hay contactos registrados en esta sección.
        </div>
        """
    else:
        result_block = """
        <div style="background:#f8fafc; border:1px dashed #cbd5e1; border-radius:10px;
                    padding:12px 16px; margin-top:0; font-size:0.82rem; color:#94a3b8;">
            ⚪ Sin visitar — la brigada aún no ha llegado a esta sección.
        </div>
        """

    st.html(f"""
    <div style="font-family:'DM Sans',sans-serif; max-width:600px;">

      <div style="background:linear-gradient(135deg,#1f2937 0%,#334155 100%);
                  border-radius:12px 12px 0 0; padding:18px 22px;">
        <div style="font-size:0.70rem; font-weight:700; letter-spacing:0.10em;
                    text-transform:uppercase; color:#94a3b8; margin-bottom:8px;">
          🎯 Sección {int(row['seccion'])} · Tlaxcala capital · {row['estado']}
        </div>
        <div style="display:flex; align-items:center; gap:18px;">
          <div>
            <span style="font-size:2.2rem; font-weight:800; color:#fff; line-height:1;">{score:.0f}</span>
            <span style="font-size:0.76rem; color:#94a3b8; margin-left:4px;">/100 · Score M2</span>
          </div>
          <div style="flex:1;">
            <div style="background:rgba(255,255,255,0.14); border-radius:6px;
                        height:10px; overflow:hidden; margin-bottom:5px;">
              <div style="height:100%; border-radius:6px; width:{int(score)}%;
                          background:{sc_color};"></div>
            </div>
            <div style="font-size:0.76rem; color:#94a3b8;">
              Lista nominal: {int(row['lista_nominal']):,} electores
            </div>
          </div>
        </div>
      </div>

      <div style="background:#fff; border:1px solid #e2e8f0; border-top:none; padding:18px 22px;">
        <div style="font-size:0.66rem; font-weight:700; letter-spacing:0.10em;
                    text-transform:uppercase; color:#64748b; margin-bottom:10px;">
          👥 ¿Quién vive aquí?
        </div>
        <span style="display:inline-block; font-size:0.68rem; font-weight:700; color:#fff;
                     padding:2px 12px; border-radius:20px; background:{badge_color}; margin-bottom:10px;">
          Prioridad: {arq['prioridad']}
        </span>
        <div style="display:flex; align-items:flex-start; gap:10px; margin-bottom:10px;">
          <span style="font-size:1.6rem; line-height:1;">{arq['emoji']}</span>
          <div>
            <div style="font-size:0.96rem; font-weight:700; color:#1e293b; margin-bottom:3px;">
              {arq_code} · {arq['nombre']}
            </div>
            <div style="font-size:0.80rem; color:#475569; line-height:1.45;">{arq['desc']}</div>
          </div>
        </div>
        <div style="background:#f8fafc; border-left:3px solid {arq['color']};
                    border-radius:0 8px 8px 0; padding:10px 14px; margin-bottom:14px;">
          <div style="font-size:0.80rem; color:#7c2d92; font-style:italic; line-height:1.45;">
            "{arq['frase']}"
          </div>
        </div>
        {result_block}
      </div>

    </div>
    """)


# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    st.markdown(CSS, unsafe_allow_html=True)

    st.markdown("""
    <div class="header-modulo">
      <div class="hm-dots"><span></span><span></span><span></span></div>
      <div class="hm-eyebrow">Módulo 03 · En operación</div>
      <h1>🎯 Inducción y Detección</h1>
      <p>Visita las secciones que importan · con el mensaje correcto · a quien puede cambiar su voto</p>
    </div>
    """, unsafe_allow_html=True)

    MUN_OPCIONES = {
        "🏙️ Tlaxcala capital": "capital",
        "🏭 Apizaco":          "apizaco",
        "🌾 Huamantla":        "huamantla",
    }
    MUN_INFO = {
        "apizaco":   {"nombre": "Apizaco",   "secciones": 40},
        "huamantla": {"nombre": "Huamantla", "secciones": 42},
    }

    col_sel, col_ctx = st.columns([1, 2], gap="medium")
    with col_sel:
        mun_label = st.selectbox(
            "📍 Municipio", options=list(MUN_OPCIONES.keys()),
            index=0, key="m3_municipio",
        )
    mun_key = MUN_OPCIONES[mun_label]

    if mun_key != "capital":
        info = MUN_INFO[mun_key]
        with col_ctx:
            st.markdown(
                f'<div style="padding:10px 0; font-size:0.84rem; color:#64748b;">'
                f'La operación de brigadas en <b>{info["nombre"]}</b> '
                f'({info["secciones"]} secciones) se activa en la siguiente fase.</div>',
                unsafe_allow_html=True,
            )
        st.markdown(f"""
        <div class="teaser-card">
          <div style="font-size:2.8rem; margin-bottom:14px;">🎯</div>
          <h3>{info['nombre']} · {info['secciones']} secciones en el piloto</h3>
          <p>
            Los datos de {info['nombre']} ya están integrados a la plataforma.<br>
            El mapa de avance, los resultados de detección y el desempeño de brigadas
            se activan en la siguiente fase del módulo.
          </p>
          <div style="margin-top:20px;">
            <span class="teaser-chip">✅ Shape INE integrado</span>
            <span class="teaser-chip">✅ Arquetipos asignados</span>
            <span class="teaser-chip">✅ Score M2 calculado</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    with col_ctx:
        st.markdown(
            '<div style="padding:10px 0; font-size:0.83rem; color:#334155; font-weight:600;">'
            '🟢 Tlaxcala capital · 43 secciones · datos de campo ficticios · '
            'geometría y arquetipos reales</div>',
            unsafe_allow_html=True,
        )

    try:
        geo, df, centroids = load_data()
    except FileNotFoundError as e:
        st.error(
            f"Archivo no encontrado: {e}\n\n"
            "Asegúrate de que `secciones_capital.geojson`, "
            "`Resultados_2024_Tlaxcala.csv` y `Lista_nominal_Tlaxcala.csv` "
            "estén en la carpeta `data/` del repositorio."
        )
        return

    # ── KPIs ──────────────────────────────────────────────────────────────
    st.markdown("---")
    n_comp     = int((df["estado"] == "Completada").sum())
    n_proc     = int((df["estado"] == "En proceso").sum())
    n_sin      = int((df["estado"] == "Sin visitar").sum())
    total_cont = int(df["n_contactos"].sum())
    total_simp = int(df["n_simp"].sum())
    total_ind  = int(df["n_ind"].sum())
    total_m4   = int(df["n_acepta"].sum())
    pct_cob    = round((n_comp + n_proc) / len(df) * 100)

    k1, k2, k3, k4, k5 = st.columns(5, gap="medium")
    kpis = [
        (k1, f"{n_comp} / {len(df)}", "Secciones completadas",    "de 43 en el piloto capital",             "#0b6b46", "demo"),
        (k2, f"{pct_cob}%",           "Cobertura activa",          "completadas + en proceso",               "#334155", "demo"),
        (k3, f"{total_cont:,}",        "Contactos capturados",      "en campo · todas las brigadas",          "#a3142b", "demo"),
        (k4, f"{total_simp}",          "Simpatizantes detectados",  f"{round(total_simp/max(total_cont,1)*100)}% del total", "#0b6b46", "demo"),
        (k5, f"{total_m4}",            "Listos para activación",    "tienen celular y aceptaron contacto",    "#334155", "demo"),
    ]
    for col, val, label, ctx, color, tag in kpis:
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="border-left-color:{color};">
              <div class="kpi-val" style="color:{color};">{val}</div>
              <div class="kpi-label">{label}</div>
              <div class="kpi-ctx">{ctx}</div>
              <span class="tag {tag}" style="margin-top:6px; display:inline-block;">{tag.upper()}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    tab1, tab2 = st.tabs(["🗺️ Mapa de avance", "📊 Desempeño de brigadas"])

    # ─────────────────────────────────────────────────────────────────────
    # TAB 1 · MAPA DE AVANCE
    # ─────────────────────────────────────────────────────────────────────
    with tab1:
        st.markdown(
            '<span class="tag demo">DEMO</span> Avance y detección ficticios · '
            'geometría INE real · arquetipos consistentes con M1 y M2',
            unsafe_allow_html=True,
        )

        col_ctrl, col_map = st.columns([1, 3], gap="medium")

        with col_ctrl:
            color_by = st.radio(
                "Colorear por",
                options=["estado", "arquetipo"],
                format_func=lambda x: (
                    "Estado de avance" if x == "estado" else "Arquetipo dominante"
                ),
                key="m3_color_by",
            )

            st.markdown("---")
            st.markdown("**Filtrar por arquetipo**")
            arq_opciones = {
                f"{arq['emoji']} {code} · {arq['nombre']}": code
                for code, arq in ARQUETIPOS.items()
                if int((df["arquetipo_dom"] == code).sum()) > 0
            }
            sel_labels = st.multiselect(
                "Mostrar solo este arquetipo",
                options=list(arq_opciones.keys()),
                default=[],
                placeholder="Todos los arquetipos",
                key="m3_arq_filter",
                label_visibility="collapsed",
            )
            arq_filter = [arq_opciones[lbl] for lbl in sel_labels] if sel_labels else None
            if arq_filter:
                n_vis = int((df["arquetipo_dom"].isin(arq_filter)).sum())
                st.markdown(
                    f'<div style="background:#fef3c7; border-radius:8px; padding:8px 10px; '
                    f'font-size:0.76rem; color:#92400e; margin-top:4px;">'
                    f'🔍 {n_vis} secciones visibles</div>',
                    unsafe_allow_html=True,
                )

            st.markdown("---")
            st.markdown("**Leyenda**")

            if color_by == "estado":
                for estado, fill in ESTADO_FILL.items():
                    st.markdown(
                        f'<div class="leyenda-item">'
                        f'<div class="leyenda-dot" style="background:{fill}; '
                        f'border:1.5px solid {ESTADO_BORDER[estado]};"></div>'
                        f'<span>{estado}</span></div>',
                        unsafe_allow_html=True,
                    )
            else:
                for code, arq in ARQUETIPOS.items():
                    n = int((df["arquetipo_dom"] == code).sum())
                    if n > 0:
                        st.html(f"""
                        <div style="display:flex; align-items:flex-start; gap:8px;
                                    margin-bottom:10px; font-family:'DM Sans',sans-serif;">
                          <div style="width:10px; height:10px; border-radius:50%;
                                      background:{arq['color']}; margin-top:4px; flex-shrink:0;"></div>
                          <div>
                            <div style="font-size:0.78rem; font-weight:700; color:#1e293b;
                                        line-height:1.2; margin-bottom:2px;">
                              {arq['emoji']} {code} · {n} secc.
                            </div>
                            <div style="font-size:0.73rem; font-weight:600; color:#475569;
                                        line-height:1.2; margin-bottom:1px;">
                              {arq['nombre']}
                            </div>
                            <div style="font-size:0.70rem; color:#94a3b8; line-height:1.3;">
                              {arq['desc']}
                            </div>
                          </div>
                        </div>
                        """)

            st.markdown("---")
            st.caption("💡 Pasa el cursor sobre una sección para ver sus datos. Haz click para ver la ficha de detección.")

        with col_map:
            filter_key = "_".join(sorted(arq_filter)) if arq_filter else "all"
            m = build_map(geo, df, color_by=color_by, arq_filter=arq_filter)
            map_data = st_folium(
                m,
                width=None, height=530,
                use_container_width=True,
                returned_objects=["last_object_clicked"],
                key=f"m3_folium_{color_by}_{filter_key}",
            )

        # ── Ficha al click ────────────────────────────────────────────────
        clicked = map_data.get("last_object_clicked") if map_data else None
        if clicked and clicked.get("lat") and clicked.get("lng"):
            clat, clng = float(clicked["lat"]), float(clicked["lng"])
            sec_click = min(
                centroids,
                key=lambda s: (centroids[s][0] - clat) ** 2 + (centroids[s][1] - clng) ** 2,
            )
            row_click = df[df["seccion"] == sec_click].iloc[0]

            st.markdown("---")
            st.markdown(
                '<div style="font-size:0.70rem; font-weight:700; letter-spacing:0.10em; '
                'text-transform:uppercase; color:#64748b; margin-bottom:12px;">'
                '📍 Sección seleccionada en el mapa</div>',
                unsafe_allow_html=True,
            )
            col_fc1, col_fc2 = st.columns([1, 1], gap="large")
            with col_fc1:
                seccion_card(row_click)
            with col_fc2:
                if int(row_click["n_contactos"]) > 0:
                    fig_det = go.Figure(go.Bar(
                        x=["🟢 Simpatizantes", "🟡 Indecisos", "🔴 Adversos"],
                        y=[int(row_click["n_simp"]), int(row_click["n_ind"]), int(row_click["n_adv"])],
                        marker_color=["#0b6b46", "#d97706", "#a3142b"],
                        text=[int(row_click["n_simp"]), int(row_click["n_ind"]), int(row_click["n_adv"])],
                        textposition="outside",
                    ))
                    fig_det.update_layout(
                        title=f"Detección · Sección {int(sec_click)}",
                        yaxis_title="Contactos",
                        margin=dict(l=8, r=8, t=40, b=10), height=270,
                    )
                    st.plotly_chart(fig_det, use_container_width=True)

                    st.markdown("#### Esta sección vs promedio visitado")
                    df_vis = df[df["n_contactos"] > 0]
                    metricas   = ["Contactos", "Simpatizantes", "Indecisos", "Adversos"]
                    vals_sec   = [int(row_click["n_contactos"]), int(row_click["n_simp"]),
                                  int(row_click["n_ind"]),  int(row_click["n_adv"])]
                    vals_prom  = [df_vis["n_contactos"].mean(), df_vis["n_simp"].mean(),
                                  df_vis["n_ind"].mean(),  df_vis["n_adv"].mean()]
                    fig_cmp = go.Figure()
                    fig_cmp.add_trace(go.Bar(name=f"Secc. {int(sec_click)}",
                                             x=metricas, y=vals_sec,
                                             marker_color="#334155", opacity=0.85))
                    fig_cmp.add_trace(go.Bar(name="Promedio visitado",
                                             x=metricas, y=vals_prom,
                                             marker_color="#94a3b8", opacity=0.70))
                    fig_cmp.update_layout(
                        barmode="group",
                        margin=dict(l=8, r=8, t=10, b=10), height=250,
                        legend=dict(orientation="h", y=-0.22),
                    )
                    st.plotly_chart(fig_cmp, use_container_width=True)
        else:
            st.caption("Haz click en cualquier sección del mapa para ver su ficha de detección completa.")

    # ─────────────────────────────────────────────────────────────────────
    # TAB 2 · DESEMPEÑO DE BRIGADAS
    # ─────────────────────────────────────────────────────────────────────
    with tab2:
        st.markdown(
            '<span class="tag demo">DEMO</span> Métricas operativas y de productividad '
            'por brigada · datos ficticios',
            unsafe_allow_html=True,
        )

        df_vis_b = df[df["brigada"] != "—"].copy()
        brig_stats = []
        for brig in BRIGADAS:
            db = df_vis_b[df_vis_b["brigada"] == brig]
            if len(db) == 0:
                continue
            n_comp_b = int((db["estado"] == "Completada").sum())
            n_cont   = int(db["n_contactos"].sum())
            n_simp   = int(db["n_simp"].sum())
            n_ind    = int(db["n_ind"].sum())
            n_adv    = int(db["n_adv"].sum())
            n_m4     = int(db["n_acepta"].sum())
            pct_s    = round(n_simp / max(n_cont, 1) * 100)
            pct_m4   = round(n_m4   / max(n_cont, 1) * 100)
            brig_stats.append({
                "Brigada":           brig,
                "Secc. asignadas":   len(db),
                "Secc. completadas": n_comp_b,
                "Contactos":         n_cont,
                "🟢 Simp.":          n_simp,
                "🟡 Ind.":           n_ind,
                "🔴 Adv.":           n_adv,
                "% Simpatizantes":   f"{pct_s}%",
                "Listos M4":         n_m4,
                "% Listos M4":       f"{pct_m4}%",
            })
        df_brig = pd.DataFrame(brig_stats)

        # KPIs brigadas
        top_brig = df_brig.loc[df_brig["Contactos"].idxmax(), "Brigada"] if not df_brig.empty else "—"
        brig_m4  = df_brig.loc[df_brig["Listos M4"].idxmax(), "Brigada"] if not df_brig.empty else "—"

        b1, b2, b3, b4 = st.columns(4, gap="medium")
        for col, val, lab, ctx, color in [
            (b1, len(BRIGADAS), "Brigadas activas",      "en Tlaxcala capital",              "#334155"),
            (b2, top_brig,     "Mayor cobertura",        "brigada con más contactos",         "#0b6b46"),
            (b3, brig_m4,      "Más listos para M4",    "más contactos activables",           "#a3142b"),
            (b4, total_ind,    "Indecisos a persuadir", "el objetivo central de la campaña",  "#d97706"),
        ]:
            with col:
                st.markdown(f"""
                <div class="kpi-card" style="border-left-color:{color};">
                  <div class="kpi-val" style="color:{color}; font-size:1.55rem;">{val}</div>
                  <div class="kpi-label">{lab}</div>
                  <div class="kpi-ctx">{ctx}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("")
        st.markdown("#### Desempeño por brigada")
        st.dataframe(df_brig, use_container_width=True, hide_index=True)

        st.markdown("---")
        col_g1, col_g2 = st.columns(2, gap="large")

        with col_g1:
            st.markdown("#### Contactos por brigada")
            fig_brig = go.Figure(go.Bar(
                x=df_brig["Brigada"], y=df_brig["Contactos"],
                marker_color="#334155", opacity=0.85,
                text=df_brig["Contactos"], textposition="outside",
            ))
            fig_brig.update_layout(
                margin=dict(l=8, r=8, t=10, b=10), height=280,
                yaxis_title="Contactos capturados",
            )
            st.plotly_chart(fig_brig, use_container_width=True)

        with col_g2:
            st.markdown("#### Composición de detección por brigada")
            fig_stack = go.Figure()
            for lbl, col_data, color in [
                ("🟢 Simpatizantes", "🟢 Simp.", "#0b6b46"),
                ("🟡 Indecisos",     "🟡 Ind.",  "#d97706"),
                ("🔴 Adversos",      "🔴 Adv.",  "#a3142b"),
            ]:
                fig_stack.add_trace(go.Bar(
                    name=lbl, x=df_brig["Brigada"], y=df_brig[col_data],
                    marker_color=color,
                ))
            fig_stack.update_layout(
                barmode="stack",
                margin=dict(l=8, r=8, t=10, b=10), height=280,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            )
            st.plotly_chart(fig_stack, use_container_width=True)

        st.markdown("---")
        col_g3, col_g4 = st.columns(2, gap="large")

        with col_g3:
            st.markdown("#### Demanda social — lo que le preocupa al electorado")
            df_dem = (
                df[df["n_contactos"] > 0]
                .groupby("demanda_top")["n_contactos"].sum()
                .reset_index()
                .sort_values("n_contactos", ascending=True)
            )
            fig_dem = go.Figure(go.Bar(
                x=df_dem["n_contactos"], y=df_dem["demanda_top"],
                orientation="h", marker_color="#334155", opacity=0.82,
                text=df_dem["n_contactos"], textposition="outside",
            ))
            fig_dem.update_layout(
                xaxis_title="Contactos que mencionan esta demanda",
                margin=dict(l=10, r=30, t=10, b=10), height=310,
            )
            st.plotly_chart(fig_dem, use_container_width=True)

        with col_g4:
            st.markdown("#### Calidad del directorio para M4")
            total_cel = int(df["n_celular"].sum())
            total_ac  = int(df["n_acepta"].sum())
            pct_cel   = round(total_cel / max(total_cont, 1) * 100)
            pct_ac    = round(total_ac  / max(total_cont, 1) * 100)

            fig_funnel = go.Figure(go.Funnel(
                y=["Total contactos", "Con celular válido", "Acepta ser contactado"],
                x=[total_cont, total_cel, total_ac],
                marker_color=["#334155", "#0891b2", "#0b6b46"],
                textinfo="value+percent initial",
            ))
            fig_funnel.update_layout(
                margin=dict(l=8, r=8, t=10, b=10), height=270,
            )
            st.plotly_chart(fig_funnel, use_container_width=True)

            st.html(f"""
            <div style="background:#f0fdf4; border:1px solid #4ade80; border-radius:10px;
                        padding:14px 16px; font-family:'DM Sans',sans-serif; margin-top:8px;">
                <div style="font-size:0.74rem; font-weight:700; color:#166534; margin-bottom:6px;
                            text-transform:uppercase; letter-spacing:0.06em;">
                    Directorio listo para Módulo 4
                </div>
                <div style="font-size:2.0rem; font-weight:800; color:#15803d; line-height:1; margin-bottom:4px;">
                    {total_ac:,} contactos
                </div>
                <div style="font-size:0.80rem; color:#166534;">
                    {pct_cel}% con celular &nbsp;·&nbsp; {pct_ac}% acepta campaña microsegmentada
                </div>
            </div>
            """)

        # Ranking de secciones por simpatizantes
        st.markdown("---")
        st.markdown("#### Ranking de secciones — mayor cantidad de simpatizantes detectados")
        df_rank = df[df["n_simp"] > 0].sort_values("n_simp", ascending=False).head(10)
        max_simp = float(df_rank["n_simp"].max()) if len(df_rank) > 0 else 1.0

        for i, (_, row) in enumerate(df_rank.iterrows()):
            bar_w = int(float(row["n_simp"]) / max_simp * 100)
            arq_c = ARQUETIPOS[str(row["arquetipo_dom"])]["color"]
            sc_c  = score_color(float(row["score"]))
            st.html(f"""
            <div style="display:flex; align-items:center; gap:10px; padding:9px 14px;
                        border-radius:10px; margin-bottom:5px; background:#f8fafc;
                        border:1px solid #e2e8f0; font-family:'DM Sans',sans-serif;">
              <div style="font-size:0.88rem; font-weight:800; color:#94a3b8;
                          min-width:22px; text-align:right;">{i+1}</div>
              <div style="font-size:0.90rem; font-weight:700; color:#1e293b;
                          min-width:76px;">Secc.&nbsp;{int(row['seccion'])}</div>
              <div style="flex:1; background:#e2e8f0; border-radius:4px; height:8px; overflow:hidden;">
                <div style="height:100%; border-radius:4px; width:{bar_w}%; background:#0b6b46;"></div>
              </div>
              <div style="font-size:0.86rem; font-weight:700; color:#0b6b46;
                          min-width:36px; text-align:right;">{int(row['n_simp'])}</div>
              <div style="width:9px; height:9px; border-radius:50%;
                          background:{arq_c}; flex-shrink:0;"></div>
              <div style="font-size:0.73rem; color:#64748b; min-width:28px;">{row['arquetipo_dom']}</div>
              <div style="font-size:0.73rem; color:#94a3b8; min-width:90px; text-align:right;">
                {row['brigada']}</div>
              <div style="font-size:0.73rem; font-weight:700; color:{sc_c};
                          min-width:50px; text-align:right;">Score {row['score']:.0f}</div>
            </div>
            """)


main()