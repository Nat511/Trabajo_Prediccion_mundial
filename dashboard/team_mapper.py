import unicodedata

def normalize_team_name(team_name):
    """
    Normalizes team names to a standard format (lowercase, no accents, no abbreviations).
    E.g. "Argentina" -> "argentina", "U.S.A." -> "usa", "Arabia Saudita" -> "saudi arabia".
    """
    if not team_name:
        return ""
    # Lowercase & strip
    name = team_name.lower().strip()
    
    # Remove accents/diacritics (Unicode normalization)
    name = "".join(
        c for c in unicodedata.normalize('NFD', name)
        if unicodedata.category(c) != 'Mn'
    )
    
    # Clean punctuation and standardize spaces
    name = name.replace(".", "").replace("-", " ")
    
    # Common English/Spanish translations and aliases
    aliases = {
        "united states": "usa",
        "united states of america": "usa",
        "estados unidos": "usa",
        "saudi arabia": "saudi arabia",
        "arabia saudita": "saudi arabia",
        "paises bajos": "netherlands",
        "holanda": "netherlands",
        "netherlands": "netherlands",
        "belgica": "belgium",
        "espana": "spain",
        "corea del sur": "south korea",
        "korea republic": "south korea",
        "south korea": "south korea",
        "alemania": "germany",
        "japon": "japan",
        "croacia": "croatia",
        "brasil": "brazil",
        "portugues": "portugal",
        "francia": "france",
        "inglaterra": "england",
        "italia": "italy",
        "marruecos": "morocco",
        "senegal": "senegal",
        "uruguay": "uruguay",
        "canada": "canada",
        "ecuador": "ecuador"
    }
    return aliases.get(name, name)

# Mapping of normalized team names to IDs as specified in arquitectura.md
TEAM_MAPPING = {
    "argentina": {"transfermarkt_id": "9", "api_football_id": 26},
    "brazil": {"transfermarkt_id": "3439", "api_football_id": 6},
    "spain": {"transfermarkt_id": "3375", "api_football_id": 9},
    "france": {"transfermarkt_id": "3377", "api_football_id": 2},
    "germany": {"transfermarkt_id": "3262", "api_football_id": 25},
    "england": {"transfermarkt_id": "3299", "api_football_id": 10},
    "portugal": {"transfermarkt_id": "3300", "api_football_id": 27},
    "italy": {"transfermarkt_id": "3376", "api_football_id": 30},
    "mexico": {"transfermarkt_id": "6303", "api_football_id": 16},
    "usa": {"transfermarkt_id": "3505", "api_football_id": 12},
    "croatia": {"transfermarkt_id": "3556", "api_football_id": 3},
    "netherlands": {"transfermarkt_id": "3379", "api_football_id": 11},
    "belgium": {"transfermarkt_id": "3382", "api_football_id": 1},
    "uruguay": {"transfermarkt_id": "3449", "api_football_id": 7},
    "japan": {"transfermarkt_id": "3485", "api_football_id": 15},
    "senegal": {"transfermarkt_id": "3499", "api_football_id": 14},
    "morocco": {"transfermarkt_id": "3575", "api_football_id": 13},
    "saudi arabia": {"transfermarkt_id": "3503", "api_football_id": 24},
    "ecuador": {"transfermarkt_id": "3448", "api_football_id": 17},
    "canada": {"transfermarkt_id": "3504", "api_football_id": 18}
}

def get_team_ids(team_name):
    """
    Get Transfermarkt and API-Football IDs for a team name.
    Normalizes the name first, then queries the map.
    """
    norm = normalize_team_name(team_name)
    return TEAM_MAPPING.get(norm, {"transfermarkt_id": None, "api_football_id": None})
