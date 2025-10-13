# GitHub Copilot Development Guide

This document provides specific guidance for working with GitHub Copilot on The Observer project.

## 🤖 Project Context for Copilot

**Project Type**: AI-powered collection cataloging system
**Primary Languages**: Python, CSV data processing, API integrations
**Domain**: Physical media collection management (games, books, music)
**Architecture**: Image processing pipeline → API enrichment → Structured catalogs

## 📋 Common Development Patterns

### 1. CSV Data Processing

```python
# Pattern for reading catalog files
import pandas as pd
import csv
from typing import Dict, List, Optional

def load_catalog(catalog_path: str) -> pd.DataFrame:
    """Load catalog CSV with proper encoding and error handling."""
    try:
        return pd.read_csv(catalog_path, encoding='utf-8')
    except UnicodeDecodeError:
        return pd.read_csv(catalog_path, encoding='latin-1')

def add_catalog_entry(catalog_path: str, entry: Dict) -> None:
    """Add new entry to catalog CSV."""
    # Implementation pattern for Copilot
    pass
```

### 2. API Integration Patterns

```python
# RAWG API integration for videogames
import requests
from time import sleep

class RAWGAPIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.rawg.io/api"
        
    def search_game(self, title: str, platform: str = None) -> Dict:
        """Search for game data with rate limiting."""
        # Implementation pattern for Copilot
        pass
        
    def get_game_details(self, game_id: int) -> Dict:
        """Get detailed game information."""
        # Implementation pattern for Copilot
        pass
```

### 3. Image Processing Utilities

```python
# OCR and image analysis patterns
from PIL import Image
import pytesseract
import cv2
import numpy as np

def extract_text_from_spine(image_path: str) -> str:
    """Extract text from book/game spine image."""
    # Common pattern for spine text extraction
    pass

def detect_platform_from_case(image_path: str) -> str:
    """Detect gaming platform from case design/color."""
    # Visual platform identification
    pass
```

## 🎯 Code Generation Prompts

Use these comment patterns to guide Copilot:

### For Data Processing
```python
# Generate unique ID for videogame entry based on platform and title
# Format: platform_title_sequence (e.g., "ps4_god_of_war_01")

# Validate required fields for books catalog entry
# Required: id, type, title, author
# Optional: volume, series, publisher, year, language

# Clean and normalize title text from OCR extraction
# Remove special characters, fix common OCR errors, standardize spacing
```

### For API Integration
```python
# Search RAWG API for game matching title and platform
# Handle rate limiting with exponential backoff
# Return structured data with error handling

# Enrich book data using Google Books API
# Search by title and author, extract publication info
# Fallback to web search if API returns insufficient data
```

### For File Operations
```python
# Process batch of images in directory
# Support resume functionality for large batches
# Log progress and errors for manual review

# Update catalog CSV while preserving existing data
# Generate backup before modifications
# Validate schema after updates
```

## 📊 Data Schema References

### Videogame Entry Structure
```python
videogame_entry = {
    "ID": "platform_title_sequence",
    "Platform": "Nintendo Switch",  # Required
    "Title": "Game Title",          # Required  
    "Publisher": "Nintendo",
    "Developer": "Nintendo EPD",
    "Year": 2023,
    "Region": "NTSC",
    "Edition": "Standard",
    "Language": "English", 
    "Copies": 1,
    "Genres": "Action, Adventure",
    "Description": "Game description...",
    "Metacritic Score": 85,
    "Price Estimate": "$40-60 USD",
    "Cover URL": "https://...",
    "Source Images": "20231013_143022.jpg",
    "Data Source": "RAWG API"
}
```

### Book/Manga Entry Structure  
```python
book_entry = {
    "id": "hash_based_unique_id",
    "type": "Manga",               # Book, Manga, Comic
    "title": "Series Title",       # Required
    "author": "Author Name",       # Required
    "volume": "1",
    "series": "Series Name",
    "publisher": "Publisher",
    "year": 2023,
    "language": "English",
    "country": "USA",
    "copies": 1,
    "cover_type": "Soft cover",
    "genre": "Action, Adventure",
    "description": "Description...",
    "cover_url": "https://...",
    "enrichment_status": "completed",
    "enrichment_date": "2025-10-13T00:00:00",
    "enrichment_source": "Google Books API",
    "search_query": "title author",
    "source_row": 1,
    "price": "$15-25 USD"
}
```

