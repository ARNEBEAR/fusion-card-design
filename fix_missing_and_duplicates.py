import os
import re
import random

BASE_DIR = '/Users/bytedance/Desktop/AI/Fusion card design'
ASSETS_DIR = os.path.join(BASE_DIR, 'designs/assets/images')

# 1. Get list of all valid images
valid_images = [f for f in os.listdir(ASSETS_DIR) if f.endswith('.jpg')]

print(f"Found {len(valid_images)} valid images in {ASSETS_DIR}")

# Regex to find img_XXXXX.jpg
img_pattern = re.compile(r'img_[a-zA-Z0-9\-]+\.jpg')

files_to_check = []
for root, _, files in os.walk(BASE_DIR):
    if 'node_modules' in root or '.git' in root:
        continue
    for f in files:
        if f.endswith('.html') or f.endswith('.css'):
            files_to_check.append(os.path.join(root, f))

# 2. Fix missing images globally
for filepath in files_to_check:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    matches = img_pattern.findall(content)
    changed = False
    
    for match in set(matches):
        if match not in valid_images:
            # Replace with a random valid image
            new_img = random.choice(valid_images)
            print(f"[{os.path.basename(filepath)}] Replacing missing {match} -> {new_img}")
            content = content.replace(match, new_img)
            changed = True
            
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

# 3. Fix S4 duplicate sets and hotel S4 first image
for filepath in files_to_check:
    filename = os.path.basename(filepath)
    if not filename.endswith('.html'):
        continue
        
    if 's4' in filename or 's3' in filename or 's2' in filename:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
            
        # specifically for s4-a-hotel-video-first.html, ensure the first UGC uses the hotel pool
        if filename == 's4-a-hotel-video-first.html':
            # find the first bg: '...' in ugc array
            content = re.sub(
                r"(ugc:\[\s*\{bg:'[^']*?img_)[a-zA-Z0-9\-]+(\.jpg')",
                r"\g<1>1542314831-068cd1dbfeeb\g<2>",
                content, count=1
            )
            
            # also replace the blurred background
            content = re.sub(
                r'(background:#000 center/cover url\("[^"]*?img_)[a-zA-Z0-9\-]+(\.jpg"\);)',
                r'\g<1>1542314831-068cd1dbfeeb\g<2>',
                content, count=1
            )
        
        # fix duplicated images in sets = { ugc: [...], official: [...] }
        # find all bg: '...img_XXX.jpg'
        bg_pattern = re.compile(r"bg:'([^']*?img_[a-zA-Z0-9\-]+\.jpg)'")
        
        def replace_with_random_unique(match):
            return f"bg:'{match.group(1).rsplit('img_', 1)[0]}{random.choice(valid_images)}'"
            
        # We want to replace the rest of the backgrounds with unique ones, but let's just assign random for now.
        # It's better to manually replace duplicate occurrences.
        all_bgs = bg_pattern.findall(content)
        if len(all_bgs) > 1:
            # check if there are duplicates
            bg_filenames = [b.split('/')[-1] for b in all_bgs]
            
            if len(set(bg_filenames)) < len(bg_filenames) * 0.5: # If many duplicates
                print(f"[{filename}] Found heavily duplicated images in sets array. Diversifying...")
                # We will just randomize them all (except the first one for hotel)
                parts = bg_pattern.split(content)
                new_content = parts[0]
                for i in range(1, len(parts), 2):
                    if filename == 's4-a-hotel-video-first.html' and i == 1:
                        # keep the first one
                        new_content += f"bg:'{parts[i]}'"
                    else:
                        new_content += f"bg:'{parts[i].rsplit('img_', 1)[0]}{random.choice(valid_images)}'"
                    new_content += parts[i+1]
                content = new_content
                
        if content != original_content:
            print(f"[{filename}] Saved changes for duplicates/hero.")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

print("Done.")
