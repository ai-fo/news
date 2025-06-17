import asyncio
import json
from datetime import datetime
from scraper import NewsletterScraper
from transcript_by_source import TranscriptBySource

async def main():
    scraper = NewsletterScraper()
    
    print("🚀 Démarrage du scraping des actualités IA...")
    articles = await scraper.scrape_all_sources()
    
    print(f"\n✅ {len(articles)} articles récupérés (après dédupplication)")
    
    # Rapport de statut
    status_report = scraper.get_status_report()
    print(f"\n📊 Rapport de statut:")
    print(f"   - Sources totales: {status_report['total_sources']}")
    print(f"   - Sources réussies: {status_report['successful']}")
    print(f"   - Sources échouées: {status_report['failed']}")
    print(f"   - Articles totaux (avant dédupplication): {status_report['total_articles']}")
    
    if status_report['failed'] > 0:
        print(f"\n❌ Sources en erreur:")
        for source, info in status_report['sources'].items():
            if info['status'] == 'failed':
                print(f"   - {source}: {info['error']}")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"data/raw_articles_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"📁 Articles sauvegardés dans {output_file}")
    
    # Sauvegarder le rapport de statut
    status_file = f"data/status_report_{timestamp}.json"
    with open(status_file, 'w', encoding='utf-8') as f:
        json.dump(status_report, f, ensure_ascii=False, indent=2)
    
    print(f"📊 Rapport de statut sauvegardé dans {status_file}")
    
    # Générer les transcripts par source
    print(f"\n📂 Génération des transcripts par source...")
    source_transcripts = TranscriptBySource()
    saved_files = source_transcripts.save_transcripts_by_source(articles)
    
    print(f"\n✅ Transcripts générés pour {len(saved_files)} sources")

if __name__ == "__main__":
    asyncio.run(main())