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
                    
                    # Extraire le texte de TOUTES les pages
                    extracted_text = []
                    pages_to_extract = num_pages  # Extraire TOUT le PDF
                    
                    print(f"  ↳ Extraction de TOUTES les {pages_to_extract} pages...")
                    
                    for page_num in range(pages_to_extract):
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        if text:
                            extracted_text.append(text)
                        
                        # Afficher la progression pour les longs PDFs
                        if (page_num + 1) % 10 == 0:
                            print(f"    ... {page_num + 1}/{pages_to_extract} pages extraites")
                    
                    full_text = '\n\n'.join(extracted_text)
                    
                    # Nettoyer le texte
                    full_text = self.clean_pdf_text(full_text)
                    
                    # Pour arXiv, on veut le texte complet structuré
                    formatted_content = self.format_full_arxiv_content(full_text, num_pages, pages_to_extract)
                    
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
        
        # Supprimer les surrogates Unicode invalides
        text = text.encode('utf-8', 'ignore').decode('utf-8', 'ignore')
        
        # Remplacer les caractères mathématiques problématiques par des versions ASCII
        replacements = {
            '\ud835\udc00': 'A', '\ud835\udc01': 'B', '\ud835\udc02': 'C',
            '\ud835\udc03': 'D', '\ud835\udc04': 'E', '\ud835\udc05': 'F',
            '\ud835\udc06': 'G', '\ud835\udc07': 'H', '\ud835\udc08': 'I',
            '\ud835\udc09': 'J', '\ud835\udc0a': 'K', '\ud835\udc0b': 'L',
            '\ud835\udc0c': 'M', '\ud835\udc0d': 'N', '\ud835\udc0e': 'O',
            '\ud835\udc0f': 'P', '\ud835\udc10': 'Q', '\ud835\udc11': 'R',
            '\ud835\udc12': 'S', '\ud835\udc13': 'T', '\ud835\udc14': 'U',
            '\ud835\udc15': 'V', '\ud835\udc16': 'W', '\ud835\udc17': 'X',
            '\ud835\udc18': 'Y', '\ud835\udc19': 'Z',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Supprimer tout caractère surrogate restant
        text = re.sub(r'[\ud800-\udfff]', '', text)
        
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
    
    def format_full_arxiv_content(self, text: str, total_pages: int, extracted_pages: int) -> str:
        """Formate le contenu complet du PDF arXiv"""
        # PAS DE LIMITE - on veut TOUT le contenu
        
        content_parts = []
        content_parts.append("📄 CONTENU COMPLET DU PAPER ARXIV")
        content_parts.append(f"Pages totales extraites: {extracted_pages} pages")
        content_parts.append(f"Caractères totaux: {len(text)}")
        content_parts.append("=" * 80)
        content_parts.append("")
        content_parts.append(text)
        content_parts.append("")
        content_parts.append("=" * 80)
        content_parts.append("FIN DU PAPER - CONTENU INTÉGRAL EXTRAIT")
        
        return '\n'.join(content_parts)