"""
M4 — Activación y Comunicación
PIE Tlaxcala · Anabel Ávalos · PRI 2027

El contacto correcto, con el mensaje que lo mueve, por el canal que usa.
"""

import os
import json
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="M4 · Activación y Comunicación · PIE Tlaxcala",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    import anthropic as _anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import requests as _requests
    from requests.auth import HTTPBasicAuth as _HTTPBasicAuth
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# ════════════════════════════════════════════════════════════════════════════
# CONSTANTES — consistentes con M1, M2, M3
# ════════════════════════════════════════════════════════════════════════════

ARQUETIPOS = {
    "A1": {"nombre": "El Leal Institucional Tricolor",       "color": "#a3142b", "prioridad": "Mantenimiento",               "emoji": "🔴"},
    "A2": {"nombre": "El Decepcionado del Gobierno Estatal", "color": "#dc2626", "prioridad": "Máxima",                      "emoji": "⚡"},
    "A3": {"nombre": "El Anti-Sistema Punitivo",             "color": "#7c2d92", "prioridad": "Alta",                        "emoji": "🛑"},
    "A4": {"nombre": "La Guardiana del Miedo de Género",     "color": "#be185d", "prioridad": "Alta — nicho",                "emoji": "🚨"},
    "A5": {"nombre": "El Rural Desatendido por el Estado",   "color": "#15803d", "prioridad": "Media-alta",                  "emoji": "🌾"},
    "A6": {"nombre": "La Conforme con la Continuidad",       "color": "#0891b2", "prioridad": "Baja",                        "emoji": "🔵"},
    "A7": {"nombre": "El Susceptible a la Ruptura",          "color": "#7c3aed", "prioridad": "Alta — oportunidad y riesgo", "emoji": "🌀"},
    "A8": {"nombre": "El Desconectado de lo Estatal",        "color": "#64748b", "prioridad": "No prioritario",              "emoji": "⬜"},
}

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

NOMBRES_M = ["Carlos", "Miguel", "José", "Luis", "Juan", "Alejandro", "Roberto", "Fernando",
             "Antonio", "Martín", "Eduardo", "Ricardo", "Sergio", "Héctor", "Pablo", "Ramón",
             "Ignacio", "Ernesto", "Aurelio", "Benigno"]
NOMBRES_F = ["María", "Ana", "Laura", "Patricia", "Rosa", "Carmen", "Verónica", "Diana",
             "Claudia", "Sandra", "Gabriela", "Leticia", "Martha", "Alicia", "Elena", "Susana",
             "Norma", "Esperanza", "Concepción", "Beatriz"]
APELLIDOS  = ["García", "Hernández", "Martínez", "López", "González", "Pérez", "Sánchez",
              "Ramírez", "Torres", "Flores", "Rivera", "Cruz", "Morales", "Reyes", "Jiménez",
              "Ortega", "Vázquez", "Mendoza", "Castillo", "Ramos", "Juárez", "Rojas", "Méndez",
              "Tláloc", "Xochitl", "Cuauhtémoc", "Nava", "Bello", "Herrera", "Muñoz"]

CANALES = ["SMS", "WhatsApp", "Correo"]
CANAL_ICON  = {"SMS": "💬", "WhatsApp": "📲", "Correo": "📧"}
URGENCIA_COLOR = {"Alta": "#dc2626", "Media": "#d97706", "Baja": "#64748b"}

# ────────────────────────────────────────────────────────────────────────────
# MENSAJES DE EJEMPLO PRE-GENERADOS (9 mínimo · 3 segmentos × 3 canales)
# Escritos con las reglas del system prompt — nunca simulan output de IA
# ────────────────────────────────────────────────────────────────────────────
MENSAJES_EJEMPLO = {
    ("Indecisos persuadibles", "SMS"): (
        "Tlaxcala merece un gobierno que responda, no que prometa. "
        "Yo escuche lo que te preocupa en tu comunidad. "
        "Dame la oportunidad. Soy Anabel Avalos."
    ),
    ("Indecisos persuadibles", "WhatsApp"): (
        "Hola 👋 Soy Anabel Ávalos. Sé que la salud y los servicios en Tlaxcala han fallado — "
        "lo escuché directamente en tu comunidad. "
        "Dame la oportunidad de cambiar eso contigo. ¿Hablamos?"
    ),
    ("Indecisos persuadibles", "Correo"): {
        "asunto": "Lo que encontré en tu comunidad me preocupa — y voy a hacer algo al respecto",
        "cuerpo": (
            "Cuando visité tu comunidad, escuché algo que no puedo ignorar: la salud "
            "y los servicios básicos están fallando a familias enteras en Tlaxcala. "
            "No son promesas lo que necesitamos — son resultados medibles y verificables.\n\n"
            "Voy a implementar un sistema de atención médica que llegue a cada rincón del estado, "
            "con cuentas claras y supervisión ciudadana. Porque gobernar bien no se improvisa "
            "— se construye con responsabilidad y escuchando a quienes más lo necesitan.\n\n"
            "Te pido una oportunidad. Tu voto puede cambiar lo que le duele a tu familia.\n\n"
            "Con respeto,\nAnabel Ávalos"
        ),
    },
    ("Simpatizantes a movilizar", "SMS"): (
        "Tu apoyo es el motor del cambio en Tlaxcala. "
        "El dia de la eleccion moviliza a tu familia y vecinos. "
        "Juntos vamos a ganar. Soy Anabel Avalos."
    ),
    ("Simpatizantes a movilizar", "WhatsApp"): (
        "¡Hola! 🔥 Gracias por estar con nosotros. "
        "El día de la elección, tu voto y el de tu familia son los que nos llevan al triunfo. "
        "¿Puedo contar contigo para movilizar a dos o tres vecinos más?"
    ),
    ("Simpatizantes a movilizar", "Correo"): {
        "asunto": "Necesito tu ayuda el día más importante",
        "cuerpo": (
            "Gracias por acompañarme en este camino. Tu apoyo no solo me da fuerza "
            "— me recuerda por qué vale la pena pelear por Tlaxcala.\n\n"
            "El día de la elección, lo que necesito de ti es sencillo: vota tú, vota tu familia, "
            "convence a dos vecinos más. Eso multiplica nuestro impacto de una manera que ninguna "
            "campaña publicitaria puede igualar.\n\n"
            "Cuento contigo para hacer historia en Tlaxcala.\nAnabel Ávalos"
        ),
    },
    ("Adversos recuperables", "SMS"): (
        "Entiendo tu enojo. Tlaxcala no ha tenido el gobierno que merece. "
        "Vengo a cambiar eso con hechos, no discursos. "
        "Soy Anabel Avalos."
    ),
    ("Adversos recuperables", "WhatsApp"): (
        "Sé que estás harto 🛑 y tienes razón en estarlo. "
        "Yo también exijo orden y resultados reales en Tlaxcala. "
        "Por eso quiero escucharte — lo que pasa en tu comunidad merece atención real, no promesas vacías."
    ),
    ("Adversos recuperables", "Correo"): {
        "asunto": "Tu enojo es válido — y por eso te escribo",
        "cuerpo": (
            "No vengo a pedirte que olvides las decepciones del pasado. "
            "Vengo a reconocer que tu enojo es completamente válido: "
            "Tlaxcala ha merecido más y no lo ha tenido.\n\n"
            "Lo que yo propongo no son palabras — son compromisos verificables: "
            "orden público medible, resultados publicados mes a mes, "
            "rendición de cuentas sin excusas. Si no cumplo, tendrás toda la razón de exigirme.\n\n"
            "Dame la oportunidad de demostrarte que esto puede ser diferente.\n\nAnabel Ávalos"
        ),
    },
}

