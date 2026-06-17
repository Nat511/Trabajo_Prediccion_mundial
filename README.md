# Plataforma Predictiva de Fútbol — Mundial 2026

Práctica Final de Inteligencia Artificial y Machine Learning — Universidad Privada del Valle (Univalle) 2026.

Este proyecto consiste en el desarrollo de una plataforma predictiva de resultados de partidos de fútbol internacional enfocado en el Mundial 2026. El sistema combina técnicas de Machine Learning convencional, modelado temporal de secuencias (LSTM), análisis de sentimiento deportivo (NLP) y explicabilidad en IA (SHAP), culminando en una aplicación web interactiva desarrollada con Streamlit.

---

## Estructura del Repositorio

```
Trabajo_Prediccion_mundial/
├── data/
│   ├── raw/                        # Datos originales sin procesar (results.csv, eloratings.csv, etc.)
│   ├── processed/                  # Dataset unificado, limpio y particiones train/val/test, y features_nlp.csv
│   └── diccionario_datos.md        # Documentación de las columnas del dataset
├── notebooks/
│   ├── 01_etl.ipynb                # Limpieza, unificación y cálculo de ELO dinámico, racha e H2H
│   ├── 02_eda.ipynb                # Análisis exploratorio y partición temporal (Train/Val/Test)
│   ├── 03_modelo_baseline.ipynb    # Modelos base (Regresión Logística, Dummies, Árboles, etc.)
│   ├── 04_modelo_recurrente.ipynb  # Modelo recurrente LSTM de dos ramas en TensorFlow
│   ├── 05_nlp.ipynb                # Análisis de sentimiento con BERT y SpaCy (simulado offline)
│   ├── 06_modelo_avanzado.ipynb    # XGBoost integrado con embeddings de LSTM y features NLP
│   └── 07_explicabilidad.ipynb     # Análisis de explicabilidad global y local con SHAP
├── saved_models/
│   ├── baseline_logreg.joblib      # Modelo de regresión logística entrenado
│   ├── lstm_model.h5               # Modelo LSTM guardado
│   ├── scaler.joblib               # StandardScaler para secuencias LSTM
│   └── xgb_advanced.joblib         # Clasificador XGBoost avanzado integrado
├── dashboard/
│   ├── app.py                      # Código de la aplicación web Streamlit (visualización e inferencia)
│   ├── api_helper.py               # Integración con Google News (feedparser) y API-Football (lesiones)
│   └── team_mapper.py              # Mapeo y normalización de nombres e identificadores de selecciones
├── docs/
│   ├── eda_plots/                  # Gráficos de distribuciones y correlaciones del EDA
│   ├── shap_plots/                 # Gráficos de atribuciones SHAP (globales y locales)
│   ├── modelo_negocio.md           # Propuesta comercial, monetización y riesgos éticos
│   └── uso_responsable.md          # Limitaciones éticas, privacidad y disclaimers
├── arquitectura.md                 # Especificación de la arquitectura de datos e integración de features
├── requirements.txt                # Librerías necesarias para ejecutar el proyecto (incluye feedparser)
└── README.md                       # Instrucciones generales y descripción del proyecto
```

---

## Fuentes de Datos Utilizadas

Este proyecto se construyó a partir de datos recopilados y publicados por miembros de la comunidad de Kaggle, a quienes se reconoce el trabajo de recopilación y mantenimiento de estas bases de datos.

* **International Football Results from 1872 to 2017**, publicado por **Mart Jürisoo (martj42)** en Kaggle:
  https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017/data

  De este conjunto de datos se utilizaron los archivos:

  * `results.csv` Historial de partidos internacionales masculinos de fútbol desde 1872 hasta la actualidad.
  * `shootouts.csv` Historial de definiciones por penaltis de partidos internacionales.
  * `former_names.csv` Mapeo histórico de los nombres anteriores y vigentes de las federaciones de fútbol.

* **International Football Elo Ratings**, publicado por **Saif Alnimri (saifalnimri)** en Kaggle:
  https://www.kaggle.com/datasets/saifalnimri/international-football-elo-ratings

  De este conjunto de datos se utilizó:

  * `eloratings.csv` Calificaciones y ratings históricos de selecciones nacionales de fútbol.

Agradecemos a los autores por poner estos recursos a disposición libre, permitiendo la construcción y evaluación de este modelo predictivo.

Los datasets fueron posteriormente integrados, depurados y transformados mediante un proceso ETL propio para generar las variables utilizadas por los modelos de ML desarrollados en este proyecto.

---

## Instalación y Configuración del Entorno

