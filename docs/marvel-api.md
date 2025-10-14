# Marvel API Integration

## Overview

The Marvel Comics API provides access to Marvel's extensive catalog of comics, characters, series, events, and creators. This integration allows The Observer to enrich comic metadata for Marvel titles in the collection.

## Configuration

API credentials are stored in `./.env.marvel`:

```
MARVEL_PUBLIC_KEY=your_public_key_here
MARVEL_PRIVATE_KEY=your_private_key_here
```

**IMPORTANT**: Keep your private key secure. Never commit it to public repositories.

## Getting API Keys

1. Visit [Marvel Developer Portal](https://developer.marvel.com/)
2. Create an account or sign in
3. Navigate to "My Developer Account"
4. Generate your API keys (public and private)

## API Endpoints

**Base URL**: `https://gateway.marvel.com/v1/public/`

### Available Resources

- `/comics` - Individual comic issues
- `/series` - Comic series collections
- `/characters` - Marvel characters
- `/creators` - Writers, artists, editors
- `/events` - Crossover events
- `/stories` - Story arcs

## Authentication

All requests require three authentication parameters:

- `ts` - Timestamp (Unix time)
- `apikey` - Your public key
- `hash` - MD5 hash of `ts + private_key + public_key`

The `MarvelAPIClient` handles authentication automatically.

## Usage Examples

### Basic Comic Search

```python
from tools.marvel_api_client import MarvelAPIClient

client = MarvelAPIClient()

# Search for comics by title
results = client.search_comics(title="Spider-Man", limit=10)

for comic in results:
    print(f"{comic['title']} - Issue #{comic['issueNumber']}")
```

### Get Comic Details

```python
# Get specific comic by Marvel ID
comic = client.get_comic_by_id(59551)
metadata = client.extract_comic_metadata(comic)

print(f"Title: {metadata['title']}")
print(f"Writers: {metadata['writers']}")
print(f"Release Date: {metadata['on_sale_date']}")
```

### Enrich from Spine Text

```python
# Main method for Observer pipeline integration
metadata = client.enrich_comic_from_spine_text(
    title="Amazing Spider-Man",
    issue_number=300,
    series_name="Amazing Spider-Man"
)

if metadata:
    print(f"Found: {metadata['title']}")
    print(f"Marvel URL: {metadata['marvel_url']}")
```

### Search Series

```python
# Find series by title
series = client.search_series(title="X-Men", limit=5)

for s in series:
    print(f"{s['title']} ({s['startYear']} - {s['endYear']})")
```

## Response Data Structure

### Comic Metadata Fields

The `extract_comic_metadata()` method returns:

```python
{
    'marvel_id': int,           # Marvel's internal comic ID
    'title': str,               # Full comic title
    'issue_number': int,        # Issue number
    'series_name': str,         # Series name
    'description': str,         # Comic description/synopsis
    'page_count': int,          # Number of pages
    'format': str,              # Format (Comic, Trade Paperback, etc.)
    'isbn': str,                # ISBN if available
    'upc': str,                 # UPC barcode
    'writers': str,             # Comma-separated writer names
    'on_sale_date': str,        # YYYY-MM-DD release date
    'cover_url': str,           # URL to cover image
    'print_price': float,       # Print price in USD
    'marvel_url': str           # Marvel.com detail page URL
}
```

## Integration with The Observer Pipeline

### Phase 1: Image Analysis
OCR extracts comic title and issue number from spines.

### Phase 2: Marvel API Enrichment
```python
client = MarvelAPIClient()
metadata = client.enrich_comic_from_spine_text(
    title=extracted_title,
    issue_number=extracted_issue,
    series_name=extracted_series
)
```

### Phase 3: Catalog Update
Map Marvel API response to Observer's comic schema:

- `marvel_id` → Additional identifier field
- `title` → `title` column
- `writers` → `author` column
- `series_name` → `series` column
- `issue_number` → `volume` column
- `on_sale_date` → `year` column (extract year)
- `description` → `description` column
- `cover_url` → `cover_url` column
- `print_price` → `price` column
- `marvel_url` → `enrichment_source` column

## API Limits and Best Practices

### Rate Limits
- 3,000 requests per day per API key
- No specified requests-per-second limit
- Use `time.sleep()` for bulk operations to be respectful

### Best Practices
1. Cache responses to avoid duplicate requests
2. Use specific search parameters to reduce API calls
3. Handle pagination for large result sets (100 max per page)
4. Implement retry logic for transient failures
5. Log failed enrichments for manual review

### Error Handling

```python
try:
    metadata = client.enrich_comic_from_spine_text(title="Unknown Comic")
    if metadata is None:
        print("No match found - requires manual enrichment")
except requests.exceptions.RequestException as e:
    print(f"API error: {e}")
    # Fall back to web search or manual entry
```

## Data Quality Considerations

### Strengths
- Comprehensive Marvel Comics catalog
- Accurate release dates and issue numbers
- High-quality cover images
- Detailed creator information
- Official Marvel data

### Limitations
- Only covers Marvel Comics (not DC, Image, etc.)
- Some variants may have incomplete metadata
- Older comics may have limited descriptions
- Trade paperbacks and collections may be separate entries
- International editions may not be included

### Fallback Strategy
For non-Marvel comics or failed lookups:
1. Try Google Books API
2. Use web search for publisher/author info
3. Flag for manual enrichment
4. Maintain source image mapping for verification

## Testing

Run the test suite:

```bash
python3 tools/marvel_api_client.py
```

Expected output:
- Successful authentication
- Search results for "Spider-Man"
- Search results for "X-Men" series
- Extracted metadata display

## Related Files

- `tools/marvel_api_client.py` - API client implementation
- `tests/.env.marvel` - API credentials (not committed)
- `output/csv/books_manga_comics_catalog.csv` - Target catalog
- `docs/rarbg-api.md` - Similar API integration for videogames

## Resources

- [Marvel Developer Portal](https://developer.marvel.com/)
- [API Documentation](https://developer.marvel.com/docs)
- [Authorization Guide](https://developer.marvel.com/documentation/authorization)
- [Interactive API Explorer](https://gateway.marvel.com/docs)
