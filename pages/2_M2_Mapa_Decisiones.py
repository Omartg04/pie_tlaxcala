"""
M2 — Mapa de Decisiones
PIE Tlaxcala · Anabel Ávalos · PRI 2027
Foco: Tlaxcala capital · datos electorales reales 2024 · lista nominal actualizada
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
    page_title="M2 · Mapa de Decisiones · PIE Tlaxcala",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Rutas ────────────────────────────────────────────────────────────────────
# pages/ está un nivel abajo del repo — subimos al root para encontrar data/
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

# ════════════════════════════════════════════════════════════════════════════
# DATOS EMBEBIDOS — arquetipos (consistentes con M1)
# ════════════════════════════════════════════════════════════════════════════

ARQUETIPOS = {
    "A1": {
        "nombre":    "El Leal Institucional Tricolor",
        "color":     "#a3142b",
        "prioridad": "Mantenimiento",
        "emoji":     "🔴",
        "desc":      "Voto duro priista. No necesita convencimiento, necesita movilizacion.",
        "frase":     'Yo nunca he dejado al partido, el partido me hizo lo que soy.',
    },
    "A2": {
        "nombre":    "El Decepcionado del Gobierno Estatal",
        "color":     "#dc2626",
        "prioridad": "Maxima",
        "emoji":     "⚡",
        "desc":      "Sin partido fijo. Busca una alternativa que hable de resultados, no de ideologia.",
        "frase":     'No soy de ningun partido, pero ya estoy cansado de que nada cambie.',
    },
    "A3": {
        "nombre":    "El Anti-Sistema Punitivo",
        "color":     "#7c2d92",
        "prioridad": "Alta",
        "emoji":     "🛑",
        "desc":      "Cree que todos los partidos son iguales. Pide ruptura y mano dura.",
        "frase":     'Aqui lo que se necesita es mano dura, ya no aguantamos la impunidad.',
    },
    "A4": {
        "nombre":    "La Guardiana del Miedo de Genero",
        "color":     "#be185d",
        "prioridad": "Alta - nicho",
        "emoji":     "🚨",
        "desc":      "Alerta permanente por la seguridad de las mujeres. Exige compromisos verificables.",
        "frase":     'A mi hija no la dejo salir sola ni de dia, y eso no deberia ser normal.',
    },
    "A5": {
        "nombre":    "El Rural Desatendido por el Estado",
        "color":     "#15803d",
        "prioridad": "Media-alta",
        "emoji":     "🌾",
        "desc":      "Depende del campo. Siente el abandono del gobierno estatal. Pide gestion, no promesas.",
        "frase":     'El camino a mi parcela lleva anos destrozado y nadie del estado lo ha visto.',
    },
    "A6": {
        "nombre":    "La Conforme con la Continuidad",
        "color":     "#0891b2",
        "prioridad": "Baja",
        "emoji":     "🔵",
        "desc":      "No asocia sus problemas con el gobierno estatal. Recibe apoyos y los valora.",
        "frase":     'A mi me ha ido bien, no tengo queja del gobierno.',
    },
    "A7": {
        "nombre":    "El Susceptible a la Ruptura",
        "color":     "#c2410c",
        "prioridad": "Alta - oportunidad y riesgo",
        "emoji":     "⚠️",
        "desc":      "El mas volatil. Se va con quien prometa orden inmediato, sin importar el partido.",
        "frase":     'Ya no me importa de que partido sea, solo quiero que alguien meta orden.',
    },
    "A8": {
        "nombre":    "El Desconectado de lo Estatal",
        "color":     "#64748b",
        "prioridad": "No prioritario",
        "emoji":     "⚪",
        "desc":      "Culpa al municipio, no al estado. Bajo retorno para gobernatura.",
        "frase":     'Aqui el problema es el ayuntamiento, eso no tiene nada que ver con el estado.',
    },
}

# Distribución de arquetipos en Tlaxcala capital (consistente con M1)
ARQ_PCT_CAPITAL = {
    "A1": 14, "A2": 16, "A3": 10, "A4": 7,
    "A5":  3, "A6": 22, "A7": 12, "A8": 16,
}

ARQ_MENSAJE = {
    "A1": "Activa la red de leales — no necesitan convencimiento, necesitan movilización. "
          "Identifica líderes locales del partido y ponlos a trabajar.",
    "A2": "Conecta el enojo directamente con el gobierno estatal. Habla de gestión y "
          "resultados concretos, no del PRI como marca.",
    "A3": "Mensaje de ruptura con el sistema actual. Propuesta de orden y rendición de "
          "cuentas — sin lenguaje partidista tradicional.",
    "A4": "Aborda la violencia de género de forma específica y medible. "
          "Compromisos verificables y concretos, nada genérico.",
    "A5": "Presencia territorial, no discurso. Gestión de infraestructura, agua y campo. "
          "Este electorado pide que alguien resuelva, no que prometa.",
    "A6": "No es target prioritario — solo monitoreo. "
          "No invertir tiempo de brigada aquí.",
    "A7": "El más volátil. Mensaje de orden inmediato y mano dura. "
          "Cuidado: puede irse con cualquier candidato que suene a resultados ya.",
    "A8": "No culpa al gobierno estatal — muy bajo retorno para gobernatura. "
          "Cero brigada aquí en esta elección.",
}

PRIORIDAD_COLOR = {
    "Maxima":                       "#dc2626",
    "Alta":                         "#c2410c",
    "Alta - nicho":                 "#be185d",
    "Alta - oportunidad y riesgo":  "#7c2d92",
    "Media-alta":                   "#0e7490",
    "Mantenimiento":                "#15803d",
    "Baja":                         "#64748b",
    "No prioritario":               "#94a3b8",
}


def score_color(score: float) -> str:
    if score >= 70:
        return "#a3142b"
    if score >= 55:
        return "#f97316"
    if score >= 40:
        return "#eab308"
    return "#94a3b8"


def score_label(score: float) -> str:
    if score >= 70:
        return "🔴 Alta rentabilidad"
    if score >= 55:
        return "🟠 Media-alta"
    if score >= 40:
        return "🟡 Media"
    return "⚪ Baja rentabilidad"


# ════════════════════════════════════════════════════════════════════════════
# CSS
# ════════════════════════════════════════════════════════════════════════════

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

[data-testid="stSidebar"] { background-color: #5c0c18 !important; }
[data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span,
[data-testid="stSidebar"] div, [data-testid="stSidebar"] label { color: #f5e6e9 !important; }

.header-modulo {
    --accent: #3f7a52;
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
.tag.imp  { background: #fee2e2; color: #991b1b; }

.kpi-card {
    background: #f8fafc; border-left: 4px solid #0b6b46;
    border-radius: 0 10px 10px 0; padding: 14px 16px; height: 100%;
}
.kpi-val   { font-size: 1.75rem; font-weight: 800; color: #1e293b; line-height: 1.1; }
.kpi-label { font-size: 0.78rem; font-weight: 600; color: #1e293b; margin-top: 4px; }
.kpi-ctx   { font-size: 0.72rem; color: #64748b; margin-top: 2px; line-height: 1.3; }

.leyenda-item {
    display: flex; align-items: center; gap: 8px;
    margin-bottom: 6px; font-size: 0.80rem; color: #334155;
}
.leyenda-dot { width: 11px; height: 11px; border-radius: 50%; flex-shrink: 0; }

.teaser-card {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    border: 1px solid #86efac; border-radius: 14px;
    padding: 36px 40px; text-align: center; margin-top: 16px;
}
.teaser-card h3 { font-size: 1.2rem; font-weight: 700; color: #14532d; margin-bottom: 10px; }
.teaser-card p  { font-size: 0.88rem; color: #166534; line-height: 1.65; margin: 0; }
.teaser-chip {
    display: inline-block; background: #fff; border: 1px solid #86efac;
    border-radius: 10px; padding: 8px 18px; font-size: 0.82rem;
    color: #14532d; font-weight: 600; margin: 4px;
}
</style>
"""

