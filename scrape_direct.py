# %% 
from bs4 import BeautifulSoup
import requests
import os
import time

def get_links_from_page(page_url: str) -> dict:
    """
    Read through a webpage and extract all links, grouped by album.
    
    Args:
        page_url: The URL of the webpage containing links
        
    Returns:
        Dictionary with album names as keys and lists of URLs as values
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(page_url, headers=headers, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the main listAlbum container
    list_album = soup.find('div', id='listAlbum')
    if not list_album:
        return {}
    
    grouped_links = {}
    current_album = None
    current_links = []
    
    # Iterate through direct children of listAlbum
    for child in list_album.children:
        # Skip text nodes and empty strings
        if isinstance(child, str):
            continue
        
        # Get element name and class safely
        elem_name = getattr(child, 'name', None)
        elem_class = getattr(child, 'get', lambda x: None)('class') or []
        
        # Check if this is an album header
        if elem_name == 'div' and 'album' in elem_class:
            # Save previous album if it exists
            if current_album is not None:
                grouped_links[current_album] = current_links
            
            # Start new album
            current_album = child.get_text(strip=True)
            current_links = []
        
        # Check if this is a song item
        elif elem_name == 'div' and 'listalbum-item' in elem_class:
            # Find the <a> tag within the item
            if hasattr(child, 'find'):
                link_tag = child.find('a', href=True)  # type: ignore
                if link_tag and current_album is not None:
                    href = str(link_tag['href'])
                    # Convert relative URLs to absolute URLs if needed
                    if href.startswith('/'):
                        base_url = '/'.join(page_url.split('/')[:3])
                        href = base_url + href
                    current_links.append(href)
    
    # Don't forget the last album
    if current_album is not None:
        grouped_links[current_album] = current_links
    
    return grouped_links


def get_song_title_and_lyrics(lyrics_url: str) -> tuple:
    """
    Extract the song title and lyrics from a song page.
    
    Args:
        lyrics_url: The URL of the lyrics page
        
    Returns:
        Tuple of (song_title, lyrics_text) or (None, None) if not found
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(lyrics_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {lyrics_url}: {e}")
        return None, None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the song title
    # Look for the <b> tag with the song title (appears before the lyrics div)
    title_tag = soup.find('b')
    song_title = title_tag.get_text(strip=True) if title_tag else None
    
    if not song_title:
        print(f"Could not find song title in {lyrics_url}")
        return None, None
    
    # Find the lyrics - they're in an unlabeled <div> that follows the song title
    # The lyrics contain <br> tags separating lines
    divs = soup.find_all('div')
    lyrics_text = None
    
    for div in divs:
        # Check if this div contains lyrics (should have multiple <br> tags)
        br_tags = div.find_all('br')
        if len(br_tags) > 5:  # Lyrics typically have many line breaks
            # Get the text, preserving line breaks
            lyrics_text = div.get_text('\n')
            break
    
    if not lyrics_text:
        print(f"Could not find lyrics in {lyrics_url}")
        return song_title, None
    
    return song_title, lyrics_text


def scrape_and_save_all_lyrics(main_page_url: str, output_dir: str = "data/lyrics") -> None:
    """
    Scrape all lyrics from albums and save them to organized folders.
    
    Args:
        main_page_url: The URL of the main page containing album links
        output_dir: Base directory to save lyrics (will create album subdirectories)
    """
    # Get all links grouped by album
    print(f"Fetching album links from {main_page_url}...")
    albums_dict = get_links_from_page(main_page_url)
    
    if not albums_dict:
        print("No albums found!")
        return
    
    print(f"Found {len(albums_dict)} albums\n")
    
    # Process each album
    for album_name, song_urls in albums_dict.items():
        # Create album folder
        album_folder = os.path.join(output_dir, album_name)
        os.makedirs(album_folder, exist_ok=True)
        
        print(f"Processing album: {album_name}")
        print(f"  Found {len(song_urls)} songs")
        
        # Scrape lyrics for each song
        for i, song_url in enumerate(song_urls, 1):
            try:
                print(f"  [{i}/{len(song_urls)}] Scraping {song_url}...")
                
                song_title, lyrics = get_song_title_and_lyrics(song_url)
                
                if song_title and lyrics:
                    # Create a filename from the song title
                    filename = f"{song_title}.txt"
                    # Replace invalid filename characters
                    for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
                        filename = filename.replace(char, '_')
                    
                    filepath = os.path.join(album_folder, filename)
                    
                    # Save lyrics to file
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(lyrics)
                    
                    print(f"      ✓ Saved: {filename}")
                else:
                    print("      ✗ Could not extract lyrics")
                
                # Be respectful to the server - add delay between requests
                if i < len(song_urls):
                    time.sleep(1)
                    
            except (requests.RequestException, OSError) as e:
                print(f"      ✗ Error: {e}")
        
        print()
    
    print(f"Done! Lyrics saved to {output_dir}")
# %%
url = "https://www.azlyrics.com/c/caparezza.html"

scrape_and_save_all_lyrics(url)