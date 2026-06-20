"""
M1 — Datos y Segmentación
PIE Tlaxcala · Anabel Ávalos · PRI 2027

Lo marcado como REAL proviene de fuentes públicas citadas en cada sección.
Lo demás es ficticio, generado para fines de la demostración.
"""

import os
import json
import requests
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="M1 · Datos y Segmentación · PIE Tlaxcala",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ════════════════════════════════════════════════════════════════════════════
# DATOS EMBEBIDOS
# ════════════════════════════════════════════════════════════════════════════

# ── BLOQUE REAL — Enkoll / El Universal, 19–22 marzo 2026, N=1,233 ───────────
ENKOLL_VOTO_GOBERNADOR = [
    {"partido": "Morena", "pct": 47.0, "color": "#7c2d12"},
    {"partido": "PRI",    "pct": 14.0, "color": "#a3142b"},
    {"partido": "PAN",    "pct": 13.0, "color": "#1d4ed8"},
    {"partido": "MC",     "pct": 10.0, "color": "#ea580c"},
    {"partido": "PT",     "pct": 4.0,  "color": "#b91c1c"},
    {"partido": "PVEM",   "pct": 4.0,  "color": "#16a34a"},
    {"partido": "Otros",  "pct": 8.0,  "color": "#94a3b8"},
]

ENKOLL_IDENTIDAD_PARTIDISTA = [
    {"partido": "Morena",      "pct": 39.0, "color": "#7c2d12"},
    {"partido": "PRI",         "pct": 11.0, "color": "#a3142b"},
    {"partido": "PAN",         "pct": 10.0, "color": "#1d4ed8"},
    {"partido": "MC",          "pct": 7.0,  "color": "#ea580c"},
    {"partido": "PT",          "pct": 4.0,  "color": "#b91c1c"},
    {"partido": "PVEM",        "pct": 3.0,  "color": "#16a34a"},
    {"partido": "Apartidista", "pct": 18.0, "color": "#64748b"},
    {"partido": "Otros / NS",  "pct": 8.0,  "color": "#cbd5e1"},
]

ENKOLL_META = {
    "fuente": "Enkoll / El Universal",
    "fecha": "19–22 de marzo de 2026",
    "n": 1233,
    "metodo": "Entrevistas cara a cara en vivienda, muestreo polietápico por secciones electorales",
    "margen_error": "± 2.8%",
    "confianza": "95%",
}

HALLAZGO_PERSONALISTA = (
    "Una medición distinta encontró que el respaldo de Ávalos depende más de su marca "
    "personal que del voto duro priista: una parte relevante de quienes la mencionan como "
    "opción provienen de fuera del PRI, incluyendo simpatizantes de Morena."
)

# ── BLOQUE FICTICIO — encuesta interna, 8 reactivos avanzados ───────────────
REACTIVOS = [
    {
        "id": "atribucion", "icono": "⚖️",
        "titulo": "Atribución de responsabilidad",
        "pregunta": "Cuando el servicio de salud falla, no hay medicamentos, o hay problemas "
                    "de seguridad en su colonia, ¿quién cree usted que es el principal responsable?",
        "tipo": "categorica",
        "datos": [
            {"opcion": "La Gobernadora (estatal)",                 "pct": 41.0},
            {"opcion": "Los partidos políticos en general",        "pct": 24.0},
            {"opcion": "El Presidente Municipal (local)",          "pct": 18.0},
            {"opcion": "La Presidenta de la República (federal)",  "pct": 9.0},
            {"opcion": "Es culpa de los mismos ciudadanos",        "pct": 8.0},
        ],
        "insight": "La pluralidad culpa al gobierno estatal, no al municipio ni a la federación "
                   "— la conexión causal exacta que necesita un mensaje de gobernatura.",
    },
    {
        "id": "autoritarismo", "icono": "🛑",
        "titulo": "Descontento y tolerancia al autoritarismo",
        "pregunta": "¿Qué tan de acuerdo está con que un gobierno con mano dura, aunque no "
                    "siempre respete las leyes o las elecciones, podría resolver mejor los "
                    "problemas de Tlaxcala que el sistema actual?",
        "tipo": "categorica",
        "datos": [{"opcion": "De acuerdo o totalmente de acuerdo", "pct": 41.0},
                  {"opcion": "En desacuerdo o sin definir",        "pct": 59.0}],
        "insight": "4 de cada 10 tlaxcaltecas ya asimiló el autoritarismo como solución legítima "
                   "ante la ineficacia burocrática — susceptible a un mensaje de ruptura.",
    },
    {
        "id": "termometro", "icono": "🌡️",
        "titulo": "Termómetro afectivo (0–100)",
        "pregunta": "En una escala de 0 a 100, donde 0 es enojo o rechazo profundo y 100 es "
                    "calidez o simpatía, ¿qué temperatura le pondría usted a…?",
        "tipo": "termometro",
        "datos": [
            {"opcion": "El partido MORENA",                         "valor": 38},
            {"opcion": "Los partidos de oposición (PRI/PAN/PRD/MC)", "valor": 31},
            {"opcion": "La Gobernadora Lorena Cuéllar",             "valor": 35},
            {"opcion": "La Policía Estatal y cuerpos de seguridad",  "valor": 29},
        ],
        "insight": "Nadie genera calidez real — ni el gobierno ni la oposición. El espacio "
                   "afectivo está abierto para quien conecte primero a nivel personal.",
    },
    {
        "id": "friccion", "icono": "🧾",
        "titulo": "Fricción burocrática",
        "pregunta": "En el último año, al intentar realizar un trámite, solicitar un servicio "
                    "público o enfrentarse a una autoridad, ¿usted o algún familiar enfrentaron "
                    "obstáculos excesivos o les sugirieron el pago de una mordida o soborno?",
        "tipo": "categorica",
        "datos": [
            {"opcion": "Sí, en varias ocasiones",    "pct": 24.0},
            {"opcion": "Sí, en al menos una ocasión", "pct": 22.0},
            {"opcion": "No, conforme a la ley",       "pct": 31.0},
            {"opcion": "No realizó ningún trámite",   "pct": 23.0},
        ],
        "insight": "46% reporta al menos un obstáculo o sugerencia de soborno — una agenda de "
                   "eficacia gubernamental, no solo de discurso.",
    },
    {
        "id": "miedo", "icono": "🚨",
        "titulo": "Vector de miedo dominante",
        "pregunta": "De las siguientes situaciones, ¿cuál le genera mayor miedo y preocupación "
                    "en su vida diaria?",
        "tipo": "categorica",
        "datos": [
            {"opcion": "Asalto en calles, cajeros o transporte público", "pct": 34.0},
            {"opcion": "Extorsión o cobro de piso a familia o negocio",  "pct": 23.0},
            {"opcion": "Abusos de autoridad o corrupción policial",      "pct": 22.0},
            {"opcion": "Trata de personas o desaparición de mujeres",    "pct": 21.0},
        ],
        "insight": "Casi parejo entre las cuatro categorías — un solo mensaje de 'seguridad' no "
                   "alcanza, cada bloque necesita su propio ángulo narrativo.",
    },
    {
        "id": "fuente_info", "icono": "📡",
        "titulo": "Fuente de información",
        "pregunta": "¿Dónde se entera principalmente de lo que pasa en política o en su "
                    "colonia/municipio?",
        "tipo": "categorica",
        "datos": [
            {"opcion": "Facebook",                   "pct": 38.0},
            {"opcion": "De boca en boca con vecinos", "pct": 24.0},
            {"opcion": "Radio local",                 "pct": 15.0},
            {"opcion": "Grupos de WhatsApp",          "pct": 14.0},
            {"opcion": "TikTok",                      "pct": 9.0},
        ],
        "insight": "Facebook domina, pero un tercio sigue siendo boca en boca o radio — la "
                   "pauta digital sola no cubre a todo el electorado.",
    },
    {
        "id": "cambio", "icono": "🔄",
        "titulo": "Disposición cambio vs. continuidad",
        "pregunta": "Si pudiera elegir, ¿prefiere que las cosas en Tlaxcala sigan igual, "
                    "cambien un poco, o cambien de fondo?",
        "tipo": "categorica",
        "datos": [
            {"opcion": "Cambien de fondo", "pct": 37.0},
            {"opcion": "Cambien un poco",  "pct": 35.0},
            {"opcion": "Sigan igual",      "pct": 18.0},
            {"opcion": "No sabe",          "pct": 10.0},
        ],
        "insight": "72% quiere algún grado de cambio — el activo central disponible para una "
                   "narrativa de alternativa, si se sabe capitalizar.",
    },
    {
        "id": "centralidad", "icono": "🧑‍🤝‍🧑",
        "titulo": "Centralidad social",
        "pregunta": "Cuando pasa algo en su colonia o municipio, ¿la gente le pregunta su "
                    "opinión, o usted organiza a los vecinos?",
        "tipo": "categorica",
        "datos": [
            {"opcion": "Sí, con frecuencia", "pct": 12.0},
            {"opcion": "Alguna vez",         "pct": 21.0},
            {"opcion": "Casi nunca",         "pct": 67.0},
        ],
        "insight": "1 de cada 3 tiene algún grado de influencia social — son los multiplicadores "
                   "que la brigada debería identificar primero en el Módulo 3.",
    },
]