## 🔧 Utility Functions to Generate

### Common Tasks Copilot Should Help With:

1. **ID Generation**
   ```python
   # Generate unique catalog ID based on category and item data
   def generate_catalog_id(category: str, item_data: Dict) -> str:
   ```

2. **Data Validation**
   ```python
   # Validate catalog entry against schema requirements  
   def validate_catalog_entry(entry: Dict, category: str) -> List[str]:
   ```

3. **Duplicate Detection**
   ```python
   # Find potential duplicates in catalog based on title similarity
   def find_duplicate_entries(catalog: pd.DataFrame, new_entry: Dict) -> List[Dict]:
   ```

4. **Price Estimation**
   ```python
   # Estimate current market price for item using web search
   def estimate_item_price(title: str, platform: str, condition: str = "used") -> str:
   ```

5. **Image Analysis**
   ```python
   # Extract metadata from image filename and EXIF data
   def extract_image_metadata(image_path: str) -> Dict:
   ```

## 🚀 Development Workflow

### When Adding New Processing Features:

1. **Create in `tools/` directory** with descriptive filename
2. **Follow existing patterns** for error handling and logging  
3. **Include docstrings** with parameter types and return values
4. **Add validation** for input data and API responses
5. **Support batch processing** with progress tracking
6. **Handle edge cases** gracefully with fallback options

### Testing New Code:

```python
# Test with small sample before processing full collection
# Validate output against existing catalog entries
# Check for data quality issues and schema compliance

def test_processing_function():
    """Test processing function with sample data."""
    sample_images = ["test_game_spine.jpg", "test_book_spine.jpg"]
    # Test implementation
    pass
```

## 🎮 Platform-Specific Patterns

### Nintendo Platforms
```python
# Nintendo DS: Small cartridge, distinctive case colors
# Nintendo Switch: Red cases, unique aspect ratio
# SNES: Colorful labels, consistent cartridge height
nintendo_platforms = ["Nintendo DS", "Nintendo 3DS", "Nintendo Switch", "SNES", "NES"]
```

### PlayStation Platforms  
```python
# PS4: Blue cases, PS4 logo visible
# PS3: Black cases, Blu-ray disc format
# PS5: White cases, taller than PS4
playstation_platforms = ["PlayStation", "PlayStation 2", "PlayStation 3", "PlayStation 4", "PlayStation 5"]
```

### Xbox Platforms
```python
# Xbox One: Green cases, Xbox branding
# Xbox 360: White/green cases, DVD format
xbox_platforms = ["Xbox", "Xbox 360", "Xbox One", "Xbox Series X/S"]
```

## 📝 Documentation Standards

When generating code, include:

- **Purpose**: What the function does
- **Parameters**: Type hints and descriptions  
- **Returns**: Expected return type and format
- **Raises**: Potential exceptions
- **Example**: Usage example with sample data

```python
def process_collection_image(image_path: str, category: str) -> Dict:
    """
    Process collection item image and extract catalog data.
    
    Args:
        image_path (str): Path to spine/case image
        category (str): Item category ('videogames', 'books', 'music')
        
    Returns:
        Dict: Extracted item data with metadata
        
    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If category not supported
        
    Example:
        >>> data = process_collection_image("game_spine.jpg", "videogames")
        >>> print(data["title"])
        "The Legend of Zelda: Breath of the Wild"
    """
    pass
```

## 🔍 Quality Assurance Patterns

```python
# Validate data completeness before adding to catalog
# Check for required fields based on category
# Verify external API data quality
# Flag entries requiring manual review

def quality_check_entry(entry: Dict, category: str) -> Tuple[bool, List[str]]:
    """Check entry quality and return validation results."""
    pass
```

This guide should help GitHub Copilot understand the project context and generate appropriate code for The Observer collection cataloging system.