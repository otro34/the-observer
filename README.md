# The Observer 📚🎮🎵

An AI-powered collection cataloging system that transforms physical media collections into structured digital databases. Uses computer vision, OCR, and external APIs to automatically catalog videogames, books, manga, comics, and vinyl records from spine and case images.

## ✨ Features

- **📸 Image Processing**: Extract information from spine images, case photos, and shelf views
- **🤖 AI-Powered Recognition**: Identify titles, platforms, and metadata from visual cues
- **🔍 Automatic Enrichment**: Enhance data using RAWG API, Marvel API, Google Books, and web search
- **📊 Structured Catalogs**: Generate comprehensive CSV databases with rich metadata
- **🎯 Smart Recommendations**: Curated playing/reading orders based on quality and narrative flow
- **🌐 Multi-Language Support**: Handle English, Spanish, and Japanese releases
- **🔄 Batch Processing**: Handle large collections with resume capability

## 📈 Current Collection

- **🎮 Videogames**: 468 items across 8 console generations
- **📚 Books/Manga/Comics**: 552+ items with multi-language support  
- **🎵 Music**: Growing vinyl collection

## 🏗️ Project Structure

```
the-observer/
├── 📁 sources/                    # Source images by category
│   ├── 📱 videogames/            # Game cases and cartridges
│   ├── 📖 books/                 # Book/manga spines
│   └── 💿 vinyls/                # Record sleeves
├── 📊 output/csv/                # Generated catalogs
│   ├── videogames_catalog.csv
│   ├── books_manga_comics_catalog.csv
│   └── music_catalog.csv
├── 🛠️ tools/                     # Processing utilities
├── 📋 recommendations/           # Curated guides
└── 📚 docs/                      # API docs and schemas
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- API keys for data enrichment:
  - RAWG API (videogames)
  - Marvel API (Marvel Comics)
  - Google Books API (books/manga)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/otro34/the-observer.git
   cd the-observer
   ```

2. **Configure API credentials**
   ```bash
   # RAWG API for videogames
   echo "API KEY = your_rawg_api_key_here" > docs/rarbg-api.md
   echo "USER = your_username" >> docs/rarbg-api.md

   # Marvel API for comics
   echo "MARVEL_PUBLIC_KEY=your_public_key_here" > .env.marvel
   echo "MARVEL_PRIVATE_KEY=your_private_key_here" >> .env.marvel
   ```

3. **Add source images**
   ```bash
   # Place images in appropriate directories
   cp your_game_images/* sources/videogames/
   cp your_book_images/* sources/books/
   cp your_vinyl_images/* sources/vinyls/
   ```

## 📊 Data Schemas

### Videogames
- Platform, Title, Publisher, Developer, Year, Genres
- Metacritic scores, descriptions, cover URLs
- Regional editions and language variants

### Books/Manga/Comics  
- Title, Author, Publisher, Series, Volume
- Genre classification, publication details
- Multi-language and regional support

### Music/Vinyls
- Artist, Album, Label, Year, Format
- Track listings, genre tags, condition notes

## 🎯 Collection Highlights

### Gaming Collection
- **Premium Titles**: Many 90+ Metacritic games including Zelda BOTW (97), Mario Odyssey (97)
- **Complete Series**: Uncharted, God of War, Metal Gear Solid
- **Platform Variety**: 8 generations from NES to PS5
- **Regional Variants**: Japanese imports, European exclusives

### Manga/Comics Collection
- **Popular Series**: Dragon Ball (complete), Evangelion, 20th Century Boys
- **Publishers**: Viz, IVREA, Planeta, Kitsune Books
- **Languages**: English, Spanish, Japanese editions
- **Special Editions**: Color editions, omnibus collections

## 🔧 Development

### Adding New Tools

Create utilities in the `tools/` directory following these patterns:

```python
# Example: CSV manipulation utility
class CatalogManager:
    def __init__(self, catalog_path):
        self.catalog_path = catalog_path
    
    def add_item(self, item_data):
        # Add item with unique ID generation
        pass
    
    def validate_schema(self):
        # Ensure required fields present
        pass
```

### Image Processing Pipeline

1. **OCR Extraction**: Extract text from spine images
2. **Platform Detection**: Identify console from case design  
3. **API Enrichment**: Fetch metadata from external sources
4. **Quality Validation**: Verify data completeness
5. **Catalog Update**: Add to appropriate CSV database

## 📈 Recommendations System  

The project includes curated recommendation guides:

- **🎮 Gaming**: 468-game playing order prioritizing masterpieces
- **📚 Manga**: Reading orders for complex series
- **📖 Comics**: Optimal story arc progression

Example gaming recommendation tiers:
- **Tier 1**: Must-play masterpieces (Uncharted 2, Last of Us, BOTW)
- **Tier 2**: Excellent experiences for variety
- **Tier 3**: Genre-specific and completion titles

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Guidelines

- **Code Style**: Follow existing patterns for consistency
- **Documentation**: Update schemas for new data fields
- **Testing**: Validate changes against existing catalogs
- **Images**: Provide sample images for new processing features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **RAWG API** for comprehensive videogame database
- **Marvel API** for official Marvel Comics metadata
- **Google Books API** for book metadata
- **OCR Technologies** powering text extraction
- **Open Source Community** for inspiration and tools

## 📞 Contact

- **GitHub**: [@otro34](https://github.com/otro34)
- **Project Link**: [https://github.com/otro34/the-observer](https://github.com/otro34/the-observer)

---

⭐ **Star this repo if you find it useful!** ⭐
