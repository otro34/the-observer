"""
Comic Data Enricher for The Observer

This module enriches comic metadata by intelligently selecting the best data source:
- Marvel API for Marvel Comics
- Google Books API for other publishers
- Web search as fallback

Integrates with the collection-data-enricher agent workflow.
"""

import csv
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
import os

try:
    from marvel_api_client import MarvelAPIClient
except ImportError:
    # Handle import from different directory
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from marvel_api_client import MarvelAPIClient


class ComicEnricher:
    """
    Enriches comic metadata using appropriate data sources.

    Uses Marvel API for Marvel-published comics, falls back to other sources
    for non-Marvel titles.
    """

    # Known Marvel character/series patterns for detection
    MARVEL_INDICATORS = [
        'spider-man', 'spiderman', 'x-men', 'avengers', 'iron man', 'thor',
        'captain america', 'hulk', 'fantastic four', 'daredevil', 'punisher',
        'deadpool', 'wolverine', 'black panther', 'doctor strange', 'venom',
        'carnage', 'ghost rider', 'blade', 'moon knight', 'silver surfer',
        'guardians of the galaxy', 'ant-man', 'wasp', 'hawkeye', 'black widow',
        'scarlet witch', 'quicksilver', 'vision', 'war machine', 'falcon',
        'winter soldier', 'ms. marvel', 'captain marvel', 'she-hulk', 'luke cage',
        'iron fist', 'jessica jones', 'elektra', 'kingpin', 'magneto',
        'cyclops', 'storm', 'rogue', 'gambit', 'jean grey', 'beast',
        'the new mutants', 'x-force', 'runaways', 'young avengers',
        'ultimate spider-man', 'ultimate x-men', 'marvel knights',
        'what if', 'marvel zombies', 'marvel team-up', 'secret wars',
        'infinity gauntlet', 'civil war', 'house of m', 'age of apocalypse'
    ]

    def __init__(self, catalog_path: str):
        """
        Initialize the Comic Enricher.

        Args:
            catalog_path: Path to books_manga_comics_catalog.csv
        """
        self.catalog_path = catalog_path
        self.marvel_client = None

        # Try to initialize Marvel API client
        try:
            self.marvel_client = MarvelAPIClient()
            print("Marvel API client initialized successfully")
        except ValueError as e:
            print(f"Marvel API not available: {e}")
            print("Will use fallback enrichment methods for all comics")

    def is_marvel_comic(self, title: str, author: str = "", publisher: str = "") -> bool:
        """
        Detect if a comic is published by Marvel.

        Args:
            title: Comic title
            author: Comic author/writer (optional)
            publisher: Publisher name (optional)

        Returns:
            True if likely a Marvel comic
        """
        # Check publisher directly
        if publisher and 'marvel' in publisher.lower():
            return True

        # Check title for Marvel characters/series
        title_lower = title.lower()
        for indicator in self.MARVEL_INDICATORS:
            if indicator in title_lower:
                return True

        return False

    def extract_issue_number(self, title: str, volume: str = "") -> Optional[int]:
        """
        Extract issue number from title or volume field.

        Args:
            title: Comic title
            volume: Volume/issue field

        Returns:
            Issue number if found, None otherwise
        """
        # Try volume field first
        if volume:
            volume_match = re.search(r'#?(\d+)', str(volume))
            if volume_match:
                return int(volume_match.group(1))

        # Try title
        # Patterns: "#123", "Vol. 123", "Issue 123", "(2023) #123"
        patterns = [
            r'#(\d+)',
            r'vol\.?\s*(\d+)',
            r'issue\s*(\d+)',
            r'\((?:\d{4})\)\s*#?(\d+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                return int(match.group(1))

        return None

    def extract_series_name(self, title: str) -> str:
        """
        Extract the series name from a full comic title.

        Examples:
            "Spider-Man (2016) #6" -> "Spider-Man"
            "Amazing Spider-Man Vol. 3 #300" -> "Amazing Spider-Man"

        Args:
            title: Full comic title

        Returns:
            Extracted series name
        """
        # Remove common patterns
        cleaned = re.sub(r'\s*\(\d{4}\s*-?\s*\d*\)', '', title)  # Remove (2016) or (2016 - 2018)
        cleaned = re.sub(r'\s*#\d+.*$', '', cleaned)  # Remove #123 and everything after
        cleaned = re.sub(r'\s*vol\.?\s*\d+.*$', '', cleaned, flags=re.IGNORECASE)  # Remove Vol. 3
        cleaned = re.sub(r'\s*issue\s*\d+.*$', '', cleaned, flags=re.IGNORECASE)  # Remove Issue 123
        cleaned = re.sub(r'\s*\([^)]*variant[^)]*\)', '', cleaned, flags=re.IGNORECASE)  # Remove variant info

        return cleaned.strip()

    def enrich_comic_with_marvel_api(self, comic_data: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Enrich a comic using the Marvel API.

        Args:
            comic_data: Dictionary with comic fields (title, author, volume, etc.)

        Returns:
            Enriched metadata dictionary or None if not found
        """
        if not self.marvel_client:
            return None

        title = comic_data.get('title', '')
        volume = comic_data.get('volume', '')

        # Extract series name and issue number
        series_name = self.extract_series_name(title)
        issue_number = self.extract_issue_number(title, volume)

        print(f"Searching Marvel API for: '{series_name}' #{issue_number or 'N/A'}")

        try:
            # Use the enrichment method from marvel_api_client
            result = self.marvel_client.enrich_comic_from_spine_text(
                title=series_name,
                issue_number=issue_number,
                series_name=series_name
            )

            if result:
                print(f"✓ Found Marvel match: {result['title']}")
                return self._map_marvel_to_catalog_schema(result, comic_data)
            else:
                print(f"✗ No Marvel API match found")
                return None

        except Exception as e:
            print(f"Marvel API error: {e}")
            return None

    def _map_marvel_to_catalog_schema(
        self,
        marvel_data: Dict[str, Any],
        original_data: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Map Marvel API response to Observer catalog schema.

        Args:
            marvel_data: Data from Marvel API
            original_data: Original catalog entry

        Returns:
            Dictionary with catalog schema fields
        """
        # Extract year from on_sale_date
        year = None
        if marvel_data.get('on_sale_date'):
            year = marvel_data['on_sale_date'].split('-')[0]

        return {
            'id': original_data.get('id', ''),
            'type': 'comic',
            'title': marvel_data.get('title', original_data.get('title', '')),
            'author': marvel_data.get('writers', original_data.get('author', '')),
            'volume': marvel_data.get('issue_number', original_data.get('volume', '')),
            'series': marvel_data.get('series_name', ''),
            'publisher': 'Marvel Comics',
            'year': year or original_data.get('year', ''),
            'language': original_data.get('language', ''),
            'country': original_data.get('country', ''),
            'copies': original_data.get('copies', ''),
            'cover_type': original_data.get('cover_type', ''),
            'genre': marvel_data.get('format', original_data.get('genre', '')),
            'description': marvel_data.get('description', ''),
            'cover_url': marvel_data.get('cover_url', ''),
            'enrichment_status': 'enriched',
            'enrichment_date': datetime.now().strftime('%Y-%m-%d'),
            'enrichment_source': f"Marvel API (ID: {marvel_data.get('marvel_id', 'N/A')})",
            'search_query': marvel_data.get('title', ''),
            'source_row': original_data.get('source_row', ''),
            'price': marvel_data.get('print_price', original_data.get('price', ''))
        }

    def enrich_comic_entry(self, comic_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Enrich a single comic entry using the best available data source.

        This is the main method called by the collection-data-enricher agent.

        Args:
            comic_data: Dictionary with comic fields from catalog

        Returns:
            Enriched metadata dictionary
        """
        title = comic_data.get('title', '')
        author = comic_data.get('author', '')
        publisher = comic_data.get('publisher', '')
        comic_type = comic_data.get('type', '')

        # Skip if not a comic
        if comic_type and comic_type.lower() != 'comic':
            print(f"Skipping {title} - not a comic (type: {comic_type})")
            return comic_data

        # Try Marvel API first if it's a Marvel comic
        if self.is_marvel_comic(title, author, publisher):
            print(f"Detected Marvel comic: {title}")
            marvel_result = self.enrich_comic_with_marvel_api(comic_data)

            if marvel_result:
                return marvel_result
            else:
                print(f"Marvel API enrichment failed, would fall back to other sources")
        else:
            print(f"Not a Marvel comic: {title}")

        # For non-Marvel comics or failed Marvel enrichment:
        # Return original data with note to use Google Books API or web search
        result = comic_data.copy()
        result['enrichment_source'] = 'manual_enrichment_needed'
        result['enrichment_status'] = 'pending'

        return result

    def batch_enrich_catalog(
        self,
        output_path: Optional[str] = None,
        filter_type: str = 'comic',
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Enrich all comics in the catalog using Marvel API where applicable.

        Args:
            output_path: Path to save enriched catalog (optional)
            filter_type: Only process items of this type (default: 'comic')
            limit: Maximum number of items to process (for testing)

        Returns:
            List of enriched comic entries
        """
        enriched_items = []

        try:
            with open(self.catalog_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                items = list(reader)

            print(f"Processing {len(items)} catalog entries...")

            for idx, item in enumerate(items):
                if limit and idx >= limit:
                    break

                # Filter by type
                if filter_type and item.get('type', '').lower() != filter_type.lower():
                    enriched_items.append(item)
                    continue

                print(f"\n[{idx + 1}/{len(items)}] Processing: {item.get('title', 'Unknown')}")
                enriched = self.enrich_comic_entry(item)
                enriched_items.append(enriched)

            # Save to output file if specified
            if output_path:
                self._save_catalog(enriched_items, output_path)
                print(f"\nEnriched catalog saved to: {output_path}")

            return enriched_items

        except FileNotFoundError:
            print(f"Catalog file not found: {self.catalog_path}")
            return []
        except Exception as e:
            print(f"Error processing catalog: {e}")
            return []

    def _save_catalog(self, items: List[Dict[str, Any]], output_path: str):
        """Save enriched items to CSV file."""
        if not items:
            return

        fieldnames = items[0].keys()

        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(items)


def main():
    """Test the comic enricher with sample data."""

    # Test data
    test_comics = [
        {
            'id': 'test_001',
            'type': 'comic',
            'title': 'Amazing Spider-Man #300',
            'author': '',
            'volume': '300',
            'series': '',
            'publisher': '',
            'year': '',
            'language': 'English',
            'country': 'USA',
            'copies': '1',
            'cover_type': '',
            'genre': '',
            'description': '',
            'cover_url': '',
            'enrichment_status': '',
            'enrichment_date': '',
            'enrichment_source': '',
            'search_query': '',
            'source_row': '',
            'price': ''
        },
        {
            'id': 'test_002',
            'type': 'comic',
            'title': 'The Sandman #1',
            'author': 'Neil Gaiman',
            'volume': '1',
            'series': 'The Sandman',
            'publisher': 'DC Comics',
            'year': '1989',
            'language': 'English',
            'country': 'USA',
            'copies': '1',
            'cover_type': '',
            'genre': '',
            'description': '',
            'cover_url': '',
            'enrichment_status': '',
            'enrichment_date': '',
            'enrichment_source': '',
            'search_query': '',
            'source_row': '',
            'price': ''
        }
    ]

    print("Testing Comic Enricher\n" + "=" * 50)

    enricher = ComicEnricher('output/csv/books_manga_comics_catalog.csv')

    for comic in test_comics:
        print(f"\n\nTesting: {comic['title']}")
        print("-" * 50)
        result = enricher.enrich_comic_entry(comic)

        print("\nEnrichment Result:")
        print(f"  Status: {result.get('enrichment_status', 'N/A')}")
        print(f"  Source: {result.get('enrichment_source', 'N/A')}")
        print(f"  Series: {result.get('series', 'N/A')}")
        print(f"  Publisher: {result.get('publisher', 'N/A')}")
        print(f"  Description: {result.get('description', 'N/A')[:100]}...")


if __name__ == "__main__":
    main()
