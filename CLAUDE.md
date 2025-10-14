# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**The Observer** is an AI-powered collection cataloging system that processes images of physical media collections (videogames, books, manga, comics, and vinyl records) to create structured digital catalogs. The system uses computer vision, OCR, and external APIs to extract information from spine images, shelf photos, and cases.

**Current Status**: Active project with 1,000+ cataloged items across multiple media types.

## Project Architecture

### Core Components

1. **Image Processing Pipeline**: Extracts text and identifies items from spine/case images
2. **Data Enrichment Engine**: Uses external APIs (RAWG, Google Books) to enhance metadata
3. **Catalog Management**: Maintains structured CSV databases with unique IDs
4. **Recommendation System**: Generates curated playing/reading orders

### Key Project Structure

```
the-observer/
├── sources/                    # Source images organized by category
│   ├── books/                 # Book, manga, comic spine images
│   ├── videogames/           # Game case and cartridge images  
│   └── vinyls/               # Vinyl record sleeve images
├── output/csv/               # Generated catalog databases
│   ├── videogames_catalog.csv    # 468 games cataloged
│   ├── books_manga_comics_catalog.csv  # 552+ items cataloged
│   └── music_catalog.csv         # Vinyl records catalog
├── docs/                     # API documentation and schemas
│   ├── rarbg-api-details.json    # RAWG API specification
│   └── rarbg-api.md              # API credentials (configure)
├── tools/                    # Processing utilities (to be developed)
├── recommendations/          # Curated recommendation guides
│   ├── VIDEOGAME_PLAYING_ORDER.md
│   ├── MANGA_READING_ORDER.md
│   └── COMIC_READING_ORDER.md
└── README.md                # Project documentation
```

## Data Processing Pipeline

The system processes collection images through these phases:

### Phase 1: Image Analysis
- **Input**: Spine images, case photos, shelf views
- **Process**: OCR text extraction, platform identification from visual cues
- **Output**: Raw text data with image metadata
- **Agent**: collection-item-identifier

### Phase 2: Data Enrichment
- **Videogames**: RAWG API for metadata, Metacritic scores, descriptions
- **Books/Manga**: Google Books API, web search for publisher/author info
- **Comics (Marvel)**: Marvel API for official Marvel Comics metadata, writers, cover art
- **Vinyls**: Web search, music databases for track listings
- **Agent**: collection-data-enricher

### Phase 3: Cataloging
- **Format**: CSV files with standardized schemas
- **Storage**: One CSV per category with unique ID generation
- **Backup**: Source image mapping for verification

### Phase 4: Quality Control
- **Validation**: Check for missing required fields
- **Deduplication**: Identify and merge duplicate entries
- **Enrichment Status**: Track completion and data sources

## Data Schemas

### Videogames Schema (videogames_catalog.csv)
```csv
ID,Platform,Title,Publisher,Developer,Year,Region,Edition,Language,Copies,
Genres,Description,Metacritic Score,Price Estimate,Cover URL,Source Images,Data Source
```

**Required Fields**: ID, Platform, Title
**Optional Fields**: Publisher, Developer, Year, Region, Edition, Language, Copies, Genres, Description, Metacritic Score, Price Estimate, Cover URL, Source Images, Data Source

### Books/Manga/Comics Schema (books_manga_comics_catalog.csv)
```csv
id,type,title,author,volume,series,publisher,year,language,country,copies,
cover_type,genre,description,cover_url,enrichment_status,enrichment_date,
enrichment_source,search_query,source_row,price
```

**Required Fields**: id, type, title, author
**Optional Fields**: volume, series, publisher, year, language, country, copies, cover_type, genre, description, cover_url, enrichment_status, enrichment_date, enrichment_source, search_query, source_row, price

### Music Schema (music_catalog.csv)
```csv
ID,Title,Artist,Publisher,Year,Format,Disc Count,Language,Copies,
Genres,Description,Tracklist,Price Estimate,Cover URL,Source Images,Data Source
```

