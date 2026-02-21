"""
CLI Tool to update item descriptions in database.yaml
Usage: python builder/change_description.py <lot_number> <markdown_content>
"""
import sys
import yaml
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
DATABASE_YAML = BASE_DIR / "docs" / "database.yaml"

def load_yaml_data(filepath):
    """Load YAML data from a file."""
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or []
    return []

def save_yaml_data(filepath, data):
    """Save data to YAML file."""
    with open(filepath, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

def update_description(lot_number, new_markdown):
    items = load_yaml_data(DATABASE_YAML)
    found = False
    
    # Normalize lot number to 4-digit string if it's numeric
    target_lot = str(lot_number).zfill(4)

    for item in items:
        # Check both string and potential integer types for 'lot #'
        current_lot = str(item.get("lot #", "")).zfill(4)
        if current_lot == target_lot:
            item["description"] = new_markdown
            found = True
            break
    
    if not found:
        print(f"Error: Lot number '{lot_number}' not found in database.")
        sys.exit(1)
    
    save_yaml_data(DATABASE_YAML, items)
    print(f"Successfully updated description for Lot {target_lot}.")

    # Try to trigger the site data update as well
    try:
        import update_site_data
        update_site_data.main()
    except ImportError:
        print("Warning: Could not import update_site_data to refresh site files.")
    except Exception as e:
        print(f"Warning: Error updating site data: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python builder/change_description.py <lot_number> [markdown_content]")
        sys.exit(1)
    
    lot_num = sys.argv[1]
    
    # If content is provided as arguments, join them
    if len(sys.argv) >= 3:
        markdown = " ".join(sys.argv[2:])
    else:
        # Fallback to interactive input if only lot number is provided
        print(f"Entering multi-line mode for Lot {lot_num}. Paste your markdown and press Ctrl+Z (then Enter) on Windows to save:")
        markdown = sys.stdin.read()
    
    update_description(lot_num, markdown)
