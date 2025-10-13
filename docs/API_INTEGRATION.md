# API Integration Guide

This document details external API integrations used by The Observer for data enrichment.

## 🎮 RAWG API (Video Games Database)

**Primary API for videogame metadata enrichment**

### Configuration
```python
# docs/rarbg-api.md should contain:
API KEY = your_rawg_api_key_here
USER = your_username_here
```

### Base URL
```
https://api.rawg.io/api
```

### Key Endpoints

#### Search Games
```python
GET /games?search={title}&platforms={platform_id}

# Example usage:
def search_rawg_game(title: str, platform: str = None) -> Dict:
    """Search RAWG API for game data."""
    url = f"https://api.rawg.io/api/games"
    params = {
        "key": API_KEY,
        "search": title,
        "search_precise": True
    }
    if platform:
        params["platforms"] = get_platform_id(platform)
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
```

#### Get Game Details
```python
GET /games/{id}

def get_rawg_game_details(game_id: int) -> Dict:
    """Get detailed game information from RAWG."""
    url = f"https://api.rawg.io/api/games/{game_id}"
    params = {"key": API_KEY}
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
```

### Platform ID Mapping
```python
RAWG_PLATFORM_IDS = {
    "Nintendo Switch": 7,
    "PlayStation 4": 2,
    "PlayStation 5": 187,
    "PlayStation 3": 16,
    "Xbox One": 3,
    "Xbox 360": 14,
    "Nintendo DS": 20,
    "Nintendo 3DS": 8,
    "SNES": 83,
    "NES": 49,
    "Nintendo 64": 25,
    "GameCube": 105,
    "Wii": 11,
    "Wii U": 10,
    "Game Boy": 26,
    "PlayStation": 15,
    "PlayStation 2": 4,
    "Xbox": 80,
    "Sega Genesis": 107,
    "PlayStation Portable": 17,
    "PlayStation Vita": 18
}
```

### Response Schema
```python
# Games search response structure
{
    "count": 123,
    "results": [
        {
            "id": 12345,
            "name": "Game Title",
            "released": "2023-01-15",
            "background_image": "https://...",
            "rating": 4.5,
            "rating_top": 5,
            "ratings_count": 1000,
            "metacritic": 85,
            "playtime": 40,
            "platforms": [...],
            "genres": [...],
            "publishers": [...],
            "developers": [...]
        }
    ]
}
```

### Rate Limiting
- **Free Tier**: 20,000 requests per month
- **Rate Limit**: 1 request per second recommended
- **Implementation**: Use time.sleep(1) between requests

```python
import time
from functools import wraps

def rate_limit(func):
    """Decorator to enforce rate limiting."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        time.sleep(1)  # 1 second delay
        return func(*args, **kwargs)
    return wrapper
```

## 📚 Google Books API

**Primary API for book/manga metadata enrichment**

### Base URL
```
https://www.googleapis.com/books/v1
```

### Search Books
```python
def search_google_books(title: str, author: str = None) -> Dict:
    """Search Google Books API for book data."""
    query = title
    if author:
        query += f"+inauthor:{author}"
    
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query,
        "maxResults": 10,
        "langRestrict": "en"  # Adjust based on collection
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
```

### Response Schema
```python
# Books search response structure
{
    "totalItems": 123,
    "items": [
        {
            "id": "book_id",
            "volumeInfo": {
                "title": "Book Title",
                "subtitle": "Subtitle if exists", 
                "authors": ["Author Name"],
                "publisher": "Publisher Name",
                "publishedDate": "2023-01-15",
                "description": "Book description...",
                "industryIdentifiers": [...],
                "categories": ["Genre"],
                "imageLinks": {
                    "thumbnail": "https://...",
                    "small": "https://...",
                    "medium": "https://...",
                    "large": "https://..."
                },
                "language": "en",
                "pageCount": 300
            }
        }
    ]
}
```

## 🔍 Web Search Fallback

**For missing data and price estimates**

### Price Estimation Pattern
```python
def estimate_price_web_search(title: str, platform: str, condition: str = "used") -> str:
    """Estimate item price using web search."""
    search_terms = [
        f"{title} {platform} {condition} price",
        f"{title} {platform} ebay sold listings",
        f"{title} {platform} amazon marketplace"
    ]
    
    # Implementation would use search APIs or scraping
    # Return format: "$XX-YY USD used" or "N/A"
    pass
```

