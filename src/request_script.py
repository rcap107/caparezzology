#!/usr/bin/env python3
"""
API Request Script

This script sends GET requests to a remote API using credentials stored in *.id files.
Supports multiple credential types and flexible API endpoints.
"""

import os
import sys
import requests
from pathlib import Path
from typing import Dict, Optional
import json
from datetime import datetime, timedelta
import base64
import time


class APIRequester:
    """Handle API requests with credential management."""
    
    def __init__(self, workspace_dir: str = "."):
        """
        Initialize the API Requester.
        
        Args:
            workspace_dir: Directory containing .id credential files
        """
        self.workspace_dir = Path(workspace_dir)
        self.credentials = self._load_credentials()
    
    def _load_credentials(self) -> Dict[str, str]:
        """
        Load all credentials from *.id files in the workspace.
        
        Returns:
            Dictionary mapping credential names to their values
        """
        credentials = {}
        
        for id_file in self.workspace_dir.glob("*.id"):
            credential_name = id_file.stem  # Filename without extension
            try:
                with open(id_file, 'r') as f:
                    value = f.read().strip()
                    credentials[credential_name] = value
                    print(f"✓ Loaded credential: {credential_name}")
            except Exception as e:
                print(f"✗ Error loading {id_file.name}: {e}", file=sys.stderr)
        
        if not credentials:
            print("⚠ No credential files (.id) found in workspace", file=sys.stderr)
        
        return credentials
    
    def get_credential(self, name: str) -> Optional[str]:
        """
        Get a specific credential by name.
        
        Args:
            name: Name of the credential (without .id extension)
            
        Returns:
            Credential value or None if not found
        """
        return self.credentials.get(name)
    
    def request(
        self,
        url: str,
        credential_name: Optional[str] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: int = 10,
        use_query_param: bool = True
    ) -> requests.Response:
        """
        Send a GET request to the API.
        
        Args:
            url: API endpoint URL
            credential_name: Name of credential to use (e.g., 'genius_key', 'client')
            params: Query parameters to include in request
            headers: Additional headers to include
            timeout: Request timeout in seconds
            use_query_param: If True, add credential as query parameter (access_token)
                           If False, add credential to headers
            
        Returns:
            Response object from requests library
            
        Raises:
            ValueError: If credential not found
            requests.RequestException: If request fails
        """
        # Set up headers and params
        request_headers = headers or {}
        request_params = params or {}
        
        # Add credential if specified
        if credential_name:
            credential = self.get_credential(credential_name)
            if not credential:
                raise ValueError(f"Credential '{credential_name}' not found")
            
            if use_query_param:
                # Add credential as query parameter
                request_params['access_token'] = credential
            else:
                # Add credential to headers
                if credential_name.lower() in ['genius_key', 'api_key', 'token']:
                    request_headers['Authorization'] = f'Bearer {credential}'
                elif credential_name.lower() in ['client', 'client_id']:
                    request_headers['X-Client-ID'] = credential
                else:
                    # Generic header as fallback
                    request_headers['Authorization'] = credential
        
        # Make request
        print(f"→ GET {url}")
        if request_params:
            print(f"  Parameters: {request_params}")
        
        response = requests.get(
            url,
            params=request_params,
            headers=request_headers,
            timeout=timeout
        )
        
        print(f"← Status: {response.status_code}")
        
        return response
    
    def request_json(
        self,
        url: str,
        credential_name: Optional[str] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: int = 10,
        use_query_param: bool = True
    ) -> Dict:
        """
        Send a GET request and parse response as JSON.
        
        Args:
            Same as request()
            
        Returns:
            Parsed JSON response
            
        Raises:
            ValueError: If credential not found
            requests.RequestException: If request fails
            json.JSONDecodeError: If response is not valid JSON
        """
        response = self.request(url, credential_name, params, headers, timeout, use_query_param)
        response.raise_for_status()
        return response.json()
  
    def request_search(
        self,
        artist_name: str,
        credential_name: str = 'genius_key',):
        """
        Search for an artist using the Genius API.
        Args:
            artist_name: Name of the artist to search for
            credential_name: Name of the credential to use
        Returns:
            Parsed JSON response from the search
        """
        return self.request_json(
            'https://api.genius.com/search',
            credential_name=credential_name,
            params={'q': artist_name}
        )
    
    def request_artist(
        self,
        artist_id: str,
        credential_name: str = 'genius_key',):
        """
        Get artist details using the Genius API.
        Args:
            artist_id: ID of the artist
            credential_name: Name of the credential to use
        Returns:
            Parsed JSON response with artist details
        """
        url = f'https://api.genius.com/artists/{artist_id}'
        return self.request_json(
            url,
            credential_name=credential_name
        )
    
    def request_songs_by_artist(
        self,
        artist_id: str,
        per_page: int = 20,
        page: int = 1,
        credential_name: str = 'genius_key',):
        """
        Get songs by an artist using the Genius API.
        Args:
            artist_id: ID of the artist
            per_page: Number of songs per page
            page: Page number to retrieve
            credential_name: Name of the credential to use
        Returns:
            Parsed JSON response with songs by the artist
        """
        url = f'https://api.genius.com/artists/{artist_id}/songs'
        params = {
            'per_page': per_page,
            'page': page
        }
        return self.request_json(
            url,
            credential_name=credential_name,
            params=params
        )
        
    def request_all_songs_by_artist(
        self,
        artist_id: str,
        credential_name: str = 'genius_key',):
        """
        Get all songs by an artist using the Genius API.
        Args:
            artist_id: ID of the artist
            credential_name: Name of the credential to use
        Returns:
            List of all songs by the artist
        """
        all_songs = []
        page = 1
        while True:
            response = self.request_songs_by_artist(
                artist_id,
                per_page=50,
                page=page,
                credential_name=credential_name
            )
            songs = response.get('response', {}).get('songs', [])
            if not songs:
                break
            all_songs.extend(songs)
            page += 1
            time.sleep(0.5)  # Rate limit protection
        return all_songs
    

  