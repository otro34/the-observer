"""
Marvel API Client for The Observer

This module provides a client for fetching comic metadata from the Marvel API.
It handles authentication, rate limiting, and data extraction for comic cataloging.

Documentation: https://developer.marvel.com/documentation/generalinfo
"""

import hashlib
import time
import requests
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode
import os
from dotenv import load_dotenv


class MarvelAPIClient:
    """Client for interacting with the Marvel Comics API."""

    BASE_URL = "https://gateway.marvel.com/v1/public"

    def __init__(self, public_key: Optional[str] = None, private_key: Optional[str] = None):
        """
        Initialize the Marvel API client.

        Args:
            public_key: Marvel API public key (defaults to env variable)
            private_key: Marvel API private key (defaults to env variable)
        """
        # Load from .env.marvel if keys not provided
        if not public_key or not private_key:
            # Try multiple possible locations for .env.marvel
            possible_paths = [
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests', '.env.marvel'),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.marvel'),
                '.env.marvel'
            ]

            for env_path in possible_paths:
                if os.path.exists(env_path):
                    load_dotenv(env_path)
                    break

        self.public_key = public_key or os.getenv('MARVEL_PUBLIC_KEY')
        self.private_key = private_key or os.getenv('MARVEL_PRIVATE_KEY')

        if not self.public_key or not self.private_key:
            raise ValueError("Marvel API keys not provided. Set MARVEL_PUBLIC_KEY and MARVEL_PRIVATE_KEY")

        self.session = requests.Session()
        self.session.headers.update({
            'Accept-Encoding': 'gzip',
            'User-Agent': 'TheObserver/1.0 (Collection Cataloging System)'
        })

    def _generate_auth_params(self) -> Dict[str, str]:
        """
        Generate authentication parameters for Marvel API requests.

        Returns:
            Dictionary with ts, apikey, and hash parameters
        """
        ts = str(int(time.time()))

        # Hash = MD5(timestamp + private_key + public_key)
        hash_string = f"{ts}{self.private_key}{self.public_key}"
        hash_value = hashlib.md5(hash_string.encode()).hexdigest()

        return {
            'ts': ts,
            'apikey': self.public_key,
            'hash': hash_value
        }

    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make an authenticated request to the Marvel API.

        Args:
            endpoint: API endpoint (e.g., '/comics', '/characters')
            params: Additional query parameters

        Returns:
            JSON response data

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        if params is None:
            params = {}

        # Add authentication parameters
        auth_params = self._generate_auth_params()
        params.update(auth_params)

        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Marvel API request failed: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise

    def search_comics(
        self,
        title: Optional[str] = None,
        issue_number: Optional[int] = None,
        series_id: Optional[int] = None,
        format: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search for comics by various criteria.

        Args:
            title: Comic title to search for
            issue_number: Issue number
            series_id: Series ID to filter by
            format: Comic format (e.g., 'comic', 'trade paperback', 'hardcover')
            limit: Number of results to return (max 100)
            offset: Pagination offset

        Returns:
            List of comic dictionaries with metadata
        """
        params = {
            'limit': min(limit, 100),
            'offset': offset
        }

        if title:
            params['titleStartsWith'] = title
        if issue_number is not None:
            params['issueNumber'] = issue_number
        if series_id is not None:
            params['series'] = series_id
        if format:
            params['format'] = format

        response = self._make_request('/comics', params)
        return response.get('data', {}).get('results', [])

    def get_comic_by_id(self, comic_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific comic.

        Args:
            comic_id: Marvel comic ID

        Returns:
            Comic metadata dictionary or None if not found
        """
        try:
            response = self._make_request(f'/comics/{comic_id}')
            results = response.get('data', {}).get('results', [])
            return results[0] if results else None
        except requests.exceptions.RequestException:
            return None

    def search_series(
        self,
        title: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search for comic series by title.

        Args:
            title: Series title to search for
            limit: Number of results to return (max 100)
            offset: Pagination offset

        Returns:
            List of series dictionaries
        """
        params = {
            'limit': min(limit, 100),
            'offset': offset
        }

        if title:
            params['titleStartsWith'] = title

        response = self._make_request('/series', params)
        return response.get('data', {}).get('results', [])

    def extract_comic_metadata(self, comic_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant metadata from Marvel API comic response for cataloging.

        Args:
            comic_data: Raw comic data from Marvel API

        Returns:
            Structured metadata dictionary for The Observer catalog
        """
        # Extract creators
        creators_data = comic_data.get('creators', {}).get('items', [])
        writers = [c['name'] for c in creators_data if c.get('role') == 'writer']

        # Extract cover image
        thumbnail = comic_data.get('thumbnail', {})
        cover_url = None
        if thumbnail.get('path') and thumbnail.get('extension'):
            cover_url = f"{thumbnail['path']}.{thumbnail['extension']}"

        # Extract prices
        prices = comic_data.get('prices', [])
        print_price = None
        for price_obj in prices:
            if price_obj.get('type') == 'printPrice':
                print_price = price_obj.get('price')
                break

        return {
            'marvel_id': comic_data.get('id'),
            'title': comic_data.get('title'),
            'issue_number': comic_data.get('issueNumber'),
            'series_name': comic_data.get('series', {}).get('name'),
            'description': comic_data.get('description', ''),
            'page_count': comic_data.get('pageCount'),
            'format': comic_data.get('format'),
            'isbn': comic_data.get('isbn', ''),
            'upc': comic_data.get('upc', ''),
            'writers': ', '.join(writers) if writers else '',
            'on_sale_date': self._extract_on_sale_date(comic_data),
            'cover_url': cover_url,
            'print_price': print_price,
            'marvel_url': next((url['url'] for url in comic_data.get('urls', [])
                               if url.get('type') == 'detail'), None)
        }

    def _extract_on_sale_date(self, comic_data: Dict[str, Any]) -> Optional[str]:
        """Extract the on-sale date from comic data."""
        dates = comic_data.get('dates', [])
        for date_obj in dates:
            if date_obj.get('type') == 'onsaleDate':
                return date_obj.get('date', '').split('T')[0]  # Get YYYY-MM-DD
        return None

    def enrich_comic_from_spine_text(
        self,
        title: str,
        issue_number: Optional[int] = None,
        series_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Enrich comic metadata from spine text extracted by OCR.

        This is the main method for integrating with The Observer's pipeline.

        Args:
            title: Comic title from spine OCR
            issue_number: Issue number if detected
            series_name: Series name if different from title

        Returns:
            Enriched metadata dictionary or None if not found
        """
        # Try searching by series name first if provided
        search_title = series_name if series_name else title

        try:
            # Search for matching comics
            results = self.search_comics(
                title=search_title,
                issue_number=issue_number,
                limit=5
            )

            if not results:
                return None

            # Return the best match (first result)
            best_match = results[0]
            return self.extract_comic_metadata(best_match)

        except requests.exceptions.RequestException as e:
            print(f"Failed to enrich comic '{title}': {e}")
            return None


def test_marvel_client():
    """Test function to verify Marvel API integration."""
    try:
        client = MarvelAPIClient()

        # Test 1: Search for a popular comic
        print("Test 1: Searching for 'Spider-Man' comics...")
        results = client.search_comics(title="Spider-Man", limit=3)
        print(f"Found {len(results)} results")

        if results:
            print(f"\nFirst result: {results[0].get('title')}")
            metadata = client.extract_comic_metadata(results[0])
            print(f"Extracted metadata: {metadata}")

        # Test 2: Search for a series
        print("\n\nTest 2: Searching for 'X-Men' series...")
        series_results = client.search_series(title="X-Men", limit=3)
        print(f"Found {len(series_results)} series")

        if series_results:
            print(f"First series: {series_results[0].get('title')}")

        print("\n\nMarvel API integration successful!")
        return True

    except Exception as e:
        print(f"Marvel API test failed: {e}")
        return False


if __name__ == "__main__":
    test_marvel_client()
