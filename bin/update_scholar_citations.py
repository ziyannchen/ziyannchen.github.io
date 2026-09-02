#!/usr/bin/env python
"""
Script to fetch citation counts from Google Scholar and store them in _data/citations.yml
This script is designed to be run by a GitHub Action.
"""

import os
import sys
import tempfile
import yaml
import time
import random
from datetime import datetime
from scholarly import scholarly

# Configuration - will be read from _data/socials.yml
CONFIG_FILE = "_config.yml"
SOCIALS_FILE = "_data/socials.yml"
OUTPUT_FILE = "_data/citations.yml"
MAX_RETRIES = 3

def get_scholar_id_from_config():
    """
    Get Google Scholar ID from Jekyll _data/socials.yml file
    """
    # First try to get from socials.yml
    try:
        with open(SOCIALS_FILE, 'r', encoding='utf-8') as f:
            socials = yaml.safe_load(f)
        
        if socials and isinstance(socials, dict):
            scholar_id = socials.get('scholar_userid')
            if scholar_id:
                print(f"Found Google Scholar ID in socials.yml: {scholar_id}")
                return scholar_id
    except Exception as e:
        print(f"Warning: Could not read {SOCIALS_FILE}: {e}")
    
    # Fallback to _config.yml
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Try different possible locations for scholar ID
        scholar_id = None
        
        # Check if there's a socials section
        if 'socials' in config and isinstance(config['socials'], dict):
            scholar_id = config['socials'].get('scholar_userid') or config['socials'].get('google_scholar_id')
        
        # Check if there's a scholar section  
        if not scholar_id and 'scholar' in config and isinstance(config['scholar'], dict):
            scholar_id = config['scholar'].get('scholar_userid') or config['scholar'].get('google_scholar_id')
        
        # Check top-level config
        if not scholar_id:
            scholar_id = config.get('scholar_userid') or config.get('google_scholar_id')
        
        if scholar_id:
            print(f"Found Google Scholar ID in config: {scholar_id}")
            return scholar_id
    except Exception as e:
        print(f"Warning: Could not read {CONFIG_FILE}: {e}")
    
    print("Error: Google Scholar ID not found in _data/socials.yml or _config.yml")
    print("Please add 'scholar_userid: YOUR_ID' to your _data/socials.yml")
    return None

# Create data directory if it doesn't exist
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

def get_scholar_citations():
    """
    Fetch citation data from Google Scholar for all papers by the specified author
    """
    # Get Scholar ID from config
    scholar_user_id = get_scholar_id_from_config()
    if not scholar_user_id:
        print("Error: Cannot proceed without Google Scholar ID")
        return None
    
    print(f"Fetching citations for Google Scholar ID: {scholar_user_id}")
    
    # Initialize citation data structure
    citation_data = {
        'metadata': {
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'scholar_userid': scholar_user_id
        },
        'papers': {}  # Initialize as empty dict, not None
    }
    
    # Try to load existing data first to avoid unnecessary requests
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r') as f:
                existing_data = yaml.safe_load(f)
                if existing_data and isinstance(existing_data, dict):
                    # Keep existing metadata if available
                    if 'papers' in existing_data and existing_data['papers'] is not None:
                        citation_data['papers'] = existing_data['papers']
        except Exception as e:
            print(f"Warning: Could not read existing citation data: {e}")

    # Fetch author data with retries
    author_data = None
    for attempt in range(MAX_RETRIES):
        try:
            author = scholarly.search_author_id(scholar_user_id)
            author_data = scholarly.fill(author)
            break
        except Exception as e:
            wait_time = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff
            print(f"Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {wait_time:.1f} seconds...")
                time.sleep(wait_time)
            else:
                print("All retries failed. Keeping existing data unchanged.")
                return None
    
    if not author_data:
        print("Could not fetch author data. Keeping existing data unchanged.")
        return None
        
    # Process publications
    processed_publications = 0
    if 'publications' in author_data and isinstance(author_data['publications'], list):
        for pub in author_data['publications']:
            try:
                # Get publication ID
                pub_id = None
                if 'pub_id' in pub and pub['pub_id']:
                    pub_id = pub['pub_id']
                elif 'author_pub_id' in pub and pub['author_pub_id']:
                    pub_id = pub['author_pub_id']
                
                if not pub_id:
                    print(f"Warning: No ID found for publication: {pub.get('bib', {}).get('title', 'Unknown')}")
                    continue
                
                # Get publication metadata
                title = "Unknown Title"
                year = "Unknown Year"
                citations = None
                
                if 'bib' in pub:
                    if 'title' in pub['bib']:
                        title = pub['bib']['title']
                    if 'pub_year' in pub['bib']:
                        year = pub['bib']['pub_year']
                
                if 'num_citations' not in pub or not isinstance(pub['num_citations'], int):
                    print(f"Warning: No valid citation count for {title}; keeping any existing record")
                    continue
                citations = pub['num_citations']
                
                print(f"Found: {title} ({year}) - Citations: {citations}")
                
                # Store citation data
                citation_data['papers'][pub_id] = {
                    'title': title,
                    'year': year,
                    'citations': citations
                }
                processed_publications += 1
                
            except Exception as e:
                print(f"Error processing publication: {str(e)}")
    else:
        print("No valid publications found in author data. Keeping existing data unchanged.")
        return None

    if processed_publications == 0:
        print("No publications with valid citation counts were fetched. Keeping existing data unchanged.")
        return None
    
    # Save to YAML file
    try:
        output_dir = os.path.dirname(OUTPUT_FILE) or "."
        temp_fd, temp_path = tempfile.mkstemp(
            dir=output_dir,
            prefix=".citations.",
            suffix=".tmp",
            text=True,
        )
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                yaml.safe_dump(citation_data, f, default_flow_style=False, sort_keys=False)
            os.replace(temp_path, OUTPUT_FILE)
        except Exception:
            try:
                os.unlink(temp_path)
            except OSError:
                pass
            raise
        print(f"Citation data saved to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error saving citation data: {str(e)}. Existing data was not replaced.")
        return None
    
    return citation_data

if __name__ == "__main__":
    sys.exit(0 if get_scholar_citations() is not None else 1)
