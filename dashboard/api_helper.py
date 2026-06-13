import os
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import requests
import spacy
from transformers import pipeline

# Global caches for lazy loading
_sentiment_analyzer = None
_spacy_nlp = None

def get_sentiment_analyzer():
    """Lazily load the HuggingFace sentiment analysis pipeline."""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        try:
            # Model matches TAREA 5 requirement: nlptown/bert-base-multilingual-uncased-sentiment
            _sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
        except Exception as e:
            print(f"Could not load HuggingFace pipeline: {e}. Falling back to rule-based lexicon analyzer.")
            _sentiment_analyzer = "fallback"
    return _sentiment_analyzer

def get_spacy_nlp():
    """Lazily load the SpaCy Spanish NLP model."""
    global _spacy_nlp
    if _spacy_nlp is None:
        try:
            _spacy_nlp = spacy.load("es_core_news_sm")
        except Exception:
            try:
                _spacy_nlp = spacy.load("en_core_web_sm")
            except Exception:
                try:
                    _spacy_nlp = spacy.blank("es")
                except Exception as e:
                    print(f"Could not initialize SpaCy: {e}")
                    _spacy_nlp = None
    return _spacy_nlp

def fetch_rss_headlines(team_name, max_results=10, return_links=False):
    """Fetch recent headlines for a team from Google News RSS feed."""
    query = f"{team_name} football team"
    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
        
        root = ET.fromstring(xml_data)
        headlines = []
        for item in root.findall('.//item')[:max_results]:
            title = item.find('title').text
            # Clean headline by stripping the source (e.g. "Headline - ESPN")
            if " - " in title:
                title = title.rsplit(" - ", 1)[0]
            link = item.find('link').text if item.find('link') is not None else ""
            if return_links:
                headlines.append({'title': title, 'link': link})
            else:
                headlines.append(title)
        return headlines
    except Exception as e:
        print(f"Error fetching RSS news for {team_name}: {e}")
        return []

def analyze_sentiment_lexical(text):
    """Rule-based fallback sentiment analysis if HuggingFace is unavailable."""
    text_lower = text.lower()
    
    # Spanish and English keywords for football sentiment
    pos_words = [
        'óptimas', 'confía', 'victoria', 'fortalece', 'regreso', 'normalidad', 
        'optimista', 'liderar', 'buen', 'excelente', 'great', 'win', 'fit', 
        'ready', 'back', 'return', 'strengthens', 'positive', 'optimistic', 
        'confirms', 'happy', 'superior', 'formidable'
    ]
    neg_words = [
        'molestias', 'lesión', 'baja', 'suspendido', 'preocupación', 'duda', 
        'lesionado', 'fiebre', 'enfermo', 'rendimiento', 'bajo', 'perderá', 
        'lesiones', 'sanción', 'derrota', 'injury', 'injured', 'out', 'miss', 
        'doubt', 'worry', 'concern', 'bad', 'suspend', 'red card', 'defeat', 'lost'
    ]
    
    pos_count = sum(1 for w in pos_words if w in text_lower)
    neg_count = sum(1 for w in neg_words if w in text_lower)
    
    if pos_count > neg_count:
        return 0.8
    elif neg_count > pos_count:
        return -0.8
    return 0.0

def get_api_football_injuries(team_name, api_key, api_url="https://v3.football.api-sports.io"):
    """Query www.api-football.com API for real-time sidelined or injured players."""
    if not api_key:
        return []
    
    headers = {
        'x-apisports-key': api_key
    }
    
    if "rapidapi" in api_url.lower():
        headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': 'api-football-v1.p.rapidapi.com'
        }
        
    try:
        # Step 1: Search for national team to get their API ID
        teams_url = f"{api_url.rstrip('/')}/teams"
        params = {'search': team_name}
        
        response = requests.get(teams_url, headers=headers, params=params, timeout=10)
        if response.status_code != 200:
            print(f"API-Football search error: {response.text}")
            return []
            
        data = response.json()
        teams = data.get('response', [])
        
        team_id = None
        # Prioritize matching national team
        for t in teams:
            team_info = t.get('team', {})
            # Match name and verify if national team
            if team_info.get('national') is True:
                team_id = team_info.get('id')
                break
                
        # Fallback to direct name match if national field is not set
        if not team_id:
            for t in teams:
                team_info = t.get('team', {})
                if team_info.get('name', '').lower() == team_name.lower():
                    team_id = team_info.get('id')
                    break
                    
        # Ultimate fallback to first result
        if not team_id and teams:
            team_id = teams[0].get('team', {}).get('id')
            
        if not team_id:
            print(f"Could not map team name '{team_name}' to API-Football team ID.")
            return []
            
        # Step 2: Fetch current injuries for this team ID
        import datetime
        current_year = datetime.date.today().year
        
        injuries_url = f"{api_url.rstrip('/')}/injuries"
        injuries_params = {
            'team': team_id,
            'season': current_year
        }
        
        response = requests.get(injuries_url, headers=headers, params=injuries_params, timeout=10)
        if response.status_code != 200:
            print(f"API-Football injuries error: {response.text}")
            return []
            
        injuries_data = response.json()
        return injuries_data.get('response', [])
        
    except Exception as e:
        print(f"Exception during API-Football request for {team_name}: {e}")
        return []

def get_live_nlp_features(team_name, api_key=None, api_url="https://v3.football.api-sports.io"):
    """
    Fetch and compile news headlines, sentiment, and injury flags for a team.
    
    Returns a dict with:
      - headlines: list of strings
      - sentiment_score: float in [-1.0, 1.0]
      - injury_flag: 0 or 1
      - news_volume: int
      - api_injuries: list of dicts (from API-Football)
    """
    # 1. Fetch live RSS news (fetching with links)
    headlines_with_links = fetch_rss_headlines(team_name, max_results=10, return_links=True)
    headlines = [item['title'] for item in headlines_with_links]
    
    # 2. Analyze headlines
    sentiment_scores = []
    injury_from_news = 0
    vol = len(headlines)
    
    classifier = get_sentiment_analyzer()
    
    for headline in headlines:
        # Sentiment extraction
        if classifier and classifier != "fallback":
            try:
                res = classifier(headline)[0]
                stars = int(res['label'][0])
                score = (stars - 3) / 2.0  # map 1-5 stars to [-1.0, 1.0]
            except Exception:
                score = analyze_sentiment_lexical(headline)
        else:
            score = analyze_sentiment_lexical(headline)
        sentiment_scores.append(score)
        
        # Check injury keywords in news
        headline_lower = headline.lower()
        injury_keywords = [
            'lesión', 'lesionado', 'baja', 'molestias', 'duda', 'suspendido', 
            'sanción', 'quirófano', 'fractura', 'desgarro', 'esguince',
            'injury', 'injured', 'sidelined', 'miss', 'out', 'surgery', 'sprain'
        ]
        if any(kw in headline_lower for kw in injury_keywords):
            injury_from_news = 1
            
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
    
    # 3. Query api-football.com if API Key is available
    injury_from_api = 0
    api_injuries_list = []
    if api_key:
        api_injuries_list = get_api_football_injuries(team_name, api_key, api_url)
        if len(api_injuries_list) > 0:
            injury_from_api = 1
            
    # Injury flag is active if reported in news OR confirmed in API
    injury_flag = max(injury_from_news, injury_from_api)
    
    return {
        'headlines': headlines,
        'headlines_with_links': headlines_with_links,
        'sentiment_score': avg_sentiment,
        'injury_flag': injury_flag,
        'news_volume': vol,
        'api_injuries': api_injuries_list
    }
