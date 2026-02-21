from PIL import Image
import os
import time
import yaml

# Configurations
# Get the absolute path to the 'sellsite' root directory (parent of 'builder')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, 'docs', 'database.yaml')
SETTINGS_PATH = os.path.join(BASE_DIR, 'docs', 'setting.yaml')
IMAGE_OUTPUT_DIR = os.path.join(BASE_DIR, 'docs', 'images')
MAX_SIZE = (800, 800)  # Maximum dimension for web-page size

def ensure_dirs():
    """Ensure output directories exist."""
    os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)

def process_image(image_path, lot_number=None, index=1):
    """Resize image and save to output directory using lot number convention. Returns the new relative path."""
    if not image_path:
        return None
    
    # Get extension
    _, ext = os.path.splitext(os.path.basename(image_path))
    ext = ext.lower()
    
    # Determine the target filename
    if lot_number:
        new_filename = f"lot{lot_number}_{index:02d}{ext}"
    else:
        name, _ = os.path.splitext(os.path.basename(image_path))
        new_filename = f"{name}_{int(time.time() * 1000)}{ext}"
    
    target_rel_path = f"images/{new_filename}"
    target_full_path = os.path.join(IMAGE_OUTPUT_DIR, new_filename)

    # Check if the image is already processed and has the correct name
    if image_path == target_rel_path:
        if os.path.exists(target_full_path):
            return target_rel_path
            
    # Resolve image_path if it's not absolute
    full_source_path = image_path
    if not os.path.isabs(image_path):
        # Check if it's relative to docs (e.g. images/...)
        test_path = os.path.join(BASE_DIR, "docs", image_path)
        if os.path.exists(test_path):
            full_source_path = test_path
        else:
            # Check if it's relative to base
            test_path = os.path.join(BASE_DIR, image_path)
            if os.path.exists(test_path):
                full_source_path = test_path

    if not os.path.exists(full_source_path):
        return None
    
    try:
        with Image.open(full_source_path) as img:
            # Maintain aspect ratio
            img.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
            img.save(target_full_path)
        
        return target_rel_path
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None

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
    
    updated_items = []
    
    for item in items:
        new_item = item.copy()
        lot_num = new_item.get('lot #', '0000')
        
        # Handle 'image_path' field (legacy or single image)
        if 'image_path' in new_item and new_item['image_path']:
            processed_path = process_image(new_item['image_path'], lot_number=lot_num, index=1)
            if processed_path:
                if new_item['image_path'] != processed_path:
                    new_item['image_path'] = processed_path
        
        # Handle 'images' field (list of images)
        if 'images' in new_item and isinstance(new_item['images'], list):
            new_images_list = []
            for i, img_path in enumerate(new_item['images']):
                processed_path = process_image(img_path, lot_number=lot_num, index=i+1)
                if processed_path:
                    new_images_list.append(processed_path)
            new_item['images'] = new_images_list
            
        updated_items.append(new_item)
    
    # Save processed items back to database.yaml
    with open(DATABASE_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(updated_items, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print(f"Processed {len(updated_items)} items.")

if __name__ == "__main__":
    main()