# ════════════════════════════════════════════════════════════════════════════
# CARGA Y PROCESAMIENTO DE DATOS
# ════════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_data():
    # GeoJSON —————————————————————————————————————————————————————————————
    geo_path = os.path.join(DATA, "secciones_capital.geojson")
    with open(geo_path) as f:
        geo = json.load(f)
    secs_geo = [feat["properties"]["seccion"] for feat in geo["features"]]
    df = pd.DataFrame({"seccion": secs_geo})

    # Resultados 2024 ——————————————————————————————————————————————————————
    df_res = pd.read_csv(os.path.join(DATA, "Resultados_2024_Tlaxcala.csv"))
    df_res = df_res[df_res["ID_MUNICIPIO"] == 33][
        ["SECCION", "PRI", "MORENA", "PAN",
         "NUM_VOTOS_VALIDOS", "TOTAL_VOTOS", "LISTA_NOMINAL"]
    ].copy()
    df_res.columns = [
        "seccion", "votos_pri", "votos_morena", "votos_pan",
        "votos_validos", "total_votos", "lista_nominal_res",
    ]

    # Lista Nominal actualizada ——————————————————————————————————————————
    df_ln = pd.read_csv(os.path.join(DATA, "Lista_nominal_Tlaxcala.csv"))
    df_ln.columns = [c.replace("\n", "_").strip() for c in df_ln.columns]
    df_ln = df_ln[df_ln["CLAVE_MUNICIPIO"] == 33][
        ["SECCION", "LISTA_NOMINAL", "LISTA_HOMBRES", "LISTA_MUJERES"]
    ].copy()
    df_ln.columns = ["seccion", "lista_nominal", "lista_hombres", "lista_mujeres"]

    # Joins ————————————————————————————————————————————————————————————————
    df = df.merge(df_res, on="seccion", how="left")
    df = df.merge(df_ln,  on="seccion", how="left")

    # Imputación — 10 secciones sin resultados 2024 (secciones nuevas/reactivadas)
    avg_part    = df_res["total_votos"].sum()  / df_ln["lista_nominal"].sum()
    avg_pct_pri = df_res["votos_pri"].sum()    / df_res["votos_validos"].sum()
    avg_pct_mor = df_res["votos_morena"].sum() / df_res["votos_validos"].sum()
    avg_pct_pan = df_res["votos_pan"].sum()    / df_res["votos_validos"].sum()

    no_res = df["votos_validos"].isna()
    df.loc[no_res, "votos_validos"] = (df.loc[no_res, "lista_nominal"] * avg_part).round()
    df.loc[no_res, "votos_pri"]     = (df.loc[no_res, "votos_validos"] * avg_pct_pri).round()
    df.loc[no_res, "votos_morena"]  = (df.loc[no_res, "votos_validos"] * avg_pct_mor).round()
    df.loc[no_res, "votos_pan"]     = (df.loc[no_res, "votos_validos"] * avg_pct_pan).round()
    df.loc[no_res, "total_votos"]   = df.loc[no_res, "votos_validos"]
    df["es_imputado"] = no_res.astype(bool)

    # Porcentajes ——————————————————————————————————————————————————————————
    df["pct_pri"]       = (df["votos_pri"]    / df["votos_validos"] * 100).round(1)
    df["pct_morena"]    = (df["votos_morena"] / df["votos_validos"] * 100).round(1)
    df["pct_pan"]       = (df["votos_pan"]    / df["votos_validos"] * 100).round(1)
    df["margen"]        = (df["pct_morena"] - df["pct_pri"]).round(1)
    df["participacion"] = (df["total_votos"]  / df["lista_nominal"] * 100).round(1)
    df["pct_otros"]     = (100 - df["pct_pri"] - df["pct_morena"] - df["pct_pan"]).clip(0).round(1)
    df["pct_mujeres"]   = (df["lista_mujeres"] / df["lista_nominal"] * 100).round(1)
    df["pct_hombres"]   = (100 - df["pct_mujeres"]).round(1)

    # Arquetipos por sección — variación Dirichlet, semilla fija ——————————
    rng = np.random.default_rng(42)
    arq_codes    = list(ARQ_PCT_CAPITAL.keys())
    base_weights = np.array([ARQ_PCT_CAPITAL[k] for k in arq_codes], dtype=float)
    base_weights /= base_weights.sum()
    mixes = rng.dirichlet(base_weights * 4, size=len(df))   # (43, 8)
    df["arquetipo_dom"] = [arq_codes[int(np.argmax(m))] for m in mixes]

    idx_p = [arq_codes.index(k) for k in ["A2", "A3", "A7"]]
    df["pct_persuadables"] = (mixes[:, idx_p].sum(axis=1) * 100).round(1)

    # Score de rentabilidad ————————————————————————————————————————————————
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

    # Centroides por sección — para lookup de click en mapa ——————————————
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

