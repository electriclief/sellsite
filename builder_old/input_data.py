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

# Add the parent directory to sys.path to allow imports from the same directory
try:
    import update_site_data
except ImportError:
    # If not in the path, try relative or absolute
    sys.path.append(str(Path(__file__).parent))
    import update_site_data

# Paths
BASE_DIR = Path(__file__).parent.parent
DATABASE_YAML = BASE_DIR / "database.yaml"


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


def get_items_table():
    """Get current items as a formatted list for display."""
    items = load_yaml_data(DATABASE_YAML)
    if not items:
        return "### No items yet."

    markdown_list = []
    for i, item in enumerate(items):
        name = item.get("name", "N/A")
        price = item.get("price", "0.00")
        images_count = len(item.get("images", []))
        markdown_list.append(f"**{i + 1}.** {name} - **${price}** ({images_count} images)")

    return "\n\n".join(markdown_list)


def add_to_temp_list(files, current_list):
    """Add selected file paths to the temporary list."""
    if files is None:
        return current_list, current_list, None

    # Extract paths from the uploaded files
    new_paths = [f.name if hasattr(f, "name") else str(f) for f in files]
    updated_list = current_list + new_paths
    return updated_list, updated_list, None


def clear_temp_list():
    """Clear the temporary image list."""
    return [], [], None


def create_item(image_paths, name, price, description):
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
        )

    # Create item dictionary with images as an array
    item = {
        "images": list(image_paths) if image_paths else [],
        "name": name,
        "price": price,
        "description": description,
    }

    # Load existing data
    existing_items = load_yaml_data(DATABASE_YAML)
    existing_items.append(item)

    # Save back to file
    save_yaml_data(DATABASE_YAML, existing_items)

    # Return success status, updated table, cleared temp list, and cleared file input
    return f"Item '{name}' added successfully!", get_items_table(), [], [], None


def delete_item(index):
    """Delete an item by index (1-based for user friendliness)."""
    items = load_yaml_data(DATABASE_YAML)

    idx_to_delete = int(index) - 1 if index > 0 else len(items) - 1

    if items and 0 <= idx_to_delete < len(items):
        deleted_item = items.pop(idx_to_delete)
        save_yaml_data(DATABASE_YAML, items)
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
    """Live update function - currently a placeholder."""
    return "Live web site update triggered (placeholder - no action taken)."


def launch_local_site():
    """Launches docs/index.html in the default web browser."""
    index_path = BASE_DIR / "docs" / "index.html"
    if index_path.exists():
        webbrowser.open(f"file://{index_path.absolute()}")
        return "Local site launched in your browser!"
    else:
        return f"Error: {index_path} not found!"


# Create Gradio interface
with gr.Blocks(title="SellSite Item Builder", theme=gr.themes.Soft()) as demo:
    # State for temporary image paths
    temp_images_state = gr.State([])

    gr.Markdown("# 🦎 SellSite Item Builder")
    gr.Markdown("Create and manage product items for your sellsite")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## Add New Item")

            name_input = gr.Textbox(
                label="Product Name", placeholder="Enter product name", lines=1
            )
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

    clear_temp_btn.click(
        fn=clear_temp_list, outputs=[temp_images_state, temp_gallery, file_input]
    )

    create_button.click(
        fn=create_item,
        inputs=[temp_images_state, name_input, price_input, description_input],
        outputs=[
            status_output,
            items_output,
            temp_images_state,
            temp_gallery,
            file_input,
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

if __name__ == "__main__":
    # Initialize database.yaml if it doesn't exist
    if not DATABASE_YAML.exists():
        save_yaml_data(DATABASE_YAML, [])

    demo.launch(server_name="0.0.0.0", server_port=7860)
