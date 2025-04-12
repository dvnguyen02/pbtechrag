$(document).ready(function() {
    // Add welcome message
    addMessage("Welcome to the Laptop Recommendation System! How can I help you today?", "assistant");

    // Send button click event
    $("#sendBtn").click(sendMessage);
    
    // Enter key event
    $("#userInput").keypress(function(e) {
        if(e.which == 13) {
            sendMessage();
        }
    });
    
    // Example query click event
    $(".example-query").click(function() {
        $("#userInput").val($(this).text());
        sendMessage();
    });
    
    function sendMessage() {
        const userInput = $("#userInput").val().trim();
        
        if(userInput === "") return;
        
        // Add user message to chat
        addMessage(userInput, "user");
        
        // Clear input
        $("#userInput").val("");
        
        // Add loading indicator
        const loadingId = "loading-" + Date.now();
        $("#chatBox").append(`<div id="${loadingId}" class="assistant-message">Thinking...</div>`);
        
        // Send to backend
        $.ajax({
            url: "/query",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ query: userInput }),
            success: function(data) {
                // Remove loading indicator
                $(`#${loadingId}`).remove();
                
                // Add response to chat
                if(data.response) {
                    if(data.response.type === "answer") {
                        addMessage(data.response.content, "assistant");
                    } else if(data.response.type === "tool") {
                        addMessage(`Tool ${data.response.name}: ${data.response.content}`, "tool");
                    }
                }
            },
            error: function(error) {
                // Remove loading indicator
                $(`#${loadingId}`).remove();
                
                // Add error message
                addMessage("Sorry, there was an error processing your request.", "assistant");
                console.error(error);
            }
        });
    }
    
    function addMessage(message, role) {
        const messageClass = role === "user" ? "user-message" : 
                             role === "assistant" ? "assistant-message" : "tool-message";
        
        // Format the assistant's message if it contains a comparison or structured content
        let formattedMessage = message;
        
        if (role === "assistant") {
            // Format comparison content
            formattedMessage = formatAssistantMessage(message);
        }
        
        $("#chatBox").append(`<div class="${messageClass}">${formattedMessage}</div>`);
        
        // Scroll to bottom
        $("#chatBox").scrollTop($("#chatBox")[0].scrollHeight);
    }
    
    function formatAssistantMessage(message) {
        // Check if message contains comparison indicators
        if (message.includes("comparing") || message.includes("comparison") || 
            message.includes("vs") || message.includes("versus") || 
            message.toLowerCase().includes("comparing between")) {
            return formatComparisonMessage(message);
        }
        
        // Check for numbered lists and add proper HTML formatting
        if (/\d+\.\s+\*\*[^*]+\*\*/.test(message)) {
            return formatListMessage(message);
        }
        
        // Basic markdown-style formatting for all messages
        return formatMarkdown(message);
    }
    
    function formatComparisonMessage(message) {
        // Replace markdown-style bold with HTML
        let formatted = message.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        
        // Add line breaks after colons and periods followed by a dash or asterisk
        formatted = formatted.replace(/:\s+-/g, ':<br>-');
        formatted = formatted.replace(/\.\s+-/g, '.<br>-');
        
        // Add paragraph breaks for numbered sections
        formatted = formatted.replace(/(\d+\.\s+\*\*[^:]+\*\*:)/g, '<p>$1</p>');
        formatted = formatted.replace(/(\d+\.\s+<strong>[^:]+<\/strong>:)/g, '<p>$1</p>');
        
        // Format comparison sections
        if (formatted.includes("Overall")) {
            const parts = formatted.split("Overall");
            formatted = parts[0] + "<p><strong>Overall</strong>: " + parts[1] + "</p>";
        }
        
        return formatted;
    }
    
    function formatListMessage(message) {
        // Convert numbered lists with markdown-style formatting to HTML
        const lines = message.split('\n');
        const formattedLines = lines.map(line => {
            // Check if line starts with a number followed by a dot and space
            if (/^\d+\.\s+/.test(line)) {
                // Format the line as an HTML list item
                return `<li>${line.replace(/^\d+\.\s+/, '')}</li>`;
            }
            return line;
        });
        
        // Join the lines and wrap numbered lists in <ol> tags
        const formattedMessage = formattedLines.join('\n');
        return formattedMessage.replace(/<li>/g, '<ol><li>').replace(/<\/li>/g, '</li></ol>');
    }
    
    function formatMarkdown(message) {
        // Convert markdown-style bold to HTML bold
        let formatted = message.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        
        // Convert markdown-style italic to HTML italic
        formatted = formatted.replace(/\*([^*]+)\*/g, '<em>$1</em>');
        
        // Convert markdown-style headers to HTML headers
        formatted = formatted.replace(/^# (.+)$/gm, '<h3>$1</h3>');
        formatted = formatted.replace(/^## (.+)$/gm, '<h4>$1</h4>');
        formatted = formatted.replace(/^### (.+)$/gm, '<h5>$1</h5>');
        
        // Convert markdown-style lists to HTML lists
        formatted = formatted.replace(/^- (.+)$/gm, '<ul><li>$1</li></ul>');
        
        // Add paragraph breaks for better readability
        formatted = formatted.replace(/\n\n/g, '<p></p>');
        
        return formatted;
    }
});