def build_map(
    geo: dict,
    df: pd.DataFrame,
    color_by: str = "score",
    arq_filter: list | None = None,
) -> folium.Map:
    lookup = df.set_index("seccion")
    filtro_activo = bool(arq_filter)

    m = folium.Map(
        location=[19.308, -98.237],
        zoom_start=13,
        tiles="CartoDB positron",
        prefer_canvas=True,
    )

    def style_fn(feature):
        sec = feature["properties"]["seccion"]
        if sec not in lookup.index:
            return {"fillColor": "#e2e8f0", "fillOpacity": 0.15, "color": "#e2e8f0", "weight": 0.5}

        row  = lookup.loc[sec]
        arq  = str(row["arquetipo_dom"])
        en_filtro = (not filtro_activo) or (arq in arq_filter)

        if not en_filtro:
            # Sección fuera del filtro — casi invisible
            return {"fillColor": "#e2e8f0", "fillOpacity": 0.12, "color": "#cbd5e1", "weight": 0.5}

        fill = (
            score_color(float(row["score"]))
            if color_by == "score"
            else ARQUETIPOS[arq]["color"]
        )
        return {"fillColor": fill, "fillOpacity": 0.80, "color": "#ffffff", "weight": 1.4}

    def highlight_fn(feature):
        return {"fillColor": "#fbbf24", "fillOpacity": 0.9, "color": "#fff", "weight": 2.5}

    # Enriquecer propiedades para tooltip
    geo_rich = json.loads(json.dumps(geo))
    for feat in geo_rich["features"]:
        sec = feat["properties"]["seccion"]
        if sec in lookup.index:
            r = lookup.loc[sec]
            feat["properties"].update({
                "Score":         int(r["score"]),
                "Arquetipo":     str(r["arquetipo_dom"]),
                "PRI 2024":      f"{r['pct_pri']:.1f}%",
                "Morena 2024":   f"{r['pct_morena']:.1f}%",
                "Margen":        f"{'+' if r['margen'] > 0 else ''}{r['margen']:.1f} pp",
                "Lista nominal": f"{int(r['lista_nominal']):,}",
                "Participación": f"{r['participacion']:.1f}%",
            })

    folium.GeoJson(
        geo_rich,
        style_function=style_fn,
        highlight_function=highlight_fn,
        tooltip=folium.GeoJsonTooltip(
            fields=["seccion", "Score", "Arquetipo",
                    "PRI 2024", "Morena 2024", "Margen",
                    "Lista nominal", "Participación"],
            aliases=["Sección", "Score", "Arquetipo",
                     "PRI 2024", "Morena 2024", "Margen",
                     "Lista nominal", "Participación"],
            sticky=True,
            labels=True,
            style=(
                "font-family:'DM Sans',sans-serif; font-size:13px;"
                "background:#fff; border:1px solid #e2e8f0; border-radius:8px;"
            ),
            max_width=260,
        ),
        name="secciones",
    ).add_to(m)

    return m


