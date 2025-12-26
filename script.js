// ICSE AI Tutor Frontend - Render Deployment
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('questionForm');
    const questionInput = document.getElementById('question');
    const subjectSelect = document.getElementById('subject');
    const chapterInput = document.getElementById('chapter');
    const responseDiv = document.getElementById('response');
    const loadingDiv = document.getElementById('loading');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const subject = subjectSelect.value;
        const chapter = chapterInput.value.trim();
        const question = questionInput.value.trim();
        
        if (!question) {
            alert('Please enter a question!');
            return;
        }
        
        // Show loading
        loadingDiv.style.display = 'block';
        responseDiv.innerHTML = '';
        
        try {
            const response = await fetch('/api/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    subject: subject,
                    chapter: chapter || 'General',
                    question: question
                })
            });
            
            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }
            
            const data = await response.json();
            displayResponse(data.answer);
            
        } catch (error) {
            console.error('Error:', error);
            displayResponse(
                `<div class="error">❌ Sorry! Something went wrong. Please try again.</div>
                 <details>
                   <summary>Debug Info</summary>
                   <pre>${error.message}</pre>
                 </details>`
            );
        } finally {
            loadingDiv.style.display = 'none';
            questionInput.value = '';
            chapterInput.value = '';
        }
    });
    
    function displayResponse(answer) {
        responseDiv.innerHTML = `
            <div class="response-card">
                <h3>🤖 AI Tutor Answer:</h3>
                <div class="answer">${answer}</div>
                <button onclick="clearResponse()" class="clear-btn">New Question</button>
            </div>
        `;
        responseDiv.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Auto-focus question input
    questionInput.focus();
});

// Utility function for clearing response
function clearResponse() {
    document.getElementById('response').innerHTML = '';
    document.getElementById('question').focus();
}
