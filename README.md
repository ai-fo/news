# AI Newsletter Scraper

Un système automatisé pour collecter et organiser les dernières actualités en Intelligence Artificielle depuis diverses sources francophones et anglophones.

## 🚀 Fonctionnalités

- **Scraping multi-sources** : Collecte automatique depuis 19+ sources RSS et API
- **Récupération de contenu complet** : Extraction intelligente du contenu complet pour les sources avec RSS tronqués
- **Extraction PDF arXiv** : Récupération automatique du contenu des papers arXiv depuis les PDFs
- **Organisation par source** : Génération de transcripts individuels par source
- **Rapport de statut** : Suivi des sources fonctionnelles et en erreur

## 📚 Sources

### Actualités générales
- ActuIA (FR)
- MIT Technology Review – AI
- TechCrunch – Artificial Intelligence
- KDnuggets
- MarkTechPost

### Recherche académique
- arXiv (cs.AI, cs.LG) - **Extraction automatique des PDFs**
- ScienceDaily – AI
- Google AI Blog
- OpenAI Blog
- AIhub

### Nouveaux outils / produits
- Product Hunt – AI
- Hugging Face Hub
- Reddit r/MachineLearning
- GitHub Trending

### Tendances marché / business
- AI Trends
- AI Business
- VentureBeat – AI
- L'Usine Digitale – IA

## ⚠️ Limitations

Certaines sources ont des protections anti-scraping :
- **AI Business** : Utilise Cloudflare et bloque l'extraction automatique. Seul le contenu RSS (résumé) est disponible.

## 🛠️ Installation

```bash
# Cloner le repository
git clone https://github.com/ai-fo/news.git
cd news

# Installer les dépendances
pip install -r requirements.txt
```

## 📖 Utilisation

### Scraping et génération de transcripts par source
```bash
python main.py
```

Cela va :
1. Scraper toutes les sources configurées
2. Sauvegarder les données brutes dans `data/`
3. Générer des transcripts individuels dans `transcripts/[source]/`

Chaque source aura son propre dossier avec un transcript au format TXT contenant tous ses articles.

### Générer uniquement les transcripts
Si vous avez déjà des données scrappées :
```bash
python generate_transcripts_only.py
# ou avec un fichier spécifique
python generate_transcripts_only.py data/raw_articles_20250617_143022.json
```

## 📁 Structure des fichiers

```
news/
├── main.py                    # Point d'entrée principal
├── scraper.py                 # Logique de scraping
├── content_extractor.py       # Extraction de contenu depuis les pages web
├── transcript_by_source.py    # Génération des transcripts par source
├── config.py                  # Configuration
├── data/                      # Données brutes (JSON)
└── transcripts/               # Transcripts générés
    └── [source]/              # Un dossier par source
```

## ⚙️ Configuration

Modifiez `config.py` pour :
- Ajouter/supprimer des sources nécessitant l'extraction complète
- Ajuster le nombre d'articles par source
- Modifier les timeouts et autres paramètres

## 📊 Format des sorties

### Transcripts individuels (TXT)
- Un fichier par source avec tous ses articles
- Format structuré avec métadonnées complètes
- Contenu wrappé à 80 caractères

### Rapport de statut (JSON)
- Sources réussies/échouées
- Nombre d'articles collectés
- Détails des erreurs

## 🤝 Contribution

Les contributions sont bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## 📝 Licence

Ce projet est sous licence MIT.