# ════════════════════════════════════════════════════════════════════════════
# FICHA DE SECCIÓN
# ════════════════════════════════════════════════════════════════════════════

def section_card(row: pd.Series) -> None:
    arq_code    = str(row["arquetipo_dom"])
    arq         = ARQUETIPOS[arq_code]
    sc          = float(row["score"])
    badge_color = PRIORIDAD_COLOR.get(arq["prioridad"], "#64748b")
    s_color     = score_color(sc)
    s_label     = score_label(sc)
    es_imp      = bool(row.get("es_imputado", False))

    tag_html = (
        '<span style="background:#fee2e2;color:#991b1b;font-size:0.62rem;'
        'font-weight:700;padding:1px 7px;border-radius:8px;text-transform:uppercase;">'
        'IMPUTADO</span>'
        if es_imp else
        '<span style="background:#dcfce7;color:#166534;font-size:0.62rem;'
        'font-weight:700;padding:1px 7px;border-radius:8px;text-transform:uppercase;">'
        'REAL</span>'
    )

    lista   = int(row["lista_nominal"])
    pct_muj = float(row["pct_mujeres"])
    pct_hom = float(row["pct_hombres"])
    margen  = float(row["margen"])
    mar_c   = "#7c2d12" if margen > 0 else "#15803d"
    mar_str = f"+{margen:.1f}" if margen > 0 else f"{margen:.1f}"

    st.html(f"""
    <div style="font-family:'DM Sans',sans-serif; max-width:600px;">

      <div style="background:linear-gradient(135deg,#04402c 0%,#0b6b46 100%);
                  border-radius:12px 12px 0 0; padding:18px 22px;">
        <div style="font-size:0.70rem; font-weight:700; letter-spacing:0.10em;
                    text-transform:uppercase; color:#d2f2e3; margin-bottom:8px;">
          🗺️ Sección {int(row['seccion'])} · Tlaxcala capital · Distrito local 7
        </div>
        <div style="display:flex; align-items:center; gap:18px;">
          <div>
            <span style="font-size:2.2rem; font-weight:800; color:#fff; line-height:1;">
              {sc:.0f}
            </span>
            <span style="font-size:0.76rem; color:#d2f2e3; margin-left:4px;">/100</span>
          </div>
          <div style="flex:1;">
            <div style="background:rgba(255,255,255,0.18); border-radius:6px;
                        height:10px; overflow:hidden; margin-bottom:5px;">
              <div style="height:100%; border-radius:6px; width:{int(sc)}%;
                          background:#fbbf24;"></div>
            </div>
            <div style="font-size:0.78rem; color:#d2f2e3;">{s_label}</div>
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
            <div style="font-size:0.80rem; color:#475569; line-height:1.45;">
              {arq['desc']}
            </div>
          </div>
        </div>
        <div style="background:#f8fafc; border-left:3px solid {arq['color']}; border-radius:0 8px 8px 0;
                    padding:10px 14px; margin-bottom:14px;">
          <div style="font-size:0.80rem; color:#7c2d92; font-style:italic; line-height:1.45;">
            {arq['frase']}
          </div>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
          <div style="background:#f0fdf4; border-radius:8px; padding:12px 14px; text-align:center;">
            <div style="font-size:1.5rem; font-weight:800; color:#0b6b46;">{lista:,}</div>
            <div style="font-size:0.72rem; color:#64748b; margin-top:2px;">
              electores lista nominal &nbsp;{tag_html}
            </div>
          </div>
          <div style="background:#f0fdf4; border-radius:8px; padding:12px 14px; text-align:center;">
            <div style="font-size:1.5rem; font-weight:800; color:#0b6b46;">{pct_muj:.0f}%</div>
            <div style="font-size:0.72rem; color:#64748b; margin-top:2px;">
              mujeres · {pct_hom:.0f}% hombres
            </div>
          </div>
        </div>
      </div>

      <div style="background:#f8fafc; border:1px solid #e2e8f0; border-top:none; padding:18px 22px;">
        <div style="font-size:0.66rem; font-weight:700; letter-spacing:0.10em;
                    text-transform:uppercase; color:#64748b; margin-bottom:10px;">
          🗳️ ¿Cómo votaron en 2024? &nbsp;{tag_html}
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; margin-bottom:12px;">
          <div style="background:#fff0f0; border-radius:8px; padding:10px; text-align:center;">
            <div style="font-size:1.55rem; font-weight:800; color:#a3142b;">
              {row['pct_pri']:.1f}%
            </div>
            <div style="font-size:0.70rem; color:#64748b;">PRI</div>
          </div>
          <div style="background:#fdf2e9; border-radius:8px; padding:10px; text-align:center;">
            <div style="font-size:1.55rem; font-weight:800; color:#7c2d12;">
              {row['pct_morena']:.1f}%
            </div>
            <div style="font-size:0.70rem; color:#64748b;">Morena</div>
          </div>
          <div style="background:#f0f9ff; border-radius:8px; padding:10px; text-align:center;">
            <div style="font-size:1.55rem; font-weight:800; color:#0369a1;">
              {row['participacion']:.1f}%
            </div>
            <div style="font-size:0.70rem; color:#64748b;">participación</div>
          </div>
        </div>
        <div style="font-size:0.83rem; color:#475569;">
          Margen Morena sobre PRI:
          <b style="color:{mar_c}; font-size:0.92rem;">{mar_str} pp</b>
        </div>
      </div>

      <div style="background:#fff; border:1px solid #e2e8f0; border-top:none;
                  border-radius:0 0 12px 12px; padding:18px 22px;">
        <div style="font-size:0.66rem; font-weight:700; letter-spacing:0.10em;
                    text-transform:uppercase; color:#64748b; margin-bottom:10px;">
          📣 ¿Qué mensaje importa en esta sección?
        </div>
        <div style="background:#fff7ed; border:1px solid #fdba74; border-radius:10px;
                    padding:14px 16px; font-size:0.86rem; color:#7c2d12; line-height:1.6;">
          {ARQ_MENSAJE[arq_code]}
        </div>
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
      <div class="hm-eyebrow">Módulo 02 · En operación</div>
      <h1>🗺️ Mapa de Decisiones</h1>
      <p>Estos son tus votantes. Aquí viven. Así ha sido la elección. Este es el mensaje que importa.</p>
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
            "📍 Municipio",
            options=list(MUN_OPCIONES.keys()),
            index=0,
            key="m2_municipio",
        )
    mun_key = MUN_OPCIONES[mun_label]

    # ── Apizaco / Huamantla → teaser ─────────────────────────────────────
    if mun_key != "capital":
        info = MUN_INFO[mun_key]
        with col_ctx:
            st.markdown(
                f'<div style="padding:10px 0; font-size:0.84rem; color:#64748b;">'
                f'El análisis detallado de <b>{info["nombre"]}</b> '
                f'({info["secciones"]} secciones) se activa en la siguiente fase.</div>',
                unsafe_allow_html=True,
            )
        st.markdown(f"""
        <div class="teaser-card">
          <div style="font-size:2.8rem; margin-bottom:14px;">🗺️</div>
          <h3>{info['nombre']} · {info['secciones']} secciones mapeadas</h3>
          <p>
            Los datos electorales reales 2024 y la lista nominal actualizada
            de {info['nombre']} ya están integrados a la plataforma.<br>
            El mapa interactivo, el ranking de rentabilidad y las fichas de brigada
            se activan en la siguiente fase del módulo.
          </p>
          <div style="margin-top:20px;">
            <span class="teaser-chip">✅ Resultados 2024 integrados</span>
            <span class="teaser-chip">✅ Lista nominal actualizada</span>
            <span class="teaser-chip">✅ Shape INE oficial</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Tlaxcala capital ──────────────────────────────────────────────────
    with col_ctx:
        st.markdown(
            '<div style="padding:10px 0; font-size:0.83rem; color:#166534; font-weight:600;">'
            '🟢 Tlaxcala capital · 43 secciones · '
            'resultados electorales reales 2024 · lista nominal actualizada</div>',
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

    # ── KPIs ─────────────────────────────────────────────────────────────
    st.markdown("---")
    total_electores = int(df["lista_nominal"].sum())
    n_alta          = int((df["score"] >= 70).sum())
    score_prom      = float(df["score"].mean())
    margen_prom     = float(df["margen"].mean())

    k1, k2, k3, k4, k5 = st.columns(5, gap="medium")
    kpis = [
        (k1, f"{total_electores:,}", "Lista nominal",        "electores registrados · capital",           "#0b6b46", "real"),
        (k2, "43",                   "Secciones mapeadas",   "Tlaxcala capital · distrito local 7",        "#0b6b46", "real"),
        (k3, str(n_alta),            "Alta rentabilidad",    "score ≥ 70 · prioridad brigada",             "#a3142b", "demo"),
        (k4, f"{score_prom:.0f}/100","Score promedio",       "competitividad + base PRI + peso electoral", "#475569", "demo"),
        (k5, f"+{margen_prom:.1f} pp","Ventaja Morena prom.","margen Morena sobre PRI · 2024",             "#7c2d12", "real"),
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

    # ── Tabs ─────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs([
        "🗺️ Mapa",
        "📊 Ranking de secciones",
        "📋 Ficha de sección",
    ])

    # TAB 1 — MAPA ────────────────────────────────────────────────────────
    with tab1:
        col_ctrl, col_map = st.columns([1, 3], gap="medium")

        with col_ctrl:
            color_by = st.radio(
                "Colorear por",
                options=["score", "arquetipo"],
                format_func=lambda x: (
                    "Score de rentabilidad" if x == "score" else "Arquetipo dominante"
                ),
                key="m2_color_by",
            )

            st.markdown("---")

            # ── Filtro por arquetipo ──────────────────────────────────────
            st.markdown("**Filtrar secciones**")
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
                key="m2_arq_filter",
                label_visibility="collapsed",
            )
            arq_filter = [arq_opciones[lbl] for lbl in sel_labels] if sel_labels else None

            if arq_filter:
                n_visibles = int((df["arquetipo_dom"].isin(arq_filter)).sum())
                st.markdown(
                    f'<div style="background:#fef3c7; border-radius:8px; padding:8px 10px; '
                    f'font-size:0.76rem; color:#92400e; margin-top:4px;">'
                    f'🔍 {n_visibles} secciones visibles</div>',
                    unsafe_allow_html=True,
                )

            st.markdown("---")
            st.markdown("**Leyenda**")

            if color_by == "score":
                for etiqueta, color in [
                    ("Alta rentabilidad (≥ 70)", "#a3142b"),
                    ("Media-alta (55–69)",        "#f97316"),
                    ("Media (40–54)",             "#eab308"),
                    ("Baja (< 40)",               "#94a3b8"),
                ]:
                    st.markdown(
                        f'<div class="leyenda-item">'
                        f'<div class="leyenda-dot" style="background:{color};"></div>'
                        f'<span>{etiqueta}</span></div>',
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
            st.caption("💡 Pasa el cursor sobre una sección para ver sus datos. Haz click para ver la ficha completa.")

        with col_map:
            m = build_map(geo, df, color_by=color_by, arq_filter=arq_filter)
            filter_key = "_".join(sorted(arq_filter)) if arq_filter else "all"
            map_data = st_folium(
                m,
                width=None,
                height=530,
                use_container_width=True,
                returned_objects=["last_object_clicked"],
                key=f"m2_folium_{color_by}_{filter_key}",
            )

        # ── Ficha al hacer click en el mapa ───────────────────────────────
        clicked = map_data.get("last_object_clicked") if map_data else None
        if clicked and clicked.get("lat") and clicked.get("lng"):
            clat, clng = float(clicked["lat"]), float(clicked["lng"])
            # Encontrar la sección más cercana al punto clicado
            sec_click = min(
                centroids,
                key=lambda s: (centroids[s][0] - clat) ** 2 + (centroids[s][1] - clng) ** 2,
            )
            row_click = df[df["seccion"] == sec_click].iloc[0]

            st.markdown("---")
            st.markdown(
                f'<div style="font-size:0.70rem; font-weight:700; letter-spacing:0.10em; '
                f'text-transform:uppercase; color:#64748b; margin-bottom:12px;">'
                f'📍 Sección seleccionada en el mapa</div>',
                unsafe_allow_html=True,
            )
            col_fc1, col_fc2 = st.columns([1, 1], gap="large")
            with col_fc1:
                section_card(row_click)
            with col_fc2:
                pcts_c = [
                    float(row_click["pct_pri"]),
                    float(row_click["pct_morena"]),
                    float(row_click["pct_pan"]),
                    float(row_click["pct_otros"]),
                ]
                fig_c = go.Figure(go.Bar(
                    x=["PRI", "Morena", "PAN", "Otros"], y=pcts_c,
                    marker_color=["#a3142b", "#7c2d12", "#1d4ed8", "#94a3b8"],
                    text=[f"{p:.1f}%" for p in pcts_c],
                    textposition="outside",
                ))
                fig_c.update_layout(
                    title=f"Resultado 2024 · Sección {int(sec_click)}",
                    yaxis=dict(range=[0, max(pcts_c) * 1.4], title="%"),
                    margin=dict(l=8, r=8, t=40, b=10), height=290,
                )
                st.plotly_chart(fig_c, use_container_width=True)

                st.markdown("#### Esta sección vs promedio capital")
                metrics_c   = ["PRI%", "Morena%", "Participación%", "Score"]
                vals_sec_c  = [
                    float(row_click["pct_pri"]),
                    float(row_click["pct_morena"]),
                    float(row_click["participacion"]),
                    float(row_click["score"]),
                ]
                vals_prom_c = [
                    float(df["pct_pri"].mean()),
                    float(df["pct_morena"].mean()),
                    float(df["participacion"].mean()),
                    float(df["score"].mean()),
                ]
                fig_cmp = go.Figure()
                fig_cmp.add_trace(go.Bar(
                    name=f"Secc. {int(sec_click)}", x=metrics_c, y=vals_sec_c,
                    marker_color="#a3142b", opacity=0.85,
                ))
                fig_cmp.add_trace(go.Bar(
                    name="Promedio capital", x=metrics_c, y=vals_prom_c,
                    marker_color="#94a3b8", opacity=0.70,
                ))
                fig_cmp.update_layout(
                    barmode="group",
                    margin=dict(l=8, r=8, t=20, b=10), height=260,
                    legend=dict(orientation="h", y=-0.22),
                )
                st.plotly_chart(fig_cmp, use_container_width=True)
        else:
            st.caption("Haz click en cualquier sección del mapa para ver su ficha completa.")

    # TAB 2 — RANKING ─────────────────────────────────────────────────────
    with tab2:
        st.markdown(
            '<span class="tag real">REAL</span> Resultados 2024 · lista nominal &nbsp;'
            '<span class="tag demo">DEMO</span> Arquetipos · score',
            unsafe_allow_html=True,
        )
        st.markdown("")

        col_rank, col_stats = st.columns([2, 1], gap="large")

        with col_rank:
            st.markdown("#### Prioridad de visita — de mayor a menor rentabilidad")
            max_sc = float(df["score"].max())

            for _, row in df.iterrows():
                sc    = float(row["score"])
                bar_w = int(sc / max_sc * 100)
                sc_c  = score_color(sc)
                nota  = " ·" if bool(row["es_imputado"]) else ""
                arq_c = ARQUETIPOS[str(row["arquetipo_dom"])]["color"]

                st.html(f"""
                <div style="display:flex; align-items:center; gap:10px; padding:9px 14px;
                            border-radius:10px; margin-bottom:5px; background:#f8fafc;
                            border:1px solid #e2e8f0; font-family:'DM Sans',sans-serif;">
                  <div style="font-size:0.88rem; font-weight:800; color:#94a3b8;
                              min-width:22px; text-align:right;">{int(row['rank'])}</div>
                  <div style="font-size:0.90rem; font-weight:700; color:#1e293b;
                              min-width:76px;">Secc.&nbsp;{int(row['seccion'])}{nota}</div>
                  <div style="flex:1; background:#e2e8f0; border-radius:4px; height:8px; overflow:hidden;">
                    <div style="height:100%; border-radius:4px; width:{bar_w}%; background:{sc_c};"></div>
                  </div>
                  <div style="font-size:0.86rem; font-weight:700; color:{sc_c};
                              min-width:36px; text-align:right;">{sc:.0f}</div>
                  <div style="width:9px; height:9px; border-radius:50%;
                              background:{arq_c}; flex-shrink:0;"></div>
                  <div style="font-size:0.73rem; color:#64748b; min-width:28px;">
                    {row['arquetipo_dom']}</div>
                  <div style="font-size:0.73rem; color:#94a3b8;
                              min-width:58px; text-align:right;">PRI {row['pct_pri']:.1f}%</div>
                </div>
                """)

            st.caption("· Resultado electoral imputado con promedio municipal 2024.")

        with col_stats:
            st.markdown("#### Distribución del score")
            fig_hist = go.Figure(go.Histogram(
                x=df["score"], nbinsx=10,
                marker_color="#0b6b46", opacity=0.85,
            ))
            fig_hist.add_vline(x=70, line_dash="dash", line_color="#a3142b",
                               annotation_text="Alta rent.", annotation_position="top right")
            fig_hist.add_vline(x=55, line_dash="dash", line_color="#f97316",
                               annotation_text="Media-alta", annotation_position="top right")
            fig_hist.update_layout(
                xaxis_title="Score", yaxis_title="Secciones",
                margin=dict(l=8, r=8, t=20, b=10), height=250,
            )
            st.plotly_chart(fig_hist, use_container_width=True)

            st.markdown("#### Top 5 · brigada aquí primero")
            top5 = df.head(5)[
                ["rank", "seccion", "score", "pct_pri", "pct_morena", "lista_nominal"]
            ].copy()
            top5.columns = ["#", "Sección", "Score", "PRI%", "Morena%", "Nominal"]
            top5["Sección"] = top5["Sección"].astype(int)
            top5["Nominal"] = top5["Nominal"].astype(int)
            st.dataframe(top5, use_container_width=True, hide_index=True)

    # TAB 3 — FICHA ───────────────────────────────────────────────────────
    with tab3:
        col_sel3, col_tip = st.columns([2, 1])
        with col_sel3:
            secs = sorted(df["seccion"].astype(int).tolist())
            sec_sel = st.selectbox(
                "Selecciona una sección",
                options=secs,
                format_func=lambda x: (
                    f"Sección {x}  ·  "
                    f"Score {df[df['seccion']==x]['score'].values[0]:.0f}  ·  "
                    f"{df[df['seccion']==x]['arquetipo_dom'].values[0]}"
                ),
                key="m2_sec_sel",
            )
        with col_tip:
            st.markdown(
                '<div style="padding-top:28px; font-size:0.79rem; color:#64748b;">'
                'Las secciones están ordenadas por número. '
                'Para ir directo a las más rentables, revisa el ranking ↑</div>',
                unsafe_allow_html=True,
            )

        row_sel = df[df["seccion"] == sec_sel].iloc[0]
        col_card, col_charts = st.columns([1, 1], gap="large")

        with col_card:
            section_card(row_sel)

        with col_charts:
            # Resultado electoral
            pcts = [
                float(row_sel["pct_pri"]),
                float(row_sel["pct_morena"]),
                float(row_sel["pct_pan"]),
                float(row_sel["pct_otros"]),
            ]
            fig_bar = go.Figure(go.Bar(
                x=["PRI", "Morena", "PAN", "Otros"], y=pcts,
                marker_color=["#a3142b", "#7c2d12", "#1d4ed8", "#94a3b8"],
                text=[f"{p:.1f}%" for p in pcts],
                textposition="outside",
            ))
            fig_bar.update_layout(
                title=f"Resultado 2024 · Sección {int(sec_sel)}",
                yaxis=dict(range=[0, max(pcts) * 1.4], title="%"),
                margin=dict(l=8, r=8, t=40, b=10), height=290,
            )
            st.plotly_chart(fig_bar, use_container_width=True)

            # Sección vs promedio capital
            st.markdown("#### Esta sección vs promedio capital")
            metrics   = ["PRI%", "Morena%", "Participación%", "Score"]
            vals_sec  = [
                float(row_sel["pct_pri"]),
                float(row_sel["pct_morena"]),
                float(row_sel["participacion"]),
                float(row_sel["score"]),
            ]
            vals_prom = [
                float(df["pct_pri"].mean()),
                float(df["pct_morena"].mean()),
                float(df["participacion"].mean()),
                float(df["score"].mean()),
            ]
            fig_comp = go.Figure()
            fig_comp.add_trace(go.Bar(
                name=f"Secc. {int(sec_sel)}", x=metrics, y=vals_sec,
                marker_color="#a3142b", opacity=0.85,
            ))
            fig_comp.add_trace(go.Bar(
                name="Promedio capital", x=metrics, y=vals_prom,
                marker_color="#94a3b8", opacity=0.70,
            ))
            fig_comp.update_layout(
                barmode="group",
                margin=dict(l=8, r=8, t=20, b=10), height=270,
                legend=dict(orientation="h", y=-0.2),
            )
            st.plotly_chart(fig_comp, use_container_width=True)


main()