1. Clone este repositorio:
   ```bash
   git clone https://github.com/Nat511/world-cup-prediction.git
   cd Trabajo_Prediccion_mundial
   ```

2. Se recomienda crear y activar un entorno virtual de Python:
   ```bash
   python -m venv .venv
   # En Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   # En macOS/Linux
   source .venv/bin/activate
   ```

3. Instale todas las dependencias requeridas:
   ```bash
   pip install -r requirements.txt
   ```

4. Descargue el modelo de idioma español para SpaCy:
   ```bash
   python -m spacy download es_core_news_sm
   ```

---

## Guía de Ejecución

Los notebooks de la carpeta `notebooks/` deben ejecutarse en **orden estricto**, ya que cada uno genera dependencias de datos y modelos para el siguiente:

1. **`01_etl.ipynb`:** Carga y limpia los datos, mapea los nombres de selecciones, y calcula secuencialmente el ELO dinámico, la racha reciente y el H2H. Genera `data/processed/matches_clean.csv`.
2. **`02_eda.ipynb`:** Realiza el análisis estadístico gráfico de localía, goles y correlaciones (guardando plots en `docs/eda_plots/`) y exporta las particiones temporales (`features_train.csv`, `features_val.csv`, `features_test.csv`).
3. **`03_modelo_baseline.ipynb`:** Entrena los clasificadores base y guarda la Regresión Logística de referencia en `saved_models/baseline_logreg.joblib`.
4. **`04_modelo_recurrente.ipynb`:** Construye secuencias de longitud 10 y entrena el modelo LSTM de dos ramas, guardando el modelo en `saved_models/lstm_model.h5`.
5. **`05_nlp.ipynb`:** Simula el volumen, entidades (SpaCy) y sentimiento (HuggingFace BERT) de las noticias y exporta `data/processed/features_nlp.csv`.
6. **`06_modelo_avanzado.ipynb`:** Extrae embeddings del LSTM y entrena el clasificador final XGBoost, guardándolo como `saved_models/xgb_advanced.joblib`.
7. **`07_explicabilidad.ipynb`:** Calcula contribuciones SHAP globales y locales en el set de prueba y guarda los diagramas waterfall y beeswarm en `docs/shap_plots/`.

---

## Ejecución del Dashboard (Streamlit)

Para iniciar la interfaz interactiva web y realizar predicciones en tiempo real para cualquier par de selecciones con análisis de explicabilidad SHAP local, asegúrese de tener activado su entorno virtual o ejecutarlo usando la ruta directa:

```bash
# Con entorno virtual activado:
streamlit run dashboard/app.py

# O bien directamente en Windows:
.venv\Scripts\streamlit.exe run dashboard/app.py
```

La aplicación estará disponible de forma predeterminada en `http://localhost:8501`.

### 🔌 Conectividad en Tiempo Real (Modo Online)
El dashboard integra un **Modo Online** para sustituir las simulaciones de NLP históricas con señales reales en vivo:
1. **Google News RSS Feed (Lector robusto con `feedparser`):** 
   - Realiza búsquedas de titulares deportivos con localización al español (`hl=es&gl=ES&ceid=ES:es`) para maximizar la relevancia en el contexto de fútbol.
   - Procesa en tiempo real los 10 titulares más recientes utilizando el modelo multilingual BERT (`nlptown/bert-base-multilingual-uncased-sentiment`) o un analizador léxico local como fallback.
   - Muestra las noticias en la sección interactiva del dashboard, y cada titular incluye un **enlace directo al artículo web original** para facilitar la verificación del usuario.
2. **API-Football (www.api-football.com):**
   - Resuelve el identificador de cada selección mediante el módulo de mapeo unificado `team_mapper.py` (con soporte para alias multilingües).
   - Realiza consultas en vivo al endpoint de lesiones (`/injuries`) utilizando la temporada actual de forma dinámica.
   - Si la información sobre lesiones para una selección nacional no está disponible en la API, el sistema ejecuta un mecanismo de contingencia para **detectar lesiones a partir de palabras clave en los titulares reales de Google News** (ej. *lesión, baja, molestias, duda*).
   - **Configuración:** Para habilitar este modo, active **"Modo Online (APIs en vivo)"** desde la barra lateral de Streamlit e introduzca su API Key, o bien defina la variable de entorno `API_FOOTBALL_KEY` antes de iniciar el servidor.

Al iniciar la aplicación, los selectores de selecciones se presentan vacíos por defecto, lo que mejora la experiencia de usuario y evita cargas innecesarias de modelos de explicabilidad en el arranque.
