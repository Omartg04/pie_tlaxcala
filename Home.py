"""
Home.py — Plataforma de Inteligencia Electoral (PIE) · Tlaxcala
Data & AI Inclusion Technologies · Anabel Ávalos · PRI rumbo a 2027
Demo · Junio 2026
"""

import streamlit as st
import os

# ── Rutas relativas ───────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")

# ── Metadatos del corte (ajustar conforme avance el piloto) ──────────────────
FECHA_CORTE_ENCUESTA  = "19–22 marzo 2026"
FECHA_CORTE_OPERATIVO = "Piloto · junio 2026"

# ── Pulso operativo — placeholders del piloto territorial ────────────────────
# NOTA: estos valores son ficticios (demo), excepto donde se indica "real".
N_CONTACTOS        = 1847   # ficticio — piloto en 3 municipios
ALCANCE_ESTIMADO    = 6649   # ficticio — N_CONTACTOS * tamaño de hogar promedio Tlaxcala (~3.6)
SECCIONES_PILOTO    = "38 / ~120"  # ficticio — secciones con presencia en los 3 municipios piloto
PCT_PRI_REAL        = 14.0   # REAL — Enkoll / El Universal, 19–22 marzo 2026
PCT_CELULAR         = 68.5   # ficticio — estimado para el piloto

