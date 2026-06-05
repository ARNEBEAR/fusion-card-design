import os
import re
import random

BASE_DIR = '/Users/bytedance/Desktop/AI/Fusion card design'
ASSETS_DIR = os.path.join(BASE_DIR, 'designs/assets/images')

valid_images = [f for f in os.listdir(ASSETS_DIR) if f.endswith('.jpg')]

unsplash_pattern = re.compile(r'https://images\.unsplash\.com/photo-[^"\'\)\s]+')

for root, _, files in os.walk(BASE_DIR):
    if 'node_modules' in root or '.git' in root:
        continue
    for f in files:
        if f.endswith('.html') or f.endswith('.css'):
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                
            matches = unsplash_pattern.findall(content)
            if matches:
                # determine relative path to assets/images
                rel_path = os.path.relpath(ASSETS_DIR, os.path.dirname(filepath))
                
                for match in set(matches):
                    new_img = random.choice(valid_images)
                    local_url = f"{rel_path}/{new_img}"
                    content = content.replace(match, local_url)
                    
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(content)
                print(f"Fixed leftover unsplash links in {os.path.basename(filepath)}")