# ── BLOQUE FICTICIO — arquetipos del elector tlaxcalteca (gobernatura) ──────
ARQUETIPOS = {
    "A1": {"nombre": "El Leal Institucional Tricolor", "pct_padron": 9.0, "color": "#a3142b",
           "prioridad": "Mantenimiento", "orden": 4, "atribucion": "Gobierno estatal",
           "term_morena": 12, "term_oposicion": 68, "term_gobernadora": 15, "pct_friccion": 38.0,
           "vector_miedo": "Abuso de autoridad", "autoritarismo": 22.0,
           "descripcion": "Recuerda con cariño los años en que el PRI gobernaba el estado y "
                          "siente que desde entonces los servicios se han deteriorado. Vota con "
                          "disciplina casi familiar, conoce a los operadores del partido desde "
                          "hace años y desconfía profundamente del proyecto de Morena.",
           "frase": "“Yo nunca he dejado al partido — el partido me hizo lo que soy.”",
           "mensaje": "Activación y multiplicación de red — no necesita ser convencido, necesita movilizarse.",
           "municipio": "Tlaxcala capital"},
    "A2": {"nombre": "El Decepcionado del Gobierno Estatal", "pct_padron": 17.0, "color": "#dc2626",
           "prioridad": "Máxima", "orden": 1, "atribucion": "Gobernadora",
           "term_morena": 28, "term_oposicion": 33, "term_gobernadora": 14, "pct_friccion": 61.0,
           "vector_miedo": "Asalto / extorsión", "autoritarismo": 35.0,
           "descripcion": "Votó por el cambio con esperanza real hace algunos años, pero hoy "
                          "siente que los servicios básicos empeoraron y que nadie en el gobierno "
                          "estatal responde. No tiene partido fijo: busca activamente una "
                          "alternativa creíble que hable de resultados, no de ideología.",
           "frase": "“No soy de ningún partido, pero ya estoy cansado de que nada cambie.”",
           "mensaje": "Conecta su enojo directamente con el cargo en disputa — target #1 de persuasión.",
           "municipio": "Apizaco"},
    "A3": {"nombre": "El Anti-Sistema Punitivo", "pct_padron": 13.0, "color": "#7c2d92",
           "prioridad": "Alta", "orden": 2, "atribucion": "Partidos en general",
           "term_morena": 19, "term_oposicion": 21, "term_gobernadora": 18, "pct_friccion": 55.0,
           "vector_miedo": "Abuso de autoridad", "autoritarismo": 64.0,
           "descripcion": "Cree que todos los partidos son lo mismo y que la política es, en el "
                          "fondo, un negocio para quienes ya están adentro. Vive con la sensación "
                          "de que las instituciones lo protegen menos de lo que un castigo "
                          "ejemplar lo haría — es el votante que puede sorprender en la boleta.",
           "frase": "“Aquí lo que se necesita es mano dura, ya no aguantamos la impunidad.”",
           "mensaje": "Exige un mensaje de ruptura, no el discurso tradicional de partido.",
           "municipio": "Huamantla"},
    "A4": {"nombre": "La Guardiana del Miedo de Género", "pct_padron": 8.0, "color": "#be185d",
           "prioridad": "Alta — nicho", "orden": 2, "atribucion": "Gobernadora",
           "term_morena": 30, "term_oposicion": 34, "term_gobernadora": 22, "pct_friccion": 40.0,
           "vector_miedo": "Trata / violencia de género", "autoritarismo": 30.0,
           "descripcion": "Vive con alerta constante por la seguridad de las mujeres de su "
                          "familia — hijas, hermanas, vecinas. No confía en la policía estatal y "
                          "siente que las autoridades minimizan la violencia de género en la "
                          "región. Un mensaje serio y específico, no genérico, se gana su confianza.",
           "frase": "“A mi hija no la dejo salir sola ni de día, y eso no debería ser normal.”",
           "mensaje": "Sensible a un mensaje serio de protección con enfoque de género.",
           "municipio": "Huamantla"},
    "A5": {"nombre": "El Rural Desatendido por el Estado", "pct_padron": 14.0, "color": "#15803d",
           "prioridad": "Media-alta", "orden": 3, "atribucion": "Gobernadora",
           "term_morena": 41, "term_oposicion": 29, "term_gobernadora": 26, "pct_friccion": 48.0,
           "vector_miedo": "Agua y campo", "autoritarismo": 33.0,
           "descripcion": "Trabaja el campo o depende de él indirectamente, y siente que los "
                          "apoyos agrícolas y la infraestructura rural llevan años de abandono "
                          "por parte del gobierno estatal, no del municipio. No pide discursos: "
                          "pide que alguien resuelva el agua o el camino a la parcela.",
           "frase": "“El camino a mi parcela lleva años destrozado y nadie del estado lo ha visto.”",
           "mensaje": "Mensaje de presencia territorial y gestión, no de discurso.",
           "municipio": "Huamantla"},
    "A6": {"nombre": "La Conforme con la Continuidad", "pct_padron": 16.0, "color": "#0891b2",
           "prioridad": "Baja", "orden": 5, "atribucion": "Ciudadanos mismos",
           "term_morena": 71, "term_oposicion": 22, "term_gobernadora": 64, "pct_friccion": 19.0,
           "vector_miedo": "Asalto / extorsión", "autoritarismo": 14.0,
           "descripcion": "Está satisfecha en general con el rumbo del estado, o al menos no lo "
                          "asocia con sus problemas personales. Recibe algún apoyo social y lo "
                          "valora. No es activista política — simplemente no ve razón para "
                          "cambiar a quien gobierna.",
           "frase": "“A mí me ha ido bien, no tengo queja del gobierno.”",
           "mensaje": "Solo monitoreo — invertir aquí desplaza recursos de targets más rentables.",
           "municipio": "Tlaxcala capital"},
    "A7": {"nombre": "El Susceptible a la Ruptura", "pct_padron": 11.0, "color": "#c2410c",
           "prioridad": "Alta — oportunidad y riesgo", "orden": 2, "atribucion": "Partidos en general",
           "term_morena": 24, "term_oposicion": 23, "term_gobernadora": 17, "pct_friccion": 57.0,
           "vector_miedo": "Asalto / extorsión", "autoritarismo": 70.0,
           "descripcion": "Combina un miedo cotidiano muy concreto a la inseguridad con una "
                          "desconfianza casi total hacia cualquier autoridad. Es el votante más "
                          "impredecible del estado: puede inclinarse hacia cualquier figura que "
                          "le ofrezca una promesa de orden inmediato, sin importar el partido.",
           "frase": "“Ya no me importa de qué partido sea, solo quiero que alguien meta orden.”",
           "mensaje": "El más volátil: se va con cualquiera que suene a 'mano dura y resultados ya'.",
           "municipio": "Apizaco"},
    "A8": {"nombre": "El Desconectado de lo Estatal", "pct_padron": 12.0, "color": "#64748b",
           "prioridad": "No prioritario", "orden": 6, "atribucion": "Municipio / federal / ciudadanos",
           "term_morena": 45, "term_oposicion": 27, "term_gobernadora": 40, "pct_friccion": 30.0,
           "vector_miedo": "Falta de medicamentos", "autoritarismo": 26.0,
           "descripcion": "Cuando algo falla en su vida diaria, su primer instinto es culpar al "
                          "presidente municipal o de plano 'a la gente', no al gobierno del "
                          "estado. Vota más por cercanía y trato personal que por una narrativa "
                          "de gobernatura.",
           "frase": "“Aquí el problema es el ayuntamiento, eso no tiene nada que ver con el estado.”",
           "mensaje": "Nunca culpa a la Gobernadora — mejor target para alcaldías, no para gobernatura.",
           "municipio": "Tlaxcala capital"},
}

