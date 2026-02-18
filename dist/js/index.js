document.addEventListener('DOMContentLoaded', () => {
    const app = document.getElementById('app');
    const navHome = document.getElementById('nav-home');
    const itemCardTemplate = document.getElementById('item-card-template');
    const itemDetailTemplate = document.getElementById('item-detail-template');

    // Use global siteData from dataobject.js
    const data = typeof siteData !== 'undefined' ? siteData : [];

    function renderGallery() {
        app.innerHTML = '';
        app.style.display = 'grid'; // Ensure grid layout for gallery

        data.forEach((item, index) => {
            const card = itemCardTemplate.content.cloneNode(true);
            
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
            card.querySelector('.item-description').textContent = item.description;

            const viewButton = card.querySelector('.view-details');
            viewButton.addEventListener('click', () => renderDetail(index));

            app.appendChild(card);
        });
    }

    function renderDetail(index) {
        const item = data[index];
        app.innerHTML = '';
        app.style.display = 'block'; // Block layout for details

        const detail = itemDetailTemplate.content.cloneNode(true);
        
        detail.querySelector('.detail-name').textContent = item.name;
        detail.querySelector('.detail-price').textContent = `$${parseFloat(item.price).toFixed(2)}`;
        detail.querySelector('.detail-description').textContent = item.description;

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
    }

    navHome.addEventListener('click', (e) => {
        e.preventDefault();
        renderGallery();
    });

    // Initial render
    renderGallery();
});