# ────────────────────────────────────────────────────────────────────────────
# POSTS DE EJEMPLO PRE-GENERADOS (uno por demanda dominante)
# ────────────────────────────────────────────────────────────────────────────
POSTS_EJEMPLO = {
    "Mejora de servicios de salud y atención estatal": {
        "copy": (
            "En Tlaxcala, una cita médica no debería ser un lujo.\n\n"
            "Cuando recorro el estado escucho lo mismo una y otra vez: horas de espera, "
            "falta de medicamentos, centros de salud que no funcionan.\n\n"
            "Como gobernadora, voy a modernizar la red de salud estatal — con citas digitales, "
            "abasto garantizado de medicamentos y supervisión ciudadana. No promesas. Resultados verificables.\n\n"
            "¿Qué problema de salud ha afectado más a tu familia en Tlaxcala?"
        ),
        "visual": "Foto de Anabel en centro de salud comunitario o con personal médico tlaxcalteca",
        "horario": "Martes o miércoles · 12:00–14:00 hrs",
        "hashtags": "#TlaxcalaSaludable #AnabelÁvalos #GobiernoQueResponde",
    },
    "Seguridad pública y combate a la impunidad": {
        "copy": (
            "No se puede vivir con miedo en tu propia colonia.\n\n"
            "En Tlaxcala, la impunidad dejó de ser la excepción — se convirtió en la regla. "
            "Y eso tiene que cambiar.\n\n"
            "Voy a implementar mando unificado de seguridad, cámaras en puntos calientes "
            "y evaluaciones públicas mensuales a las corporaciones policiales. "
            "La seguridad no se improvisa — se construye con disciplina y rendición de cuentas.\n\n"
            "¿Tu colonia o municipio ha sentido el abandono en materia de seguridad?"
        ),
        "visual": "Infografía sobre incidencia delictiva en Tlaxcala · fondo oscuro con datos clave",
        "horario": "Jueves · 18:00–20:00 hrs",
        "hashtags": "#TlaxcalaSegura #AnabelÁvalos #ImpunidadCero",
    },
    "Protección a mujeres y espacios seguros": {
        "copy": (
            "Ninguna mujer en Tlaxcala debería tener miedo de salir sola. "
            "Eso no es normal — y no voy a aceptarlo como normal.\n\n"
            "Voy a crear una red de espacios seguros, fortalecer el sistema de alertas "
            "y garantizar que las denuncias tengan seguimiento real. "
            "Las mujeres de Tlaxcala merecen un estado que las proteja de verdad.\n\n"
            "Etiqueta a esa mujer en tu vida que merece un Tlaxcala más seguro. 💜"
        ),
        "visual": "Imagen con frase motivacional en colores morado y blanco · sin logos partidistas",
        "horario": "Viernes · 19:00–21:00 hrs · o fechas clave (8M, 25N)",
        "hashtags": "#MujeresTlaxcala #AnabelÁvalos #TlaxcalaSeguraParaTodas",
    },
    "Infraestructura rural y apoyos al campo": {
        "copy": (
            "El campo tlaxcalteca alimenta al estado — y el estado lo ha ignorado.\n\n"
            "Caminos destruidos, apoyos que no llegan, cosechas que no tienen mercado.\n\n"
            "Voy a poner al campo en el centro de mi gobierno: infraestructura rural, "
            "acceso a mercados y apoyo técnico real para los productores tlaxcaltecas.\n\n"
            "¿Cuántos años llevan esperando que arreglen el camino a su comunidad?"
        ),
        "visual": "Foto de paisaje rural tlaxcalteca o de Anabel con productores en trabajo de campo",
        "horario": "Sábado · 8:00–10:00 hrs · audiencia rural madrugadora",
        "hashtags": "#CampoTlaxcalteca #AnabelÁvalos #AgriculturaDignidad",
    },
    "Orden público y resultados inmediatos": {
        "copy": (
            "Tlaxcala no puede esperar otros seis años para ver resultados.\n\n"
            "El desorden y la ineficiencia gubernamental tienen un costo — y lo pagamos todos.\n\n"
            "Voy a gobernar con indicadores claros, publicados cada mes. "
            "Si no funciona, se corrige. Si no cumple, se cambia. "
            "Eso es lo que significa gobernar con responsabilidad.\n\n"
            "¿Qué es lo primero que cambiarías del gobierno estatal?"
        ),
        "visual": "Infografía de compromisos con fechas y metas específicas · diseño limpio",
        "horario": "Lunes · 7:00–9:00 hrs · inicio de semana laboral",
        "hashtags": "#TlaxcalaConResultados #AnabelÁvalos #GobiernoEficiente",
    },
    "Servicios municipales básicos (bacheo, agua, luz)": {
        "copy": (
            "¿Cuántas veces has reportado el mismo bache y no pasa nada? "
            "¿Cuántos días sin agua en tu colonia?\n\n"
            "Los servicios básicos no son un favor del gobierno — son un derecho.\n\n"
            "Voy a crear un sistema de atención ciudadana digital para que cada reporte "
            "tenga seguimiento y cada problema tenga solución con fecha.\n\n"
            "Etiqueta tu colonia y dime cuál es el problema que llevas más tiempo esperando."
        ),
        "visual": "Collage de reportes ciudadanos de problemas de infraestructura urbana",
        "horario": "Miércoles · 12:00–14:00 hrs",
        "hashtags": "#ServiciosBásicos #AnabelÁvalos #TlaxcalaQueResponde",
    },
    "Movilización y red de apoyo de base": {
        "copy": (
            "Tlaxcala se construye desde abajo — desde cada colonia, cada comunidad, cada familia.\n\n"
            "Si quieres un cambio real, el primer paso es estar presente el día de la elección. "
            "Tu voto y el de las personas que te rodean son la base de todo lo que viene.\n\n"
            "¿Ya le dijiste a tu familia que cuentes con ellos?"
        ),
        "visual": "Foto de Anabel con grupos de ciudadanos en evento comunitario · colores cálidos",
        "horario": "Domingo · 10:00–12:00 hrs · momento familiar",
        "hashtags": "#TlaxcalaUnida #AnabelÁvalos #VotaConRazón",
    },
    "Continuidad de programas sociales": {
        "copy": (
            "Los apoyos que llegan a tu familia no deben depender de a quién conozcas "
            "ni del partido que gobierne. Deben estar garantizados por ley.\n\n"
            "Como gobernadora, voy a institucionalizar los programas sociales para que ningún "
            "cambio político los quite. Tus derechos no son favores — son compromisos de gobierno.\n\n"
            "¿Cuál es el apoyo social que más valoras en tu familia?"
        ),
        "visual": "Infografía de programas sociales garantizados · tonos verdes y blancos",
        "horario": "Martes · 14:00–16:00 hrs",
        "hashtags": "#DerechosSociales #AnabelÁvalos #TlaxcalaConGarantías",
    },
}


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
    --accent: #e8a33d;
    background: #14181f;
    padding: 28px 32px 24px 32px;
    border-radius: 8px; margin-bottom: 22px;
    position: relative; overflow: hidden;
    border-bottom: 2px solid var(--accent);
}
.header-modulo::after {
    content: ''; position: absolute; top: -45px; right: -45px;
    width: 180px; height: 180px; border-radius: 50%;
    background: rgba(255,255,255,0.04);
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
.tag.live { background: #dcfce7; color: #166534; border: 1px solid #4ade80; }

.kpi-card {
    background: #f8fafc; border-left: 4px solid #b8860b;
    border-radius: 0 10px 10px 0; padding: 14px 16px; height: 100%;
}
.kpi-val   { font-size: 1.75rem; font-weight: 800; color: #1e293b; line-height: 1.1; }
.kpi-label { font-size: 0.78rem; font-weight: 600; color: #1e293b; margin-top: 4px; }
.kpi-ctx   { font-size: 0.72rem; color: #64748b; margin-top: 2px; line-height: 1.3; }

.seg-card {
    background: #fff; border: 1px solid #e2e8f0; border-radius: 14px;
    padding: 18px 20px; margin-bottom: 12px; cursor: pointer;
    transition: box-shadow 0.15s;
}
.seg-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
.seg-card.selected { border-color: #b8860b; box-shadow: 0 0 0 2px #fde68a; }

.preview-sms-wrap {
    background: #f2f2f7; border-radius: 16px; padding: 20px 24px;
}
.preview-wa-wrap {
    background: #e5ddd5; border-radius: 16px; padding: 20px 24px;
    background-image: url("https://web.whatsapp.com/img/bg-chat-tile-dark_a4be512e7195b6b733d9110b408f075d.png");
}
.preview-email-wrap {
    border: 1px solid #e2e8f0; border-radius: 14px; overflow: hidden;
}

.dest-row {
    display: flex; align-items: center; gap: 10px; padding: 8px 14px;
    border-radius: 8px; background: #f8fafc; border: 1px solid #e2e8f0;
    margin-bottom: 6px; font-family: 'DM Sans', sans-serif;
}

.post-card {
    background: #fff; border: 1px solid #e2e8f0; border-radius: 14px;
    padding: 20px 22px; margin-top: 12px;
}
.post-header {
    display: flex; align-items: center; gap: 10px; margin-bottom: 14px;
}
.post-avatar {
    width: 42px; height: 42px; border-radius: 50%; background: #a3142b;
    display: flex; align-items: center; justify-content: center;
    color: #fff; font-weight: 700; font-size: 1.1rem; flex-shrink: 0;
}
.post-name { font-size: 0.88rem; font-weight: 700; color: #1e293b; }
.post-handle { font-size: 0.76rem; color: #64748b; }
.post-body { font-size: 0.88rem; color: #1e293b; line-height: 1.65; white-space: pre-line; }
.post-hashtags { font-size: 0.82rem; color: #3b82f6; margin-top: 10px; }
.post-meta { font-size: 0.74rem; color: #94a3b8; margin-top: 12px; border-top: 1px solid #f1f5f9; padding-top: 10px; }

.banner-ok { background: #f0fdf4; border: 1px solid #4ade80; border-radius: 12px;
             padding: 14px 18px; font-family: 'DM Sans', sans-serif; margin-top: 12px; }
.banner-err { background: #fef2f2; border: 1px solid #f87171; border-radius: 12px;
              padding: 14px 18px; font-family: 'DM Sans', sans-serif; margin-top: 12px; }
</style>
"""


# ════════════════════════════════════════════════════════════════════════════
# GENERACIÓN DE DIRECTORIO — rng(99) · independiente de M3
# ════════════════════════════════════════════════════════════════════════════

@st.cache_data
def generar_directorio() -> pd.DataFrame:
    rng = np.random.default_rng(99)
    n   = 40

    sexo = rng.choice(["M", "F"], size=n)
    nm_lista = [
        NOMBRES_M[rng.integers(0, len(NOMBRES_M))] if s == "M"
        else NOMBRES_F[rng.integers(0, len(NOMBRES_F))]
        for s in sexo
    ]
    ap1 = [APELLIDOS[i] for i in rng.integers(0, len(APELLIDOS), size=n)]
    ap2 = [APELLIDOS[i] for i in rng.integers(0, len(APELLIDOS), size=n)]
    nombres = [f"{nm} {a1} {a2}" for nm, a1, a2 in zip(nm_lista, ap1, ap2)]

    prefijos = ["246", "241", "246", "222", "241"]
    celulares = [
        f"{prefijos[rng.integers(0, len(prefijos))]}{rng.integers(1000000, 9999999)}"
        for _ in range(n)
    ]
    correos = [
        f"{nm.lower()[:8].replace(' ', '')}{rng.integers(10, 99)}@gmail.com"
        for nm in nm_lista
    ]

    arq_pool    = list(ARQUETIPOS.keys())
    arq_weights = np.array([10, 20, 12, 10, 10, 12, 15, 11], dtype=float)
    arq_weights /= arq_weights.sum()
    arquetipos  = rng.choice(arq_pool, size=n, p=arq_weights)

    posiciones = [
        rng.choice(["Simpatizante", "Indeciso", "Adverso"], p=ARQ_POS_PROB[a])
        for a in arquetipos
    ]
    demandas = [ARQ_DEMANDA[a] for a in arquetipos]
    enojo    = rng.integers(1, 6, size=n)
    acepta   = rng.choice(["Sí", "No"], size=n, p=[0.75, 0.25])
    # Secciones representativas Tlaxcala capital (rango INE ~3001-3043)
    secciones = rng.integers(3001, 3044, size=n)

    return pd.DataFrame({
        "nombre":          nombres,
        "celular":         celulares,
        "correo":          correos,
        "arquetipo":       arquetipos.tolist(),
        "posicion":        posiciones,
        "demanda":         demandas,
        "enojo":           enojo.tolist(),
        "acepta_contacto": acepta.tolist(),
        "seccion":         secciones.tolist(),
    })


# ════════════════════════════════════════════════════════════════════════════
# CÁLCULO DE MICROSEGMENTOS — programático, no hardcodeado
# ════════════════════════════════════════════════════════════════════════════

def calcular_segmentos(df: pd.DataFrame) -> list[dict]:
    arq_prio = ["A2", "A3", "A4", "A5", "A7"]

    def _seg(mask, id_, nombre, desc, canal, urgencia):
        idx = df[mask].index.tolist()
        if not idx:
            return None
        sub = df.loc[idx]
        return {
            "id":           id_,
            "nombre":       nombre,
            "descripcion":  desc,
            "n":            len(idx),
            "indices":      idx,
            "arquetipo_base": sub["arquetipo"].mode()[0],
            "demanda_dom":  sub["demanda"].mode()[0],
            "canal":        canal,
            "urgencia":     urgencia,
        }

    # 1 · Indecisos persuadibles
    m1 = (df["posicion"] == "Indeciso") & (df["enojo"] >= 3) & (df["arquetipo"].isin(arq_prio))
    # 2 · Simpatizantes a movilizar
    m2 = (df["posicion"] == "Simpatizante") & (df["acepta_contacto"] == "Sí")
    # 3 · Adversos recuperables (A7 primero; ampliar si hay pocos)
    m3a = (df["arquetipo"] == "A7") & (df["posicion"] == "Adverso") & (df["enojo"] >= 4)
    m3  = m3a if m3a.sum() >= 2 else (
        (df["posicion"] == "Adverso") & (df["enojo"] >= 4) & (df["arquetipo"].isin(["A7", "A3", "A2"]))
    )
    # 4 · Base dura
    m4 = (df["arquetipo"] == "A1") & (df["posicion"] == "Simpatizante")
    # 5 · Indecisos contactables (complemento de m1, acepta contacto)
    ya_en_m1 = set(df[m1].index.tolist())
    m5 = (df["posicion"] == "Indeciso") & (df["acepta_contacto"] == "Sí") & (~df.index.isin(ya_en_m1))

    candidatos = [
        (m1, "indecisos_persuadibles",  "Indecisos persuadibles",
         "Ciudadanos sin decisión firme con enojo alto — objetivo principal de persuasión.",
         "WhatsApp", "Alta"),
        (m2, "simpatizantes_movilizar", "Simpatizantes a movilizar",
         "Base propia que aceptó contacto — listos para activación el día de la elección.",
         "SMS", "Alta"),
        (m3, "adversos_recuperables",   "Adversos recuperables",
         "Ciudadanos adversos con alto enojo — volátiles que pueden reencuadrarse con el mensaje correcto.",
         "WhatsApp", "Media"),
        (m4, "base_dura",               "Base dura a activar",
         "Voto duro que no necesita convencimiento — necesita movilización y red de arrastre.",
         "SMS", "Media"),
        (m5, "indecisos_contactables",  "Indecisos contactables",
         "Indecisos que aceptaron ser contactados — puerta abierta para la persuasión.",
         "Correo", "Media"),
    ]

    return [s for m, *args in candidatos if (s := _seg(m, *args)) is not None]


# ════════════════════════════════════════════════════════════════════════════
# CLAUDE API — generación de mensajes
# ════════════════════════════════════════════════════════════════════════════

def generar_mensaje_claude(seg: dict, canal: str) -> str | dict:
    if not HAS_ANTHROPIC:
        return "⚠️ Instala la librería 'anthropic' para usar esta función."

    instrucciones = {
        "SMS":      "SMS de MÁXIMO 160 caracteres. Sin emojis. Sin acentos. Lenguaje llano y directo. Solo el texto.",
        "WhatsApp": "Máximo 3 oraciones. Puedes incluir 1 emoji relevante. Tono cercano. Solo el texto.",
        "Correo":   (
            "Responde ÚNICAMENTE con un objeto JSON válido con las claves 'asunto' y 'cuerpo'. "
            "Asunto: una línea. Cuerpo: 2-3 párrafos cortos, cierre con nombre de Anabel. "
            "Sin markdown. Sin explicaciones fuera del JSON."
        ),
    }

    system = (
        "Eres el equipo de comunicación de Anabel Ávalos, candidata a gobernadora de Tlaxcala 2027.\n\n"
        "REGLAS ESTRICTAS:\n"
        "- Voz de Anabel Ávalos, primera persona, tono cercano y directo\n"
        "- Ancla el mensaje en la demanda dominante del segmento\n"
        "- NUNCA menciones al PRI como institución — la marca es la persona\n"
        "- Nunca prometas resultados que no se puedan verificar\n"
        "- Sin lenguaje partidista ni institucional\n"
        "- El mensaje SIEMPRE debe comenzar con 'Hola {nombre},' — usa exactamente esa cadena "
        "como marcador de personalización; se reemplazará con el primer nombre real de cada destinatario\n"
        "- Responde ÚNICAMENTE con el texto del mensaje listo para enviar, "
        "sin explicaciones, sin comillas, sin preamble"
    )

    prompt = (
        f"Segmento: {seg['nombre']}\n"
        f"Descripción: {seg['descripcion']}\n"
        f"Demanda dominante del segmento: {seg['demanda_dom']}\n"
        f"Canal: {canal}\n"
        f"Instrucciones de formato: {instrucciones[canal]}\n\n"
        "Genera el mensaje ahora:"
    )

    try:
        client   = _anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        texto = response.content[0].text.strip()

        if canal == "Correo":
            clean = texto.replace("```json", "").replace("```", "").strip()
            try:
                return json.loads(clean)
            except Exception:
                return {"asunto": "Mensaje para ti", "cuerpo": texto}

        return texto

    except Exception as e:
        return f"Error al conectar con Claude API: {e}"


# ════════════════════════════════════════════════════════════════════════════
# CLAUDE API — contenido para redes sociales (con web search)
# ════════════════════════════════════════════════════════════════════════════

def generar_post_claude(tema: str, formato: str) -> dict:
    if not HAS_ANTHROPIC:
        return {"copy": "⚠️ Instala 'anthropic' para usar esta función.",
                "visual": "", "horario": "", "hashtags": ""}

    system = (
        "Eres el equipo de comunicación digital de Anabel Ávalos, candidata a gobernadora de Tlaxcala 2027.\n\n"
        "REGLAS:\n"
        "- Voz de Anabel, primera persona, tono auténtico y cercano\n"
        "- Anclado en la demanda social real del electorado tlaxcalteca\n"
        "- Sin mención al PRI como institución\n"
        "- Sin promesas no verificables\n"
        "- Genera conversación e identificación\n"
        "- Responde ÚNICAMENTE con un JSON válido con las claves: copy, visual, horario, hashtags\n"
        "- Sin explicaciones fuera del JSON, sin markdown"
    )

    prompt = (
        f"Genera un post de {formato} para Anabel Ávalos sobre: \"{tema}\".\n"
        "Usa contexto actual de Tlaxcala si es relevante para el post."
    )

    try:
        client = _anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

        tools = [{"type": "web_search_20250305", "name": "web_search"}]
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=700,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            tools=tools,
        )

        texto = ""
        for block in response.content:
            if hasattr(block, "type") and block.type == "text":
                texto = block.text.strip()

        clean = texto.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(clean)
        except Exception:
            return {"copy": texto, "visual": "Foto de Anabel con ciudadanos",
                    "horario": "Viernes · 18:00–20:00 hrs", "hashtags": "#AnabelÁvalos #Tlaxcala2027"}

    except Exception as e:
        return {"copy": f"Error: {e}", "visual": "", "horario": "", "hashtags": ""}


# ════════════════════════════════════════════════════════════════════════════
# PERSONALIZACIÓN Y ENVÍO SMS
# ════════════════════════════════════════════════════════════════════════════

def personalizar_mensaje(template: str, nombre: str) -> str:
    """Reemplaza {nombre} con el primer nombre real del destinatario."""
    primer_nombre = nombre.split()[0].strip() if nombre.strip() else "ciudadano"
    return template.replace("{nombre}", primer_nombre)


def enviar_sms_labsmobile(template: str, destinatarios: list) -> list:
    """Envía un SMS personalizado por destinatario. Retorna lista de resultados."""
    if not HAS_REQUESTS:
        return [{"nombre": d["nombre"], "numero_masked": d.get("numero_masked", "***"),
                 "ok": False, "msg": "Instala 'requests'."}
                for d in destinatarios]
    try:
        url    = "https://api.labsmobile.com/json/send"
        user   = st.secrets.get("LABSMOBILE_USER", "")
        pwd    = st.secrets.get("LABSMOBILE_PASSWORD", "")
        sender = st.secrets.get("LABSMOBILE_SENDER", "PIEDemo")
    except Exception:
        return [{"nombre": d["nombre"], "numero_masked": d.get("numero_masked", "***"),
                 "ok": False, "msg": "Secrets no configurados."}
                for d in destinatarios]

    resultados = []
    for d in destinatarios:
        mensaje_personal = personalizar_mensaje(template, d["nombre"])
        try:
            resp = _requests.post(
                url,
                json={"message": mensaje_personal, "recipient": [{"msisdn": d["numero"]}], "sender": sender},
                auth=_HTTPBasicAuth(user, pwd),
                headers={"Content-Type": "application/json"},
                timeout=15,
            )
            ok   = resp.status_code == 200
            body = resp.json() if resp.content else {}
            resultados.append({
                "nombre":        d["nombre"],
                "numero_masked": d.get("numero_masked", "***"),
                "mensaje":       mensaje_personal,
                "ok":            ok,
                "status":        resp.status_code,
                "body":          body,
            })
        except Exception as e:
            resultados.append({
                "nombre":        d["nombre"],
                "numero_masked": d.get("numero_masked", "***"),
                "mensaje":       mensaje_personal,
                "ok":            False,
                "msg":           str(e),
            })
    return resultados


# ════════════════════════════════════════════════════════════════════════════
# HELPERS DE RENDER
# ════════════════════════════════════════════════════════════════════════════

def _mask_number(num: str) -> str:
    """521246123456 → 521246***456"""
    if len(num) >= 10:
        return f"{num[:6]}***{num[-3:]}"
    return f"***{num[-3:]}"


def render_preview_sms(mensaje: str):
    chars = len(mensaje)
    color_chars = "#166534" if chars <= 160 else "#dc2626"
    label_chars = f"{chars}/160 ✅" if chars <= 160 else f"{chars}/160 ⚠️ Supera el límite"
    st.html(f"""
    <div style="font-family:'DM Sans',sans-serif; padding:10px 0;">
      <div style="font-size:0.72rem; font-weight:700; color:#64748b;
                  text-transform:uppercase; letter-spacing:0.05em; margin-bottom:10px;">
        Vista previa · SMS
      </div>
      <div style="background:#f2f2f7; border-radius:16px; padding:20px 24px;">
        <div style="display:flex; justify-content:flex-end; padding-right:4px;">
          <div style="max-width:76%;">
            <div style="background:#e5e5ea; border-radius:18px 18px 4px 18px;
                        padding:12px 16px; font-size:0.88rem; color:#1c1c1e; line-height:1.55;">
              {mensaje}
            </div>
            <div style="font-size:0.70rem; color:#8e8e93; margin-top:4px; text-align:right;">
              Enviado · Ahora
            </div>
          </div>
        </div>
        <div style="margin-top:10px; font-size:0.74rem; font-weight:600;
                    color:{color_chars}; text-align:right;">
          {label_chars}
        </div>
      </div>
    </div>
    """)


def render_preview_whatsapp(mensaje: str):
    st.html(f"""
    <div style="font-family:'DM Sans',sans-serif; padding:10px 0;">
      <div style="font-size:0.72rem; font-weight:700; color:#64748b;
                  text-transform:uppercase; letter-spacing:0.05em; margin-bottom:10px;">
        Vista previa · WhatsApp
      </div>
      <div style="background:#ddd7ce; border-radius:16px; padding:20px 24px;">
        <div style="display:flex; justify-content:flex-end; padding-right:4px;">
          <div style="max-width:80%;">
            <div style="background:#dcf8c6; border-radius:18px 18px 4px 18px;
                        padding:12px 16px; font-size:0.88rem; color:#1c1c1e; line-height:1.55;
                        box-shadow:0 1px 3px rgba(0,0,0,0.12);">
              {mensaje}
              <div style="font-size:0.68rem; color:#8e8e93; text-align:right; margin-top:6px;">
                ✓✓
              </div>
            </div>
            <div style="font-size:0.70rem; color:#555; margin-top:3px; text-align:right;">
              Ahora
            </div>
          </div>
        </div>
      </div>
    </div>
    """)


def render_preview_correo(asunto: str, cuerpo: str):
    cuerpo_html = (
        cuerpo.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
              .replace("\n\n", "</p><p style='margin:0 0 12px 0;'>")
              .replace("\n", "<br>")
    )
    st.html(f"""
    <div style="font-family:'DM Sans',sans-serif; padding:10px 0;">
      <div style="font-size:0.72rem; font-weight:700; color:#64748b;
                  text-transform:uppercase; letter-spacing:0.05em; margin-bottom:10px;">
        Vista previa · Correo electrónico
      </div>
      <div style="border:1px solid #e2e8f0; border-radius:14px; overflow:hidden; max-width:540px;">
        <div style="background:#f8fafc; padding:14px 18px; border-bottom:1px solid #e2e8f0;">
          <div style="font-size:0.74rem; color:#64748b; margin-bottom:6px;">
            <b>De:</b> Anabel Ávalos &lt;anabel@tlaxcala2027.mx&gt;<br>
            <b>Asunto:</b>
          </div>
          <div style="font-size:0.92rem; font-weight:700; color:#1e293b;">{asunto}</div>
        </div>
        <div style="padding:18px 22px; background:#fff;">
          <p style="font-size:0.88rem; color:#334155; line-height:1.70; margin:0 0 12px 0;">
            {cuerpo_html}
          </p>
        </div>
      </div>
    </div>
    """)


def render_post_card(post: dict, formato: str):
    copy_html = (
        post.get("copy", "")
            .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace("\n", "<br>")
    )
    st.html(f"""
    <div style="font-family:'DM Sans',sans-serif; background:#fff;
                border:1px solid #e2e8f0; border-radius:14px; padding:20px 22px; margin-top:10px;">
      <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px;">
        <div style="width:42px; height:42px; border-radius:50%; background:#a3142b;
                    display:flex; align-items:center; justify-content:center;
                    color:#fff; font-weight:700; font-size:1.05rem; flex-shrink:0;">AA</div>
        <div>
          <div style="font-size:0.88rem; font-weight:700; color:#1e293b;">Anabel Ávalos</div>
          <div style="font-size:0.76rem; color:#64748b;">@AnabelAvalosT · {formato}</div>
        </div>
      </div>
      <div style="font-size:0.88rem; color:#1e293b; line-height:1.65;">{copy_html}</div>
      <div style="font-size:0.82rem; color:#3b82f6; margin-top:10px;">
        {post.get('hashtags', '')}
      </div>
      <div style="font-size:0.74rem; color:#94a3b8; margin-top:12px;
                  border-top:1px solid #f1f5f9; padding-top:10px; display:flex; gap:20px;">
        <span>🕐 {post.get('horario', '—')}</span>
        <span>🖼️ {post.get('visual', '—')}</span>
      </div>
    </div>
    """)


# ════════════════════════════════════════════════════════════════════════════
# DIALOG — confirmación de envío SMS
# ════════════════════════════════════════════════════════════════════════════

@st.dialog("Confirmar envío de SMS personalizado", width="large")
def modal_envio_sms(template: str, destinatarios: list):
    st.markdown(
        '<span class="tag live">REAL · EN VIVO</span> '
        'Cada destinatario recibe su versión personalizada del mensaje.',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # Tabla de mensajes personalizados por destinatario
    st.markdown(f"**{len(destinatarios)} mensajes personalizados que se enviarán:**")
    for d in destinatarios:
        msg_personal = personalizar_mensaje(template, d["nombre"])
        chars = len(msg_personal)
        chars_color = "#166534" if chars <= 160 else "#dc2626"
        st.html(f"""
        <div style="font-family:'DM Sans',sans-serif; background:#f8fafc;
                    border:1px solid #e2e8f0; border-radius:10px;
                    padding:12px 16px; margin-bottom:8px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <span style="font-size:0.84rem; font-weight:700; color:#1e293b;">{d['nombre']}</span>
            <span style="font-size:0.72rem; font-family:monospace; color:#64748b;">{d['numero_masked']}</span>
          </div>
          <div style="background:#e5e5ea; border-radius:12px 12px 3px 12px;
                      padding:10px 14px; font-size:0.84rem; color:#1c1c1e; line-height:1.5;">
            {msg_personal}
          </div>
          <div style="font-size:0.70rem; color:{chars_color}; text-align:right; margin-top:4px;">
            {chars}/160 chars
          </div>
        </div>
        """)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Confirmar y enviar", type="primary", use_container_width=True):
            resultados = enviar_sms_labsmobile(template, destinatarios)
            st.session_state["m4_sms_enviado"]       = True
            st.session_state["m4_sms_resultado"]     = resultados
            st.session_state["m4_sms_destinatarios"] = destinatarios
            st.session_state["m4_sms_template"]      = template
            st.rerun()
    with col2:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

def main():
    st.markdown(CSS, unsafe_allow_html=True)

    st.html("""
    <div class="header-modulo">
      <div class="hm-dots"><span></span><span></span><span></span></div>
      <div class="hm-eyebrow">Módulo 04 · En operación</div>
      <h1>📱 Activación y Comunicación</h1>
      <p>El contacto correcto · con el mensaje que lo mueve · por el canal que usa</p>
    </div>
    """)

    df = generar_directorio()
    segmentos = calcular_segmentos(df)

    # ── KPIs generales ────────────────────────────────────────────────────
    total_act   = int((df["acepta_contacto"] == "Sí").sum())
    total_ind   = int((df["posicion"] == "Indeciso").sum())
    seg_mayor   = max(segmentos, key=lambda s: s["n"]) if segmentos else None
    seg_urgente = next((s for s in segmentos if s["urgencia"] == "Alta"), segmentos[0] if segmentos else None)

    k1, k2, k3, k4 = st.columns(4, gap="medium")
    kpis = [
        (k1, f"{total_act}",
         "Contactos activables",      "aceptaron ser contactados",        "#b8860b"),
        (k2, f"{len(segmentos)}",
         "Microsegmentos detectados", "calculados desde el directorio M3", "#334155"),
        (k3, seg_mayor["nombre"].split()[0] + "…" if seg_mayor else "—",
         "Segmento más grande",       f"{seg_mayor['n']} contactos" if seg_mayor else "", "#0b6b46"),
        (k4, seg_urgente["nombre"].split()[0] + "…" if seg_urgente else "—",
         "Segmento de mayor urgencia", "prioridad Alta · activar primero",  "#a3142b"),
    ]
    for col, val, label, ctx, color in kpis:
        with col:
            st.html(f"""
            <div class="kpi-card" style="border-left-color:{color};">
              <div class="kpi-val" style="color:{color}; font-size:1.55rem;">{val}</div>
              <div class="kpi-label">{label}</div>
              <div class="kpi-ctx">{ctx}</div>
            </div>
            """)

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs([
        "🎯 Microsegmentos",
        "💬 Generador de mensajes",
        "📣 Contenido para redes",
    ])

    # ─────────────────────────────────────────────────────────────────────
    # TAB 1 · MICROSEGMENTOS
    # ─────────────────────────────────────────────────────────────────────
    with tab1:
        st.markdown(
            '<span class="tag demo">DEMO</span> Segmentos calculados programáticamente '
            'desde el directorio de campo · cruce arquetipo × posición × enojo',
            unsafe_allow_html=True,
        )
        st.markdown("")

        col_segs, col_tabla = st.columns([2, 3], gap="large")

        with col_segs:
            st.markdown("#### Microsegmentos detectados")
            for seg in segmentos:
                arq = ARQUETIPOS[seg["arquetipo_base"]]
                urg_color = URGENCIA_COLOR[seg["urgencia"]]
                canal_icon = CANAL_ICON.get(seg["canal"], "📨")
                st.html(f"""
                <div style="background:#fff; border:1px solid #e2e8f0; border-radius:14px;
                            padding:16px 18px; margin-bottom:10px; cursor:default;">
                  <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
                    <div style="font-size:0.94rem; font-weight:700; color:#1e293b;">
                      {seg['nombre']}
                    </div>
                    <div style="font-size:0.74rem; font-weight:700; color:{urg_color};
                                background:{urg_color}15; padding:2px 10px; border-radius:20px;
                                flex-shrink:0; margin-left:8px;">
                      {seg['urgencia']}
                    </div>
                  </div>
                  <div style="font-size:0.80rem; color:#64748b; line-height:1.45; margin-bottom:10px;">
                    {seg['descripcion']}
                  </div>
                  <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
                    <div style="display:flex; align-items:center; gap:5px;">
                      <div style="width:9px; height:9px; border-radius:50%;
                                  background:{arq['color']}; flex-shrink:0;"></div>
                      <span style="font-size:0.76rem; color:#475569; font-weight:600;">
                        {seg['arquetipo_base']} · {arq['nombre'].split(' ')[2] if len(arq['nombre'].split()) > 2 else arq['nombre'][:12]}
                      </span>
                    </div>
                    <span style="font-size:0.76rem; color:#475569;">
                      {canal_icon} {seg['canal']}
                    </span>
                    <span style="font-size:0.88rem; font-weight:800; color:#1e293b;">
                      {seg['n']} contactos
                    </span>
                  </div>
                </div>
                """)

        with col_tabla:
            st.markdown("#### Directorio del segmento")
            seg_opts = {s["nombre"]: s for s in segmentos}
            sel_nom  = st.selectbox("Selecciona segmento", options=list(seg_opts.keys()),
                                    key="m4_seg_tabla")
            seg_sel  = seg_opts[sel_nom]
            df_seg   = df.loc[seg_sel["indices"]].copy()

            st.caption(
                f"{len(df_seg)} contactos · Demanda dominante: **{seg_sel['demanda_dom']}**"
            )

            # Mostrar tabla limpia
            df_display = df_seg[["nombre", "posicion", "arquetipo", "enojo",
                                  "acepta_contacto", "celular", "seccion"]].copy()
            df_display.columns = ["Nombre", "Posición", "Arquetipo", "Enojo", "Acepta", "Celular", "Sección"]

            # Color enojo
            def _color_enojo(v):
                colors = {1: "#dcfce7", 2: "#fef9c3", 3: "#fed7aa", 4: "#fecaca", 5: "#fca5a5"}
                return f"background-color: {colors.get(v, '#fff')}"

            st.dataframe(
                df_display.style.map(_color_enojo, subset=["Enojo"]),
                use_container_width=True, hide_index=True, height=350,
            )

            # KPIs del segmento
            t1, t2, t3 = st.columns(3)
            n_acepta = int((df_seg["acepta_contacto"] == "Sí").sum())
            n_ind    = int((df_seg["posicion"] == "Indeciso").sum())
            enojo_m  = float(df_seg["enojo"].mean())
            for col, val, lbl in [
                (t1, n_acepta, "Acepta contacto"),
                (t2, n_ind,    "Indecisos en el segmento"),
                (t3, f"{enojo_m:.1f}/5", "Enojo promedio"),
            ]:
                with col:
                    st.metric(lbl, val)

    # ─────────────────────────────────────────────────────────────────────
    # TAB 2 · GENERADOR DE MENSAJES + ENVÍO SMS
    # ─────────────────────────────────────────────────────────────────────
    with tab2:
        # Inicializar session state
        for key, default in [
            ("m4_mensaje_generado",  None),
            ("m4_canal_activo",      "SMS"),
            ("m4_seg_activo",        segmentos[0]["nombre"] if segmentos else ""),
            ("m4_stakeholder_num",    ""),
            ("m4_stakeholder_nombre", ""),
            ("m4_sms_enviado",        False),
            ("m4_sms_resultado",      None),
            ("m4_sms_destinatarios",  []),
            ("m4_sms_template",       ""),
        ]:
            if key not in st.session_state:
                st.session_state[key] = default

        # Banner de resultado de envío previo
        if st.session_state["m4_sms_enviado"] and st.session_state["m4_sms_resultado"]:
            resultados = st.session_state["m4_sms_resultado"]
            # resultados es ahora una lista de dicts por destinatario
            if isinstance(resultados, list):
                n_ok  = sum(1 for r in resultados if r.get("ok"))
                n_err = len(resultados) - n_ok
                titulo = f"✅ {n_ok} SMS enviado{'s' if n_ok != 1 else ''} exitosamente" + (
                    f" · ⚠️ {n_err} con error" if n_err else ""
                )
                banner_class = "banner-ok" if n_err == 0 else "banner-err"
                filas = ""
                for r in resultados:
                    icon = "✅" if r.get("ok") else "⚠️"
                    filas += (
                        f'<div style="font-size:0.80rem; color:#334155; padding:3px 0;">'
                        f'{icon} <b>{r["nombre"]}</b> · '
                        f'<span style="font-family:monospace; font-size:0.74rem;">{r["numero_masked"]}</span>'
                        f'<br><span style="font-size:0.76rem; color:#64748b; padding-left:18px;">'
                        f'"{r.get("mensaje","")[:60]}{"…" if len(r.get("mensaje","")) > 60 else ""}"'
                        f'</span></div>'
                    )
                st.html(f"""
                <div class="{banner_class}" style="margin-bottom:10px;">
                  <div style="font-size:0.74rem; font-weight:700; color:#166534 if {n_err}==0 else #991b1b;
                              text-transform:uppercase; letter-spacing:0.05em; margin-bottom:8px;">
                    {titulo}
                  </div>
                  {filas}
                </div>
                """)
            if st.button("Limpiar y generar nuevo mensaje", key="m4_btn_limpiar"):
                st.session_state["m4_sms_enviado"]      = False
                st.session_state["m4_sms_resultado"]    = None
                st.session_state["m4_mensaje_generado"] = None
                st.rerun()

        st.markdown("---")

        col_gen, col_prev = st.columns([1, 1], gap="large")

        with col_gen:
            st.markdown("#### Configura el mensaje")

            seg_nombres = [s["nombre"] for s in segmentos]
            seg_activo_nom = st.selectbox(
                "Segmento",
                options=seg_nombres,
                index=seg_nombres.index(st.session_state["m4_seg_activo"])
                      if st.session_state["m4_seg_activo"] in seg_nombres else 0,
                key="m4_sel_seg",
            )
            st.session_state["m4_seg_activo"] = seg_activo_nom
            seg_activo = next(s for s in segmentos if s["nombre"] == seg_activo_nom)

            canal = st.radio(
                "Canal",
                options=CANALES,
                index=CANALES.index(st.session_state["m4_canal_activo"])
                      if st.session_state["m4_canal_activo"] in CANALES else 0,
                horizontal=True,
                key="m4_sel_canal",
            )
            st.session_state["m4_canal_activo"] = canal

            # Info del segmento
            arq_b = ARQUETIPOS[seg_activo["arquetipo_base"]]
            st.html(f"""
            <div style="background:#f8fafc; border-left:3px solid {arq_b['color']};
                        border-radius:0 8px 8px 0; padding:10px 14px; margin:8px 0 14px 0;
                        font-family:'DM Sans',sans-serif;">
              <div style="font-size:0.74rem; font-weight:700; color:#64748b; margin-bottom:4px;">
                Demanda dominante del segmento
              </div>
              <div style="font-size:0.86rem; font-weight:600; color:#1e293b;">
                {seg_activo['demanda_dom']}
              </div>
              <div style="font-size:0.76rem; color:#64748b; margin-top:4px;">
                {seg_activo['n']} contactos · {arq_b['emoji']} {arq_b['nombre']}
              </div>
            </div>
            """)

            cb1, cb2 = st.columns(2)
            with cb1:
                if st.button("✨ Generar mensaje", type="primary",
                             use_container_width=True, key="m4_btn_generar_msg"):
                    with st.spinner("Generando con Claude API…"):
                        resultado = generar_mensaje_claude(seg_activo, canal)
                        st.session_state["m4_mensaje_generado"] = resultado
                        st.session_state["m4_sms_enviado"] = False
                        st.rerun()
            with cb2:
                if st.button("Ver ejemplo", use_container_width=True, key="m4_btn_ejemplo_msg"):
                    ejemplo = MENSAJES_EJEMPLO.get((seg_activo_nom, canal))
                    if ejemplo is None:
                        # Fallback: primer segmento que tenga ejemplo para este canal
                        ejemplo = next(
                            (v for (k_seg, k_can), v in MENSAJES_EJEMPLO.items() if k_can == canal),
                            "Ejemplo no disponible para esta combinación."
                        )
                    st.session_state["m4_mensaje_generado"] = ejemplo
                    st.session_state["m4_sms_enviado"] = False
                    st.rerun()

            # ── Campo de redacción manual ──────────────────────────────
            st.markdown("##### ✏️ O redacta el mensaje manualmente")
            texto_manual = st.text_area(
                "Escribe aquí el texto del mensaje",
                value=(
                    st.session_state["m4_mensaje_generado"]
                    if isinstance(st.session_state.get("m4_mensaje_generado"), str)
                    else ""
                ),
                placeholder="Escribe tu propio mensaje o edita el que generó Claude…",
                height=100,
                key="m4_texto_manual",
                label_visibility="collapsed",
            )
            if texto_manual.strip():
                # El campo manual siempre pisa el estado del generador
                if texto_manual.strip() != st.session_state.get("m4_mensaje_generado"):
                    if st.button("Usar este texto", key="m4_btn_usar_manual",
                                 use_container_width=True):
                        st.session_state["m4_mensaje_generado"] = texto_manual.strip()
                        st.session_state["m4_sms_enviado"] = False
                        st.rerun()
                if canal == "SMS":
                    chars = len(texto_manual.strip())
                    color = "#166534" if chars <= 160 else "#dc2626"
                    st.markdown(
                        f'<span style="font-size:0.76rem; font-weight:600; color:{color};">'
                        f'{chars}/160 caracteres</span>',
                        unsafe_allow_html=True,
                    )

            # ── Sección SMS: destinatarios ─────────────────────────────
            if canal == "SMS":
                st.markdown("---")
                st.markdown(
                    '<span class="tag live">REAL · EN VIVO</span> '
                    'Destinatarios del envío SMS',
                    unsafe_allow_html=True,
                )

                # Lista fija del equipo (desde secrets)
                try:
                    demo_nums = list(st.secrets.get("DEMO_DESTINATARIOS", []))
                except Exception:
                    demo_nums = []

                # secrets ahora es array de objetos {nombre, numero}
                team_dests = []
                for item in demo_nums:
                    if isinstance(item, dict):
                        nombre_d = item.get("nombre", "Equipo Data & AI")
                        numero_d = item.get("numero", "")
                    else:
                        nombre_d = "Equipo Data & AI"
                        numero_d = str(item)
                    if numero_d:
                        team_dests.append({
                            "nombre":        nombre_d,
                            "numero":        numero_d,
                            "numero_masked": _mask_number(numero_d),
                            "tipo":          "equipo",
                        })

                if team_dests:
                    for td in team_dests:
                        msg_prev = personalizar_mensaje(
                            st.session_state.get("m4_mensaje_generado") or "Hola {nombre}…",
                            td["nombre"]
                        ) if isinstance(st.session_state.get("m4_mensaje_generado"), str) else ""
                        st.html(f"""
                        <div class="dest-row">
                          <div style="font-size:0.80rem; font-weight:600; color:#1e293b; min-width:130px;">
                            {td['nombre']}</div>
                          <div style="font-size:0.76rem; color:#475569; flex:1; font-style:italic;">
                            {msg_prev[:45] + ('…' if len(msg_prev) > 45 else '') if msg_prev else '—'}</div>
                          <div style="font-size:0.70rem; color:#64748b; font-family:monospace; white-space:nowrap;">
                            {td['numero_masked']}</div>
                          <div style="font-size:0.70rem; color:#0b6b46; font-weight:700; white-space:nowrap;">FIJO</div>
                        </div>
                        """)
                else:
                    st.caption("No hay destinatarios fijos configurados en secrets.")

                # Campo stakeholder — nombre + número en la misma fila
                st.markdown("**Agregar stakeholder a este envío:**")
                sh_col1, sh_col2 = st.columns([1, 1], gap="small")
                with sh_col1:
                    nom_sh = st.text_input(
                        "Nombre",
                        value=st.session_state["m4_stakeholder_nombre"],
                        placeholder="Anabel Ávalos",
                        key="m4_input_sh_nombre",
                    )
                    st.session_state["m4_stakeholder_nombre"] = nom_sh.strip()
                with sh_col2:
                    num_sh = st.text_input(
                        "Número",
                        value=st.session_state["m4_stakeholder_num"],
                        placeholder="521XXXXXXXXXX",
                        key="m4_input_stakeholder",
                    )
                    st.session_state["m4_stakeholder_num"] = num_sh.strip()

                dest_final = list(team_dests)
                if num_sh.strip():
                    nombre_sh = nom_sh.strip() or "Stakeholder"
                    msg_sh_prev = personalizar_mensaje(
                        st.session_state.get("m4_mensaje_generado") or "Hola {nombre}…",
                        nombre_sh
                    ) if isinstance(st.session_state.get("m4_mensaje_generado"), str) else ""
                    dest_final.append({
                        "nombre":        nombre_sh,
                        "numero":        num_sh.strip(),
                        "numero_masked": _mask_number(num_sh.strip()),
                        "tipo":          "stakeholder",
                    })
                    if msg_sh_prev:
                        st.html(f"""
                        <div class="dest-row" style="border-color:#b8860b; background:#fffbeb;">
                          <div style="font-size:0.80rem; font-weight:700; color:#92400e; min-width:130px;">
                            {nombre_sh} ★</div>
                          <div style="font-size:0.76rem; color:#78350f; flex:1; font-style:italic;">
                            {msg_sh_prev[:45] + ('…' if len(msg_sh_prev) > 45 else '')}</div>
                          <div style="font-size:0.70rem; color:#78350f; font-family:monospace; white-space:nowrap;">
                            {_mask_number(num_sh.strip())}</div>
                          <div style="font-size:0.70rem; color:#b8860b; font-weight:700;">SESIÓN</div>
                        </div>
                        """)

                # Botón de envío
                msg_actual = st.session_state.get("m4_mensaje_generado")
                puede_enviar = (
                    msg_actual is not None
                    and isinstance(msg_actual, str)
                    and "{nombre}" in msg_actual
                    and len(dest_final) > 0
                )
                # También permitir envío si el mensaje no tiene {nombre} (manual sin marcador)
                puede_enviar_sin_marker = (
                    msg_actual is not None
                    and isinstance(msg_actual, str)
                    and len(dest_final) > 0
                )
                if st.button(
                    "📤 Enviar SMS personalizado",
                    type="primary",
                    disabled=not puede_enviar_sin_marker,
                    use_container_width=True,
                    key="m4_btn_enviar_sms",
                ):
                    modal_envio_sms(msg_actual, dest_final)

                if not puede_enviar_sin_marker:
                    st.caption("Genera o carga un ejemplo de mensaje primero.")
                elif not puede_enviar and puede_enviar_sin_marker:
                    st.caption(
                        "💡 El mensaje no contiene `{nombre}` — "
                        "se enviará el mismo texto a todos los destinatarios."
                    )

        with col_prev:
            st.markdown("#### Vista previa")

            msg = st.session_state.get("m4_mensaje_generado")

            if msg is None:
                st.html("""
                <div style="background:#f8fafc; border:1px dashed #cbd5e1; border-radius:14px;
                            padding:40px 30px; text-align:center; font-family:'DM Sans',sans-serif;">
                  <div style="font-size:2.0rem; margin-bottom:12px;">✍️</div>
                  <div style="font-size:0.88rem; color:#64748b; line-height:1.55;">
                    Selecciona segmento y canal,<br>luego genera el mensaje o carga un ejemplo.
                  </div>
                </div>
                """)
            else:
                # Es SMS o WhatsApp (str) o Correo (dict)
                if canal == "SMS":
                    if isinstance(msg, str):
                        render_preview_sms(msg)
                    else:
                        st.markdown(
                            '<span class="tag demo">DEMO</span> '
                            'El ejemplo de Correo está activo. Selecciona SMS para ver la burbuja.',
                            unsafe_allow_html=True,
                        )
                elif canal == "WhatsApp":
                    texto_wa = msg.get("cuerpo", str(msg)) if isinstance(msg, dict) else msg
                    render_preview_whatsapp(texto_wa)
                elif canal == "Correo":
                    if isinstance(msg, dict):
                        render_preview_correo(
                            msg.get("asunto", "Sin asunto"),
                            msg.get("cuerpo", ""),
                        )
                    else:
                        render_preview_correo("Mensaje generado", str(msg))

                # Preview de personalización — muestra cómo llega a cada persona
                if isinstance(msg, str) and "{nombre}" in msg:
                    seg_idx = seg_activo.get("indices", [])
                    muestra = df.loc[seg_idx[:3]] if seg_idx else df.iloc[:3]
                    st.markdown("---")
                    st.markdown(
                        '<span class="tag demo">DEMO</span> '
                        '**Así llega a cada persona del segmento**',
                        unsafe_allow_html=True,
                    )
                    for _, row in muestra.iterrows():
                        msg_personal = personalizar_mensaje(msg, row["nombre"])
                        primer_nombre = row["nombre"].split()[0]
                        arq_color = ARQUETIPOS.get(row["arquetipo"], {}).get("color", "#94a3b8")
                        st.html(f"""
                        <div style="font-family:'DM Sans',sans-serif; margin-bottom:10px;">
                          <div style="display:flex; align-items:center; gap:6px; margin-bottom:5px;">
                            <div style="width:7px; height:7px; border-radius:50%;
                                        background:{arq_color}; flex-shrink:0;"></div>
                            <span style="font-size:0.76rem; font-weight:600; color:#334155;">
                              {row['nombre']} · {row['arquetipo']} · Secc. {row['seccion']}
                            </span>
                          </div>
                          <div style="display:flex; justify-content:flex-end; padding-right:4px;">
                            <div style="max-width:85%;">
                              <div style="background:#e5e5ea; border-radius:14px 14px 3px 14px;
                                          padding:9px 13px; font-size:0.82rem;
                                          color:#1c1c1e; line-height:1.5;">
                                {msg_personal}
                              </div>
                            </div>
                          </div>
                        </div>
                        """)

                # Área de texto para copiar el template
                if isinstance(msg, str):
                    st.text_area("Template del mensaje", value=msg,
                                 height=80, key="m4_textarea_copy", label_visibility="collapsed")
                elif isinstance(msg, dict):
                    st.text_area(
                        "Texto del mensaje",
                        value=f"Asunto: {msg.get('asunto','')}\n\n{msg.get('cuerpo','')}",
                        height=120, key="m4_textarea_copy_email",
                        label_visibility="collapsed",
                    )

    # ─────────────────────────────────────────────────────────────────────
    # TAB 3 · CONTENIDO PARA REDES SOCIALES
    # ─────────────────────────────────────────────────────────────────────
    with tab3:
        st.markdown(
            '<span class="tag demo">DEMO</span> Posts anclados en las demandas detectadas en campo · '
            '<span class="tag real">REAL</span> Generación en vivo con Claude API + web search',
            unsafe_allow_html=True,
        )
        st.markdown("")

        # Temas disponibles (demandas del directorio)
        demandas_dir = sorted(df["demanda"].unique().tolist())
        demandas_extra = [d for d in POSTS_EJEMPLO.keys() if d not in demandas_dir]
        temas_disponibles = demandas_dir + demandas_extra

        col_ctrl3, col_post = st.columns([1, 2], gap="large")

        with col_ctrl3:
            st.markdown("#### Configura el post")

            tema_sel = st.selectbox(
                "Tema / Demanda social",
                options=temas_disponibles,
                key="m4_tema_post",
            )
            formato_sel = st.selectbox(
                "Formato",
                options=["Facebook", "Historia de Instagram (copy)", "Grupo de WhatsApp"],
                key="m4_formato_post",
            )

            if "m4_post_generado" not in st.session_state:
                st.session_state["m4_post_generado"] = None

            p1, p2 = st.columns(2)
            with p1:
                if st.button("✨ Generar en vivo", type="primary",
                             use_container_width=True, key="m4_btn_generar_post"):
                    with st.spinner("Consultando Claude + web search…"):
                        post_gen = generar_post_claude(tema_sel, formato_sel)
                        st.session_state["m4_post_generado"] = ("live", post_gen)
                        st.rerun()
            with p2:
                if st.button("Ver ejemplo", use_container_width=True, key="m4_btn_ejemplo_post"):
                    ejemplo_post = POSTS_EJEMPLO.get(tema_sel)
                    if ejemplo_post is None:
                        # Fallback al primer post de ejemplo disponible
                        ejemplo_post = next(iter(POSTS_EJEMPLO.values()))
                    st.session_state["m4_post_generado"] = ("ejemplo", ejemplo_post)
                    st.rerun()

            # Fuentes de info del electorado
            st.markdown("---")
            st.markdown("**¿Dónde se informa el electorado tlaxcalteca?**")
            st.html("""
            <div style="font-family:'DM Sans',sans-serif;">
              <div style="display:flex; justify-content:space-between; align-items:center;
                          padding:5px 0; border-bottom:1px solid #f1f5f9;">
                <span style="font-size:0.80rem; color:#334155;">📘 Facebook</span>
                <span style="font-size:0.84rem; font-weight:700; color:#3b82f6;">38%</span>
              </div>
              <div style="display:flex; justify-content:space-between; align-items:center;
                          padding:5px 0; border-bottom:1px solid #f1f5f9;">
                <span style="font-size:0.80rem; color:#334155;">🗣️ Boca en boca</span>
                <span style="font-size:0.84rem; font-weight:700; color:#64748b;">24%</span>
              </div>
              <div style="display:flex; justify-content:space-between; align-items:center;
                          padding:5px 0; border-bottom:1px solid #f1f5f9;">
                <span style="font-size:0.80rem; color:#334155;">📻 Radio</span>
                <span style="font-size:0.84rem; font-weight:700; color:#64748b;">15%</span>
              </div>
              <div style="display:flex; justify-content:space-between; align-items:center;
                          padding:5px 0;">
                <span style="font-size:0.80rem; color:#334155;">💬 WhatsApp</span>
                <span style="font-size:0.84rem; font-weight:700; color:#64748b;">14%</span>
              </div>
            </div>
            """)
            st.caption("Fuente: Módulo 1 · encuesta interna ficticia")

        with col_post:
            st.markdown("#### Vista previa del post")

            post_state = st.session_state.get("m4_post_generado")

            if post_state is None:
                st.html("""
                <div style="background:#f8fafc; border:1px dashed #cbd5e1; border-radius:14px;
                            padding:40px 30px; text-align:center; font-family:'DM Sans',sans-serif;">
                  <div style="font-size:2.2rem; margin-bottom:12px;">📣</div>
                  <div style="font-size:0.88rem; color:#64748b; line-height:1.55;">
                    Selecciona un tema y formato,<br>
                    luego genera en vivo o carga un ejemplo.
                  </div>
                </div>
                """)
            else:
                modo, post_data = post_state

                # Tag de modo
                if modo == "live":
                    st.markdown(
                        '<span class="tag live">REAL · EN VIVO</span> '
                        'Generado por Claude API con web search habilitado',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        '<span class="tag demo">EJEMPLO ILUSTRATIVO</span> '
                        'Post pre-generado con las reglas de comunicación de Anabel Ávalos',
                        unsafe_allow_html=True,
                    )

                render_post_card(post_data, formato_sel)

                # Texto para copiar
                if post_data.get("copy"):
                    st.text_area(
                        "Texto del post (para copiar)",
                        value=f"{post_data['copy']}\n\n{post_data.get('hashtags','')}",
                        height=140,
                        key="m4_post_copy",
                        label_visibility="collapsed",
                    )

        # ── Galería de ejemplos por demanda ───────────────────────────────
        st.markdown("---")
        st.markdown("#### Biblioteca de ejemplos · un post por demanda social")
        st.caption("Posts escritos en voz de Anabel Ávalos, sin lenguaje partidista, formato Facebook.")

        cols_grid = st.columns(2, gap="medium")
        for i, (dem, post) in enumerate(list(POSTS_EJEMPLO.items())[:6]):
            with cols_grid[i % 2]:
                dem_short = dem[:45] + "…" if len(dem) > 45 else dem
                preview_copy = post["copy"][:120] + "…" if len(post["copy"]) > 120 else post["copy"]
                st.html(f"""
                <div style="font-family:'DM Sans',sans-serif; background:#fff;
                            border:1px solid #e2e8f0; border-radius:12px;
                            padding:14px 16px; margin-bottom:10px;">
                  <div style="font-size:0.72rem; font-weight:700; color:#b8860b;
                              text-transform:uppercase; letter-spacing:0.05em; margin-bottom:6px;">
                    {dem_short}
                  </div>
                  <div style="font-size:0.82rem; color:#334155; line-height:1.55; margin-bottom:8px;">
                    {preview_copy}
                  </div>
                  <div style="font-size:0.74rem; color:#3b82f6;">{post.get('hashtags','')}</div>
                  <div style="font-size:0.72rem; color:#94a3b8; margin-top:6px;">
                    🕐 {post.get('horario','—')}
                  </div>
                </div>
                """)


main()