PRIORIDAD_COLOR = {
    "Máxima": "#dc2626", "Alta": "#c2410c", "Alta — nicho": "#be185d",
    "Alta — oportunidad y riesgo": "#7c2d92", "Media-alta": "#0e7490",
    "Baja": "#64748b", "Mantenimiento": "#15803d", "No prioritario": "#94a3b8",
}

TEMAS_DESCONTENTO = [
    "Inseguridad (asalto / extorsión)",
    "Agua y campo",
    "Trata / violencia de género",
    "Corrupción / mordida",
    "Críticas directas a la Gobernadora",
    "Falta de medicamentos / desabasto de salud",
]
FUENTES_TIPO = [
    "Prensa local indexada",
    "Declaraciones y comunicados oficiales",
    "Conversación pública en redes (búsqueda web)",
]

# ── Página de Facebook a analizar (Tab 3, prueba de valor con Apify) ───────
FACEBOOK_PAGE_URL = "https://www.facebook.com/elsoldetlaxcala"
# Actor oficial de Apify (publicado por la propia Apify, no un tercero), verificado
# contra apify.com/apify/facebook-posts-scraper/input-schema: acepta startUrls=[{"url":...}]
# y resultsLimit=int; el actor solo lee posts públicos de la página (no comentarios).
# Costo de referencia (consultado jun 2026): ~$2.00 USD por cada 1,000 posts.
APIFY_ACTOR_ID = "apify~facebook-posts-scraper"

# ── EJEMPLO ILUSTRATIVO — solo para previsualizar el diseño, NUNCA se mezcla ──
# con datos en vivo. Mismo esquema que devolvería la llamada real a Claude.
EJEMPLO_RESULTADO_TEMAS = {
    "ranking": [
        {"tema": "Inseguridad (asalto / extorsión)",              "volumen": 88, "descontento": 81},
        {"tema": "Críticas directas a la Gobernadora",             "volumen": 74, "descontento": 69},
        {"tema": "Falta de medicamentos / desabasto de salud",     "volumen": 66, "descontento": 77},
        {"tema": "Agua y campo",                                   "volumen": 58, "descontento": 64},
        {"tema": "Corrupción / mordida",                           "volumen": 52, "descontento": 71},
        {"tema": "Trata / violencia de género",                    "volumen": 40, "descontento": 85},
    ],
    "matriz": {
        "Inseguridad (asalto / extorsión)":              {"Prensa local indexada": 78, "Declaraciones y comunicados oficiales": 35, "Conversación pública en redes (búsqueda web)": 84},
        "Agua y campo":                                   {"Prensa local indexada": 60, "Declaraciones y comunicados oficiales": 41, "Conversación pública en redes (búsqueda web)": 66},
        "Trata / violencia de género":                    {"Prensa local indexada": 70, "Declaraciones y comunicados oficiales": 22, "Conversación pública en redes (búsqueda web)": 90},
        "Corrupción / mordida":                           {"Prensa local indexada": 65, "Declaraciones y comunicados oficiales": 18, "Conversación pública en redes (búsqueda web)": 73},
        "Críticas directas a la Gobernadora":              {"Prensa local indexada": 72, "Declaraciones y comunicados oficiales": 12, "Conversación pública en redes (búsqueda web)": 80},
        "Falta de medicamentos / desabasto de salud":      {"Prensa local indexada": 75, "Declaraciones y comunicados oficiales": 30, "Conversación pública en redes (búsqueda web)": 79},
    },
    "voz_calle": {
        "Inseguridad (asalto / extorsión)": [
            {"cita": "Vecinos de la capital reportan más asaltos en transporte público que el año pasado.",
             "fuente": "Ejemplo ilustrativo — prensa local (fecha simulada)",
             "narrativa_sugerida": "Reconocer el miedo cotidiano sin prometer cifras irreales; "
                                    "anclar la propuesta en presencia visible, no solo en discurso."},
        ],
        "Falta de medicamentos / desabasto de salud": [
            {"cita": "Usuarios de centros de salud en Huamantla denuncian desabasto recurrente de medicamentos básicos.",
             "fuente": "Ejemplo ilustrativo — prensa local (fecha simulada)",
             "narrativa_sugerida": "Proponer un compromiso verificable y medible de abasto, no una "
                                    "promesa genérica de 'mejorar la salud'."},
        ],
    },
}

EJEMPLO_FB_POSTS = [
    {"text": "Ejemplo ilustrativo — Reporte vecinal sobre bacheo en la avenida principal de Apizaco.",
     "likes": 312, "comments": 47},
    {"text": "Ejemplo ilustrativo — Cobertura de desabasto de medicamentos en centro de salud de Huamantla.",
     "likes": 540, "comments": 96},
    {"text": "Ejemplo ilustrativo — Nota sobre vialidad y obra pública en Tlaxcala capital.",
     "likes": 188, "comments": 22},
]

# ════════════════════════════════════════════════════════════════════════════
# FILTRO POR MUNICIPIO — Opción B: datos reales distintos por territorio
# ════════════════════════════════════════════════════════════════════════════

MUNICIPIO_OPCIONES = {
    "🗺️ Estatal (todos los municipios)": "estatal",
    "🏙️ Tlaxcala capital":               "capital",
    "🏭 Apizaco":                         "apizaco",
    "🌾 Huamantla":                       "huamantla",
}

# % del padrón por arquetipo y municipio — los números se mueven de verdad
ARQ_PCT_X_MUN = {
    # estatal = los promedios del dict ARQUETIPOS principal
    "estatal":   {"A1": 9,  "A2": 17, "A3": 13, "A4": 8,  "A5": 14, "A6": 16, "A7": 11, "A8": 12},
    # capital: más institucional, más conforme, menos rural
    "capital":   {"A1": 14, "A2": 16, "A3": 10, "A4": 7,  "A5":  3, "A6": 22, "A7": 12, "A8": 16},
    # apizaco: más decepcionado y susceptible — ciudad periférica con alta fricción
    "apizaco":   {"A1":  8, "A2": 24, "A3": 14, "A4":  8, "A5":  6, "A6": 12, "A7": 18, "A8": 10},
    # huamantla: muy rural, domina el archivos rural desatendido y el anti-sistema
    "huamantla": {"A1":  7, "A2": 13, "A3": 16, "A4": 10, "A5": 28, "A6": 14, "A7":  7, "A8":  5},
}

