import asyncio
import aiohttp
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
from typing import List, Dict, Optional
import re
from content_extractor import ContentExtractor
from pdf_extractor import PDFExtractor
from config import SOURCES_NEED_FULL_CONTENT, ARTICLES_PER_SOURCE, MIN_CONTENT_LENGTH

class NewsletterScraper:
    def __init__(self):
        self.source_status = {}
        self.content_extractor = ContentExtractor()
        self.pdf_extractor = PDFExtractor()
        self.rss_sources = {
            "ActuIA": "https://www.actuia.com/feed",
            "MIT Tech Review AI": "https://www.technologyreview.com/feed/",
            "TechCrunch AI": "https://techcrunch.com/tag/artificial-intelligence/feed/",
            "KDnuggets": "https://www.kdnuggets.com/feed",
            "MarkTechPost": "https://www.marktechpost.com/feed",
            "arXiv AI": "https://export.arxiv.org/rss/cs.AI",
            "arXiv ML": "https://export.arxiv.org/rss/cs.LG",
            "ScienceDaily AI": "https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml",
            "Google AI Blog": "https://ai.googleblog.com/feeds/posts/default",
            "OpenAI Blog": "https://openai.com/blog/rss/",
            "AIhub": "https://aihub.org/feed/",
            "Papers With Code": "https://paperswithcode.com/rss",
            "AI Trends": "https://www.aitrends.com/feed/",
            "AI Business": "https://aibusiness.com/rss.xml",
            "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
            "L'Usine Digitale IA": "https://www.usine-digitale.fr/themes/intelligence-artificielle/rss.xml"
        }
        
        self.web_sources = {
            "Product Hunt AI": "https://www.producthunt.com/topics/artificial-intelligence",
            "Futurepedia": "https://www.futurepedia.io/",
            "FutureTools": "https://www.futuretools.io/",
            "There's An AI For That": "https://theresanaiforthat.com/",
            "GitHub Trending": "https://github.com/trending?since=daily",
            "Reddit ML": "https://www.reddit.com/r/MachineLearning/.json",
            "Hugging Face": "https://huggingface.co/api/models"
        }
        
        self.articles = []
        
    async def fetch_rss(self, session: aiohttp.ClientSession, name: str, url: str, fetch_full_content: bool = True) -> List[Dict]:
        try:
            async with session.get(url, timeout=30) as response:
                content = await response.text()
                feed = feedparser.parse(content)
                
                articles = []
                for entry in feed.entries[:ARTICLES_PER_SOURCE]:
                    # Récupération du contenu depuis le RSS
                    rss_content = ""
                    
                    # Pour AI Business, essayer d'extraire plus de contenu du RSS
                    if name == "AI Business":
                        # Chercher dans tous les champs possibles
                        content_fields = []
                        
                        if entry.get("content"):
                            for content_item in entry.get("content", []):
                                if isinstance(content_item, dict) and content_item.get("value"):
                                    content_fields.append(content_item.get("value", ""))
                        
                        if entry.get("content_detail") and entry.get("content_detail", {}).get("value"):
                            content_fields.append(entry.get("content_detail", {}).get("value", ""))
                        
                        if entry.get("summary_detail") and entry.get("summary_detail", {}).get("value"):
                            content_fields.append(entry.get("summary_detail", {}).get("value", ""))
                        
                        if entry.get("description"):
                            content_fields.append(entry.get("description", ""))
                        
                        if entry.get("summary"):
                            content_fields.append(entry.get("summary", ""))
                        
                        # Prendre le contenu le plus long
                        if content_fields:
                            rss_content = max(content_fields, key=len)
                    else:
                        # Logique standard pour les autres sources
                        if entry.get("content"):
                            rss_content = entry.get("content", [{}])[0].get("value", "")
                        elif entry.get("content_detail"):
                            rss_content = entry.get("content_detail", {}).get("value", "")
                        elif entry.get("description"):
                            rss_content = entry.get("description", "")
                        
                        # Pour certains flux, le contenu peut être dans d'autres champs
                        if not rss_content and entry.get("summary_detail"):
                            rss_content = entry.get("summary_detail", {}).get("value", "")
                    
                    # Nettoyer le contenu HTML du RSS
                    if rss_content:
                        rss_content = self.content_extractor.clean_html(rss_content)
                    
                    # Pour ActuIA et autres sources avec contenu partiel, récupérer depuis la page
                    full_content = rss_content
                    
                    # Traitement spécial pour arXiv : extraire depuis le PDF
                    if name in ["arXiv AI", "arXiv ML"] and fetch_full_content:
                        article_url = entry.get("link")
                        if article_url:
                            try:
                                pdf_content = await self.pdf_extractor.extract_arxiv_content(article_url, session)
                                if pdf_content:
                                    full_content = pdf_content
                                    print(f"  ↳ Contenu PDF extrait pour: {entry.get('title', '')[:50]}...")
                            except Exception as e:
                                print(f"  ↳ Impossible d'extraire le PDF: {str(e)}")
                    
                    # Pour les autres sources nécessitant l'extraction web
                    elif fetch_full_content and name in SOURCES_NEED_FULL_CONTENT:
                        article_url = entry.get("link")
                        if article_url and (not rss_content or len(rss_content) < MIN_CONTENT_LENGTH):
                            try:
                                extracted_content = await self.content_extractor.extract_full_content(article_url, session)
                                if extracted_content and len(extracted_content) > len(rss_content):
                                    full_content = extracted_content
                                    print(f"  ↳ Contenu complet récupéré pour: {entry.get('title', '')[:50]}...")
                            except Exception as e:
                                print(f"  ↳ Impossible de récupérer le contenu complet: {str(e)}")
                    
                    article = {
                        "source": name,
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "published": entry.get("published", entry.get("updated", "")),
                        "summary": entry.get("summary", "")[:500] if entry.get("summary") else "",
                        "content": full_content,
                        "author": entry.get("author", entry.get("author_detail", {}).get("name", "")),
                        "tags": [tag.term for tag in entry.get("tags", [])] if entry.get("tags") else [],
                        "scraped_at": datetime.now().isoformat()
                    }
                    articles.append(article)
                
                print(f"✓ {name}: {len(articles)} articles")
                self.source_status[name] = {"status": "success", "count": len(articles), "error": None}
                return articles
                
        except Exception as e:
            print(f"✗ Erreur {name}: {str(e)}")
            self.source_status[name] = {"status": "failed", "count": 0, "error": str(e)}
            return []
    
    async def fetch_reddit(self, session: aiohttp.ClientSession) -> List[Dict]:
        try:
            headers = {"User-Agent": "AI Newsletter Bot 1.0"}
            async with session.get(self.web_sources["Reddit ML"], headers=headers, timeout=30) as response:
                data = await response.json()
                
                articles = []
                for post in data["data"]["children"][:10]:
                    post_data = post["data"]
                    if post_data.get("is_self", False):  # Text posts only
                        article = {
                            "source": "Reddit r/MachineLearning",
                            "title": post_data.get("title", ""),
                            "link": f"https://reddit.com{post_data.get('permalink', '')}",
                            "published": datetime.fromtimestamp(post_data.get("created_utc", 0)).isoformat(),
                            "summary": post_data.get("selftext", "")[:500],
                            "content": post_data.get("selftext", ""),
                            "score": post_data.get("score", 0),
                            "scraped_at": datetime.now().isoformat()
                        }
                        articles.append(article)
                
                print(f"✓ Reddit ML: {len(articles)} posts")
                self.source_status["Reddit ML"] = {"status": "success", "count": len(articles), "error": None}
                return articles
                
        except Exception as e:
            print(f"✗ Erreur Reddit: {str(e)}")
            self.source_status["Reddit ML"] = {"status": "failed", "count": 0, "error": str(e)}
            return []
    
    async def fetch_huggingface(self, session: aiohttp.ClientSession) -> List[Dict]:
        try:
            async with session.get(self.web_sources["Hugging Face"], timeout=30) as response:
                models = await response.json()
                
                articles = []
                for model in models[:10]:  # Top 10 models
                    model_id = model.get('modelId', '')
                    
                    # Récupérer le README du modèle
                    readme_content = await self.fetch_huggingface_readme(session, model_id)
                    
                    # Créer un résumé plus détaillé
                    summary_parts = []
                    if model.get('pipeline_tag'):
                        summary_parts.append(f"Type: {model.get('pipeline_tag')}")
                    if model.get('downloads'):
                        summary_parts.append(f"Downloads: {model.get('downloads'):,}")
                    if model.get('likes'):
                        summary_parts.append(f"Likes: {model.get('likes'):,}")
                    if model.get('library_name'):
                        summary_parts.append(f"Library: {model.get('library_name')}")
                    
                    # Construire le contenu complet
                    content_parts = []
                    
                    # Ajouter les informations de base
                    content_parts.append("=== INFORMATIONS DU MODÈLE ===")
                    content_parts.append(f"Pipeline: {model.get('pipeline_tag', 'Non spécifié')}")
                    content_parts.append(f"Bibliothèque: {model.get('library_name', 'Non spécifiée')}")
                    content_parts.append(f"Auteur: {model.get('author', 'Non spécifié')}")
                    content_parts.append(f"Dernière modification: {model.get('lastModified', 'Non spécifiée')}")
                    
                    # Ajouter les tags
                    if model.get('tags'):
                        content_parts.append(f"\nTags: {', '.join(model.get('tags', []))}")
                    
                    # Ajouter les données de la carte du modèle
                    if model.get('cardData'):
                        card_data = model.get('cardData', {})
                        if card_data.get('license'):
                            content_parts.append(f"Licence: {card_data.get('license')}")
                        if card_data.get('language'):
                            content_parts.append(f"Langues: {', '.join(card_data.get('language', []))}")
                    
                    # Ajouter le README si disponible
                    if readme_content:
                        content_parts.append("\n=== DESCRIPTION DU MODÈLE (README) ===")
                        content_parts.append(readme_content)
                    
                    article = {
                        "source": "Hugging Face Hub",
                        "title": f"Model: {model_id}",
                        "link": f"https://huggingface.co/{model_id}",
                        "published": model.get("lastModified", ""),
                        "summary": " | ".join(summary_parts),
                        "content": "\n".join(content_parts),
                        "tags": model.get("tags", []),
                        "scraped_at": datetime.now().isoformat()
                    }
                    articles.append(article)
                
                print(f"✓ Hugging Face: {len(articles)} models avec contenu complet")
                self.source_status["Hugging Face"] = {"status": "success", "count": len(articles), "error": None}
                return articles
                
        except Exception as e:
            print(f"✗ Erreur Hugging Face: {str(e)}")
            self.source_status["Hugging Face"] = {"status": "failed", "count": 0, "error": str(e)}
            return []
    
    async def fetch_huggingface_readme(self, session: aiohttp.ClientSession, model_id: str) -> str:
        """Récupère le README d'un modèle Hugging Face"""
        try:
            readme_url = f"https://huggingface.co/{model_id}/raw/main/README.md"
            async with session.get(readme_url, timeout=10) as response:
                if response.status == 200:
                    content = await response.text()
                    # Limiter la longueur du README
                    if len(content) > 5000:
                        content = content[:5000] + "\n\n[... README tronqué à 5000 caractères ...]"
                    return content
                else:
                    return ""
        except Exception as e:
            print(f"  ↳ Impossible de récupérer le README pour {model_id}: {str(e)}")
            return ""
    
    async def scrape_github_trending(self, session: aiohttp.ClientSession) -> List[Dict]:
        try:
            async with session.get(self.web_sources["GitHub Trending"], timeout=30) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                articles = []
                repos = soup.find_all('article', class_='Box-row')[:10]
                
                for repo in repos:
                    title_elem = repo.find('h2', class_='h3')
                    if title_elem:
                        repo_path = title_elem.find('a')['href']
                        title = repo_path.strip('/')
                        
                        description = repo.find('p', class_='col-9')
                        description_text = description.text.strip() if description else ""
                        
                        stars = repo.find('span', class_='d-inline-block float-sm-right')
                        stars_text = stars.text.strip() if stars else "0"
                        
                        article = {
                            "source": "GitHub Trending",
                            "title": title,
                            "link": f"https://github.com{repo_path}",
                            "published": datetime.now().isoformat(),
                            "summary": description_text,
                            "content": f"Stars today: {stars_text}",
                            "scraped_at": datetime.now().isoformat()
                        }
                        articles.append(article)
                
                print(f"✓ GitHub Trending: {len(articles)} repos")
                self.source_status["GitHub Trending"] = {"status": "success", "count": len(articles), "error": None}
                return articles
                
        except Exception as e:
            print(f"✗ Erreur GitHub: {str(e)}")
            self.source_status["GitHub Trending"] = {"status": "failed", "count": 0, "error": str(e)}
            return []
    
    async def scrape_all_sources(self) -> List[Dict]:
        async with aiohttp.ClientSession() as session:
            # RSS feeds
            rss_tasks = [
                self.fetch_rss(session, name, url) 
                for name, url in self.rss_sources.items()
            ]
            
            # Special sources
            special_tasks = [
                self.fetch_reddit(session),
                self.fetch_huggingface(session),
                self.scrape_github_trending(session)
            ]
            
            all_tasks = rss_tasks + special_tasks
            results = await asyncio.gather(*all_tasks, return_exceptions=True)
            
            all_articles = []
            for result in results:
                if isinstance(result, list):
                    all_articles.extend(result)
            
            # Dédupliquer par titre
            seen_titles = set()
            unique_articles = []
            for article in all_articles:
                if article["title"] not in seen_titles:
                    seen_titles.add(article["title"])
                    unique_articles.append(article)
            
            return unique_articles
    
    def get_status_report(self) -> Dict:
        total_sources = len(self.source_status)
        successful = sum(1 for s in self.source_status.values() if s["status"] == "success")
        failed = sum(1 for s in self.source_status.values() if s["status"] == "failed")
        total_articles = sum(s["count"] for s in self.source_status.values())
        
        return {
            "total_sources": total_sources,
            "successful": successful,
            "failed": failed,
            "total_articles": total_articles,
            "sources": self.source_status
        }