**Required Fields**: ID, Title, Artist
**Optional Fields**: Publisher, Year, Format, Disc Count, Language, Copies, Genres, Description, Tracklist, Price Estimate, Cover URL, Source Images, Data Source

## Collection Statistics (Current)

- **Videogames**: 468 items across 8 console generations
  - PlayStation dominance: PS3 (101), PS4 (51), PS5 (33)
  - Strong Nintendo presence: Switch (67), SNES (39), DS/3DS (25+)
  - Classic systems: N64, Xbox 360, Genesis
  - High-quality collection with many 90+ Metacritic scores

- **Books/Manga/Comics**: 552+ items
  - Heavy manga focus with popular series (Dragon Ball, Evangelion)
  - Multi-language: Spanish, English, Japanese editions
  - Publishers: Viz, IVREA, Planeta, Kitsune Books

- **Music**: 3 vinyl records (collection just started)
  - Diverse genres: Pop, anime soundtracks, movie soundtracks

## Important Processing Considerations

### Image Analysis Challenges
- **Spine Recognition**: Items viewed from side requiring platform ID from case design
- **Multi-Photo Items**: Same item may appear in adjacent shelf photos
- **Language Detection**: Critical for Spanish, English, Japanese releases
- **Special Cases**: Sandman collection forms complete image when stacked
- **Quality Variance**: OCR accuracy depends on image quality and lighting

### Platform Identification Strategies
- **Nintendo DS**: Distinctive white/black cases, small cartridge visible
- **PlayStation**: Blue cases (PS4), black cases (PS3), white cases (PS5)
- **SNES**: Colorful cartridge labels, consistent height
- **Switch**: Red cases, unique aspect ratio

### Data Quality Requirements
- **Unique IDs**: Generate consistent IDs for deduplication
- **Source Tracking**: Maintain image-to-item mapping for verification
- **Batch Processing**: Handle large image sets with resume capability
- **Error Handling**: Graceful failure for unreadable/damaged items

## API Integration & External Data Sources

### RAWG API (Primary for Videogames)
- **Endpoint**: https://api.rawg.io/api
- **Credentials**: Configure in `docs/rarbg-api.md` 
- **Data**: Metacritic scores, descriptions, cover art, genre info
- **Rate Limits**: Respect API quotas

### Marvel API (Marvel Comics)
- **Endpoint**: https://gateway.marvel.com/v1/public
- **Credentials**: Configure in `.env.marvel`
- **Data**: Official Marvel metadata, issue numbers, writers, release dates, cover art
- **Rate Limits**: 3,000 requests per day
- **Use For**: Marvel-published comics only (Spider-Man, X-Men, Avengers, etc.)

### Google Books API (Books/Manga)
- **Use For**: Author info, publication details, cover images
- **Fallback**: Web search when API data insufficient

### Web Search (All Categories)
- **Price Estimates**: eBay, Amazon price checking
- **Missing Data**: Publisher info, release dates
- **Verification**: Cross-reference API data accuracy

## Code Development Guidelines

### Tool Creation (`tools/` directory)
When creating processing utilities, follow these patterns:

1. **CSV Manipulation**: Create reusable functions for reading/writing catalogs
2. **Image Processing**: Standardized OCR and computer vision utilities  
3. **API Integration**: Wrapper classes for external service calls
4. **Data Validation**: Schema enforcement and quality checks
5. **Progress Tracking**: Resumable batch processing with state management

### File Naming Conventions
- **Images**: Use timestamp format `YYYYMMDD_HHMMSS.jpg`
- **Generated IDs**: Use consistent patterns per category
  - Videogames: `platform_title_##` (e.g., `ds_brain_age_01`)
  - Books: Hash-based IDs (e.g., `4667e4c18430`)
  - Music: `vinyl_###_artist_title` format

### Error Handling Patterns
- **Graceful Degradation**: Partial data better than no data
- **Retry Logic**: Handle API timeouts and rate limits
- **Logging**: Detailed logs for debugging failed extractions
- **Manual Review**: Flag uncertain extractions for human verification