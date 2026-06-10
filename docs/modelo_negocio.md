# Modelo de Negocio — Plataforma Predictiva Mundial 2026

Este documento describe la propuesta comercial, el análisis de clientes, las fuentes de ingresos y los riesgos éticos asociados a la Plataforma Predictiva de Fútbol Mundial 2026.

## 1. Propuesta de Valor

La plataforma se diferencia de las herramientas convencionales de predicción y las casas de apuestas a través de tres pilares tecnológicos:
- **Explicabilidad en IA (XAI):** Permite a los usuarios visualizar exactamente qué variables (ELO, racha, H2H, noticias) influyen en las probabilidades calculadas por partido mediante atribuciones locales SHAP.
- **Modelado Recurrente (LSTM):** Analiza la dinámica secuencial y temporal de las rachas de los equipos en lugar de simplemente resumirlas en promedios planos.
- **Fusión Contextual de Prensa (NLP):** Incorpora el sentimiento de las noticias deportivas y las bajas de último minuto en tiempo real.

## 2. Segmentos de Clientes y Oferta

| Segmento de Cliente | Necesidad Clave | Oferta de la Plataforma |
|---|---|---|
| **Medios de Comunicación y Periodistas** | Redacción rápida y con rigor analítico de las previas de partidos del Mundial. | Suscripción B2B con reportes automatizados de previas de partidos y gráficos de atribución de factores SHAP exportables. |
| **Aficionados Premium y Analistas** | Datos profundos, explicaciones lógicas y análisis libre de sesgos emocionales. | Plan freemium con acceso al dashboard interactivo para el Mundial 2026. |
| **Instituciones Educativas e Investigadores** | Casos de estudio prácticos sobre IA y Machine Learning aplicado al deporte. | Licencias educativas con acceso a los datasets procesados y códigos de los notebooks. |

## 3. Fuentes de Ingresos

1. **Suscripción B2B (Medios Deportivos):** Acceso corporativo a la API predictiva y a la descarga de reportes automáticos en PDF para complementar la cobertura periodística de las previas.
2. **Modelo Freemium (Usuarios Finales):** Acceso básico gratuito a predicciones del día. Suscripción premium de pago para habilitar la simulación personalizada de cualquier partido y visualización del SHAP local.
3. **Licencias Educativas:** Venta de material académico y licencias de laboratorio de ciencia de datos aplicada.

## 4. Riesgos Éticos y Mitigación

- **Incentivo y adicción a las apuestas:** La plataforma no ofrece apuestas y muestra una **advertencia obligatoria explícita** al inicio de cada vista. Además, se recalca de forma activa la incertidumbre intrínseca de los pronósticos.
- **Sesgo de predicción:** Documentado en la sección de análisis exploratorio para garantizar transparencia.
- **Confianza excesiva en la IA:** El indicador de incertidumbre dinámica alerta al usuario cuando las señales históricas son débiles o contradictorias.
