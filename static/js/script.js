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
    if (typeof content !== 'string') {
        return content;
    }

    // Kiểm tra và tách phần gallery hình ảnh đặc biệt
    let mainContent = content;
    let imageGalleryHTML = '';

    // Tìm khối image-gallery
    const imageGalleryMatch = content.match(/```image-gallery\n([\s\S]*?)```/);
    if (imageGalleryMatch && imageGalleryMatch[1]) {
        // Tách nội dung chính và phần gallery
        mainContent = content.replace(/```image-gallery\n[\s\S]*?```/, '');

        // Xử lý phần gallery
        const galleryContent = imageGalleryMatch[1];
        const imageLinks = galleryContent.match(/\[([^\]]+)\]\(([^)]+)\)/g);

        if (imageLinks && imageLinks.length > 0) {
            imageGalleryHTML = '<div class="image-gallery">';

            imageLinks.forEach(link => {
                const titleMatch = link.match(/\[([^\]]+)\]/);
                const urlMatch = link.match(/\(([^)]+)\)/);

                if (titleMatch && urlMatch) {
                    const title = titleMatch[1];
                    const url = urlMatch[1];

                    imageGalleryHTML += `
                        <div class="gallery-item">
                            <img src="${url}" alt="${title}" class="gallery-image">
                            <div class="gallery-caption">${title}</div>
                        </div>
                    `;
                }
            });

            imageGalleryHTML += '</div>';
        }
    }

    // Cấu hình Marked.js
    marked.setOptions({
        renderer: new marked.Renderer(),
        highlight: function(code, lang) {
            // Không xử lý highlight cho khối image-gallery
            if (lang === 'image-gallery') return code;

            const language = hljs.getLanguage(lang) ? lang : 'plaintext';
            return hljs.highlight(code, { language }).value;
        },
        langPrefix: 'hljs language-',
        pedantic: false,
        gfm: true,
        breaks: true,
        sanitize: false,
        smartypants: false,
        xhtml: false
    });

    // Chuyển đổi Markdown sang HTML
    let formattedContent = marked.parse(mainContent);

    // Xử lý hình ảnh để hiển thị đẹp hơn
    formattedContent = formattedContent.replace(/<img src="([^"]+)"([^>]*)>/g,
        '<a href="$1" target="_blank"><img src="$1" class="chat-image" $2></a>');

    // Xử lý liên kết để mở trong tab mới
    formattedContent = formattedContent.replace(/<a href="([^"]+)"([^>]*)>/g,
        '<a href="$1" target="_blank" $2>');

    // Thêm gallery hình ảnh vào cuối nội dung
    if (imageGalleryHTML) {
        formattedContent += imageGalleryHTML;
    }

    return formattedContent;
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
        } else if (line.includes('Hình ảnh:') || line.includes('Images:')) {
            // Tìm tất cả các URL hình ảnh trong các dòng tiếp theo
            let i = lines.indexOf(line) + 1;
            while (i < lines.length && (lines[i].includes('http') || lines[i].includes('*'))) {
                const urlMatch = lines[i].match(/(https?:\/\/[^\s]+)/);
                if (urlMatch) {
                    images.push(urlMatch[0]);
                }
                i++;
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
        imageHtml = `<a href="${images[0]}" target="_blank"><img src="${images[0]}" alt="${title}" class="product-image"></a>`;

        // Nếu có nhiều hình ảnh, hiển thị dưới dạng gallery thu nhỏ
        if (images.length > 1) {
            imageHtml += '<div class="product-gallery">';
            for (let i = 1; i < Math.min(images.length, 4); i++) {
                imageHtml += `<a href="${images[i]}" target="_blank"><img src="${images[i]}" alt="${title} - Image ${i+1}" class="gallery-thumbnail"></a>`;
            }
            if (images.length > 4) {
                imageHtml += `<div class="more-images">+${images.length - 4}</div>`;
            }
            imageHtml += '</div>';
        }
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

// Khởi tạo highlight.js
document.addEventListener('DOMContentLoaded', function() {
    // Khởi tạo highlight.js
    hljs.configure({
        languages: ['javascript', 'python', 'html', 'css', 'json', 'bash', 'markdown']
    });

    // Xử lý sự kiện click cho hình ảnh
    document.body.addEventListener('click', function(e) {
        // Xử lý click cho hình ảnh trong tin nhắn thông thường
        if (e.target.tagName === 'IMG' && e.target.parentNode.tagName === 'A') {
            // Ngăn chặn hành vi mặc định của thẻ a
            e.preventDefault();

            // Mở hình ảnh trong tab mới
            window.open(e.target.parentNode.href, '_blank');
        }

        // Xử lý click cho hình ảnh trong gallery
        if (e.target.classList.contains('gallery-image')) {
            // Mở hình ảnh trong tab mới
            window.open(e.target.src, '_blank');
        }
    });

    // Load user orders if user ID exists
    if (userId) {
        loadUserOrders(userId);
    }
});