# ── CSS global — colores institucionales PRI (rojo / verde / blanco) ────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── Header ── */
.home-header {
    background: linear-gradient(135deg, #5c0c18 0%, #a3142b 55%, #d4263f 100%);
    border-radius: 16px;
    padding: 36px 40px 28px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.home-header::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 240px; height: 240px;
    border-radius: 50%;
    background: rgba(255,255,255,0.05);
}
.home-header::after {
    content: '';
    position: absolute;
    bottom: -40px; left: 40%;
    width: 180px; height: 180px;
    border-radius: 50%;
    background: rgba(255,255,255,0.04);
}
.header-tag {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    color: #ffd166;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.header-title {
    font-size: 2.0rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.2;
    margin-bottom: 6px;
}
.header-sub {
    font-size: 1.0rem;
    color: #fbd7dc;
    margin-bottom: 16px;
}
.header-corte {
    display: inline-block;
    background: rgba(255,255,255,0.14);
    border: 1px solid rgba(255,255,255,0.22);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.78rem;
    color: #ffffff;
    font-weight: 500;
    margin-right: 8px;
}

/* ── Sección títulos ── */
.section-title {
    font-size: 1.0rem;
    font-weight: 700;
    color: #1e293b;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 8px;
    margin-top: 36px;
    margin-bottom: 18px;
}

/* ── Cards principales (4 módulos) ── */
.journey-card {
    border-radius: 16px;
    padding: 26px 24px 22px;
    min-height: 250px;
    position: relative;
    overflow: hidden;
    color: #ffffff;
}
.journey-card.card-1 {
    background:
        radial-gradient(circle at 85% 15%, rgba(255,209,102,0.18) 0%, transparent 55%),
        linear-gradient(145deg, #5c0c18 0%, #8c0f22 100%);
}
.journey-card.card-2 {
    background:
        radial-gradient(circle at 85% 15%, rgba(110,231,183,0.18) 0%, transparent 55%),
        linear-gradient(145deg, #04402c 0%, #0b6b46 100%);
}
.journey-card.card-3 {
    background:
        radial-gradient(circle at 85% 15%, rgba(148,163,184,0.20) 0%, transparent 55%),
        linear-gradient(145deg, #1f2937 0%, #334155 100%);
}
.journey-card.card-4 {
    background:
        radial-gradient(circle at 85% 15%, rgba(255,209,102,0.22) 0%, transparent 55%),
        linear-gradient(145deg, #7a4a04 0%, #b8860b 100%);
}
.journey-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image: repeating-linear-gradient(
        -45deg,
        rgba(255,255,255,0.028) 0px,
        rgba(255,255,255,0.028) 1px,
        transparent 1px,
        transparent 18px
    );
    pointer-events: none;
}
.journey-card::after {
    content: '';
    position: absolute;
    top: -45px; right: -45px;
    width: 150px; height: 150px;
    border-radius: 50%;
    background: rgba(255,255,255,0.07);
    pointer-events: none;
}
.card-concept {
    font-size: 0.80rem;
    font-weight: 700;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    margin-bottom: 12px;
    opacity: 0.72;
    color: #ffffff;
    position: relative;
    z-index: 1;
}
.card-icon-bg {
    font-size: 2.4rem;
    margin-bottom: 8px;
    display: block;
    position: relative;
    z-index: 1;
}
.card-title {
    font-size: 1.18rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 9px;
    line-height: 1.25;
    position: relative;
    z-index: 1;
}
.card-body {
    font-size: 0.84rem;
    color: rgba(255,255,255,0.74);
    line-height: 1.55;
    margin-bottom: 0;
    position: relative;
    z-index: 1;
}

/* ── Pulso ── */
.pulso-card {
    background: #f8fafc;
    border-left: 4px solid #a3142b;
    border-radius: 0 12px 12px 0;
    padding: 18px 20px;
    height: 100%;
}
.pulso-card.verde   { border-left-color: #0b6b46; }
.pulso-card.rojo    { border-left-color: #a3142b; }
.pulso-card.naranja { border-left-color: #b8860b; }
.pulso-card.gris    { border-left-color: #475569; }
.pulso-card.teal    { border-left-color: #0891b2; }
.pulso-valor {
    font-size: 1.85rem;
    font-weight: 700;
    color: #1e293b;
    line-height: 1.1;
}
.pulso-label { font-size: 0.80rem; font-weight: 600; color: #1e293b; margin-top: 5px; }
.pulso-ctx   { font-size: 0.74rem; color: #64748b; margin-top: 2px; line-height: 1.35; }
.pulso-badge {
    display: inline-block; font-size: 0.66rem; font-weight: 700;
    padding: 1px 8px; border-radius: 10px; margin-top: 6px;
}
.pulso-badge.real    { background: #dcfce7; color: #166534; }
.pulso-badge.demo    { background: #fef3c7; color: #92400e; }

/* ── Hallazgos ── */
.hallazgo-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 10px;
    display: flex;
    align-items: flex-start;
    gap: 12px;
}
.hallazgo-card .h-icon { font-size: 1.4rem; flex-shrink: 0; margin-top: 1px; }
.hallazgo-card .h-dato {
    font-size: 0.92rem; font-weight: 700; color: #1e293b;
    margin-bottom: 3px; line-height: 1.3;
}
.hallazgo-card .h-impl { font-size: 0.82rem; color: #64748b; line-height: 1.45; }
.h-tag {
    display: inline-block; font-size: 0.64rem; font-weight: 700;
    padding: 1px 7px; border-radius: 9px; margin-bottom: 4px;
    letter-spacing: 0.04em; text-transform: uppercase;
}
.h-tag.real     { background: #dcfce7; color: #166534; }
.h-tag.proximo  { background: #e0e7ff; color: #3730a3; }

/* ── Cómo lo construimos ── */
.construimos-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 10px;
}
.construimos-title { font-size: 0.92rem; font-weight: 700; color: #1e293b; margin-bottom: 5px; }
.construimos-desc  { font-size: 0.82rem; color: #64748b; line-height: 1.45; }
.construimos-meta  { font-size: 0.72rem; color: #94a3b8; margin-top: 6px; font-weight: 500; }

/* ── Footer ── */
.footer {
    margin-top: 40px;
    padding-top: 16px;
    border-top: 1px solid #e2e8f0;
    text-align: center;
    font-size: 0.73rem;
    color: #94a3b8;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] { background-color: #5c0c18 !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div:not([data-testid="stButton"]) > div,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #f5e6e9 !important; }
</style>
"""


def main():
    st.markdown(CSS, unsafe_allow_html=True)

    # ── HEADER ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="home-header">
        <div class="header-tag">Data &amp; AI Inclusion Technologies · Plataforma de Inteligencia Electoral · Tlaxcala</div>
        <div class="header-title">PIE Tlaxcala · Anabel Ávalos</div>
        <div class="header-sub">De la intuición a la evidencia. Construye terreno electoral antes de la candidatura, con datos propios.</div>
        <span class="header-corte">📅 Encuesta: {FECHA_CORTE_ENCUESTA}</span>
        <span class="header-corte">🚩 Operativo: {FECHA_CORTE_OPERATIVO}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── CARDS — LOS 4 MÓDULOS ────────────────────────────────────────────────
    st.markdown(
        '<div class="section-title">La plataforma genera tus datos, construye inteligencia territorial y activa la operación rumbo a 2027</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="medium")
    col3, col4 = st.columns(2, gap="medium")

    with col1:
        st.markdown("""
        <div class="journey-card card-1">
            <div class="card-concept">Módulo 1 · Datos y Segmentación</div>
            <span class="card-icon-bg">📊</span>
            <div class="card-title">¿Qué piensa el electorado tlaxcalteca?</div>
            <div class="card-body">Vas más allá de si te conocen o no: sabes qué arquetipos de
            votante hay en Tlaxcala, qué los enoja, qué tema puede mover su voto, y qué se dice
            de ti en redes.</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/1_M1_Datos_Segmentacion.py", label="Ver datos y segmentación →", use_container_width=True)

    with col2:
        st.markdown("""
        <div class="journey-card card-2">
            <div class="card-concept">Módulo 2 · Mapa de Decisiones</div>
            <span class="card-icon-bg">🗺️</span>
            <div class="card-title">¿A dónde voy primero?</div>
            <div class="card-body">Sabes quién vive en cada sección, qué arquetipo domina, cómo
            votó antes y cuánto rinde tu visita — para mandar a tu equipo exactamente donde
            más pesa.</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/2_M2_Mapa_Decisiones.py", label="Ver mapa de decisiones →", use_container_width=True)

    with col3:
        st.markdown("""
        <div class="journey-card card-3">
            <div class="card-concept">Módulo 3 · Inducción y Detección</div>
            <span class="card-icon-bg">🎯</span>
            <div class="card-title">¿Cómo va tu equipo en la calle?</div>
            <div class="card-body">Ves en tiempo real qué sección ya cubrió la brigada, a quién
            encontró —simpatizante, indeciso o adverso— y qué le preocupa, casa por casa. Nadie
            camina a ciegas.</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/3_M3_Induccion_Deteccion.py", label="Ver inducción y detección →", use_container_width=True)

    with col4:
        st.markdown("""
        <div class="journey-card card-4">
            <div class="card-concept">Módulo 4 · Activación y Comunicación</div>
            <span class="card-icon-bg">📱</span>
            <div class="card-title">¿A quién le mando el mensaje correcto?</div>
            <div class="card-body">Cada contacto recibe el mensaje que a él lo mueve, no uno
            genérico — por SMS, correo o WhatsApp, más el contenido que tu equipo de redes
            necesita publicar esta semana.</div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/4_M4_Activacion_Comunicacion.py", label="Ver activación y comunicación →", use_container_width=True)

    st.info(
        "Navega también desde el menú en la **barra lateral izquierda** (ícono ☰ en móvil).",
        icon="💡",
    )

    # ── PULSO OPERATIVO ───────────────────────────────────────────────────────
    st.markdown(
        '<div class="section-title">⚡ Pulso operativo</div>',
        unsafe_allow_html=True,
    )

    p1, p2, p3, p4, p5 = st.columns(5, gap="medium")
    with p1:
        st.markdown(f"""
        <div class="pulso-card verde">
            <div class="pulso-valor">{N_CONTACTOS:,}</div>
            <div class="pulso-label">Personas contactadas</div>
            <div class="pulso-ctx">en campo · piloto en 3 municipios</div>
            <span class="pulso-badge demo">DEMO</span>
        </div>
        """, unsafe_allow_html=True)
    with p2:
        st.markdown(f"""
        <div class="pulso-card teal">
            <div class="pulso-valor">~{ALCANCE_ESTIMADO:,}</div>
            <div class="pulso-label">Alcance estimado</div>
            <div class="pulso-ctx">~3.6 integrantes promedio por hogar</div>
            <span class="pulso-badge demo">DEMO</span>
        </div>
        """, unsafe_allow_html=True)
    with p3:
        st.markdown(f"""
        <div class="pulso-card gris">
            <div class="pulso-valor">{SECCIONES_PILOTO}</div>
            <div class="pulso-label">Secciones con presencia</div>
            <div class="pulso-ctx">Tlaxcala capital, Apizaco, Huamantla</div>
            <span class="pulso-badge demo">DEMO</span>
        </div>
        """, unsafe_allow_html=True)
    with p4:
        st.markdown(f"""
        <div class="pulso-card rojo">
            <div class="pulso-valor">{PCT_PRI_REAL:.1f}%</div>
            <div class="pulso-label">Preferencia PRI gubernatura</div>
            <div class="pulso-ctx">Enkoll / El Universal · 19–22 mar 2026</div>
            <span class="pulso-badge real">REAL</span>
        </div>
        """, unsafe_allow_html=True)
    with p5:
        st.markdown(f"""
        <div class="pulso-card naranja">
            <div class="pulso-valor">{PCT_CELULAR:.1f}%</div>
            <div class="pulso-label">Con celular válido</div>
            <div class="pulso-ctx">listos para WhatsApp o SMS</div>
            <span class="pulso-badge demo">DEMO</span>
        </div>
        """, unsafe_allow_html=True)

    # ── HALLAZGOS ─────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="section-title">🔍 Lo que cambia la estrategia — hallazgos</div>',
        unsafe_allow_html=True,
    )

    hallazgos = [
        ("real", "📉",
         "Morena domina con 47% de intención de voto directa para gobernador; el PRI queda en segundo lugar lejano, con 14%.",
         "La brecha de marca es enorme. El PRI por sí solo no cierra esa distancia — la campaña tiene que ser de la persona, no del partido."),
        ("real", "👤",
         "Ávalos depende más de su marca personal que del voto duro priista: buena parte de quienes la mencionan como opción vienen de fuera del PRI.",
         "Hay que blindar ese voto cruzado y construir un mensaje que no dependa del sello del partido."),
        ("real", "🗳️",
         "En 2021, Ávalos ya llegó a 37% estatal frente a Lorena Cuéllar (Morena) — la base de competitividad existe.",
         "No se arranca de cero: el reto es reactivar y territorializar esa base, no construirla desde el principio."),
        ("real", "🧭",
         "Tlaxcala tiene 15 distritos locales y 60 municipios — el piloto arranca enfocado en 3: capital, Apizaco y Huamantla.",
         "Foco antes que cobertura total. Se prioriza donde el peso poblacional y la disputabilidad son mayores."),
        ("proximo", "🧩",
         "Los arquetipos del elector tlaxcalteca y su distribución por sección se construyen en el Módulo 1.",
         "Encuesta interna propia + Machine Learning sobre reactivos accionables — no solo horse race."),
        ("proximo", "📍",
         "El mapa de secciones más rentables para capturar indecisos se construye en el Módulo 2.",
         "Combina encuesta propia, censo a nivel sección y el historial electoral 2016–2021."),
    ]

    col_h1, col_h2 = st.columns(2, gap="medium")
    for i, (tag, icon, dato, impl) in enumerate(hallazgos):
        col = col_h1 if i % 2 == 0 else col_h2
        tag_label = "Real" if tag == "real" else "Próximo módulo"
        with col:
            st.markdown(f"""
            <div class="hallazgo-card">
                <span class="h-icon">{icon}</span>
                <div>
                    <span class="h-tag {tag}">{tag_label}</span>
                    <div class="h-dato">{dato}</div>
                    <div class="h-impl">{impl}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── CÓMO LO CONSTRUIMOS ───────────────────────────────────────────────────
    with st.expander("🔬 ¿Cómo lo construimos? — la inteligencia detrás del sistema"):
        st.markdown("""
        <div style="font-size:0.85rem; color:#475569; margin-bottom:16px; line-height:1.6;">
            Encuesta real Enkoll/El Universal (1,233 entrevistas, marzo 2026) &nbsp;·&nbsp;
            Encuesta interna propia y ágil &nbsp;·&nbsp; Historial electoral 2016–2021 &nbsp;·&nbsp;
            Censo a nivel sección · 3 municipios piloto<br>
            <span style="color:#94a3b8;">Datos generados y operados por el equipo de la aspirante —
            no de un consultor externo, no del partido.</span>
        </div>
        """, unsafe_allow_html=True)

        cc1, cc2 = st.columns(2, gap="medium")
        with cc1:
            st.markdown("""
            <div class="construimos-card">
                <div class="construimos-title">👥 Arquetipos del Votante Tlaxcalteca</div>
                <div class="construimos-desc">Arquetipos generados a partir de una encuesta interna
                ágil y propia, con reactivos optimizados matemáticamente para alimentar modelos de
                Machine Learning — no solo reconocimiento de nombre e intención de voto.</div>
                <div class="construimos-meta">Módulo 1 · Datos y Segmentación</div>
            </div>
            """, unsafe_allow_html=True)
            st.page_link("pages/1_M1_Datos_Segmentacion.py", label="Ver arquetipos del votante →", use_container_width=True)

        with cc2:
            st.markdown("""
            <div class="construimos-card">
                <div class="construimos-title">📊 Mapa con Historial Electoral por Sección</div>
                <div class="construimos-desc">Proyección de arquetipos sobre las secciones de
                Tlaxcala capital, Apizaco y Huamantla, cruzada con sociodemografía censal e
                historial electoral 2016–2021 para priorizar dónde operar primero.</div>
                <div class="construimos-meta">Módulo 2 · Mapa de Decisiones</div>
            </div>
            """, unsafe_allow_html=True)
            st.page_link("pages/2_M2_Mapa_Decisiones.py", label="Ver mapa de decisiones →", use_container_width=True)

    # ── FOOTER ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="footer">
        Data & AI Inclusion Technologies · Plataforma de Inteligencia Electoral · Anabel Ávalos · PRI Tlaxcala 2027 · Confidencial<br>
        Uso exclusivo del equipo de campaña
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# NAVEGACIÓN — se declara en el nivel del módulo, fuera de main()
# ════════════════════════════════════════════════════════════════════════════════
pg = st.navigation(
    {
        "La Plataforma": [
            st.Page(main, title="🏠  Inicio", default=True),
        ],
        "Tu línea base propia": [
            st.Page("pages/1_M1_Datos_Segmentacion.py", title="📊  Datos y Segmentación"),
        ],
        "Tu mapa de decisiones": [
            st.Page("pages/2_M2_Mapa_Decisiones.py", title="🗺️  Mapa de Decisiones"),
        ],
        "Tu operación en territorio": [
            st.Page("pages/3_M3_Induccion_Deteccion.py", title="🎯  Inducción y Detección"),
        ],
        "Tu operación activada": [
            st.Page("pages/4_M4_Activacion_Comunicacion.py", title="📱  Activación y Comunicación"),
        ],
    },
    position="sidebar",
)

st.set_page_config(
    page_title="PIE · Tlaxcala · Anabel Ávalos",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

pg.run()
