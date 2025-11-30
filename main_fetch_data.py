# %%
import sys
import csv
from pathlib import Path
from src.request_script import APIRequester


def fetch_artist_songs(requester, artist_id: int, per_page: int = 50):
    """
    Fetch all songs for a given artist ID from Genius API.
    
    Args:
        requester: APIRequester instance
        artist_id: The Genius artist ID
        per_page: Number of results per page (max 50)
        
    Returns:
        List of all songs by the artist
    """
    all_songs = []
    page = 1
    
    while True:
        print(f"→ Fetching page {page}...")
        
        # Fetch songs for this page
        response = requester.request_json(
            f'https://api.genius.com/artists/{artist_id}/songs',
            credential_name='genius_key',
            params={'per_page': per_page, 'page': page}
        )
        
        if not response.get('response'):
            break
        
        songs = response['response'].get('songs', [])
        if not songs:
            break
        
        all_songs.extend(songs)
        
        # Check if there are more pages
        pagination = response['response'].get('next_page')
        if pagination is None:
            break
        
        page += 1
    
    return all_songs


def save_songs_to_csv(songs: list, filename: str = "artist_songs.csv"):
    """
    Save songs data to a CSV file.
    
    Args:
        songs: List of song dictionaries from Genius API
        filename: Output CSV filename
    """
    if not songs:
        print("No songs to save")
        return
    
    # Extract relevant fields
    fieldnames = ['title', 'url', 'primary_artist']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for song in songs:
            writer.writerow({
                'title': song.get('title', ''),
                'url': song.get('url', ''),
                'primary_artist': song.get('primary_artist', {}).get('name', '')
            })
    
    print(f"✓ Saved {len(songs)} songs to {filename}")


def main():
    """Fetch and display all songs for artist ID 24580 (Caparezza)."""
    
    # Get workspace directory from command line or use current directory
    workspace_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    # Initialize requester
    requester = APIRequester(workspace_dir)
    
    print("\n=== Available Credentials ===")
    if requester.credentials:
        for name in requester.credentials.keys():
            print(f"  • {name}")
    
    # Fetch all songs for artist ID 24580 (Caparezza)
    artist_id = 24580
    print(f"\n=== Fetching all songs for Artist ID {artist_id} ===")
    
    songs = fetch_artist_songs(requester, artist_id)
    
    print(f"\n✓ Found {len(songs)} songs:\n")
    for i, song in enumerate(songs, 1):
        print(f"{i}. {song['title']}")
        print(f"   URL: {song['url']}")
        print()
    
    # Save to CSV
    save_songs_to_csv(songs, "artist_songs.csv")


if __name__ == "__main__":
    main()