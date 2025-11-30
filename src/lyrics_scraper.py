#!/usr/bin/env python3
"""
Lyrics Scraper

This script scrapes lyrics from webpages where lyrics are contained
in <div> elements with the 'data-lyrics-container' attribute.
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional, List
import time


class LyricsScraper:
    """Scrape lyrics from webpages."""
    
    def __init__(self, genius_key: Optional[str] = None, timeout: int = 10):
        """
        Initialize the lyrics scraper.
        
        Args:
            genius_key: Genius API key for authorization header
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.genius_key = genius_key
        # Set a user agent to avoid being blocked
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Add authorization header if genius key provided
        if genius_key:
            self.headers['Authorization'] = f'Bearer {genius_key}'
            print("✓ Authorization header set with Genius API key")
    
    def scrape_lyrics(self, url: str, delay: float = 0) -> Optional[str]:
        """
        Scrape lyrics from a URL.
        
        Args:
            url: URL of the lyrics webpage
            delay: Delay in seconds before making request (for rate limiting)
            
        Returns:
            Combined lyrics text or None if not found
            
        Raises:
            requests.RequestException: If request fails
        """
        if delay > 0:
            print(f"⏳ Waiting {delay}s before scraping...")
            time.sleep(delay)
        
        print(f"→ Scraping: {url}")
        
        # Fetch the webpage
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all lyrics containers
        lyrics_divs = soup.find_all('div', {'data-lyrics-container': True})
        
        if not lyrics_divs:
            print("✗ No lyrics containers found")
            return None
        
        print(f"✓ Found {len(lyrics_divs)} lyrics container(s)")
        
        # Extract text from all containers
        lyrics_lines = []
        for div in lyrics_divs:
            # Get text and preserve line breaks
            text = div.get_text(separator='\n', strip=True)
            if text:
                lyrics_lines.append(text)
        
        # Combine all lyrics
        lyrics = '\n\n'.join(lyrics_lines)
        
        return lyrics if lyrics else None
    
    def scrape_multiple_urls(
        self,
        urls: List[str],
        delay: float = 1.0,
        stop_on_error: bool = False
    ) -> dict:
        """
        Scrape lyrics from multiple URLs.
        
        Args:
            urls: List of URLs to scrape
            delay: Delay between requests in seconds
            stop_on_error: If True, stop on first error; if False, continue
            
        Returns:
            Dictionary mapping URLs to their lyrics
        """
        results = {}
        
        for i, url in enumerate(urls):
            try:
                # Add delay before each request (except the first)
                request_delay = delay if i > 0 else 0
                lyrics = self.scrape_lyrics(url, delay=request_delay)
                results[url] = lyrics
            except requests.RequestException as e:
                print(f"✗ Error scraping {url}: {e}")
                if stop_on_error:
                    break
                results[url] = None
        
        return results
    
    def save_lyrics(self, lyrics: str, filename: str) -> None:
        """
        Save lyrics to a text file.
        
        Args:
            lyrics: Lyrics text to save
            filename: Output filename
        """
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(lyrics)
        print(f"✓ Saved lyrics to {filename}")

