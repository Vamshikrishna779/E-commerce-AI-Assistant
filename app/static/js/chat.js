document.addEventListener('DOMContentLoaded', function() {
    // Scroll to bottom of chat
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Copy SQL button functionality
    document.querySelectorAll('.copy-sql').forEach(button => {
        button.addEventListener('click', function() {
            const sql = this.getAttribute('data-sql');
            navigator.clipboard.writeText(sql).then(() => {
                const originalText = this.innerHTML;
                this.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg> Copied!';
                setTimeout(() => {
                    this.innerHTML = originalText;
                }, 2000);
            });
        });
    });

    // Clear chat button
    const clearChatBtn = document.getElementById('clear-chat');
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            if (confirm('Are you sure you want to clear this chat?')) {
                const sessionId = window.location.pathname.split('/')[2];
                await fetch(`/chat/${sessionId}/clear`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                window.location.reload();
            }
        });
    }

    // Export chat button
    const exportChatBtn = document.getElementById('export-chat');
    if (exportChatBtn) {
        exportChatBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            const sessionId = window.location.pathname.split('/')[2];
            window.location.href = `/chat/${sessionId}/export`;
        });
    }
});