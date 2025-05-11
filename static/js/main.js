/**
 * Main JavaScript for Product Recommendation Engine
 */

// Track user interaction
function trackInteraction(userId, productId, type, value = null) {
    const data = {
        user_id: userId,
        product_id: productId,
        type: type
    };

    if (value !== null) {
        data.value = value;
    }

    fetch('/api/track_interaction', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log(`Tracked ${type} interaction for product ${productId}`);
            } else {
                console.error('Failed to track interaction:', data.error);
            }
        })
        .catch(error => {
            console.error('Error tracking interaction:', error);
        });
}

// Load user interaction history
function loadUserHistory(userId) {
    const historyContainer = document.querySelector('.history-container');
    const loadingElem = historyContainer.querySelector('.loading');
    const tableElem = historyContainer.querySelector('.history-table');
    const tableBody = document.getElementById('history-data');

    if (!tableBody) return;

    fetch(`/api/user_interactions/${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.interactions) {
                // Hide loading, show table
                loadingElem.style.display = 'none';
                tableElem.style.display = 'table';

                // Clear existing rows
                tableBody.innerHTML = '';

                // Add interactions to table
                data.interactions.forEach(interaction => {
                    const row = document.createElement('tr');

                    // Format date
                    const date = new Date(interaction.timestamp);
                    const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();

                    // Create row content
                    row.innerHTML = `
                        <td>${interaction.product_name || interaction.product_id}</td>
                        <td>${interaction.type}</td>
                        <td>${formattedDate}</td>
                        <td>${interaction.rating !== undefined ? interaction.rating : '-'}</td>
                    `;

                    tableBody.appendChild(row);
                });

                if (data.interactions.length === 0) {
                    const emptyRow = document.createElement('tr');
                    emptyRow.innerHTML = '<td colspan="4" style="text-align: center;">No interactions found</td>';
                    tableBody.appendChild(emptyRow);
                }
            } else {
                loadingElem.textContent = 'Failed to load user activity.';
            }
        })
        .catch(error => {
            console.error('Error loading user history:', error);
            loadingElem.textContent = 'Error loading user activity.';
        });
}

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Product view buttons
    document.querySelectorAll('.btn.view').forEach(button => {
        button.addEventListener('click', function() {
            const userId = this.dataset.userId;
            const productId = this.dataset.productId;
            trackInteraction(userId, productId, 'view');
            alert(`Viewing product ${productId}`);
        });
    });

    // Add to cart buttons
    document.querySelectorAll('.btn.add-to-cart').forEach(button => {
        button.addEventListener('click', function() {
            const userId = this.dataset.userId;
            const productId = this.dataset.productId;
            trackInteraction(userId, productId, 'purchase');
            alert(`Added product ${productId} to cart`);
        });
    });

    // Star rating system
    document.querySelectorAll('.star-rating').forEach(container => {
        const stars = container.querySelectorAll('.star');
        const userId = container.dataset.userId;
        const productId = container.dataset.productId;

        stars.forEach(star => {
            // Hover effect
            star.addEventListener('mouseover', function() {
                const rating = parseInt(this.dataset.value);
                
                stars.forEach((s, index) => {
                    if (index < rating) {
                        s.textContent = '★';
                    } else {
                        s.textContent = '☆';
                    }
                });
            });

            // Reset stars on mouse out
            container.addEventListener('mouseout', function() {
                stars.forEach(s => {
                    if (s.classList.contains('active')) {
                        s.textContent = '★';
                    } else {
                        s.textContent = '☆';
                    }
                });
            });

            // Click to rate
            star.addEventListener('click', function() {
                const rating = parseInt(this.dataset.value);
                
                // Set active state
                stars.forEach((s, index) => {
                    if (index < rating) {
                        s.classList.add('active');
                        s.textContent = '★';
                    } else {
                        s.classList.remove('active');
                        s.textContent = '☆';
                    }
                });

                // Track rating
                trackInteraction(userId, productId, 'rating', rating);
                
                // Reload history after a short delay
                setTimeout(() => {
                    loadUserHistory(userId);
                }, 1000);
            });
        });
    });
});