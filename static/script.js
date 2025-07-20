document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('chat-form');
    const input = document.getElementById('message-input');
    const messagesContainer = document.getElementById('chat-messages');
    const typingIndicator = document.getElementById('typing-indicator');
    const activeChatId = form.dataset.chatId;

    // Przewiń na dół po załadowaniu
    scrollToBottom();

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const messageText = input.value.trim();

        if (messageText) {
            addMessage(messageText, 'user');
            input.value = '';
            input.focus();
            showTypingIndicator();

            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        message: messageText,
                        chat_id: activeChatId
                    }),
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                hideTypingIndicator();
                handleJarvisResponse(data);

            } catch (error) {
                console.error('Błąd:', error);
                hideTypingIndicator();
                addMessage('Przepraszam, wystąpił błąd komunikacji.', 'jarvis');
            }
        }
    });

    function handleJarvisResponse(data) {
        if (data.type === 'link') {
            addMessage(`Otwieram: ${data.content}`, 'jarvis');
            window.open(data.content, '_blank');
        } else {
            addMessage(data.content, 'jarvis');
        }
    }

    function addMessage(text, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        messageElement.innerText = text;
        // Wstawiamy nową wiadomość przed wskaźnikiem pisania
        messagesContainer.insertBefore(messageElement, typingIndicator);
        scrollToBottom();
    }

    function showTypingIndicator() {
        typingIndicator.style.display = 'flex';
        scrollToBottom();
    }

    function hideTypingIndicator() {
        typingIndicator.style.display = 'none';
    }

    function scrollToBottom() {
        messagesContainer.scrollTo({
            top: messagesContainer.scrollHeight,
            behavior: 'smooth'
        });
    }
});
