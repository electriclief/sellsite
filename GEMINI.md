# Jim's stuff for Sale

## Intent
Create a "duct tape and glue" themed marketplace for selling Jim's items.

## Directory Structure
- \sellsite - Main repository
- \sellsite\builder - Python Gradio interface for creating items
- \sellsite\docs - GitHub Pages deployment directory
- \sellsite\docs\js
- \sellsite\docs\css
- \sellsite\docs\Items
- \sellsite\GEMINI.md - Project documentation
- \sellsite\requirement.txt - Python dependencies

## To-Do List

### Step 1: Create Directory Structure
- [x] Create \sellsite directory
- [x] Create \sellsite\builder directory
- [x] Create \sellsite\docs directory
- [x] Create \sellsite\docs\js directory
- [x] Create \sellsite\docs\css directory
- [x] Create \sellsite\docs\Items directory
- [x] Create \sellsite\requirement.txt with gradio
- [x] Initialize git repository in \sellsite

### Step 2: Build the Gradio Builder
- [x] Create the main builder.py file in \sellsite\builder
- [x] Implement item creation interface with Gradio
- [x] Add image upload functionality
- [x] Add product details form
- [x] Implement item saving to local storage/database
- [x] Added JS export to bypass CORS (database.js, setting.js)

### Step 3: Create Frontend
- [x] Create HTML structure for item display
- [x] Build CSS styling for the website
- [x] Create JavaScript for rendering items
- [x] Add clickable item cards and Lot # display
- [x] Implement URL-based navigation (?lot=)
- [x] Resolve CORS issue for local file:// access
- [ ] Add cart functionality

### Step 4: Integration
- [ ] Connect Gradio builder to frontend
- [ ] Set up data persistence
- [ ] Configure GitHub Pages for \sellsite\docs

### Step 5: Testing & Deployment
- [ ] Test item creation process
- [ ] Test item display
- [ ] Deploy to GitHub Pages
- [ ] Verify functionality

## Technical Notes
- **Server Binding**: The builder application (`input_data.py`) must be hardcoded to `192.168.1.100` to ensure local network accessibility for mobile devices.