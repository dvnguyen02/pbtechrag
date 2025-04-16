from flask import Flask, render_template, request, jsonify, session, send_from_directory
import uuid
from backend.core.rag import build_langgraph
from dotenv import load_dotenv
import os
from pathlib import Path
from backend.core.token_counter import TokenCounter

load_dotenv()
app = Flask(__name__, static_folder='./build/static', template_folder='./build')
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
graph = build_langgraph()

# Initialize the token counter
token_counter = TokenCounter(
    daily_limit=int(os.environ.get("DAILY_TOKEN_LIMIT", 100000)),
    request_limit=int(os.environ.get("REQUEST_TOKEN_LIMIT", 10000))
)

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve React App"""
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    elif path != "" and os.path.exists(app.template_folder + '/' + path):
        return send_from_directory(app.template_folder, path)
    else:
        # If 'thread_id' not in session, create it
        if 'thread_id' not in session:
            session['thread_id'] = str(uuid.uuid4())
        return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    """Handle user queries with token limit enforcement"""
    user_input = request.json.get('query', '')
    thread_id = session.get('thread_id', str(uuid.uuid4()))
    config = {"configurable": {"thread_id": thread_id}}
    
    # Estimate token usage for this request
    estimated_tokens = token_counter.count_tokens(user_input)
    
    # Check token limits
    within_limits, message = token_counter.check_limits(thread_id, estimated_tokens)
    if not within_limits:
        return jsonify({
            "responses": [{
                "type": "answer", 
                "content": f"⚠️ {message}. Please try again later or contact duynguyen290502@gmail.com for increased limits."
            }],
            "response": {
                "type": "answer", 
                "content": f"⚠️ {message}. Please try again later or contact duynguyen290502@gmail.com for increased limits."
            },
            "token_limit_exceeded": True
        })
    
    # Process query through existing RAG
    responses = []
    try:
        # Track actual input tokens
        token_counter.track_tokens(thread_id, estimated_tokens)
        
        # IMPORTANT: Just pass the current user message
        # The LangGraph will handle the conversation history internally
        # based on the thread_id in the config
        for step in graph.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            stream_mode="values",
            config=config
        ):
            latest_message = step["messages"][-1]
            # format based on message type
            if latest_message.type == "ai":
                response_content = latest_message.content
                # Track response tokens
                response_tokens = token_counter.count_tokens(response_content)
                token_counter.track_tokens(thread_id, response_tokens)
                responses.append({"type": "answer", "content": response_content})
            elif latest_message.type == "tool":
                tool_name = latest_message.name
                tool_content = latest_message.content
                # Track tool response tokens
                tool_tokens = token_counter.count_tokens(tool_content)
                token_counter.track_tokens(thread_id, tool_tokens)
                responses.append({"type": "tool", "name": tool_name, "content": tool_content})
        
        # Get usage stats to return to client
        usage_stats = token_counter.get_usage_stats(thread_id)
        
        # Return all responses including AI messages and System Messages/Tool Messages
        if responses:
            return jsonify({
                "responses": responses, 
                "response": responses[-1],
                "token_usage": usage_stats
            })
        else:
            return jsonify({
                "responses": [], 
                "response": {"type": "answer", "content": "No response generated"},
                "token_usage": usage_stats
            })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/token-usage', methods=['GET'])
def get_token_usage():
    """Get current token usage statistics"""
    thread_id = session.get('thread_id')
    if not thread_id:
        return jsonify({"error": "No active session"}), 400
    
    usage_stats = token_counter.get_usage_stats(thread_id)
    return jsonify(usage_stats)

@app.route('/reset-conversation', methods=['POST'])
def reset_conversation():
    """Reset the conversation history"""
    # Generate a new thread ID to start a fresh conversation
    new_thread_id = str(uuid.uuid4())
    session['thread_id'] = new_thread_id
    
    return jsonify({"success": True, "new_thread_id": new_thread_id})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port)