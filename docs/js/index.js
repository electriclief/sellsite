document.addEventListener('DOMContentLoaded', () => {
    const app = document.getElementById('app');
    const logoLink = document.getElementById('logo-link');
    const itemCardTemplate = document.getElementById('item-card-template');
    const itemDetailTemplate = document.getElementById('item-detail-template');
    const filterContainer = document.getElementById('filter-container');
    const categoryFilter = document.getElementById('category-filter');

    // Use global siteData from dataobject.js
    const data = typeof siteData !== 'undefined' ? (siteData.items || []) : [];
    const categories = typeof siteData !== 'undefined' ? (siteData.categories || ["All"]) : ["All"];

    // Populate filter dropdown
    if (categoryFilter) {
        categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat;
            option.textContent = cat;
            categoryFilter.appendChild(option);
        });

        categoryFilter.addEventListener('change', () => {
            renderGallery();
        });
    }

    function renderGallery() {
        app.innerHTML = '';
        app.style.display = 'grid'; // Ensure grid layout for gallery
        if (filterContainer) filterContainer.style.display = 'block'; // Show filter on gallery page

        const selectedCategory = categoryFilter ? categoryFilter.value : "All";

        data.forEach((item, index) => {
            // Filter logic
            if (selectedCategory !== "All") {
                const itemCategories = item.Categories || [];
                if (!itemCategories.includes(selectedCategory)) {
                    return;
                }
            }

            const cardTemplate = itemCardTemplate.content.cloneNode(true);
            const card = cardTemplate.querySelector('.item-card');
            
            // Handle both image_path and images list
            let mainImage = '';
            if (item.image_path) {
                mainImage = item.image_path;
            } else if (item.images && item.images.length > 0) {
                mainImage = item.images[0];
            }

            const img = card.querySelector('.item-image');
            img.src = mainImage || 'placeholder.png'; // Add a default placeholder if no image
            img.alt = item.name;

            card.querySelector('.item-name').textContent = item.name;
            card.querySelector('.item-price').textContent = `$${parseFloat(item.price).toFixed(2)}`;

            card.addEventListener('click', () => renderDetail(index));

            app.appendChild(card);
        });
        
        // Clean URL when back to gallery
        window.history.pushState({}, '', window.location.pathname);
    }

    function renderDetail(index) {
        const item = data[index];
        app.innerHTML = '';
        app.style.display = 'block'; // Block layout for details
        if (filterContainer) filterContainer.style.display = 'none'; // Hide filter on item page

        const detail = itemDetailTemplate.content.cloneNode(true);
        
        const lotNumber = item['lot #'] || (index + 1);
        detail.querySelector('.detail-lot').textContent = `Lot #${lotNumber}`;
        detail.querySelector('.detail-name').textContent = item.name;
        detail.querySelector('.detail-price').textContent = `$${parseFloat(item.price).toFixed(2)}`;
        
        const descriptionDiv = detail.querySelector('.detail-description');
        if (typeof marked !== 'undefined') {
            descriptionDiv.innerHTML = marked.parse(item.description || '');
        } else {
            descriptionDiv.textContent = item.description;
        }

        // Navigation Logic
        const prevButton = detail.querySelector('.prev-button');
        const nextButton = detail.querySelector('.next-button');

        if (index > 0) {
            const prevItem = data[index - 1];
            prevButton.textContent = `← ${prevItem.name}`;
            prevButton.onclick = () => renderDetail(index - 1);
        } else {
            prevButton.disabled = true;
            prevButton.textContent = '← Beginning';
        }

        if (index < data.length - 1) {
            const nextItem = data[index + 1];
            nextButton.textContent = `${nextItem.name} →`;
            nextButton.onclick = () => renderDetail(index + 1);
        } else {
            nextButton.disabled = true;
            nextButton.textContent = 'End →';
        }

        const gallery = detail.querySelector('.image-gallery');
        const imagesToDisplay = [];
        
        if (item.image_path) imagesToDisplay.push(item.image_path);
        if (item.images) imagesToDisplay.push(...item.images);

        // Remove duplicates and filter empty
        const uniqueImages = [...new Set(imagesToDisplay)].filter(img => img);

        uniqueImages.forEach(imgSrc => {
            const img = document.createElement('img');
            img.src = imgSrc;
            img.alt = item.name;
            gallery.appendChild(img);
        });

        detail.querySelector('.back-button').addEventListener('click', (e) => {
            e.preventDefault();
            renderGallery();
        });

        app.appendChild(detail);
        
        // Update URL with lot number
        window.history.pushState({}, '', `?lot=${lotNumber}`);
    }

    logoLink.addEventListener('click', (e) => {
        e.preventDefault();
        renderGallery();
    });

    // Initial render
    const urlParams = new URLSearchParams(window.location.search);
    const lotParam = urlParams.get('lot');
    
    if (lotParam) {
        const lotIndex = data.findIndex(item => item['lot #'] === lotParam);
        if (lotIndex !== -1) {
            renderDetail(lotIndex);
        } else {
            // Try numeric index if lot number doesn't match
            const idx = parseInt(lotParam) - 1;
            if (idx >= 0 && idx < data.length) {
                renderDetail(idx);
            } else {
                renderGallery();
            }
        }
    } else {
        renderGallery();
    }
});