# Overrides de datos de reactivos por municipio
# Solo se reemplazan los reactivos que cambian de forma narrativamente significativa.
REACTIVOS_DELTA = {
    "estatal": {},  # sin override — usa los datos base
    "capital": {
        "atribucion": [
            {"opcion": "La Gobernadora (estatal)",                 "pct": 38.0},
            {"opcion": "Los partidos políticos en general",        "pct": 26.0},
            {"opcion": "El Presidente Municipal (local)",          "pct": 20.0},
            {"opcion": "La Presidenta de la República (federal)",  "pct": 9.0},
            {"opcion": "Es culpa de los mismos ciudadanos",        "pct": 7.0},
        ],
        "termometro": [
            {"opcion": "El partido MORENA",                          "valor": 41},
            {"opcion": "Los partidos de oposición (PRI/PAN/PRD/MC)", "valor": 33},
            {"opcion": "La Gobernadora Lorena Cuéllar",              "valor": 38},
            {"opcion": "La Policía Estatal y cuerpos de seguridad",  "valor": 31},
        ],
        "miedo": [
            {"opcion": "Asalto en calles, cajeros o transporte público", "pct": 40.0},
            {"opcion": "Extorsión o cobro de piso a familia o negocio",  "pct": 23.0},
            {"opcion": "Abusos de autoridad o corrupción policial",      "pct": 25.0},
            {"opcion": "Trata de personas o desaparición de mujeres",    "pct": 12.0},
        ],
        "fuente_info": [
            {"opcion": "Facebook",                   "pct": 42.0},
            {"opcion": "De boca en boca con vecinos", "pct": 18.0},
            {"opcion": "Radio local",                 "pct": 10.0},
            {"opcion": "Grupos de WhatsApp",          "pct": 18.0},
            {"opcion": "TikTok",                      "pct": 12.0},
        ],
        "cambio": [
            {"opcion": "Cambien de fondo", "pct": 35.0},
            {"opcion": "Cambien un poco",  "pct": 36.0},
            {"opcion": "Sigan igual",      "pct": 20.0},
            {"opcion": "No sabe",          "pct": 9.0},
        ],
    },
    "apizaco": {
        "atribucion": [
            {"opcion": "La Gobernadora (estatal)",                 "pct": 44.0},
            {"opcion": "Los partidos políticos en general",        "pct": 22.0},
            {"opcion": "El Presidente Municipal (local)",          "pct": 17.0},
            {"opcion": "La Presidenta de la República (federal)",  "pct": 10.0},
            {"opcion": "Es culpa de los mismos ciudadanos",        "pct": 7.0},
        ],
        "termometro": [
            {"opcion": "El partido MORENA",                          "valor": 32},
            {"opcion": "Los partidos de oposición (PRI/PAN/PRD/MC)", "valor": 30},
            {"opcion": "La Gobernadora Lorena Cuéllar",              "valor": 27},
            {"opcion": "La Policía Estatal y cuerpos de seguridad",  "valor": 25},
        ],
        "miedo": [
            {"opcion": "Asalto en calles, cajeros o transporte público", "pct": 38.0},
            {"opcion": "Extorsión o cobro de piso a familia o negocio",  "pct": 28.0},
            {"opcion": "Abusos de autoridad o corrupción policial",      "pct": 21.0},
            {"opcion": "Trata de personas o desaparición de mujeres",    "pct": 13.0},
        ],
        "fuente_info": [
            {"opcion": "Facebook",                   "pct": 40.0},
            {"opcion": "De boca en boca con vecinos", "pct": 22.0},
            {"opcion": "Radio local",                 "pct": 13.0},
            {"opcion": "Grupos de WhatsApp",          "pct": 15.0},
            {"opcion": "TikTok",                      "pct": 10.0},
        ],
        "cambio": [
            {"opcion": "Cambien de fondo", "pct": 42.0},
            {"opcion": "Cambien un poco",  "pct": 33.0},
            {"opcion": "Sigan igual",      "pct": 17.0},
            {"opcion": "No sabe",          "pct": 8.0},
        ],
    },
    "huamantla": {
        "atribucion": [
            {"opcion": "La Gobernadora (estatal)",                 "pct": 48.0},
            {"opcion": "Los partidos políticos en general",        "pct": 21.0},
            {"opcion": "El Presidente Municipal (local)",          "pct": 14.0},
            {"opcion": "La Presidenta de la República (federal)",  "pct": 10.0},
            {"opcion": "Es culpa de los mismos ciudadanos",        "pct": 7.0},
        ],
        "termometro": [
            {"opcion": "El partido MORENA",                          "valor": 43},
            {"opcion": "Los partidos de oposición (PRI/PAN/PRD/MC)", "valor": 26},
            {"opcion": "La Gobernadora Lorena Cuéllar",              "valor": 29},
            {"opcion": "La Policía Estatal y cuerpos de seguridad",  "valor": 27},
        ],
        "miedo": [
            {"opcion": "Asalto en calles, cajeros o transporte público", "pct": 18.0},
            {"opcion": "Extorsión o cobro de piso a familia o negocio",  "pct": 22.0},
            {"opcion": "Abusos de autoridad o corrupción policial",      "pct": 19.0},
            {"opcion": "Trata de personas o desaparición de mujeres",    "pct": 41.0},
        ],
        "fuente_info": [
            {"opcion": "Facebook",                   "pct": 31.0},
            {"opcion": "De boca en boca con vecinos", "pct": 33.0},
            {"opcion": "Radio local",                 "pct": 22.0},
            {"opcion": "Grupos de WhatsApp",          "pct": 10.0},
            {"opcion": "TikTok",                      "pct": 4.0},
        ],
        "cambio": [
            {"opcion": "Cambien de fondo", "pct": 34.0},
            {"opcion": "Cambien un poco",  "pct": 37.0},
            {"opcion": "Sigan igual",      "pct": 22.0},
            {"opcion": "No sabe",          "pct": 7.0},
        ],
    },
}


def get_reactivos_filtrados(mun_key):
    """Devuelve la lista REACTIVOS con los datos de cada reactivo
    reemplazados si existe un override para ese municipio."""
    delta = REACTIVOS_DELTA.get(mun_key, {})
    resultado = []
    for r in REACTIVOS:
        if r["id"] in delta:
            r = {**r, "datos": delta[r["id"]]}
        resultado.append(r)
    return resultado


def get_arquetipos_filtrados(mun_key):
    """Devuelve ARQUETIPOS con los pct_padron del municipio seleccionado."""
    pcts = ARQ_PCT_X_MUN.get(mun_key, ARQ_PCT_X_MUN["estatal"])
    resultado = {}
    for code, arq in ARQUETIPOS.items():
        resultado[code] = {**arq, "pct_padron": float(pcts.get(code, arq["pct_padron"]))}
    return resultado


# ════════════════════════════════════════════════════════════════════════════
# CSS
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

