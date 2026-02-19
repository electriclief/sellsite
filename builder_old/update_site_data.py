import yaml
import os
from PIL import Image
import json
import shutil

# Configurations
# Get the absolute path to the 'sellsite' root directory (parent of 'builder')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, 'database.yaml')
IMAGE_OUTPUT_DIR = os.path.join(BASE_DIR, 'docs', 'images')
JS_OUTPUT_PATH = os.path.join(BASE_DIR, 'docs', 'js', 'dataobject.js')
MAX_SIZE = (800, 800)  # Maximum dimension for web-page size

def ensure_dirs():
    """Ensure output directories exist."""
    os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(JS_OUTPUT_PATH), exist_ok=True)

def process_image(image_path):
    """Resize image and save to output directory. Returns the new relative path."""
    if not image_path or not os.path.exists(image_path):
        return None
    
    filename = os.path.basename(image_path)
    # Ensure a unique filename if necessary, but for now we'll just use the original
    output_path = os.path.join(IMAGE_OUTPUT_DIR, filename)
    
    try:
        with Image.open(image_path) as img:
            # Maintain aspect ratio
            img.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
            img.save(output_path)
        
        # Return the path relative to 'docs' (which will be the web root)
        # However, for dataobject.js, the path should likely be relative to index.html
        # which is in 'docs'. So it should be 'images/filename'
        return f"images/{filename}"
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None

def main():
    ensure_dirs()
    
    if not os.path.exists(DATABASE_PATH):
        print(f"Error: {DATABASE_PATH} not found.")
        return
    
    with open(DATABASE_PATH, 'r') as f:
        items = yaml.safe_load(f) or []
    
    site_data = []
    
    for item in items:
        new_item = item.copy()
        
        # Handle 'image_path' field
        if 'image_path' in new_item and new_item['image_path']:
            processed_path = process_image(new_item['image_path'])
            if processed_path:
                new_item['image_path'] = processed_path
        
        # Handle 'images' field (list of images)
        if 'images' in new_item and isinstance(new_item['images'], list):
            new_images_list = []
            for img_path in new_item['images']:
                processed_path = process_image(img_path)
                if processed_path:
                    new_images_list.append(processed_path)
            new_item['images'] = new_images_list
            
        site_data.append(new_item)
    
    # Write to dataobject.js
    with open(JS_OUTPUT_PATH, 'w') as f:
        f.write(f"const siteData = {json.dumps(site_data, indent=2)};")
    
    print(f"Successfully updated {JS_OUTPUT_PATH} and processed images.")

if __name__ == "__main__":
    main()
