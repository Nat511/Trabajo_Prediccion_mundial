# Anexo de Uso Responsable y Limitaciones Éticas

Este documento contiene la declaración de uso responsable, el descargo de responsabilidad, y el análisis detallado de limitaciones y sesgos del modelo de la Plataforma Predictiva Mundial 2026.

## 1. Descargo de Responsabilidad (Disclaimer)

> [!WARNING]
> Las predicciones son estimaciones probabilísticas basadas en datos históricos y modelos de Inteligencia Artificial. No garantizan resultados reales y no deben interpretarse como recomendación de apuesta, inversión o decisión económica de ningún tipo. El uso de los datos predictivos es responsabilidad exclusiva del usuario final.

## 2. Limitaciones del Modelo

La IA predice en base a variables estructuradas históricas, pero carece de la capacidad de modelar factores impredecibles del fútbol real:
- **Factores psicológicos o climáticos:** Cambios emocionales de los jugadores, el clima del estadio, o el estado del césped.
- **Decisiones arbitrales y VAR:** Penales polémicos, tarjetas rojas tempranas o goles anulados.
- **Eventos fortuitos durante el juego:** Lesiones imprevistas en los primeros minutos de juego, autogoles accidentales o balones al poste.
- **Táctica en tiempo real:** Ajustes que realiza el director técnico durante el desarrollo del partido.

## 3. Sesgos del Dataset y Mitigaciones

Nuestros análisis del EDA revelaron sesgos clave que los usuarios deben comprender:
- **Sesgo de Localía:** Los partidos muestran una tasa de victoria local superior al 45%. El modelo tiende a preferir la predicción de localía. Esto se mitiga en la interfaz web mostrando activamente el nivel de incertidumbre.
- **Sesgo de Representación Temporal:** Las selecciones con más de 100 años de historia futbolística (Inglaterra, Brasil, Argentina) tienen un volumen de partidos mucho mayor que las selecciones emergentes. El rating ELO de los equipos tradicionales es más estable y maduro, lo que puede infravalorar a equipos de ligas menos registradas históricamente.
- **Sesgo de Datos en NLP:** Las noticias de prensa se concentran casi en su totalidad en las grandes estrellas mundiales (ej. Messi, Mbappé, Ronaldo), de modo que los indicadores NLP son significativamente más ricos para selecciones grandes que para selecciones pequeñas.

## 4. Declaración de Privacidad de Datos

De acuerdo con las directrices de Inteligencia Artificial responsable:
- **No se procesan datos de carácter personal:** No se recolectan ni analizan nombres, identificadores, correos o ubicaciones de usuarios finales.
- **Límites de análisis de texto:** El procesamiento de noticias (NLP) se limita estrictamente a titulares de prensa pública deportiva sobre selecciones y jugadores de fútbol, garantizando el respeto a la privacidad individual.
