"""
Gradio Interface for Selling Items
Creates and manages product data for the sellsite project
"""
import gradio as gr
import yaml
from pathlib import Path
import os
import sys
import webbrowser
import subprocess

# Add the parent directory to sys.path to allow imports from the same directory
try:
    import update_site_data
except ImportError:
    # If not in the path, try relative or absolute
    sys.path.append(str(Path(__file__).parent))
    import update_site_data

# Paths
BASE_DIR = Path(__file__).parent.parent
DATABASE_YAML = BASE_DIR / "docs" / "database.yaml"
SETTINGS_YAML = BASE_DIR / "docs" / "setting.yaml"


def load_yaml_data(filepath):
    """Load YAML data from a file."""
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if data is not None else []
    return []


def save_yaml_data(filepath, data):
    """Save data to YAML file."""
    with open(filepath, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def load_settings():
    """Load settings from setting.yaml."""
    if SETTINGS_YAML.exists():
        with open(SETTINGS_YAML, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def save_settings(settings):
    """Save settings to setting.yaml."""
    with open(SETTINGS_YAML, "w", encoding="utf-8") as f:
        yaml.dump(settings, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def get_next_lot_number():
    """Get the next lot number as a 4-digit string."""
    settings = load_settings()
    last_lot = settings.get("last_lot_number", 0)
    return f"{last_lot + 1:04d}"


def get_items_table():
    """Get current items as a formatted list for display."""
    items = load_yaml_data(DATABASE_YAML)
    if not items:
        return "### No items yet."

    markdown_list = []
    for i, item in enumerate(items):
        name = item.get("name", "N/A")
        price = item.get("price", "0.00")
        lot_num = item.get("lot #", "N/A")
        images_count = len(item.get("images", []))
        markdown_list.append(f"**{i + 1}.** [Lot {lot_num}] {name} - **${price}** ({images_count} images)")

    return "\n\n".join(markdown_list)


def add_to_temp_list(files, current_list):
    """Add selected file paths to the temporary list."""
    if files is None:
        return current_list, current_list, None

    # Handle single file (from camera) or multiple files (from upload)
    if not isinstance(files, list):
        files = [files]

    # Extract paths from the uploaded files
    new_paths = [f.name if hasattr(f, "name") else str(f) for f in files]
    updated_list = current_list + new_paths
    return updated_list, updated_list, None


def clear_temp_list():
    """Clear the temporary image list and categories."""
    return [], [], None, None, ["All"], "### Selected Categories: All"


def add_category_to_list(category, current_categories):
    """Add a category to the list if not already present."""
    if category and category not in current_categories:
        current_categories.append(category)
    
    display_text = "### Selected Categories: " + ", ".join(current_categories)
    return current_categories, display_text


def create_item(image_paths, name, price, description, categories):
    """
    Create a new item and save it to database.yaml
    """
    if not name:
        return (
            "Error: Product Name is required.",
            get_items_table(),
            image_paths,
            image_paths,
            None,
            None,
            get_next_lot_number(),
            ["All"],
            "### Selected Categories: All",
        )

    # Process images immediately (resize and move to docs/images)
    processed_images = []
    if image_paths:
        for path in image_paths:
            proc_path = update_site_data.process_image(path)
            if proc_path:
                processed_images.append(proc_path)

    # Get and update lot number
    settings = load_settings()
    last_lot = settings.get("last_lot_number", 0)
    next_lot = last_lot + 1
    lot_number_str = f"{next_lot:04d}"

    # Create item dictionary with images as an array
    item = {
        "images": processed_images,
        "name": name,
        "price": price,
        "description": description,
        "lot #": lot_number_str,
        "Categories": categories,
    }

    # Load existing data
    existing_items = load_yaml_data(DATABASE_YAML)
    existing_items.append(item)

    # Save back to file
    save_yaml_data(DATABASE_YAML, existing_items)

    # Update settings
    settings["last_lot_number"] = next_lot
    save_settings(settings)

    # Update dataobject.js immediately
    update_site_data.main()

    # Return success status, updated table, cleared temp list, and cleared file input
    return (
        f"Item '{name}' added successfully (Lot {lot_number_str})!",
        get_items_table(),
        [],
        [],
        None,
        None,
        get_next_lot_number(),
        ["All"],
        "### Selected Categories: All",
    )


def delete_item(index):
    """Delete an item by index (1-based for user friendliness)."""
    items = load_yaml_data(DATABASE_YAML)

    idx_to_delete = int(index) - 1 if index > 0 else len(items) - 1

    if items and 0 <= idx_to_delete < len(items):
        deleted_item = items.pop(idx_to_delete)
        save_yaml_data(DATABASE_YAML, items)
        # Update dataobject.js
        update_site_data.main()
        return f"Deleted: {deleted_item.get('name', 'N/A')}", get_items_table()
    return "Invalid index", get_items_table()


def run_local_update():
    """Executes update_site_data.py logic."""
    try:
        update_site_data.main()
        return "Local site data updated successfully!"
    except Exception as e:
        return f"Error during local update: {str(e)}"


def run_live_update():
    """Executes git commands to push changes to GitHub."""
    try:
        # First ensure the local data is up to date
        update_site_data.main()

        # 1. Add all changes
        add_result = subprocess.run(["git", "add", "."], capture_output=True, text=True, cwd=BASE_DIR)
        if add_result.returncode != 0:
            return f"Error during git add: {add_result.stderr}"

        # 2. Check if there are changes to commit
        status_result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=BASE_DIR)
        if not status_result.stdout.strip():
            return "No changes to update."

        # 3. Commit changes
        commit_result = subprocess.run(["git", "commit", "-m", "Update site data and images via Builder"], capture_output=True, text=True, cwd=BASE_DIR)
        if commit_result.returncode != 0:
            return f"Error during git commit: {commit_result.stderr}"

        # 4. Push to GitHub
        push_result = subprocess.run(["git", "push"], capture_output=True, text=True, cwd=BASE_DIR)
        if push_result.returncode != 0:
            return f"Error during git push: {push_result.stderr}"

        return "Live web site updated successfully! Changes pushed to GitHub."
    except Exception as e:
        return f"Unexpected error during live update: {str(e)}"


def launch_local_site():
    """Launches docs/index.html in the default web browser."""
    index_path = BASE_DIR / "docs" / "index.html"
    if index_path.exists():
        webbrowser.open(f"file://{index_path.absolute()}")
        return "Local site launched in your browser!"
    else:
        return f"Error: {index_path} not found!"


# Create Gradio interface
with gr.Blocks(title="SellSite Item Builder") as demo:
    # State for temporary image paths and categories
    temp_images_state = gr.State([])
    temp_categories_state = gr.State(["All"])

    # Load categories for selection
    settings = load_settings()
    available_categories = settings.get("categories", ["All"])

    gr.Markdown("# 🦎 SellSite Item Builder")
    gr.Markdown("Create and manage product items for your sellsite")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## Add New Item")

            lot_display = gr.Textbox(
                label="Next Lot #", value=get_next_lot_number(), interactive=False
            )

            name_input = gr.Textbox(
                label="Product Name", placeholder="Enter product name", lines=1
            )

            with gr.Row():
                category_input = gr.Dropdown(
                    label="Category", choices=available_categories, value="All", scale=2
                )
                add_category_btn = gr.Button("Add Category", scale=1)

            categories_display = gr.Markdown("### Selected Categories: All")

            price_input = gr.Number(label="Price ($)", value=0.00, precision=2)
            description_input = gr.Textbox(
                label="Description", placeholder="Describe your product...", lines=3
            )

            gr.Markdown("### Images")
            file_input = gr.File(
                label="Upload Product Images",
                file_count="multiple",
                file_types=["image"]
            )

            camera_input = gr.Image(
                label="Take a Photo (Mobile)",
                sources=["webcam"],
                type="filepath"
            )

            # Replaced Textbox with Gallery for better visualization
            temp_gallery = gr.Gallery(
                label="Selected Images",
                columns=3,
                rows=2,
                height="auto",
                object_fit="contain",
                preview=True
            )

            with gr.Row():
                clear_temp_btn = gr.Button("Clear Images", variant="secondary")
                create_button = gr.Button("Create Item", variant="primary")

        with gr.Column(scale=1):
            gr.Markdown("## Current Items List")
            items_output = gr.Markdown(get_items_table())

            with gr.Row():
                delete_index = gr.Number(
                    label="Item Number to Delete (0 for last)", value=0, precision=0
                )
                delete_button = gr.Button("Delete Item", variant="stop")

            gr.Markdown("## Site Deployment")
            with gr.Row():
                update_local_btn = gr.Button("Update Local Site", variant="secondary")
                update_live_btn = gr.Button("Update Live Web Site", variant="primary")
            
            launch_local_btn = gr.Button("Launch Local Web Site", variant="secondary")

            status_output = gr.Textbox(label="Status", interactive=False)

    gr.Markdown("### Instructions:")
    gr.Markdown("- Select one or more images using the file picker")
    gr.Markdown("- You can add images multiple times; they will accumulate in the gallery")
    gr.Markdown("- Fill in details and click 'Create Item' to save to `database.yaml`")

    # Event handlers
    file_input.upload(
        fn=add_to_temp_list,
        inputs=[file_input, temp_images_state],
        outputs=[temp_images_state, temp_gallery, file_input],
    )

    camera_input.change(
        fn=add_to_temp_list,
        inputs=[camera_input, temp_images_state],
        outputs=[temp_images_state, temp_gallery, camera_input],
    )

    add_category_btn.click(
        fn=add_category_to_list,
        inputs=[category_input, temp_categories_state],
        outputs=[temp_categories_state, categories_display],
    )

    clear_temp_btn.click(
        fn=clear_temp_list, outputs=[temp_images_state, temp_gallery, file_input, camera_input, temp_categories_state, categories_display]
    )

    create_button.click(
        fn=create_item,
        inputs=[temp_images_state, name_input, price_input, description_input, temp_categories_state],
        outputs=[
            status_output,
            items_output,
            temp_images_state,
            temp_gallery,
            file_input,
            camera_input,
            lot_display,
            temp_categories_state,
            categories_display,
        ],
    )

    delete_button.click(
        fn=delete_item,
        inputs=[delete_index],
        outputs=[status_output, items_output],
    )

    update_local_btn.click(
        fn=run_local_update,
        outputs=status_output
    )

    update_live_btn.click(
        fn=run_live_update,
        outputs=status_output
    )

    launch_local_btn.click(
        fn=launch_local_site,
        outputs=status_output
    )

    # Load initial data on startup
    demo.load(fn=get_items_table, outputs=items_output)
    demo.load(fn=get_next_lot_number, outputs=lot_display)

if __name__ == "__main__":
    # Initialize database.yaml if it doesn't exist
    if not DATABASE_YAML.exists():
        save_yaml_data(DATABASE_YAML, [])

    demo.launch(server_name="192.168.1.100", server_port=7860, theme=gr.themes.Soft())
