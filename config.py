"""Configuration pour le scraper de newsletter IA"""

# Sources qui nécessitent de récupérer le contenu complet depuis la page web
SOURCES_NEED_FULL_CONTENT = [
    "ActuIA",
    "MIT Tech Review AI", 
    "TechCrunch AI",
    "VentureBeat AI",
    "L'Usine Digitale IA",
    "AI Trends"
]

# Sources avec des restrictions d'accès (403 sur extraction)
RESTRICTED_SOURCES = ["AI Business"]

# Sources qui nécessitent une approche spéciale
SPECIAL_HANDLING_SOURCES = {
    "AI Business": {
        "use_rss_content": True,
        "note": "Source avec protection anti-scraping. Utilisation du contenu RSS uniquement."
    }
}

# Limite d'articles par source
ARTICLES_PER_SOURCE = 10

# Timeout pour les requêtes HTTP (en secondes)
REQUEST_TIMEOUT = 30

# User-Agent pour les requêtes
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Longueur minimale du contenu RSS avant d'essayer de récupérer depuis la page
MIN_CONTENT_LENGTH = 500

# Longueur maximale du contenu à stocker (sauf pour arXiv)
MAX_CONTENT_LENGTH = 5000

# Pas de limite pour arXiv - on veut le PDF complet
ARXIV_NO_LIMIT = True