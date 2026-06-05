import os
import re
import urllib.request
import glob
import random

BASE_DIR = '/Users/bytedance/Desktop/AI/Fusion card design'
ASSETS_DIR = os.path.join(BASE_DIR, 'designs/assets/images')
os.makedirs(ASSETS_DIR, exist_ok=True)

# 1. Download any remaining Unsplash links
def download_and_replace():
    files_to_check = []
    for root, _, files in os.walk(BASE_DIR):
        if 'node_modules' in root or '.git' in root:
            continue
        for f in files:
            if f.endswith('.html') or f.endswith('.css'):
                files_to_check.append(os.path.join(root, f))
                
    unsplash_pattern = re.compile(r'https://images\.unsplash\.com/photo-([a-zA-Z0-9\-]+)[^"\'\)\s]*')
    
    for filepath in files_to_check:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        matches = unsplash_pattern.findall(content)
        if not matches:
            continue
            
        print(f"Found unsplash links in {filepath}")
        for match in set(matches):
            photo_id = match
            # Find the full url
            full_url_match = re.search(rf'https://images\.unsplash\.com/photo-{photo_id}[^"\'\)\s]*', content)
            if not full_url_match:
                continue
            full_url = full_url_match.group(0)
            
            local_filename = f"img_{photo_id}.jpg"
            local_filepath = os.path.join(ASSETS_DIR, local_filename)
            
            if not os.path.exists(local_filepath):
                print(f"Downloading {full_url} to {local_filename}...")
                try:
                    # Request with User-Agent
                    req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req) as response, open(local_filepath, 'wb') as out_file:
                        out_file.write(response.read())
                except Exception as e:
                    print(f"Failed to download {full_url}: {e}")
                    # If it fails, we'll assign a random existing image later
                    
            # Determine relative path
            # If filepath is in designs/standalone/verticals/ -> ../../assets/images/
            # If filepath is in designs/standalone/ -> ../assets/images/
            # If filepath is in designs/verticals/ -> ../assets/images/
            # If filepath is in designs/ -> assets/images/
            # If filepath is in BASE_DIR -> designs/assets/images/
            rel_path = os.path.relpath(ASSETS_DIR, os.path.dirname(filepath))
            local_url = f"{rel_path}/{local_filename}"
            
            # Replace all occurrences of this full_url
            # Need to be careful with escaping in CSS
            content = content.replace(full_url, local_url)
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

download_and_replace()