[data-testid="stSidebar"] { background-color: #5c0c18 !important; }
[data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span,
[data-testid="stSidebar"] div, [data-testid="stSidebar"] label { color: #f5e6e9 !important; }

.header-modulo {
    --accent: #c41230;
    background: #14181f;
    padding: 28px 32px 24px 32px; border-radius: 8px; margin-bottom: 18px;
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
    color: #eef1f0; font-size: 1.85rem; letter-spacing: -0.005em; margin: 0 0 6px 0; line-height: 1.05;
}
.header-modulo p  { color: #8b95a8; font-size: 0.92rem; margin: 0; max-width: 620px; line-height: 1.5; }
.header-modulo .hm-dots { position: absolute; right: 28px; top: 26px; display: flex; gap: 6px; }
.header-modulo .hm-dots span { width: 5px; height: 5px; border-radius: 50%; background: var(--accent); opacity: 0.55; }
.header-modulo .hm-dots span:first-child { opacity: 1; }

.tag { font-family: 'JetBrains Mono', monospace; display:inline-block; font-size:0.62rem; font-weight:700; padding:2px 8px;
       border-radius:3px; margin-right:5px; letter-spacing:0.05em; text-transform:uppercase; }
.tag.real { background:#dcfce7; color:#166534; }
.tag.demo { background:#fef3c7; color:#92400e; }
.tag.otra { background:#e0e7ff; color:#3730a3; }

.ejemplo-banner {
    background:#fff7ed; border:1px solid #fb923c; border-radius:10px;
    padding:10px 16px; margin-bottom:14px; font-size:0.82rem; color:#9a3412; font-weight:600;
}
.filtro-banner {
    background:#f0fdf4; border:1px solid #4ade80; border-radius:10px;
    padding:10px 16px; margin-bottom:6px; font-size:0.82rem; color:#166534; font-weight:600;
}

.insight-card {
    background:#ffffff; border:1px solid #e2e8f0; border-radius:12px;
    padding:16px 18px; margin-bottom:12px; height:100%;
}
.insight-card .i-head { font-size:0.92rem; font-weight:700; color:#1e293b; margin-bottom:6px; }
.insight-card .i-preg { font-size:0.78rem; color:#64748b; line-height:1.4; margin-bottom:10px;
                         font-style:italic; }
.insight-card .i-text { font-size:0.82rem; color:#475569; line-height:1.5; margin-top:8px;
                         border-top:1px solid #f1f5f9; padding-top:8px; }

.arq-card {
    background:#ffffff; border-radius:12px; padding:16px 18px;
    border-top:5px solid #ccc; box-shadow:0 1px 4px rgba(0,0,0,0.07); height:100%;
}
.arq-name { font-size:0.98rem; font-weight:700; color:#1e293b; margin-bottom:8px; }
.arq-meta { font-size:0.76rem; color:#94a3b8; margin-bottom:10px; }

/* Número grande + barra de progreso */
.arq-pct-wrap { margin-bottom:12px; }
.arq-pct-num {
    font-size:2.2rem; font-weight:800; line-height:1; display:block; margin-bottom:2px;
}
.arq-pct-label { font-size:0.74rem; color:#64748b; display:block; margin-bottom:6px; }
.arq-bar-bg {
    background:#f1f5f9; border-radius:6px; height:8px; width:100%; overflow:hidden;
}
.arq-bar-fill { height:100%; border-radius:6px; transition:width 0.3s ease; }
.arq-desc { font-size:0.82rem; color:#334155; line-height:1.55; margin-bottom:10px; }
.arq-frase { font-size:0.8rem; color:#7c2d92; font-style:italic; line-height:1.4;
             margin-top:8px; padding-top:8px; border-top:1px solid #f1f5f9; }
.arq-row  { display:flex; justify-content:space-between; font-size:0.78rem;
            padding:3px 0; border-bottom:1px solid #f1f5f9; }
.arq-row span:first-child { color:#64748b; }
.arq-row span:last-child  { font-weight:700; color:#1e293b; }
.arq-msg { font-size:0.78rem; color:#475569; margin-top:8px; line-height:1.4;
           border-top:1px solid #f1f5f9; padding-top:8px; }
.prio-badge { display:inline-block; font-size:0.68rem; font-weight:700; color:#fff;
              padding:2px 10px; border-radius:20px; margin-bottom:6px; }

.voz-card { background:#f8fafc; border-left:4px solid #a3142b; border-radius:0 10px 10px 0;
            padding:14px 16px; margin-bottom:10px; }
.voz-cita { font-size:0.85rem; color:#1e293b; line-height:1.5; }
.voz-fuente { font-size:0.72rem; color:#94a3b8; margin-top:6px; }
.narrativa-box { background:#fef3c7; border:1px solid #f59e0b; border-radius:10px;
                  padding:14px 16px; margin-top:10px; font-size:0.84rem; color:#78350f; line-height:1.5; }
.fb-card { background:#eff6ff; border:1px solid #bfdbfe; border-radius:12px; padding:18px 20px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-modulo">
    <div class="hm-dots"><span></span><span></span><span></span></div>
    <div class="hm-eyebrow">Módulo 01 · En operación</div>
    <h1>📊 Datos y Segmentación</h1>
    <p>Diagnóstico real + encuesta interna ágil + arquetipos del elector tlaxcalteca + termómetro de descontento y humor social</p>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# HELPERS — API
# ════════════════════════════════════════════════════════════════════════════

def get_anthropic_key():
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        return os.environ.get("ANTHROPIC_API_KEY")


def get_apify_token():
    try:
        return st.secrets["APIFY_API_TOKEN"]
    except Exception:
        return os.environ.get("APIFY_API_TOKEN")


def analizar_temas_con_claude(temas, fuentes):
    """
    Llamada REAL a la API de Claude con la herramienta web_search habilitada.
    Devuelve un dict con:
      - matriz: {tema: {fuente: score_descontento_0_100}}
      - ranking: [{"tema":..., "volumen":..., "descontento":...}]
      - voz_calle: {tema: [{"cita":..., "fuente":..., "narrativa_sugerida":...}]}
    Si falla, levanta la excepción para que la UI la maneje explícitamente.
    """
    api_key = get_anthropic_key()
    if not api_key:
        raise RuntimeError("Falta configurar ANTHROPIC_API_KEY en st.secrets.")

    system_prompt = (
        "Eres un analista de inteligencia política para una campaña a la gubernatura de "
        "Tlaxcala, México. Vas a usar búsqueda web para investigar la conversación pública "
        "y de prensa reciente sobre temas específicos en Tlaxcala.\n\n"
        "REGLAS DE DERECHOS DE AUTOR — sin excepciones:\n"
        "1. Nunca cites más de 15 palabras textuales de una misma fuente.\n"
        "2. Como máximo una cita corta por fuente; el resto, parafrasea con tus propias palabras.\n"
        "3. Si no encuentras información confiable sobre un tema, dilo explícitamente — nunca "
        "inventes datos, cifras o citas.\n\n"
        "FORMATO DE RESPUESTA — responde ÚNICAMENTE con un JSON válido, sin texto adicional, "
        "con esta forma exacta:\n"
        "{\n"
        '  "matriz": {"<tema>": {"<fuente>": <entero 0-100 de nivel de descontento>}},\n'
        '  "ranking": [{"tema": "<tema>", "volumen": <entero 0-100>, "descontento": <entero 0-100>}],\n'
        '  "voz_calle": {"<tema>": [{"cita": "<paráfrasis o cita corta>", "fuente": "<medio y fecha>", '
        '"narrativa_sugerida": "<respuesta de comunicación política sugerida, 1-2 frases>"}]}\n'
        "}\n"
        f"Los temas a evaluar son exactamente: {json.dumps(temas, ensure_ascii=False)}.\n"
        f"Los tipos de fuente (columnas de la matriz) son exactamente: {json.dumps(fuentes, ensure_ascii=False)}."
    )

    user_prompt = (
        "Investiga la conversación pública y de prensa más reciente en Tlaxcala sobre cada uno "
        "de los temas indicados. Para cada tema, evalúa el nivel de descontento ciudadano por "
        "tipo de fuente, dame un ranking por volumen de conversación y descontento promedio, y "
        "para cada tema incluye 1-2 citas reales de prensa (parafraseadas, con fuente) más una "
        "narrativa de respuesta política sugerida."
    )

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 8000,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
            "tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 4}],
        },
        timeout=180,
    )
    response.raise_for_status()
    data = response.json()

    stop_reason = data.get("stop_reason")
    texto = "".join(
        block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
    ).strip()
    texto = texto.replace("```json", "").replace("```", "").strip()

    if not texto:
        # No se generó ningún bloque de texto — casi siempre porque la respuesta se
        # truncó a media búsqueda (stop_reason == "max_tokens") antes de escribir el JSON.
        tipos = [b.get("type") for b in data.get("content", [])]
        raise RuntimeError(
            f"Claude no devolvió texto (stop_reason={stop_reason}, bloques recibidos={tipos}). "
            "Probablemente se quedó sin espacio de tokens investigando antes de redactar el "
            "JSON final — intenta de nuevo; si persiste, reduce el número de temas por corrida."
        )

    # Extracción tolerante: si el modelo agregó algo de texto alrededor del JSON,
    # nos quedamos solo con el primer '{' al último '}'.
    inicio, fin = texto.find("{"), texto.rfind("}")
    if inicio == -1 or fin == -1 or fin < inicio:
        raise RuntimeError(f"La respuesta no contenía un JSON reconocible: {texto[:300]!r}")
    texto_json = texto[inicio:fin + 1]

    try:
        return json.loads(texto_json)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"El JSON devuelto por Claude no se pudo parsear ({e}). "
            f"stop_reason={stop_reason}. Primeros 300 caracteres: {texto_json[:300]!r}"
        )


@st.cache_data(ttl=86400, show_spinner=False)
def analizar_temas_con_claude_cacheado(temas, fuentes, dia, forzar_contador):
    """
    Envoltura con caché de 24h sobre analizar_temas_con_claude.
    - `dia` y `forzar_contador` son parte de la llave de caché: cambia `dia` y
      expira solo (una vez al día); cambia `forzar_contador` (botón "Forzar
      nueva consulta") y se dispara una llamada real aunque sea el mismo día.
    - El timestamp se calcula DENTRO de la función, así que solo se actualiza
      cuando de verdad hubo una llamada nueva — en un cache hit se reutiliza
      el mismo timestamp guardado, nunca se finge "recién actualizado".
    """
    resultado = analizar_temas_con_claude(list(temas), list(fuentes))
    resultado["_fetched_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")
    return resultado


def analizar_facebook_con_apify(page_url):
    """
    Llamada REAL al actor oficial de Apify "apify/facebook-posts-scraper" vía el
    endpoint run-sync-get-dataset-items — una sola llamada HTTP, sin polling.
    Analiza únicamente posts de la página (no comentarios de terceros).

    Esquema verificado contra la documentación oficial de Apify (apify.com/apify/
    facebook-posts-scraper/input-schema): startUrls=[{"url": ...}], resultsLimit=int.
    El run síncrono puede tardar hasta 300s antes de expirar del lado de Apify.
    """
    token = get_apify_token()
    if not token:
        raise RuntimeError("Falta configurar APIFY_API_TOKEN en st.secrets.")

    url = f"https://api.apify.com/v2/acts/{APIFY_ACTOR_ID}/run-sync-get-dataset-items"
    payload = {
        "startUrls": [{"url": page_url}],
        "resultsLimit": 15,
    }
    try:
        resp = requests.post(url, params={"token": token}, json=payload, timeout=240)
    except requests.exceptions.Timeout:
        raise RuntimeError(
            "Apify no respondió a tiempo (más de 240s). El actor puede estar lento o "
            "bloqueado por Facebook en este momento — intenta de nuevo en unos minutos."
        )

    if not resp.ok:
        # Apify devuelve {"error": {"type": ..., "message": ...}} en fallos —
        # mostramos ese mensaje real en vez de solo el código HTTP.
        try:
            detalle = resp.json().get("error", {}).get("message", resp.text[:300])
        except Exception:
            detalle = resp.text[:300]
        raise RuntimeError(f"Apify respondió {resp.status_code}: {detalle}")

    posts = resp.json()
    if not isinstance(posts, list):
        raise RuntimeError("Formato de respuesta de Apify inesperado — verificar esquema del actor.")
    if not posts:
        raise RuntimeError(
            "Apify no devolvió posts. Verifica que la página sea pública y que la URL "
            f"sea correcta: {page_url}"
        )
    return posts


# ════════════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════════════

# ── Selector de municipio — filtra Tab 1 (encuesta interna) y Tab 2 (arquetipos) ──
st.markdown("---")
col_fil, col_nota = st.columns([1, 2], gap="medium")
with col_fil:
    mun_label = st.selectbox(
        "📍 Ver resultados por",
        options=list(MUNICIPIO_OPCIONES.keys()),
        index=0,
        key="m1_municipio",
        help="Filtra la encuesta interna y los arquetipos por territorio. "
             "La encuesta Enkoll es estatal y no cambia con este filtro.",
    )
mun_key = MUNICIPIO_OPCIONES[mun_label]
with col_nota:
    if mun_key == "estatal":
        st.markdown(
            '<div class="filtro-banner">🗺️ Mostrando promedio estatal — '
            'selecciona un municipio para ver cómo cambia el perfil del electorado.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="filtro-banner">📍 Encuesta interna y arquetipos filtrados para '
            f'<b>{mun_label.split(" ", 1)[1]}</b> — el perfil del electorado cambia de forma '
            f'real según el territorio.</div>',
            unsafe_allow_html=True,
        )

# Calcular los datos filtrados una sola vez para usarlos en Tab 1 y Tab 2
reactivos_filtrados  = get_reactivos_filtrados(mun_key)
arquetipos_filtrados = get_arquetipos_filtrados(mun_key)

tab1, tab2, tab3 = st.tabs([
    "📋 Diagnóstico de Opinión",
    "👥 Arquetipos del Elector",
    "🌡️ Termómetro de Descontento y Humor Social",
])

# ──────────────────────────────────────────────────────────────────────────
# TAB 1 — DIAGNÓSTICO DE OPINIÓN
# ──────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<span class="tag real">REAL</span> Enkoll / El Universal · '
                f'{ENKOLL_META["fecha"]} · N={ENKOLL_META["n"]:,} · <i>dato estatal, no varía por municipio</i>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2, gap="large")
    with col_a:
        df_voto = pd.DataFrame(ENKOLL_VOTO_GOBERNADOR)
        fig = go.Figure(go.Bar(
            x=df_voto["pct"], y=df_voto["partido"], orientation="h",
            marker_color=df_voto["color"], text=df_voto["pct"].astype(str) + "%",
            textposition="outside",
        ))
        fig.update_layout(
            title="Intención de voto directa para gobernador(a)",
            xaxis_title="%", yaxis=dict(autorange="reversed"),
            margin=dict(l=10, r=10, t=40, b=10), height=320,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        df_id = pd.DataFrame(ENKOLL_IDENTIDAD_PARTIDISTA)
        fig2 = go.Figure(go.Bar(
            x=df_id["pct"], y=df_id["partido"], orientation="h",
            marker_color=df_id["color"], text=df_id["pct"].astype(str) + "%",
            textposition="outside",
        ))
        fig2.update_layout(
            title="Identificación partidista",
            xaxis_title="%", yaxis=dict(autorange="reversed"),
            margin=dict(l=10, r=10, t=40, b=10), height=320,
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown(f"""
    <div class="insight-card" style="border-left:4px solid #3730a3;">
        <span class="tag otra">OTRA FUENTE</span>
        <div class="i-text" style="margin-top:8px;">{HALLAZGO_PERSONALISTA}</div>
    </div>
    """, unsafe_allow_html=True)

    st.caption(
        f"Metodología Enkoll/El Universal: {ENKOLL_META['metodo']} · "
        f"margen de error {ENKOLL_META['margen_error']} · confianza {ENKOLL_META['confianza']}."
    )

    st.markdown("---")
    st.markdown(
        '<span class="tag demo">DEMO</span> Encuesta interna — reactivos avanzados '
        '(diseñados para alimentar segmentación, no solo horse race)',
        unsafe_allow_html=True,
    )

    cols = st.columns(2, gap="medium")
    for i, r in enumerate(reactivos_filtrados):
        col = cols[i % 2]
        with col:
            if r["tipo"] == "termometro":
                df_t = pd.DataFrame(r["datos"])
                fig_t = go.Figure(go.Bar(
                    x=df_t["valor"], y=df_t["opcion"], orientation="h",
                    marker_color="#a3142b", text=df_t["valor"], textposition="outside",
                ))
                fig_t.update_layout(
                    xaxis=dict(range=[0, 100], title="0 = rechazo · 100 = calidez"),
                    yaxis=dict(autorange="reversed"),
                    margin=dict(l=10, r=10, t=10, b=10), height=220,
                )
            else:
                df_r = pd.DataFrame(r["datos"])
                fig_t = go.Figure(go.Bar(
                    x=df_r["pct"], y=df_r["opcion"], orientation="h",
                    marker_color="#a3142b", text=df_r["pct"].astype(str) + "%",
                    textposition="outside",
                ))
                fig_t.update_layout(
                    xaxis=dict(range=[0, max(df_r["pct"]) * 1.25], title="%"),
                    yaxis=dict(autorange="reversed"),
                    margin=dict(l=10, r=10, t=10, b=10), height=220,
                )

            st.markdown(f"""
            <div class="insight-card">
                <div class="i-head">{r['icono']} {r['titulo']}</div>
                <div class="i-preg">"{r['pregunta']}"</div>
            </div>
            """, unsafe_allow_html=True)
            st.plotly_chart(fig_t, use_container_width=True, key=f"reactivo_{r['id']}")
            st.markdown(f"""
            <div class="insight-card" style="margin-top:-12px;">
                <div class="i-text">💡 {r['insight']}</div>
            </div>
            """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# TAB 2 — ARQUETIPOS DEL ELECTOR
# ──────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown(
        '<span class="tag demo">DEMO</span> 8 arquetipos derivados de los reactivos avanzados, '
        'priorizados específicamente para la elección de gobernatura',
        unsafe_allow_html=True,
    )

    # Cuando hay filtro activo, el orden es por peso en ese municipio (más visible = más importante).
    # En "estatal" se mantiene el orden de prioridad estratégica.
    if mun_key == "estatal":
        arqs_ordenados = sorted(arquetipos_filtrados.items(), key=lambda kv: kv[1]["orden"])
    else:
        arqs_ordenados = sorted(
            arquetipos_filtrados.items(), key=lambda kv: kv[1]["pct_padron"], reverse=True
        )

    for fila_inicio in range(0, len(arqs_ordenados), 2):
        cols = st.columns(2, gap="medium")
        for j, (code, arq) in enumerate(arqs_ordenados[fila_inicio:fila_inicio + 2]):
            with cols[j]:
                pct = arq["pct_padron"]
                pct_max = max(a["pct_padron"] for a in arquetipos_filtrados.values())
                bar_w = int((pct / pct_max) * 100)
                badge_color = PRIORIDAD_COLOR.get(arq["prioridad"], "#64748b")
                filas_html = "".join(f"""
                    <div style="display:flex; justify-content:space-between; font-size:0.78rem;
                                padding:4px 0; border-bottom:1px solid #f1f5f9;">
                        <span style="color:#64748b;">{k}</span>
                        <span style="font-weight:700; color:#1e293b;">{v}</span>
                    </div>""" for k, v in [
                    ("Atribuye la falla a",   arq["atribucion"]),
                    ("Termómetro Morena",      f"{arq['term_morena']}/100"),
                    ("Termómetro oposición",   f"{arq['term_oposicion']}/100"),
                    ("Termómetro Gobernadora", f"{arq['term_gobernadora']}/100"),
                    ("Fricción burocrática",   f"{arq['pct_friccion']:.0f}%"),
                    ("Vector de miedo",        arq["vector_miedo"]),
                    ("Score autoritarismo",    f"{arq['autoritarismo']:.0f}/100"),
                ])
                st.html(f"""
                <div style="background:#ffffff; border-radius:12px; padding:18px 18px 14px;
                            border-top:5px solid {arq['color']};
                            box-shadow:0 1px 4px rgba(0,0,0,0.07); margin-bottom:4px;
                            font-family:'DM Sans',sans-serif;">

                    <span style="display:inline-block; font-size:0.68rem; font-weight:700;
                                 color:#fff; padding:2px 10px; border-radius:20px;
                                 margin-bottom:8px; background:{badge_color};">
                        Prioridad: {arq['prioridad']}
                    </span>

                    <div style="font-size:0.98rem; font-weight:700; color:#1e293b; margin-bottom:10px;">
                        {arq['nombre']}
                    </div>

                    <div style="margin-bottom:14px;">
                        <span style="font-size:2.4rem; font-weight:800; line-height:1;
                                     color:{arq['color']}; display:block; margin-bottom:2px;">
                            {pct:.0f}%
                        </span>
                        <span style="font-size:0.74rem; color:#64748b; display:block; margin-bottom:7px;">
                            del padrón estimado · predomina en {arq['municipio']}
                        </span>
                        <div style="background:#f1f5f9; border-radius:6px; height:8px;
                                    width:100%; overflow:hidden;">
                            <div style="height:100%; border-radius:6px; width:{bar_w}%;
                                        background:{arq['color']};"></div>
                        </div>
                    </div>

                    <div style="font-size:0.82rem; color:#334155; line-height:1.55; margin-bottom:12px;">
                        {arq['descripcion']}
                    </div>

                    {filas_html}

                    <div style="font-size:0.8rem; color:#7c2d92; font-style:italic;
                                line-height:1.4; margin-top:10px; padding-top:8px;
                                border-top:1px solid #f1f5f9;">
                        {arq['frase']}
                    </div>

                    <div style="font-size:0.78rem; color:#475569; margin-top:8px;
                                line-height:1.4; padding-top:8px; border-top:1px solid #f1f5f9;">
                        🎯 {arq['mensaje']}
                    </div>
                </div>
                """)

    st.markdown("---")
    suma = sum(a["pct_padron"] for a in arquetipos_filtrados.values())
    territorio = mun_label.split(" ", 1)[1] if mun_key != "estatal" else "el estado"
    st.caption(f"Los 8 arquetipos suman {suma:.0f}% del padrón estimado para {territorio}. "
               "La sección/municipio exacto de cada elector se refina en el Módulo 2 "
               "una vez integrado el shapefile oficial.")

# ──────────────────────────────────────────────────────────────────────────
# TAB 3 — TERMÓMETRO DE DESCONTENTO Y HUMOR SOCIAL
# ──────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown(
        '<span class="tag real">REAL — EN VIVO</span> Esta pestaña llama en vivo a la API de '
        'Claude con búsqueda web. No usa datos de respaldo: si la llamada falla, se muestra '
        'el error en vez de un dato simulado. Para controlar costo, el resultado se guarda '
        '24 horas — si lo necesitas más fresco, usa "Forzar nueva consulta".',
        unsafe_allow_html=True,
    )

    if "m1_forzar_contador" not in st.session_state:
        st.session_state["m1_forzar_contador"] = 0

    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn1:
        disparar_temas = st.button("🔄 Analizar temas en vivo", type="primary")
    with col_btn2:
        forzar_temas = st.button("⚡ Forzar nueva consulta (ignora caché de 24h)")
    with col_btn3:
        ver_ejemplo_temas = st.button("👁️ Ver ejemplo de diseño")

    if forzar_temas:
        st.session_state["m1_forzar_contador"] += 1
    if disparar_temas or forzar_temas:
        with st.spinner("Buscando y analizando conversación pública sobre Tlaxcala…"):
            try:
                hoy = datetime.now().strftime("%Y-%m-%d")
                resultado = analizar_temas_con_claude_cacheado(
                    tuple(TEMAS_DESCONTENTO), tuple(FUENTES_TIPO),
                    hoy, st.session_state["m1_forzar_contador"],
                )
                st.session_state["m1_resultado_temas"] = resultado
                st.session_state["m1_error_temas"] = None
                st.session_state["m1_modo_temas"] = "vivo"
            except Exception as e:
                st.session_state["m1_resultado_temas"] = None
                st.session_state["m1_error_temas"] = str(e)
                st.session_state["m1_modo_temas"] = "vivo"
    if ver_ejemplo_temas:
        st.session_state["m1_resultado_temas"] = EJEMPLO_RESULTADO_TEMAS
        st.session_state["m1_error_temas"] = None
        st.session_state["m1_modo_temas"] = "ejemplo"

    resultado = st.session_state.get("m1_resultado_temas")
    error = st.session_state.get("m1_error_temas")
    modo = st.session_state.get("m1_modo_temas")

    if error:
        st.error(f"⚠️ No se pudo actualizar en vivo: {error}\n\nReintenta con el botón de arriba.")
    elif resultado is None:
        st.info(
            "Presiona **Analizar temas en vivo** para correr el diagnóstico con datos reales, "
            "o **Ver ejemplo de diseño** para revisar cómo se ve sin necesitar las APIs configuradas.",
            icon="💡",
        )
    else:
        if modo == "ejemplo":
            st.markdown(
                '<div class="ejemplo-banner">👁️ Estás viendo un EJEMPLO ILUSTRATIVO para revisar '
                'el diseño — no proviene de una llamada en vivo y las citas no son reales.</div>',
                unsafe_allow_html=True,
            )
        elif modo == "vivo" and resultado.get("_fetched_at"):
            st.caption(
                f"🕒 Última actualización real: {resultado['_fetched_at']} "
                "(resultado vigente hasta 24h o hasta que uses 'Forzar nueva consulta')."
            )

        ranking = resultado.get("ranking", [])
        matriz = resultado.get("matriz", {})
        voz_calle = resultado.get("voz_calle", {})

        st.markdown("#### Ranking de temas — volumen y descontento promedio")
        if ranking:
            df_rank = pd.DataFrame(ranking).sort_values("descontento", ascending=False)
            fig_rank = go.Figure()
            fig_rank.add_trace(go.Bar(
                x=df_rank["tema"], y=df_rank["volumen"], name="Volumen de conversación",
                marker_color="#94a3b8",
            ))
            fig_rank.add_trace(go.Scatter(
                x=df_rank["tema"], y=df_rank["descontento"], name="Descontento promedio",
                mode="markers+lines", marker=dict(size=12, color="#a3142b"),
            ))
            fig_rank.update_layout(height=380, margin=dict(l=10, r=10, t=20, b=80))
            st.plotly_chart(fig_rank, use_container_width=True)

        st.markdown("#### Mapa de calor — tema × tipo de fuente")
        if matriz:
            df_matriz = pd.DataFrame(matriz).T.reindex(columns=FUENTES_TIPO)
            fig_heat = px.imshow(
                df_matriz, color_continuous_scale="Reds", aspect="auto",
                labels=dict(color="Descontento"),
            )
            fig_heat.update_layout(height=380, margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_heat, use_container_width=True)

        st.markdown("#### 🗣️ La Voz de la Calle")
        tema_sel = st.selectbox("Filtrar por tema", TEMAS_DESCONTENTO, key="m1_tema_voz")
        entradas = voz_calle.get(tema_sel, [])
        if not entradas:
            st.caption("No hay citas disponibles para este tema en esta corrida.")
        for entrada in entradas:
            st.markdown(f"""
            <div class="voz-card">
                <div class="voz-cita">"{entrada.get('cita', '')}"</div>
                <div class="voz-fuente">— {entrada.get('fuente', 'fuente no especificada')}</div>
            </div>
            <div class="narrativa-box">
                📣 <b>Narrativa de marketing político sugerida:</b><br>{entrada.get('narrativa_sugerida', '')}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        '<span class="tag real">REAL — EN VIVO</span> Prueba de valor: posts de una página de '
        'Facebook vía Apify (no comentarios de terceros)',
        unsafe_allow_html=True,
    )
    st.caption(
        "Analiza los posts públicos de la página de Facebook que indiques — útil para comparar "
        "medios locales, la página de la aspirante, o cuentas institucionales — para "
        "complementar el ranking de arriba con señal real de qué se está cubriendo esta semana."
    )

    if "m1_fb_url" not in st.session_state:
        st.session_state["m1_fb_url"] = FACEBOOK_PAGE_URL

    url_input = st.text_input(
        "📎 URL de la página de Facebook a analizar",
        value=st.session_state["m1_fb_url"],
        key="m1_fb_url_input",
        help="Solo páginas públicas (no perfiles personales ni grupos cerrados). "
             "Ej: https://www.facebook.com/elsoldetlaxcala",
    )

    col_fb1, col_fb2 = st.columns([1, 1])
    with col_fb1:
        if st.button("🔄 Actualizar Facebook en vivo"):
            url_limpia = url_input.strip()
            if not url_limpia.startswith("https://www.facebook.com/") and \
               not url_limpia.startswith("https://facebook.com/"):
                st.session_state["m1_fb_posts"] = None
                st.session_state["m1_fb_error"] = (
                    "La URL debe ser una página pública de Facebook, por ejemplo: "
                    "https://www.facebook.com/nombredepagina"
                )
                st.session_state["m1_fb_modo"] = "vivo"
            else:
                st.session_state["m1_fb_url"] = url_limpia
                with st.spinner(f"Consultando posts públicos de {url_limpia}…"):
                    try:
                        posts = analizar_facebook_con_apify(url_limpia)
                        st.session_state["m1_fb_posts"] = posts
                        st.session_state["m1_fb_error"] = None
                        st.session_state["m1_fb_modo"] = "vivo"
                    except Exception as e:
                        st.session_state["m1_fb_posts"] = None
                        st.session_state["m1_fb_error"] = str(e)
                        st.session_state["m1_fb_modo"] = "vivo"
    with col_fb2:
        if st.button("👁️ Ver ejemplo de diseño ", key="m1_fb_ejemplo"):
            st.session_state["m1_fb_posts"] = EJEMPLO_FB_POSTS
            st.session_state["m1_fb_error"] = None
            st.session_state["m1_fb_modo"] = "ejemplo"

    fb_posts = st.session_state.get("m1_fb_posts")
    fb_error = st.session_state.get("m1_fb_error")
    fb_modo = st.session_state.get("m1_fb_modo")

    if fb_error:
        st.error(
            f"⚠️ No se pudo actualizar Facebook en vivo: {fb_error}\n\n"
            "Si el error menciona el actor o el formato de entrada, verifica el `APIFY_ACTOR_ID` "
            "y el esquema de `startUrls` contra la consola de Apify — el actor exacto debe "
            "confirmarse antes de usarlo con el cliente."
        )
    elif fb_posts is None:
        st.caption(
            "Presiona **Actualizar Facebook en vivo** para correr la prueba de valor, o "
            "**Ver ejemplo de diseño** para revisar cómo se ve sin necesitar el token de Apify."
        )
    else:
        if fb_modo == "ejemplo":
            st.markdown(
                '<div class="ejemplo-banner">👁️ Estás viendo un EJEMPLO ILUSTRATIVO — estos posts '
                'no son reales, solo muestran cómo se vería el panel con datos en vivo.</div>',
                unsafe_allow_html=True,
            )


        reacciones = [p.get("likes") or p.get("reactionsCount") or p.get("reactions", 0) or 0 for p in fb_posts]
        comentarios = [p.get("comments") or p.get("commentsCount", 0) or 0 for p in fb_posts]

        c1, c2, c3 = st.columns(3)
        c1.metric("Posts analizados", len(fb_posts))
        c2.metric("Promedio de reacciones", f"{(sum(reacciones)/len(reacciones)):.0f}" if reacciones else "—")
        c3.metric("Promedio de comentarios", f"{(sum(comentarios)/len(comentarios)):.0f}" if comentarios else "—")

        if fb_posts:
            st.markdown(f"**Top {min(5, len(fb_posts))} posts por interacción**")
            orden = sorted(range(len(fb_posts)), key=lambda i: reacciones[i], reverse=True)
            for rank, idx in enumerate(orden[:5], start=1):
                p = fb_posts[idx]
                texto = (p.get("text") or p.get("message") or "(sin texto)")[:280]
                fecha = p.get("time") or p.get("date") or ""
                fecha_txt = f" · {fecha[:10]}" if fecha else ""
                st.markdown(f"""
                <div class="fb-card" style="margin-bottom:10px;">
                    <b>#{rank}{fecha_txt}</b><br>
                    <div style="margin-top:6px; font-size:0.88rem; color:#1e293b;">
                        {texto}
                    </div>
                    <div style="margin-top:8px; font-size:0.78rem; color:#64748b;">
                        {reacciones[idx]} reacciones · {comentarios[idx]} comentarios
                    </div>
                </div>
                """, unsafe_allow_html=True)

            if len(fb_posts) < 15 and fb_modo == "vivo":
                st.caption(
                    f"⚠️ Se pidieron hasta 15 posts y Apify devolvió {len(fb_posts)}. Esto puede "
                    "deberse a que la página tiene pocos posts recientes visibles sin login, o a "
                    "que el actor se detuvo antes de completar el límite — no es necesariamente "
                    "un error, pero si esperabas más, vale la pena revisar la corrida en la "
                    "consola de Apify."
                )