import aiohttp
from bs4 import BeautifulSoup
import re
from typing import Optional

class ContentExtractor:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    async def extract_full_content(self, url: str, session: aiohttp.ClientSession) -> Optional[str]:
        """Extrait le contenu complet d'une page web"""
        try:
            async with session.get(url, headers=self.headers, timeout=30) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Supprimer les scripts et styles
                for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                    script.decompose()
                
                # Stratégies d'extraction selon le site
                content = None
                
                # Recherche des conteneurs communs d'articles
                article_selectors = [
                    'article',
                    'div[class*="article-content"]',
                    'div[class*="post-content"]',
                    'div[class*="entry-content"]',
                    'div[class*="content-body"]',
                    'main',
                    'div[role="main"]',
                    'div[class*="story-body"]',
                    # Sélecteurs spécifiques pour ActuIA et sites WordPress
                    'div.td-post-content',
                    'div.td_block_wrap',
                    'div.td-ss-main-content',
                    'div.wpb_wrapper',
                    'div.vc_column_container',
                    'div.entry',
                    'div.post-entry',
                    'div.single-post-content',
                    'div.post-inner',
                    'section.post-content'
                ]
                
                for selector in article_selectors:
                    element = soup.select_one(selector)
                    if element:
                        content = element.get_text(separator='\n', strip=True)
                        if len(content) > 200:  # Contenu suffisant
                            break
                
                # Si pas de contenu trouvé, essayer avec les paragraphes
                if not content or len(content) < 200:
                    paragraphs = soup.find_all('p')
                    if len(paragraphs) > 3:
                        content = '\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])
                
                # Nettoyer le texte
                if content:
                    content = re.sub(r'\n{3,}', '\n\n', content)
                    content = re.sub(r' {2,}', ' ', content)
                    return content[:5000]  # Limiter la taille
                
                return None
                
        except Exception as e:
            print(f"Erreur extraction {url}: {str(e)}")
            return None
    
    def clean_html(self, html_content: str) -> str:
        """Nettoie le contenu HTML et extrait le texte"""
        if not html_content:
            return ""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        
        # Nettoyer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        return text