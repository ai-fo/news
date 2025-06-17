from datetime import datetime
from typing import List, Dict
import re

class TranscriptGenerator:
    def __init__(self):
        self.categories = {
            "research": ["arXiv", "Papers With Code", "Google AI Blog", "OpenAI Blog", "ScienceDaily"],
            "news": ["MIT Tech Review", "TechCrunch", "VentureBeat", "AI Business", "AI Trends", "ActuIA", "L'Usine Digitale"],
            "tools": ["Product Hunt", "Futurepedia", "FutureTools", "There's An AI For That", "Hugging Face"],
            "community": ["Reddit", "GitHub Trending", "KDnuggets", "MarkTechPost", "AIhub"]
        }
    
    def categorize_articles(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        categorized = {
            "research": [],
            "news": [],
            "tools": [],
            "community": [],
            "other": []
        }
        
        for article in articles:
            source = article.get("source", "")
            placed = False
            
            for category, sources in self.categories.items():
                if any(s in source for s in sources):
                    categorized[category].append(article)
                    placed = True
                    break
            
            if not placed:
                categorized["other"].append(article)
        
        return categorized
    
    def clean_text(self, text: str) -> str:
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def generate_transcript(self, articles: List[Dict]) -> str:
        categorized = self.categorize_articles(articles)
        
        transcript = f"""# Newsletter IA - {datetime.now().strftime('%d %B %Y')}

## 📊 Résumé
- **Total d'articles**: {len(articles)}
- **Recherche**: {len(categorized['research'])} articles
- **Actualités**: {len(categorized['news'])} articles
- **Nouveaux outils**: {len(categorized['tools'])} articles
- **Communauté**: {len(categorized['community'])} articles

---

"""
        
        # Section Recherche
        if categorized['research']:
            transcript += "## 🔬 Recherche & Publications\n\n"
            for article in categorized['research'][:5]:  # Top 5
                transcript += f"### {article['title']}\n"
                transcript += f"**Source**: {article['source']}\n"
                transcript += f"**Lien**: {article['link']}\n"
                summary = self.clean_text(article.get('summary', article.get('content', '')))[:300]
                if summary:
                    transcript += f"**Résumé**: {summary}...\n"
                transcript += "\n---\n\n"
        
        # Section Actualités
        if categorized['news']:
            transcript += "## 📰 Actualités du secteur\n\n"
            for article in categorized['news'][:5]:
                transcript += f"### {article['title']}\n"
                transcript += f"**Source**: {article['source']}\n"
                transcript += f"**Lien**: {article['link']}\n"
                summary = self.clean_text(article.get('summary', article.get('content', '')))[:300]
                if summary:
                    transcript += f"**Résumé**: {summary}...\n"
                transcript += "\n---\n\n"
        
        # Section Outils
        if categorized['tools']:
            transcript += "## 🛠️ Nouveaux outils & Produits\n\n"
            for article in categorized['tools'][:5]:
                transcript += f"### {article['title']}\n"
                transcript += f"**Source**: {article['source']}\n"
                transcript += f"**Lien**: {article['link']}\n"
                summary = self.clean_text(article.get('summary', article.get('content', '')))[:200]
                if summary:
                    transcript += f"**Description**: {summary}...\n"
                transcript += "\n---\n\n"
        
        # Section Communauté
        if categorized['community']:
            transcript += "## 👥 Communauté & Open Source\n\n"
            for article in categorized['community'][:5]:
                transcript += f"### {article['title']}\n"
                transcript += f"**Source**: {article['source']}\n"
                transcript += f"**Lien**: {article['link']}\n"
                if article['source'] == "Reddit r/MachineLearning" and 'score' in article:
                    transcript += f"**Score**: {article['score']} points\n"
                summary = self.clean_text(article.get('summary', article.get('content', '')))[:200]
                if summary:
                    transcript += f"**Aperçu**: {summary}...\n"
                transcript += "\n---\n\n"
        
        transcript += f"\n\n---\n*Généré automatiquement le {datetime.now().strftime('%d/%m/%Y à %H:%M')}*"
        
        return transcript