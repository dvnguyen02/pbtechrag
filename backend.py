from flask import Flask, render_template, request, jsonify, session, send_from_directory
import uuid
from app import build_langgraph
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()
app = Flask(__name__, static_folder='./build/static', template_folder='./build')
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
graph = build_langgraph()

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
                tool_name = latest_message.name
                tool_content = latest_message.content
                responses.append({"type": "tool", "name": tool_name, "content": tool_content})
        
        # Return all responses including AI messages and System Messages/Tool Messages
        if responses:
            return jsonify({"responses": responses, "response": responses[-1]})
        else:
            return jsonify({"responses": [], "response": {"type": "answer", "content": "No response generated"}})
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)