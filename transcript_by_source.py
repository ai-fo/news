import os
import re
from datetime import datetime
from typing import List, Dict
from collections import defaultdict

class TranscriptBySource:
    def __init__(self, base_dir="transcripts"):
        self.base_dir = base_dir
        
    def sanitize_filename(self, name: str) -> str:
        """Nettoie un nom pour en faire un nom de fichier/dossier valide"""
        # Remplacer les caractères problématiques
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        name = re.sub(r'\s+', '_', name)
        name = re.sub(r'_+', '_', name)
        return name.strip('_')
    
    def create_source_directory(self, source_name: str) -> str:
        """Crée un dossier pour une source et retourne le chemin"""
        safe_name = self.sanitize_filename(source_name)
        source_dir = os.path.join(self.base_dir, safe_name)
        os.makedirs(source_dir, exist_ok=True)
        return source_dir
    
    def generate_article_transcript(self, article: Dict) -> str:
        """Génère le transcript pour un seul article"""
        transcript = []
        
        # Titre
        transcript.append(f"TITRE: {article.get('title', 'Sans titre')}")
        transcript.append("-" * 80)
        
        # Métadonnées
        if article.get('author'):
            transcript.append(f"AUTEUR: {article['author']}")
        
        if article.get('published'):
            transcript.append(f"PUBLIÉ: {article['published']}")
        
        transcript.append(f"LIEN: {article.get('link', 'N/A')}")
        
        if article.get('tags'):
            transcript.append(f"TAGS: {', '.join(article['tags'])}")
        
        transcript.append("")  # Ligne vide
        
        # Résumé
        if article.get('summary'):
            transcript.append("RÉSUMÉ:")
            transcript.append(article['summary'])
            transcript.append("")
        
        # Contenu principal
        if article.get('content'):
            transcript.append("CONTENU COMPLET:")
            transcript.append("-" * 40)
            # Formater le contenu en paragraphes
            content = article['content']
            # Diviser en paragraphes sur les doubles retours à la ligne
            paragraphs = re.split(r'\n\s*\n', content)
            for para in paragraphs:
                if para.strip():
                    # Wrapper les lignes longues
                    wrapped = self.wrap_text(para.strip(), 80)
                    transcript.append(wrapped)
                    transcript.append("")  # Ligne vide entre paragraphes
        elif article.get('summary'):
            # Si pas de contenu complet, utiliser le résumé étendu
            transcript.append("CONTENU:")
            transcript.append("(Contenu complet non disponible, résumé étendu affiché)")
        
        transcript.append("=" * 80)
        transcript.append("")  # Ligne vide finale
        
        return "\n".join(transcript)
    
    def wrap_text(self, text: str, width: int = 80) -> str:
        """Découpe le texte en lignes de largeur maximale"""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word)
            if current_length + word_length + len(current_line) <= width:
                current_line.append(word)
                current_length += word_length
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '\n'.join(lines)
    
    def generate_source_transcript(self, source_name: str, articles: List[Dict]) -> str:
        """Génère le transcript complet pour une source"""
        timestamp = datetime.now()
        
        header = []
        header.append("=" * 80)
        header.append(f"TRANSCRIPT - {source_name}")
        header.append(f"Date de génération: {timestamp.strftime('%d/%m/%Y %H:%M:%S')}")
        header.append(f"Nombre d'articles: {len(articles)}")
        header.append("=" * 80)
        header.append("")
        
        content = ["\n".join(header)]
        
        # Ajouter chaque article
        for i, article in enumerate(articles, 1):
            content.append(f"\n### ARTICLE {i}/{len(articles)} ###\n")
            content.append(self.generate_article_transcript(article))
        
        # Footer
        footer = []
        footer.append("\n" + "=" * 80)
        footer.append(f"FIN DU TRANSCRIPT - {source_name}")
        footer.append(f"Généré le {timestamp.strftime('%d/%m/%Y à %H:%M:%S')}")
        footer.append("=" * 80)
        
        content.append("\n".join(footer))
        
        return "\n".join(content)
    
    def save_transcripts_by_source(self, articles: List[Dict]) -> Dict[str, str]:
        """Sauvegarde les transcripts organisés par source"""
        # Grouper les articles par source
        articles_by_source = defaultdict(list)
        for article in articles:
            source = article.get('source', 'Unknown')
            articles_by_source[source].append(article)
        
        saved_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for source_name, source_articles in articles_by_source.items():
            # Créer le dossier de la source
            source_dir = self.create_source_directory(source_name)
            
            # Générer le transcript
            transcript = self.generate_source_transcript(source_name, source_articles)
            
            # Sauvegarder le fichier
            filename = f"transcript_{timestamp}.txt"
            filepath = os.path.join(source_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(transcript)
            
            saved_files[source_name] = filepath
            print(f"✅ {source_name}: {len(source_articles)} articles → {filepath}")
        
        # Créer aussi un fichier index
        self.create_index_file(saved_files, timestamp)
        
        return saved_files
    
    def create_index_file(self, saved_files: Dict[str, str], timestamp: str):
        """Crée un fichier index listant tous les transcripts générés"""
        index_path = os.path.join(self.base_dir, f"index_{timestamp}.txt")
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("INDEX DES TRANSCRIPTS\n")
            f.write(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            for source, filepath in sorted(saved_files.items()):
                f.write(f"Source: {source}\n")
                f.write(f"Fichier: {filepath}\n")
                f.write("-" * 40 + "\n")
            
            f.write(f"\nTotal: {len(saved_files)} sources\n")
        
        print(f"\n📇 Index créé: {index_path}")