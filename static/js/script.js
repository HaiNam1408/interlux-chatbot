// Store user session
let userId = localStorage.getItem('userId') || null;
let chatHistory = [];

// DOM elements
const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const ordersList = document.getElementById('orders-list');

// Event listeners
sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Functions
function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessageToChat('user', message);
    messageInput.value = '';

    // Show loading indicator
    const loadingMessage = addMessageToChat('bot', '<div class="loading"></div>');

    // Send message to server
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'message': message,
            'user_id': userId || ''
        })
    })
        .then(response => response.json())
        .then(data => {
            // Remove loading indicator
            chatMessages.removeChild(loadingMessage);

            // Add bot response to chat
            addMessageToChat('bot', data.response);

            // Store user ID if not already stored
            if (!userId && data.user_id) {
                userId = data.user_id;
                localStorage.setItem('userId', userId);

                // Load user orders
                loadUserOrders(userId);
            }

            // Update chat history
            chatHistory = data.history;
        })
        .catch(error => {
            console.error('Error:', error);
            chatMessages.removeChild(loadingMessage);
            addMessageToChat('bot', 'Sorry, an error occurred. Please try again later.');
        });
}

function addMessageToChat(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.innerHTML = formatMessageContent(content);

    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return messageDiv;
}

function formatMessageContent(content) {
    // Format product information if present
    if (typeof content === 'string' && content.includes('Products:')) {
        const parts = content.split('Products:');
        let formattedContent = parts[0];

        const productParts = parts[1].split('- Title:');
        for (let i = 1; i < productParts.length; i++) {
            const productInfo = '- Title:' + productParts[i];
            const productCard = createProductCard(productInfo);
            formattedContent += productCard;
        }

        return formattedContent;
    }

    return content;
}

function createProductCard(productInfo) {
    const lines = productInfo.split('\n');
    let title = '', description = '', price = '', categoryId = '', attributes = {}, images = [];
    let discount = 0;

    for (const line of lines) {
        if (line.includes('- Title:')) {
            title = line.replace('- Title:', '').trim();
        } else if (line.includes('Description:')) {
            description = line.replace('Description:', '').trim();
        } else if (line.includes('Price:')) {
            const priceText = line.replace('Price:', '').trim();
            // Check if there's discount information
            if (priceText.includes('Discount:')) {
                const parts = priceText.split('(Discount:');
                price = parts[0].trim();
                discount = parseInt(parts[1].replace('%)', '').trim());
            } else {
                price = priceText;
            }
        } else if (line.includes('Category ID:')) {
            categoryId = line.replace('Category ID:', '').trim();
        } else if (line.includes('Attributes:')) {
            const attributesText = line.replace('Attributes:', '').trim();
            const attributePairs = attributesText.split(',');
            attributePairs.forEach(pair => {
                const [key, value] = pair.split(':').map(item => item.trim());
                attributes[key] = value;
            });
        } else if (line.includes('Images:')) {
            const imagesText = line.replace('Images:', '').trim();
            if (imagesText.includes('available')) {
                // Just a count of images, not actual URLs
                const count = parseInt(imagesText.split(' ')[0]);
                for (let i = 0; i < count; i++) {
                    images.push(`/images/placeholder_${i+1}.jpg`);
                }
            }
        }
    }

    // Create attributes HTML
    let attributesHtml = '';
    if (Object.keys(attributes).length > 0) {
        attributesHtml = '<div class="product-attributes">';
        for (const [key, value] of Object.entries(attributes)) {
            attributesHtml += `<span>${key}: ${value}</span>`;
        }
        attributesHtml += '</div>';
    }

    // Create image HTML
    let imageHtml = '';
    if (images.length > 0) {
        imageHtml = `<img src="${images[0]}" alt="${title}" class="product-image">`;
    }

    // Create discount badge
    let discountHtml = '';
    if (discount > 0) {
        discountHtml = `<div class="discount-badge">-${discount}%</div>`;
    }

    return `
        <div class="product-card">
            ${discountHtml}
            ${imageHtml}
            <h4>${title}</h4>
            <p>${description}</p>
            <p class="product-price">${price}</p>
            <p>Category ID: ${categoryId}</p>
            ${attributesHtml}
        </div>
    `;
}

function loadUserOrders(userId) {
    fetch(`/orders/${userId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('No orders found');
            }
            return response.json();
        })
        .then(data => {
            if (data.orders && data.orders.length > 0) {
                ordersList.innerHTML = '';
                data.orders.forEach(order => {
                    const orderItem = document.createElement('div');
                    orderItem.className = 'order-item';

                    const orderContent = `
                        <div class="order-id">Order #${order.id}</div>
                        <div class="order-status">${order.status}</div>
                        <div class="order-total">Total: ${new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(order.total_amount/23000)}</div>
                    `;

                    orderItem.innerHTML = orderContent;
                    ordersList.appendChild(orderItem);
                });
            }
        })
        .catch(error => {
            console.log('Error loading orders:', error);
        });
}

// Initialize - load user orders if user ID exists
if (userId) {
    loadUserOrders(userId);
}