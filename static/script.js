$(document).ready(function() {
    // Add welcome message
    addMessage("Welcome to PBTech! How can I help you today?", "assistant");

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
        $("#chatBox").append(`<div id="${loadingId}" class="assistant-message">...</div>`);
        
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
        
        $("#chatBox").append(`<div class="${messageClass}">${message}</div>`);
        
        // Scroll to bottom
        $("#chatBox").scrollTop($("#chatBox")[0].scrollHeight);
    }
});