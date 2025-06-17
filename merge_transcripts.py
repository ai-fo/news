#!/usr/bin/env python3
"""Script pour fusionner tous les transcripts en un seul document"""

import os
import sys
from datetime import datetime
from collections import defaultdict
import re

class TranscriptMerger:
    def __init__(self, transcripts_dir="transcripts"):
        self.transcripts_dir = transcripts_dir
        
    def find_latest_transcripts(self):
        """Trouve les transcripts les plus récents pour chaque source"""
        source_files = defaultdict(list)
        
        # Parcourir tous les sous-dossiers
        for source_dir in os.listdir(self.transcripts_dir):
            source_path = os.path.join(self.transcripts_dir, source_dir)
            
            if os.path.isdir(source_path) and source_dir not in ['.', '..']:
                # Lister tous les fichiers transcript dans ce dossier
                for filename in os.listdir(source_path):
                    if filename.startswith("transcript_") and filename.endswith(".txt"):
                        filepath = os.path.join(source_path, filename)
                        # Extraire le timestamp du nom de fichier
                        match = re.search(r'transcript_(\d{8}_\d{6})\.txt', filename)
                        if match:
                            timestamp = match.group(1)
                            source_files[source_dir].append({
                                'path': filepath,
                                'timestamp': timestamp,
                                'mtime': os.path.getmtime(filepath)
                            })
        
        # Garder seulement le plus récent pour chaque source
        latest_files = {}
        for source, files in source_files.items():
            if files:
                # Trier par timestamp décroissant
                files.sort(key=lambda x: x['timestamp'], reverse=True)
                latest_files[source] = files[0]['path']
        
        return latest_files
    
    def merge_transcripts(self, transcript_files=None, output_file=None):
        """Fusionne tous les transcripts en un seul fichier"""
        if transcript_files is None:
            transcript_files = self.find_latest_transcripts()
        
        if not transcript_files:
            print("❌ Aucun transcript trouvé")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if output_file is None:
            output_file = os.path.join(self.transcripts_dir, f"merged_transcript_{timestamp}.txt")
        
        print(f"📄 Fusion de {len(transcript_files)} transcripts...")
        
        # Header du document fusionné
        merged_content = []
        merged_content.append("=" * 100)
        merged_content.append("TRANSCRIPT FUSIONNÉ - TOUTES SOURCES")
        merged_content.append(f"Date de fusion: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        merged_content.append(f"Nombre de sources: {len(transcript_files)}")
        merged_content.append("=" * 100)
        merged_content.append("")
        merged_content.append("SOURCES INCLUSES:")
        for source in sorted(transcript_files.keys()):
            merged_content.append(f"  - {source}")
        merged_content.append("")
        merged_content.append("=" * 100)
        merged_content.append("\n")
        
        # Statistiques globales
        total_articles = 0
        articles_by_source = {}
        
        # Fusionner chaque transcript
        for source in sorted(transcript_files.keys()):
            filepath = transcript_files[source]
            print(f"  ✓ Lecture de {source}...")
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Compter les articles
                article_count = len(re.findall(r'### ARTICLE \d+/\d+ ###', content))
                total_articles += article_count
                articles_by_source[source] = article_count
                
                # Ajouter un séparateur de source
                merged_content.append("\n" + "#" * 100)
                merged_content.append(f"### SOURCE: {source.upper()} ###")
                merged_content.append("#" * 100 + "\n")
                
                # Ajouter le contenu (sans le header/footer original)
                lines = content.split('\n')
                start_idx = 0
                end_idx = len(lines)
                
                # Trouver le début du contenu (après le header)
                for i, line in enumerate(lines):
                    if "### ARTICLE 1/" in line:
                        start_idx = i
                        break
                
                # Trouver la fin du contenu (avant le footer)
                for i in range(len(lines)-1, -1, -1):
                    if lines[i].startswith("FIN DU TRANSCRIPT"):
                        end_idx = i - 1
                        break
                
                # Ajouter le contenu
                merged_content.extend(lines[start_idx:end_idx])
                
            except Exception as e:
                print(f"  ✗ Erreur avec {source}: {str(e)}")
                continue
        
        # Footer avec statistiques
        merged_content.append("\n\n" + "=" * 100)
        merged_content.append("STATISTIQUES FINALES")
        merged_content.append("=" * 100)
        merged_content.append(f"Total d'articles: {total_articles}")
        merged_content.append(f"Sources traitées: {len(articles_by_source)}")
        merged_content.append("\nDétail par source:")
        for source in sorted(articles_by_source.keys()):
            merged_content.append(f"  - {source}: {articles_by_source[source]} articles")
        merged_content.append("")
        merged_content.append("=" * 100)
        merged_content.append(f"FIN DU TRANSCRIPT FUSIONNÉ")
        merged_content.append(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}")
        merged_content.append("=" * 100)
        
        # Écrire le fichier fusionné
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(merged_content))
        
        print(f"\n✅ Transcript fusionné créé: {output_file}")
        print(f"   - Total: {total_articles} articles de {len(articles_by_source)} sources")
        
        return output_file
    
    def merge_by_timestamp(self, timestamp_pattern):
        """Fusionne tous les transcripts correspondant à un timestamp"""
        transcript_files = {}
        
        for source_dir in os.listdir(self.transcripts_dir):
            source_path = os.path.join(self.transcripts_dir, source_dir)
            
            if os.path.isdir(source_path):
                for filename in os.listdir(source_path):
                    if timestamp_pattern in filename and filename.endswith(".txt"):
                        transcript_files[source_dir] = os.path.join(source_path, filename)
        
        if transcript_files:
            output_file = os.path.join(self.transcripts_dir, f"merged_{timestamp_pattern}.txt")
            return self.merge_transcripts(transcript_files, output_file)
        else:
            print(f"❌ Aucun transcript trouvé pour le timestamp: {timestamp_pattern}")
            return None

def main():
    merger = TranscriptMerger()
    
    if len(sys.argv) > 1:
        # Si un timestamp est fourni, fusionner les transcripts de ce timestamp
        timestamp = sys.argv[1]
        print(f"🔍 Fusion des transcripts du timestamp: {timestamp}")
        merger.merge_by_timestamp(timestamp)
    else:
        # Sinon, fusionner les derniers transcripts de chaque source
        print("🔍 Fusion des derniers transcripts de chaque source...")
        merger.merge_transcripts()

if __name__ == "__main__":
    main()