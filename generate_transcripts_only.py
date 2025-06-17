#!/usr/bin/env python3
"""Script pour générer uniquement les transcripts à partir de données existantes"""

import json
import os
import sys
from datetime import datetime
from transcript_by_source import TranscriptBySource
from transcript_generator import TranscriptGenerator

def find_latest_data_file():
    """Trouve le fichier de données le plus récent"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        return None
    
    files = [f for f in os.listdir(data_dir) if f.startswith("raw_articles_") and f.endswith(".json")]
    if not files:
        return None
    
    # Trier par date de modification
    files.sort(key=lambda x: os.path.getmtime(os.path.join(data_dir, x)), reverse=True)
    return os.path.join(data_dir, files[0])

def main():
    # Trouver le fichier de données
    if len(sys.argv) > 1:
        data_file = sys.argv[1]
    else:
        data_file = find_latest_data_file()
    
    if not data_file or not os.path.exists(data_file):
        print("❌ Aucun fichier de données trouvé.")
        print("Usage: python generate_transcripts_only.py [fichier_json]")
        return
    
    print(f"📂 Chargement des données depuis: {data_file}")
    
    # Charger les articles
    with open(data_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    print(f"✅ {len(articles)} articles chargés")
    
    # Générer les transcripts par source
    print(f"\n📝 Génération des transcripts par source...")
    source_transcripts = TranscriptBySource()
    saved_files = source_transcripts.save_transcripts_by_source(articles)
    
    print(f"\n✅ Transcripts générés pour {len(saved_files)} sources")
    
    # Optionnel: générer aussi la newsletter globale
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    generator = TranscriptGenerator()
    transcript = generator.generate_transcript(articles)
    
    transcript_file = f"transcripts/newsletter_{timestamp}.md"
    with open(transcript_file, 'w', encoding='utf-8') as f:
        f.write(transcript)
    
    print(f"📄 Newsletter globale générée dans {transcript_file}")

if __name__ == "__main__":
    main()