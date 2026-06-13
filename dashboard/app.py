import os
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
import shap
import streamlit as st
import plotly.graph_objects as go
import sys

# Ensure dashboard path is in sys.path for importing api_helper
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
import api_helper

# --- PAGE SETUP ---
st.set_page_config(page_title="Plataforma Predictiva Mundial 2026", page_icon="⚽", layout="wide")

# Custom CSS for modern premium styling (dark/light harmonious design)
st.markdown("""
<style>
    .main {
        background-color: #f7f9fc;
        font-family: 'Outfit', 'Inter', sans-serif;
    }
    .stAlert {
        border-radius: 10px;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .title-text {
        font-size: 36px;
        font-weight: 700;
        color: #1e3d59;
        text-align: center;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# Cache models and data loading
@st.cache_resource
def load_models():
    xgb_model = joblib.load("saved_models/xgb_advanced.joblib")
    lstm_model = tf.keras.models.load_model("saved_models/lstm_model.h5")
    feature_extractor = tf.keras.Model(inputs=lstm_model.inputs, outputs=lstm_model.get_layer('dense_layer').output)
    scaler = joblib.load("saved_models/scaler.joblib")
    return xgb_model, feature_extractor, scaler

@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/features_nlp.csv")
    df['date'] = pd.to_datetime(df['date'])
    return df

xgb_model, feature_extractor, scaler = load_models()
df = load_data()

# --- ADVERTENCIA OBLIGATORIA (Responsible Use) ---
st.warning(
    "⚠️ **Advertencia de Uso Responsable:** Las predicciones mostradas son estimaciones probabilísticas "
    "basadas en datos históricos y modelos de Inteligencia Artificial. No garantizan resultados reales "
    "y no deben interpretarse como recomendación de apuesta, inversión o decisión económica de ningún tipo."
)

st.markdown("<div class='title-text'>Plataforma Predictiva de Fútbol — Mundial 2026</div>", unsafe_allow_html=True)

# Get unique list of teams
equipos = sorted(list(set(df['home_team'].unique()) | set(df['away_team'].unique())))

# Selectors layout
col1, col2, col3 = st.columns([2, 1, 2])
with col1:
    st.markdown("### 🏠 Selección Local")
    equipo_local = st.selectbox("Selecciona equipo local", equipos, index=None, placeholder="Seleccione equipo local...")
with col2:
    st.markdown("<h3 style='text-align:center; margin-top:40px;'>VS</h3>", unsafe_allow_html=True)
with col3:
    st.markdown("### ✈️ Selección Visitante")
    equipo_visitante = st.selectbox("Selecciona equipo visitante", equipos, index=None, placeholder="Seleccione equipo visitante...")

# Options layout
st.sidebar.markdown("## ⚙️ Configuración del Partido")
is_neutral = st.sidebar.checkbox("¿Se juega en campo neutral?", value=False)
tournament_type = st.sidebar.selectbox("Tipo de Torneo", ["FIFA World Cup", "Friendly", "Otros Torneos"])
phase_type = st.sidebar.selectbox("Fase del Partido", ["Fase de Grupos", "Eliminatoria Directa (Knockout)"])

# Conectividad en Tiempo Real
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔌 Conectividad en Tiempo Real")
online_mode = st.sidebar.toggle("Modo Online (APIs en vivo)", value=False, help="Activa la búsqueda en tiempo real de noticias en Google News y lesiones en API-Football.")

api_key = ""
api_url = "https://v3.football.api-sports.io"
if online_mode:
    # Read default from env variable if exists
    default_key = os.environ.get("API_FOOTBALL_KEY", "")
    api_key = st.sidebar.text_input("API-Football Key", value=default_key, type="password", help="Tu API Key de www.api-football.com")
    api_url = st.sidebar.text_input("API-Football Base URL", value=api_url, help="URL base de la API-Football")

# Map UI settings to features
is_neutral_val = 1 if is_neutral else 0
tourn_weight_val = 3 if tournament_type == "FIFA World Cup" else (1 if tournament_type == "Friendly" else 5)
phase_encoded_val = 1 if phase_type == "Eliminatoria Directa (Knockout)" else 0

if equipo_local is None or equipo_visitante is None:
    st.info("💡 **Predicción del Partido:** Por favor, selecciona el equipo local y el equipo visitante en los selectores de arriba para ver la predicción y el análisis explicable del partido.")
elif equipo_local == equipo_visitante:
    st.error("Error: Las selecciones local y visitante no pueden ser la misma.")
else:
    # --- FEATURE ENGINEERING ON THE FLY ---
    
    # ELO ratings (last known in dataset)
    df_sorted = df.sort_values('date')
    
    # Get last known Elo for home team
    home_matches = df_sorted[(df_sorted['home_team'] == equipo_local) | (df_sorted['away_team'] == equipo_local)]
    if len(home_matches) > 0:
        last_match = home_matches.iloc[-1]
        elo_home = last_match['elo_home'] if last_match['home_team'] == equipo_local else last_match['elo_away']
    else:
        elo_home = 1500.0
        
    # Get last known Elo for away team
    away_matches = df_sorted[(df_sorted['home_team'] == equipo_visitante) | (df_sorted['away_team'] == equipo_visitante)]
    if len(away_matches) > 0:
        last_match = away_matches.iloc[-1]
        elo_away = last_match['elo_home'] if last_match['home_team'] == equipo_visitante else last_match['elo_away']
    else:
        elo_away = 1500.0
        
    elo_diff = elo_home - elo_away

    # Recent Form (windows of 5, 10, 20)
    # We retrieve the last matches of both teams to build the features
    def get_recent_matches_stats(team):
        matches = df_sorted[(df_sorted['home_team'] == team) | (df_sorted['away_team'] == team)].tail(20)
        outcomes = []
        goals_scored = 0
        goals_conceded = 0
        wins_10 = 0
        wins_20 = 0
        
        for idx, row in matches.iterrows():
            is_home = row['home_team'] == team
            res = row['result']
            
            # Outcome perspective
            if is_home:
                outcome = res # 2=win, 1=draw, 0=loss
                g_s = row['home_score']
                g_c = row['away_score']
            else:
                outcome = 2 - res
                g_s = row['away_score']
                g_c = row['home_score']
                
            outcomes.append(outcome)
            goals_scored += g_s
            goals_conceded += g_c
            
        # Extract windows
        o5 = outcomes[-5:] if len(outcomes) >= 5 else outcomes
        wins_5 = sum(1 for x in o5 if x == 2)
        draws_5 = sum(1 for x in o5 if x == 1)
        losses_5 = sum(1 for x in o5 if x == 0)
        
        o10 = outcomes[-10:] if len(outcomes) >= 10 else outcomes
        wins_10 = sum(1 for x in o10 if x == 2)
        
        wins_20 = sum(1 for x in outcomes if x == 2)
        
        # Format string for emojis
        emoji_map = {2: "✅", 1: "⬜", 0: "❌"}
        emoji_outcomes = [emoji_map[x] for x in outcomes[-5:]]
        
        return wins_5, draws_5, losses_5, goals_scored, goals_conceded, wins_10, wins_20, emoji_outcomes
        
    h_w5, h_d5, h_l5, h_gs, h_gc, h_w10, h_w20, home_emojis = get_recent_matches_stats(equipo_local)
    a_w5, a_d5, a_l5, a_gs, a_gc, a_w10, a_w20, away_emojis = get_recent_matches_stats(equipo_visitante)

    # H2H (last 10 direct matches)
    h2h_matches = df_sorted[((df_sorted['home_team'] == equipo_local) & (df_sorted['away_team'] == equipo_visitante)) |
                            ((df_sorted['home_team'] == equipo_visitante) & (df_sorted['away_team'] == equipo_local))].tail(10)
    
    h2h_w_home = 0
    h2h_d = 0
    h2h_w_away = 0
    h2h_g_home = 0
    h2h_g_away = 0
    
    for idx, row in h2h_matches.iterrows():
        is_home = row['home_team'] == equipo_local
        h_score = row['home_score']
        a_score = row['away_score']
        
        if is_home:
            h2h_g_home += h_score
            h2h_g_away += a_score
            if h_score > a_score: h2h_w_home += 1
            elif h_score == a_score: h2h_d += 1
            else: h2h_w_away += 1
        else:
            h2h_g_home += a_score
            h2h_g_away += h_score
            if a_score > h_score: h2h_w_home += 1
            elif a_score == h_score: h2h_d += 1
            else: h2h_w_away += 1
            
    n_h2h = len(h2h_matches)
    h2h_g_home_avg = h2h_g_home / n_h2h if n_h2h > 0 else 0.0
    h2h_g_away_avg = h2h_g_away / n_h2h if n_h2h > 0 else 0.0

    # NLP rolling values (last known or live from API)
    home_nlp_data = None
    away_nlp_data = None
    
    if online_mode:
        with st.spinner("Obteniendo noticias y lesiones en tiempo real de APIs..."):
            home_nlp_data = api_helper.get_live_nlp_features(equipo_local, api_key=api_key, api_url=api_url)
            sentiment_home = home_nlp_data['sentiment_score']
            injury_home = home_nlp_data['injury_flag']
            vol_home = home_nlp_data['news_volume']
            
            away_nlp_data = api_helper.get_live_nlp_features(equipo_visitante, api_key=api_key, api_url=api_url)
            sentiment_away = away_nlp_data['sentiment_score']
            injury_away = away_nlp_data['injury_flag']
            vol_away = away_nlp_data['news_volume']
    else:
        sentiment_home = df_sorted[df_sorted['home_team'] == equipo_local]['sentiment_score_home'].iloc[-1] if len(df_sorted[df_sorted['home_team'] == equipo_local]) > 0 else 0.0
        sentiment_away = df_sorted[df_sorted['home_team'] == equipo_visitante]['sentiment_score_away'].iloc[-1] if len(df_sorted[df_sorted['home_team'] == equipo_visitante]) > 0 else 0.0
        injury_home = int(df_sorted[df_sorted['home_team'] == equipo_local]['injury_flag_home'].iloc[-1] if len(df_sorted[df_sorted['home_team'] == equipo_local]) > 0 else 0)
        injury_away = int(df_sorted[df_sorted['home_team'] == equipo_visitante]['injury_flag_away'].iloc[-1] if len(df_sorted[df_sorted['home_team'] == equipo_visitante]) > 0 else 0)
        vol_home = int(df_sorted[df_sorted['home_team'] == equipo_local]['news_volume_home'].iloc[-1] if len(df_sorted[df_sorted['home_team'] == equipo_local]) > 0 else 0)
        vol_away = int(df_sorted[df_sorted['home_team'] == equipo_visitante]['news_volume_away'].iloc[-1] if len(df_sorted[df_sorted['home_team'] == equipo_visitante]) > 0 else 0)

    # --- LSTM Recurrent Sequence Embedding ---
    # Construct sequence of last 10 matches for each team
    def build_sequence(team):
        matches = df_sorted[(df_sorted['home_team'] == team) | (df_sorted['away_team'] == team)].tail(10)
        seq = []
        for idx, row in matches.iterrows():
            is_home = row['home_team'] == team
            res = row['result']
            outcome = res if is_home else (2 - res)
            g_s = row['home_score'] if is_home else row['away_score']
            g_c = row['away_score'] if is_home else row['home_score']
            opp_elo = row['elo_away'] if is_home else row['elo_home']
            es_loc = 1.0 if is_home else 0.0
            seq.append([float(outcome), float(g_s), float(g_c), float(opp_elo), es_loc, float(row['tournament_weight'])])
            
        n_feat = 6
        if len(seq) < 10:
            padding = [[0.0] * n_feat] * (10 - len(seq))
            seq_padded = padding + seq
        else:
            seq_padded = seq
        return np.array(seq_padded, dtype=np.float32)

    seq_h = build_sequence(equipo_local)
    seq_a = build_sequence(equipo_visitante)

    # Scale sequences using saved scaler
    seq_h_scaled = scaler.transform(seq_h).reshape(1, 10, 6)
    seq_a_scaled = scaler.transform(seq_a).reshape(1, 10, 6)

    # Predict 16-dimensional embedding using tensorflow
    emb = feature_extractor.predict([seq_h_scaled, seq_a_scaled])[0]

    # Combine all 47 features
    features = [
        elo_home, elo_away, elo_diff,
        h_w5, h_d5, h_l5, h_gs, h_gc, h_w10, h_w20,
        a_w5, a_d5, a_l5, a_gs, a_gc, a_w10, a_w20,
        h2h_w_home, h2h_d, h2h_w_away, h2h_g_home_avg, h2h_g_away_avg,
        is_neutral_val, tourn_weight_val, phase_encoded_val,
        sentiment_home, sentiment_away, injury_home, injury_away, vol_home, vol_away
    ] + list(emb)

    feature_cols = [
        'elo_home', 'elo_away', 'elo_diff',
        'home_wins_5', 'home_draws_5', 'home_losses_5', 'home_goals_scored_5', 'home_goals_conceded_5', 'home_wins_10', 'home_wins_20',
        'away_wins_5', 'away_draws_5', 'away_losses_5', 'away_goals_scored_5', 'away_goals_conceded_5', 'away_wins_10', 'away_wins_20',
        'h2h_home_wins', 'h2h_draws', 'h2h_away_wins', 'h2h_home_goals_avg', 'h2h_away_goals_avg',
        'is_neutral', 'tournament_weight', 'phase_encoded',
        'sentiment_score_home', 'sentiment_score_away', 'injury_flag_home', 'injury_flag_away', 'news_volume_home', 'news_volume_away'
    ] + [f'lstm_emb_{i}' for i in range(16)]

    X_input = pd.DataFrame([features], columns=feature_cols)

    # --- MODEL PREDICTION ---
    y_proba = xgb_model.predict_proba(X_input)[0]

    p_loss = y_proba[0] # Victoria visitante (0)
    p_draw = y_proba[1] # Empate (1)
    p_win = y_proba[2]  # Victoria local (2)

    # --- SECCIÓN 2: Probabilidades Predichas ---
    st.markdown("---")
    st.markdown("### 📊 Probabilidades Predichas")
    
    # Plot horizontal bar chart
    fig = go.Figure(go.Bar(
        x=[p_win, p_draw, p_loss],
        y=['Victoria Local', 'Empate', 'Victoria Visitante'],
        orientation='h',
        marker=dict(color=['#2b5c8f', '#a8dadc', '#e63946']),
        text=[f"{p_win*100:.1f}%", f"{p_draw*100:.1f}%", f"{p_loss*100:.1f}%"],
        textposition='auto'
    ))
    fig.update_layout(
        xaxis=dict(range=[0, 1], tickformat=".0%"),
        height=250,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- SECCIÓN 6: Nivel de Incertidumbre ---
    max_prob = max(y_proba)
    if max_prob < 0.45:
        st.info("ℹ️ **Nivel de Incertidumbre:** 🔴 **Alta Incertidumbre**. Ninguna de las opciones tiene una probabilidad dominante. El partido se perfila muy disputado.")
    elif max_prob < 0.60:
        st.info("ℹ️ **Nivel de Incertidumbre:** 🟡 **Incertidumbre Moderada**. El modelo muestra una ligera inclinación hacia una opción, pero con bajo margen estadístico.")
    else:
        st.info("ℹ️ **Nivel de Incertidumbre:** 🟢 **Señal Relativamente Clara (Aún Probabilística)**. El modelo detecta una tendencia sólida de cara al encuentro.")

    # Two column layout for SHAP & Recent Form
    col_l, col_r = st.columns(2)

    # --- SECCIÓN 3: Factores Clave (SHAP Top 5) ---
    with col_l:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("### 🔍 Factores Clave de la Predicción (SHAP)")
        
        # Compute local SHAP values for this match (targeting Class 2 - Victoria Local)
        explainer = shap.TreeExplainer(xgb_model)
        shap_val = explainer(X_input)
        
        # Get values for class 2
        local_shap = shap_val.values[0, :, 2]
        
        # Find top 5 absolute features
        top_indices = np.argsort(np.abs(local_shap))[-5:]
        top_features = [feature_cols[idx] for idx in top_indices]
        top_values = [local_shap[idx] for idx in top_indices]
        
        # Translate feature names for display
        trans_map = {
            'elo_home': 'ELO Local', 'elo_away': 'ELO Visitante', 'elo_diff': 'Diferencia ELO',
            'home_wins_5': 'Victorias Local (5p)', 'home_goals_scored_5': 'Goles Local (5p)',
            'away_wins_5': 'Victorias Vis. (5p)', 'away_goals_scored_5': 'Goles Vis. (5p)',
            'sentiment_score_home': 'Sentimiento Local', 'sentiment_score_away': 'Sentimiento Visitante',
            'is_neutral': 'Sede Neutral', 'tournament_weight': 'Peso Torneo', 'phase_encoded': 'Fase Eliminatoria',
            'h2h_home_wins': 'Victorias H2H Local', 'h2h_draws': 'Empates H2H'
        }
        translated_features = [trans_map.get(f, f) for f in top_features]
        
        # Plot Plotly bar chart
        fig_shap = go.Figure(go.Bar(
            x=top_values,
            y=translated_features,
            orientation='h',
            marker=dict(color=['#e63946' if x < 0 else '#2a9d8f' for x in top_values])
        ))
        fig_shap.update_layout(
            title="Variables con mayor impacto en el resultado",
            xaxis_title="Impacto SHAP (Dirección)",
            height=300,
            margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig_shap, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- SECCIÓN 4: Forma Reciente & NLP ---
    with col_r:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("### 📈 Forma Reciente e Indicadores")
        
        # ELO ratings indicators
        st.markdown(f"**ELO {equipo_local} (Local):** `{int(elo_home)}` | **ELO {equipo_visitante} (Visitante):** `{int(elo_away)}` (Dif: `{int(elo_diff)}`)")
        
        # Recent form emojis
        h_emojis_str = " ".join(home_emojis) if len(home_emojis) > 0 else "Sin datos"
        a_emojis_str = " ".join(away_emojis) if len(away_emojis) > 0 else "Sin datos"
        
        st.markdown(f"**Racha {equipo_local} (Local):** {h_emojis_str}")
        st.markdown(f"**Racha {equipo_visitante} (Visitante):** {a_emojis_str}")
        
        # H2H summary
        st.markdown(f"**Historial Directo (Últimos {n_h2h} enfrentamientos):**")
        st.markdown(f"• Victorias Local: `{h2h_w_home}` | Empates: `{h2h_d}` | Victorias Visitante: `{h2h_w_away}`")
        st.markdown(f"• Promedio Goles Local: `{h2h_g_home_avg:.2f}` | Promedio Goles Visitante: `{h2h_g_away_avg:.2f}`")
        
        # --- SECCIÓN 5: Señal NLP ---
        st.markdown("#### 📰 Señales NLP de la Prensa")
        
        sentiment_label_h = "Positivo" if sentiment_home > 0.2 else ("Negativo" if sentiment_home < -0.2 else "Neutro")
        sentiment_label_a = "Positivo" if sentiment_away > 0.2 else ("Negativo" if sentiment_away < -0.2 else "Neutro")
        
        injury_label_h = "🚨 Baja confirmada / Lesión" if injury_home == 1 else "✅ Plantel completo / Sin reportes"
        injury_label_a = "🚨 Baja confirmada / Lesión" if injury_away == 1 else "✅ Plantel completo / Sin reportes"
        
        st.markdown(f"**Prensa {equipo_local}:** Sentimiento `{sentiment_label_h}` (`{sentiment_home:.2f}`) | `{injury_label_h}` (Noticias: `{vol_home}`)")
        st.markdown(f"**Prensa {equipo_visitante}:** Sentimiento `{sentiment_label_a}` (`{sentiment_away:.2f}`) | `{injury_label_a}` (Noticias: `{vol_away}`)")
        
        # Premium live details if Online Mode is active
        if online_mode and home_nlp_data and away_nlp_data:
            st.markdown("---")
            st.markdown("##### 🔴 Detalle en Tiempo Real (APIs)")
            
            # Local Team News Expander
            with st.expander(f"📰 Noticias Recientes de {equipo_local}"):
                if home_nlp_data.get('headlines_with_links'):
                    for item in home_nlp_data['headlines_with_links']:
                        title = item['title']
                        link = item['link']
                        st.markdown(f"- [{title}]({link})")
                elif home_nlp_data.get('headlines'):
                    for hl in home_nlp_data['headlines']:
                        st.write(f"- {hl}")
                else:
                    st.info("No se encontraron noticias recientes en Google News.")
                    
            # Visitante Team News Expander
            with st.expander(f"📰 Noticias Recientes de {equipo_visitante}"):
                if away_nlp_data.get('headlines_with_links'):
                    for item in away_nlp_data['headlines_with_links']:
                        title = item['title']
                        link = item['link']
                        st.markdown(f"- [{title}]({link})")
                elif away_nlp_data.get('headlines'):
                    for hl in away_nlp_data['headlines']:
                        st.write(f"- {hl}")
                else:
                    st.info("No se encontraron noticias recientes en Google News.")
            
            # API-Football Injuries
            if api_key:
                col_inj_h, col_inj_a = st.columns(2)
                with col_inj_h:
                    st.write(f"🏥 **Lesiones Oficiales {equipo_local}:**")
                    if home_nlp_data.get('api_injuries'):
                        for inj in home_nlp_data['api_injuries']:
                            player_name = inj.get('player', {}).get('name', 'Jugador')
                            inj_type = inj.get('player', {}).get('type', 'Lesión / Baja')
                            st.write(f"- 🔴 **{player_name}**: {inj_type}")
                    else:
                        st.write("✅ Sin lesionados reportados con la API.")
                with col_inj_a:
                    st.write(f"🏥 **Lesiones Oficiales {equipo_visitante}:**")
                    if away_nlp_data.get('api_injuries'):
                        for inj in away_nlp_data['api_injuries']:
                            player_name = inj.get('player', {}).get('name', 'Jugador')
                            inj_type = inj.get('player', {}).get('type', 'Lesión / Baja')
                            st.write(f"- 🔴 **{player_name}**: {inj_type}")
                    else:
                        st.write("✅ Sin lesionados reportados con la API.")
                        
        st.markdown("</div>", unsafe_allow_html=True)
