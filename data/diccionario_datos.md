# Diccionario de Datos — matches_clean.csv

Este archivo describe la estructura y cada una de las columnas del dataset procesado final `data/processed/matches_clean.csv`, utilizado para entrenar los modelos predictivos de la plataforma.

## Columnas Básicas (Originales)

| Nombre de Columna | Tipo de Dato | Descripción |
|---|---|---|
| `date` | `YYYY-MM-DD` | Fecha en la que se disputó el encuentro. |
| `home_team` | Categoría (String) | Nombre de la selección nacional que jugó como local (normalizado). |
| `away_team` | Categoría (String) | Nombre de la selección nacional que jugó como visitante (normalizado). |
| `home_score` | Entero | Goles marcados por el equipo local. |
| `away_score` | Entero | Goles marcados por el equipo visitante. |
| `tournament` | Categoría (String) | Nombre de la competición (ej. FIFA World Cup, Friendly). |
| `city` | String | Ciudad donde se disputó el encuentro. |
| `country` | String | País donde se disputó el encuentro. |
| `neutral` | Booleano | Indica si el partido se jugó en terreno neutral (`True` o `False`). |

## Variables Objetivo (Target)

| Nombre de Columna | Tipo de Dato | Valores | Descripción |
|---|---|---|---|
| `result` | Entero | `0`, `1`, `2` | Resultado final desde la perspectiva local:<br>`0`: Victoria visitante (derrota local)<br>`1`: Empate<br>`2`: Victoria local |

## Variables de Fuerza ELO (Pre-Partido)

> [!NOTE]
> Estas variables se calculan cronológicamente antes del inicio del encuentro para evitar *data leakage*.

| Nombre de Columna | Tipo de Dato | Descripción |
|---|---|---|
| `elo_home` | Decimal (Float) | Puntuación ELO estimada del equipo local antes del partido (inicializada en 1500). |
| `elo_away` | Decimal (Float) | Puntuación ELO estimada del equipo visitante antes del partido (inicializada en 1500). |
| `elo_diff` | Decimal (Float) | Diferencia de puntuación ELO (`elo_home` - `elo_away`). |

## Variables de Forma Reciente (Pre-Partido)

> [!NOTE]
> Calculadas usando ventanas históricas de partidos disputados por cada equipo antes del partido actual.

| Nombre de Columna | Tipo de Dato | Descripción |
|---|---|---|
| `home_wins_5` | Entero | Número de victorias de la selección local en sus últimos 5 encuentros. |
| `home_draws_5` | Entero | Número de empates de la selección local en sus últimos 5 encuentros. |
| `home_losses_5` | Entero | Número de derrotas de la selección local en sus últimos 5 encuentros. |
| `home_goals_scored_5` | Entero | Goles anotados por la selección local en sus últimos 5 encuentros. |
| `home_goals_conceded_5` | Entero | Goles recibidos por la selección local en sus últimos 5 encuentros. |
| `home_wins_10` | Entero | Número de victorias de la selección local en sus últimos 10 encuentros. |
| `home_wins_20` | Entero | Número de victorias de la selección local en sus últimos 20 encuentros. |
| `away_wins_5` | Entero | Número de victorias de la selección visitante en sus últimos 5 encuentros. |
| `away_draws_5` | Entero | Número de empates de la selección visitante en sus últimos 5 encuentros. |
| `away_losses_5` | Entero | Número de derrotas de la selección visitante en sus últimos 5 encuentros. |
| `away_goals_scored_5` | Entero | Goles anotados por la selección visitante en sus últimos 5 encuentros. |
| `away_goals_conceded_5` | Entero | Goles recibidos por la selección visitante en sus últimos 5 encuentros. |
| `away_wins_10` | Entero | Número de victorias de la selección visitante en sus últimos 10 encuentros. |
| `away_wins_20` | Entero | Número de victorias de la selección visitante en sus últimos 20 encuentros. |

## Historial de Enfrentamientos Directos (H2H)

| Nombre de Columna | Tipo de Dato | Descripción |
|---|---|---|
| `h2h_home_wins` | Entero | Victorias de la selección local actual en los últimos 10 enfrentamientos directos directos contra el rival actual. |
| `h2h_draws` | Entero | Empates entre ambas selecciones en los últimos 10 enfrentamientos directos. |
| `h2h_away_wins` | Entero | Victorias de la selección visitante actual en los últimos 10 enfrentamientos directos contra el rival actual. |
| `h2h_home_goals_avg` | Decimal (Float) | Promedio de goles anotados por el local actual contra el visitante actual en sus últimos 10 partidos directos. |
| `h2h_away_goals_avg` | Decimal (Float) | Promedio de goles anotados por el visitante actual contra el local actual en sus últimos 10 partidos directos. |

## Variables de Contexto

| Nombre de Columna | Tipo de Dato | Valores | Descripción |
|---|---|---|---|
| `is_neutral` | Entero | `0`, `1` | `1` si el partido es en sede neutral; `0` en caso contrario. |
| `tournament_weight` | Entero | `1`, `3`, `5` | Peso del torneo según la importancia deportiva:<br>`1`: Amistoso (Friendly)<br>`3`: Copa del Mundo (FIFA World Cup)<br>`5`: Resto de competiciones |
| `phase_encoded` | Entero | `0`, `1` | Tipo de fase del torneo:<br>`0`: Fase de grupos / Regular<br>`1`: Eliminatoria directa (Knockout) / Con definición por penales (si aplica) |
