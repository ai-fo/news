import aiohttp
import asyncio
from io import BytesIO
import PyPDF2
from typing import Optional
import re

class PDFExtractor:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; AI Newsletter Bot/1.0; +https://github.com/ai-fo/news)"
        }
    
    async def extract_arxiv_content(self, arxiv_url: str, session: aiohttp.ClientSession) -> Optional[str]:
        """Extrait le contenu d'un paper arXiv depuis le PDF"""
        try:
            # Convertir l'URL abs en URL pdf
            pdf_url = arxiv_url.replace('/abs/', '/pdf/')
            if not pdf_url.endswith('.pdf'):
                pdf_url += '.pdf'
            
            print(f"  ↳ Téléchargement du PDF depuis: {pdf_url}")
            
            async with session.get(pdf_url, headers=self.headers, timeout=60) as response:
                if response.status != 200:
                    print(f"  ↳ Erreur téléchargement PDF: HTTP {response.status}")
                    return None
                
                # Lire le PDF en mémoire
                pdf_bytes = await response.read()
                pdf_file = BytesIO(pdf_bytes)
                
                # Extraire le texte du PDF
                try:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    
                    # Informations sur le PDF
                    num_pages = len(pdf_reader.pages)
                    print(f"  ↳ PDF chargé: {num_pages} pages")
                    
                    # Extraire le texte de plus de pages pour avoir plus de contenu
                    extracted_text = []
                    pages_to_extract = min(15, num_pages)  # Augmenter à 15 pages
                    
                    for page_num in range(pages_to_extract):
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        if text:
                            extracted_text.append(f"\n--- PAGE {page_num + 1} ---\n{text}")
                    
                    full_text = '\n'.join(extracted_text)
                    
                    # Nettoyer le texte
                    full_text = self.clean_pdf_text(full_text)
                    
                    # Extraire les sections principales
                    sections = self.extract_paper_sections(full_text)
                    
                    # Formater le contenu
                    formatted_content = self.format_arxiv_content(sections, num_pages)
                    
                    print(f"  ↳ Contenu extrait: {len(formatted_content)} caractères")
                    
                    return formatted_content
                    
                except Exception as e:
                    print(f"  ↳ Erreur lecture PDF: {str(e)}")
                    return None
                    
        except Exception as e:
            print(f"  ↳ Erreur extraction PDF arXiv: {str(e)}")
            return None
    
    def clean_pdf_text(self, text: str) -> str:
        """Nettoie le texte extrait du PDF"""
        # Supprimer les caractères de contrôle
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        # Remplacer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        # Corriger les mots coupés par des retours à la ligne
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        
        # Remplacer les retours à la ligne simples par des espaces
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
        
        return text.strip()
    
    def extract_paper_sections(self, text: str) -> dict:
        """Extrait les sections principales d'un paper"""
        sections = {
            'title': '',
            'authors': '',
            'abstract': '',
            'introduction': '',
            'methods': '',
            'results': '',
            'content_preview': ''
        }
        
        # Titre (généralement en première ligne ou avant Abstract)
        title_match = re.search(r'^(.+?)(?:\n|Abstract)', text, re.MULTILINE | re.DOTALL)
        if title_match:
            sections['title'] = title_match.group(1).strip()
        
        # Abstract
        abstract_match = re.search(r'Abstract[:\s]*(.+?)(?:1\.|Introduction|Keywords|CCS Concepts|$)', text, re.IGNORECASE | re.DOTALL)
        if abstract_match:
            sections['abstract'] = abstract_match.group(1).strip()[:1500]
        
        # Introduction
        intro_match = re.search(r'(?:1\.|1\s+)?Introduction[:\s]*(.+?)(?:2\.|Related Work|Background|Method|Approach|$)', text, re.IGNORECASE | re.DOTALL)
        if intro_match:
            sections['introduction'] = intro_match.group(1).strip()[:2000]
        
        # Méthodes/Approche
        method_match = re.search(r'(?:Method|Approach|Methodology|Proposed Method|Our Approach)[:\s]*(.+?)(?:Experiment|Result|Evaluation|$)', text, re.IGNORECASE | re.DOTALL)
        if method_match:
            sections['methods'] = method_match.group(1).strip()[:2000]
        
        # Résultats
        results_match = re.search(r'(?:Result|Experiment|Evaluation)[s]?[:\s]*(.+?)(?:Discussion|Conclusion|Related Work|$)', text, re.IGNORECASE | re.DOTALL)
        if results_match:
            sections['results'] = results_match.group(1).strip()[:2000]
        
        # Contenu général - prendre une grande portion du texte
        if len(text) > 5000:
            sections['content_preview'] = text[2000:8000]  # 6000 caractères de contenu
        
        return sections
    
    def format_arxiv_content(self, sections: dict, total_pages: int) -> str:
        """Formate le contenu extrait pour le transcript"""
        content_parts = []
        
        content_parts.append("📄 CONTENU DU PAPER ARXIV")
        content_parts.append(f"Pages extraites: 15 premières pages sur {total_pages} pages totales")
        content_parts.append("-" * 40)
        
        if sections['abstract']:
            content_parts.append("\nABSTRACT:")
            content_parts.append(sections['abstract'])
        
        if sections['introduction']:
            content_parts.append("\nINTRODUCTION:")
            content_parts.append(sections['introduction'])
        
        # Ajouter plus de contenu
        if sections.get('methods'):
            content_parts.append("\nMETHODOLOGIE:")
            content_parts.append(sections['methods'][:2000])
        
        if sections.get('results'):
            content_parts.append("\nRESULTATS:")
            content_parts.append(sections['results'][:2000])
        
        if sections['content_preview']:
            content_parts.append("\nCONTENU ADDITIONNEL:")
            content_parts.append(sections['content_preview'][:3000])
        
        content_parts.append("\n" + "-" * 40)
        content_parts.append("Note: Extraction des 15 premières pages du paper.")
        content_parts.append("Pour lire le paper complet, consultez le lien PDF ci-dessus.")
        
        return '\n'.join(content_parts)