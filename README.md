# Plataforma Predictiva de Fútbol — Mundial 2026

Práctica Final de Inteligencia Artificial y Machine Learning — Universidad del Valle (Univalle) 2026.

Este proyecto consiste en el desarrollo de una plataforma predictiva de resultados de partidos de fútbol internacional enfocado en el Mundial 2026. El sistema combina técnicas de Machine Learning convencional, modelado temporal de secuencias (LSTM), análisis de sentimiento deportivo (NLP) y explicabilidad en IA (SHAP), culminando en una aplicación web interactiva desarrollada con Streamlit.

---

## Estructura del Repositorio

```
Trabajo_Prediccion_mundial/
├── data/
│   ├── raw/                        # Datos originales sin procesar (results.csv, etc.)
│   ├── processed/                  # Dataset unificado y particiones train/val/test
│   └── diccionario_datos.md        # Documentación de las columnas del dataset
├── notebooks/
│   ├── 01_etl.ipynb                # Limpieza, unificación y cálculo de ELO dinámico, racha e H2H
│   ├── 02_eda.ipynb                # Análisis exploratorio y partición temporal (Train/Val/Test)
│   ├── 03_modelo_baseline.ipynb    # Modelos base (Regresión Logística, Dummies, Árboles, etc.)
│   ├── 04_modelo_recurrente.ipynb  # Modelo recurrente LSTM de dos ramas en TensorFlow
│   ├── 05_nlp.ipynb                # Corpus de noticias y análisis de sentimiento con BERT y SpaCy
│   ├── 06_modelo_avanzado.ipynb    # XGBoost integrado con embeddings de LSTM y features NLP
│   └── 07_explicabilidad.ipynb     # Análisis de explicabilidad global y local con SHAP
├── saved_models/
│   ├── baseline_logreg.joblib      # Modelo de regresión logística entrenado
│   ├── lstm_model.h5               # Modelo LSTM guardado
│   ├── scaler.joblib               # StandardScaler para secuencias LSTM
│   └── xgb_advanced.joblib         # Clasificador XGBoost avanzado integrado
├── dashboard/
│   └── app.py                      # Código de la aplicación web Streamlit
├── docs/
│   ├── eda_plots/                  # Gráficos de distribuciones y correlaciones del EDA
│   ├── shap_plots/                 # Gráficos de atribuciones SHAP (globales y locales)
│   ├── modelo_negocio.md           # Propuesta comercial, monetización y riesgos éticos
│   └── uso_responsable.md          # Limitaciones éticas, privacidad y disclaimers
├── requirements.txt                # Librerías necesarias para ejecutar el proyecto
└── README.md                       # Instrucciones generales
```

---

## Fuentes de Datos Utilizadas

Los datos primarios fueron obtenidos de Kaggle e incluyen:
- **results.csv:** Historial de partidos internacionales masculinos de fútbol desde 1872 hasta la actualidad.
- **eloratings.csv:** Calificaciones y ratings históricos de selecciones nacionales de fútbol.
- **shootouts.csv:** Historial de definiciones por penaltis de partidos internacionales.
- **former_names.csv:** Mapeo histórico de los nombres anteriores y vigentes de las federaciones de fútbol.

---

## Instalación y Configuración del Entorno

1. Clone este repositorio:
   ```bash
   git clone https://github.com/Nat511/Trabajo_Prediccion_mundial.git
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

Para iniciar la interfaz interactiva web y realizar predicciones en tiempo real para cualquier par de selecciones con análisis de explicabilidad SHAP local:

```bash
streamlit run dashboard/app.py
```

La aplicación estará disponible de forma predeterminada en `http://localhost:8501`.
