document.addEventListener('DOMContentLoaded', () => {
    const launcher = document.getElementById('chat-launcher');
    const chatWindow = document.getElementById('chat-window');
    const chatClose = document.getElementById('chat-close');
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const chatSend = document.getElementById('chat-send');
    const chatLoading = document.getElementById('chat-loading');
    const suggestions = document.getElementById('chat-suggestions');

    const bookBtnTrigger = document.getElementById('book-btn-trigger');
    const formContainer = document.getElementById('appointment-form-container');
    const closeFormBtn = document.getElementById('close-form-btn');
    const appointmentForm = document.getElementById('appointment-form');

    const BASE_URL = 'http://127.0.0.1:8000';
    let sessionId = null;

    launcher.addEventListener('click', () => {
        chatWindow.classList.toggle('hidden');
        chatInput.focus();
    });

    chatClose.addEventListener('click', () => {
        chatWindow.classList.add('hidden');
    });

    bookBtnTrigger.addEventListener('click', () => {
        formContainer.classList.remove('hidden');
    });

    closeFormBtn.addEventListener('click', () => {
        formContainer.classList.add('hidden');
    });

    document.querySelectorAll('.suggest-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            const query = e.target.getAttribute('data-query');
            sendMessage(query);
            suggestions.remove();
        });
    });

    chatSend.addEventListener('click', submitInput);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') submitInput();
    });

    function submitInput() {
        const text = chatInput.value.trim();
        if (!text) return;
        sendMessage(text);
        chatInput.value = '';
    }

    async function sendMessage(userMessageText) {
        appendBubble(userMessageText, 'user');
        chatLoading.classList.remove('hidden');
        scrollToBottom();

        try {
            const response = await fetch(`${BASE_URL}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: userMessageText,
                    session_id: sessionId
                })
            });

            if (!response.ok) throw new Error('Network query failed');

            const data = await response.json();
            if (data.session_id) sessionId = data.session_id;

            appendBubble(data.response, 'assistant', data.sources);
        } catch (error) {
            console.error('Error contacting backend:', error);
            appendBubble('Unable to reach our server. Please call us at +92-55-1234567.', 'assistant');
        } finally {
            chatLoading.classList.add('hidden');
            scrollToBottom();
        }
    }

    appointmentForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const payload = {
            patient_name: document.getElementById('patient_name').value.trim(),
            contact_number: document.getElementById('contact_number').value.trim(),
            preferred_date: document.getElementById('pref_date').value,
            preferred_time: document.getElementById('pref_time').value,
            service_requested: document.getElementById('service').value.trim() || null
        };

        formContainer.classList.add('hidden');
        appendBubble("📅 Sent appointment request details...", 'user');
        chatLoading.classList.remove('hidden');

        try {
            const response = await fetch(`${BASE_URL}/api/appointments`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) throw new Error('Booking insertion failed');

            const result = await response.json();
            
            appendBubble(
                `Thank you, ${result.patient_name}! Your appointment request has been recorded (Ref ID: #${result.id}).\n\n` +
                `⚠️ Please note: Your appointment is requested but NOT confirmed until our clinic staff contacts you to approve it.`,
                'assistant'
            );
            appointmentForm.reset();

        } catch (error) {
            console.error('Database connection error:', error);
            appendBubble('We encountered an error saving your request. Please call us directly at +92-55-1234567.', 'assistant');
        } finally {
            chatLoading.classList.add('hidden');
            scrollToBottom();
        }
    });

    function appendBubble(text, sender, sources = []) {
        const bubble = document.createElement('div');
        bubble.classList.add('message', sender);
        
        const textNode = document.createElement('p');
        textNode.style.whiteSpace = 'pre-line';
        textNode.textContent = text;
        bubble.appendChild(textNode);

        if (sources && sources.length > 0) {
            const sourceInfo = document.createElement('span');
            sourceInfo.classList.add('source-tag');
            sourceInfo.textContent = `Sources: [${sources.join(', ')}]`;
            bubble.appendChild(sourceInfo);
        }

        chatMessages.appendChild(bubble);
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});