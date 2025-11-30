from src.lyrics_scraper import LyricsScraper
import polars as pl

def main():
    """Example usage of the LyricsScraper."""
    
    scraper = LyricsScraper()
    
    df = pl.read_csv("data/caparezza_songs.csv")
    songs = df.select(["title", "url"]).to_dicts()
        
    print(f"=== Scraping {len(songs)} URLs ===\n")
    results = scraper.scrape_multiple_urls([song["url"] for song in songs], delay=1.0)
   
    for song, url in zip(songs, results.keys()):
        lyrics = results[url]
        if lyrics:
            filename = f"data/lyrics/{song['title'].replace(' ', '_')}.txt"
            scraper.save_lyrics(lyrics, filename)
            print(f"✓ Saved lyrics for '{song['title']}' to {filename}\n")
        else:
            print(f"✗ Failed to scrape lyrics for '{song['title']}' from {url}\n")
    
if __name__ == "__main__":
    main()