### Data Enrichment Pattern
```python
def enrich_with_web_search(item_data: Dict, category: str) -> Dict:
    """Enrich item data using web search."""
    enriched_data = item_data.copy()
    
    # Search for missing publisher, year, genre info
    if not enriched_data.get("publisher"):
        # Perform targeted search
        pass
    
    if not enriched_data.get("year"):
        # Search for release date
        pass
        
    return enriched_data
```

## 🔄 API Integration Patterns

### Error Handling
```python
class APIError(Exception):
    """Custom exception for API errors."""
    pass

def safe_api_call(func):
    """Decorator for safe API calls with retry logic."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise APIError(f"API call failed after {max_retries} attempts: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
    return wrapper
```

### Data Mapping Functions
```python
def map_rawg_to_catalog(rawg_data: Dict) -> Dict:
    """Map RAWG API response to catalog entry format."""
    return {
        "Title": rawg_data.get("name", ""),
        "Year": extract_year(rawg_data.get("released", "")),
        "Genres": ", ".join([g["name"] for g in rawg_data.get("genres", [])]),
        "Description": rawg_data.get("description", ""),
        "Metacritic Score": rawg_data.get("metacritic"),
        "Cover URL": rawg_data.get("background_image", ""),
        "Publisher": extract_publisher(rawg_data.get("publishers", [])),
        "Developer": extract_developer(rawg_data.get("developers", [])),
        "Data Source": "RAWG API"
    }

def map_google_books_to_catalog(books_data: Dict) -> Dict:
    """Map Google Books API response to catalog entry format."""
    if not books_data.get("items"):
        return {}
        
    item = books_data["items"][0]["volumeInfo"]
    return {
        "title": item.get("title", ""),
        "author": ", ".join(item.get("authors", [])),
        "publisher": item.get("publisher", ""),
        "year": extract_year(item.get("publishedDate", "")),
        "description": item.get("description", ""),
        "genre": ", ".join(item.get("categories", [])),
        "cover_url": item.get("imageLinks", {}).get("thumbnail", ""),
        "enrichment_source": "Google Books API"
    }
```

### Batch Processing with APIs
```python
def process_items_batch(items: List[Dict], api_func, batch_size: int = 10) -> List[Dict]:
    """Process items in batches to respect API limits."""
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = []
        
        for item in batch:
            try:
                result = api_func(item)
                batch_results.append(result)
            except Exception as e:
                print(f"Error processing item {item}: {e}")
                batch_results.append(None)
        
        results.extend(batch_results)
        
        # Rate limiting between batches
        if i + batch_size < len(items):
            time.sleep(5)
    
    return results
```

## 📊 API Usage Monitoring

### Track API Usage
```python
class APIUsageTracker:
    """Track API usage and costs."""
    
    def __init__(self):
        self.usage_stats = {
            "rawg": {"requests": 0, "errors": 0},
            "google_books": {"requests": 0, "errors": 0}
        }
    
    def record_request(self, api_name: str, success: bool = True):
        """Record API request for monitoring."""
        self.usage_stats[api_name]["requests"] += 1
        if not success:
            self.usage_stats[api_name]["errors"] += 1
    
    def get_usage_report(self) -> str:
        """Generate usage report."""
        report = "API Usage Report:\n"
        for api, stats in self.usage_stats.items():
            report += f"{api}: {stats['requests']} requests, {stats['errors']} errors\n"
        return report
```

## 🛡️ Best Practices

1. **Always include API keys in request headers or params**
2. **Respect rate limits to avoid being blocked**
3. **Implement exponential backoff for retries**  
4. **Cache responses when possible to reduce API calls**
5. **Validate API responses before using data**
6. **Log API errors for debugging**
7. **Use appropriate timeout values**
8. **Handle API changes gracefully**

## 🔧 Testing API Integration

```python
def test_api_integration():
    """Test API integration with sample data."""
    # Test RAWG API
    test_games = ["The Legend of Zelda", "Super Mario Odyssey"]
    for game in test_games:
        try:
            result = search_rawg_game(game)
            assert result.get("results"), f"No results for {game}"
            print(f"✓ RAWG API working for {game}")
        except Exception as e:
            print(f"✗ RAWG API failed for {game}: {e}")
    
    # Test Google Books API  
    test_books = [("Dragon Ball", "Akira Toriyama")]
    for title, author in test_books:
        try:
            result = search_google_books(title, author)
            assert result.get("items"), f"No results for {title}"
            print(f"✓ Google Books API working for {title}")
        except Exception as e:
            print(f"✗ Google Books API failed for {title}: {e}")
```

This API guide provides comprehensive patterns for integrating external data sources into The Observer collection cataloging system.