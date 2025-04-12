from flask import Flask, render_template, request, jsonify, session
import uuid
from app import build_langgraph
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
graph = build_langgraph()

@app.route('/')
def index(): 
    """Serve the main page"""
    if 'thread_id' not in session: 
        session['thread_id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/query', methods = ['POST'])
def query(): 
    """Handle user queries"""
    user_input = request.json.get('query', '')
    thread_id = session.get('thread_id', str(uuid.uuid4()))
    config = {"configurable": {"thread_id": thread_id}}
    # Process query through existing RAG
    responses = []
    try: 
        for step in graph.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            stream_mode="values",
            config=config
        ): 

            latest_message = step["messages"][-1]
            # format based on message type
            if latest_message.type == "ai": 
                response_content = latest_message.content
                responses.append({"type": "answer", "content": response_content})
            elif latest_message.type == "tool": 
                tool_name = latest_message.name  # Changed from .tool to .name
                tool_content = latest_message.content
                responses.append({"type": "tool", "name": tool_name, "content": tool_content})
        
        # Return the last response    
        if responses: 
            response_content = responses[-1]
        else: 
            response_content = {"type": "answer", "content": "No response generated"}
        
        return jsonify({"response": response_content})
    
    except Exception as e: 
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)