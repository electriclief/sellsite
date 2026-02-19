import yaml
import os
from PIL import Image
import json
import shutil
import time

# Configurations
# Get the absolute path to the 'sellsite' root directory (parent of 'builder')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, 'docs', 'database.yaml')
SETTINGS_PATH = os.path.join(BASE_DIR, 'docs', 'setting.yaml')
IMAGE_OUTPUT_DIR = os.path.join(BASE_DIR, 'docs', 'images')
JS_OUTPUT_PATH = os.path.join(BASE_DIR, 'docs', 'js', 'dataobject.js')
MAX_SIZE = (800, 800)  # Maximum dimension for web-page size

def ensure_dirs():
    """Ensure output directories exist."""
    os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(JS_OUTPUT_PATH), exist_ok=True)

def process_image(image_path):
    """Resize image and save to output directory. Returns the new relative path."""
    if not image_path:
        return None
    
    # If it's already a relative path to an existing image in docs/images, return it
    if image_path.startswith("images/"):
        full_path = os.path.join(BASE_DIR, "docs", image_path)
        if os.path.exists(full_path):
            return image_path
            
    if not os.path.exists(image_path):
        return None
    
    # Generate a unique filename to avoid collisions
    original_filename = os.path.basename(image_path)
    name, ext = os.path.splitext(original_filename)
    # Add timestamp for uniqueness
    unique_name = f"{name}_{int(time.time() * 1000)}{ext}"
    output_path = os.path.join(IMAGE_OUTPUT_DIR, unique_name)
    
    try:
        with Image.open(image_path) as img:
            # Maintain aspect ratio
            img.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
            img.save(output_path)
        
        # Return the path relative to 'docs'
        return f"images/{unique_name}"
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None

def update_js_data(items, categories=None):
    """Write the items and categories to dataobject.js."""
    ensure_dirs()
    data = {
        "items": items,
        "categories": categories or ["All"]
    }
    with open(JS_OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(f"const siteData = {json.dumps(data, indent=2)};")
    print(f"Successfully updated {JS_OUTPUT_PATH}")

def main():
    ensure_dirs()
    
    if not os.path.exists(DATABASE_PATH):
        print(f"Error: {DATABASE_PATH} not found.")
        return
    
    with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
        items = yaml.safe_load(f) or []

    categories = ["All"]
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
            settings = yaml.safe_load(f) or {}
            categories = settings.get('categories', ["All"])
    
    site_data = []
    updated_items = []
    
    for item in items:
        new_item = item.copy()
        item_changed = False
        
        # Handle 'image_path' field (legacy or single image)
        if 'image_path' in new_item and new_item['image_path']:
            processed_path = process_image(new_item['image_path'])
            if processed_path:
                if new_item['image_path'] != processed_path:
                    new_item['image_path'] = processed_path
                    item_changed = True
        
        # Handle 'images' field (list of images)
        if 'images' in new_item and isinstance(new_item['images'], list):
            new_images_list = []
            for img_path in new_item['images']:
                processed_path = process_image(img_path)
                if processed_path:
                    new_images_list.append(processed_path)
                    if img_path != processed_path:
                        item_changed = True
            new_item['images'] = new_images_list
            
        site_data.append(new_item)
        updated_items.append(new_item)
    
    # Save processed items back to database.yaml if anything changed
    # We always save to ensure consistency with processed paths
    with open(DATABASE_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(updated_items, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    # Write to dataobject.js
    update_js_data(site_data, categories)
    
    print(f"Processed {len(site_data)} items.")

if __name__ == "__main__":
    main()
