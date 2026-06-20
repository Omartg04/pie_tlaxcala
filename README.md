# PIE Tlaxcala · Anabel Ávalos

Demo de la Plataforma de Inteligencia Electoral (PIE) para Anabel Ávalos, aspirante del PRI
a la gubernatura de Tlaxcala (proceso electoral 2027). Construido por Data & AI Inclusion
Technologies, adaptando la arquitectura del sistema PIE Zacatlán a un nuevo repositorio.

## Estado actual

- ✅ **Home** — narrativa completa, 4 módulos enlazados, pulso operativo y hallazgos (datos híbridos).
- ✅ **Módulo 1 · Datos y Segmentación** — completo: 3 pestañas (Diagnóstico de Opinión real+ficticio,
  8 Arquetipos del Elector, Termómetro de Descontento y Humor Social con llamadas reales en vivo).
- 🚧 **Módulo 2 · Mapa de Decisiones** — placeholder, pendiente de desarrollo y del shapefile oficial de secciones.
- 🚧 **Módulo 3 · Inducción y Detección** — placeholder, pendiente de desarrollo.
- 🚧 **Módulo 4 · Activación y Comunicación** — placeholder, pendiente de desarrollo.

Cada módulo se desarrolla en una conversación separada del proyecto. Al terminar una sesión,
descarga el repo actualizado; al abrir la siguiente, vuelve a subir `Home.py` (o el repo completo)
para que la nueva conversación parta del mismo estado — el entorno de archivos no persiste entre
conversaciones de Claude.

## Datos reales usados en el Home

- **Encuesta Enkoll / El Universal**, 1,233 entrevistas cara a cara, levantamiento 19–22 de marzo
  de 2026: Morena 47% vs. PRI 14% en intención de voto directa para gobernador(a).
- **Resultado oficial 2021**: Lorena Cuéllar (Morena) 305,468 votos vs. Anabell Ávalos (PRI) 232,548 votos.
- **Estructura territorial**: 15 distritos locales, 60 municipios. Piloto enfocado en 3 municipios:
  Tlaxcala capital, Apizaco y Huamantla.

Todo lo demás marcado como "DEMO" en el Pulso Operativo es ficticio, para fines de la presentación.

## Secrets necesarios

El Módulo 1 (Pestaña 3) hace llamadas reales en vivo. Configura en `.streamlit/secrets.toml`
(local) o en *Secrets* de Streamlit Cloud:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
APIFY_API_TOKEN = "apify_api_..."
```

**Nota sobre Apify**: el `APIFY_ACTOR_ID` y el esquema de `startUrls` en
`pages/1_M1_Datos_Segmentacion.py` siguen el patrón documentado de los actores
"Facebook Posts Scraper" sin login. No se pudo probar en vivo desde el entorno de
desarrollo (sin acceso a `apify.com`) — verifica el actor exacto y los nombres de
campo en tu consola de Apify antes de usarlo frente al cliente.

## Pendiente de insumos del cliente

- Shapefile/geojson oficial de secciones electorales de Tlaxcala (INE) — necesario para el Módulo 2.
- Confirmación de si se requiere censo ITER a nivel sección o basta con aproximaciones por municipio.
- Logo de Data & AI Inclusion Technologies y/o de la campaña, si se quiere en el header.

## Correr localmente

```bash
pip install -r requirements.txt
streamlit run Home.py
```

## Desplegar en Streamlit Cloud

1. Sube este repo a GitHub (nuevo, separado del proyecto Zacatlán).
2. En [share.streamlit.io](https://share.streamlit.io), conecta el repo y selecciona `Home.py` como archivo principal.
3. Si el Módulo 4 usa la API de Claude, agrega `ANTHROPIC_API_KEY` en *Secrets* de la app.

## Stack

Python 3.11+ · Streamlit · pandas · geopandas · Folium · Plotly · scikit-learn · scipy · prince · kmodes
LLM: Claude (modelo `claude-sonnet-4-6` o el más reciente disponible) vía `st.secrets["ANTHROPIC_API_KEY"]`.
