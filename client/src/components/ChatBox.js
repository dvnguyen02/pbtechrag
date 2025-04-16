import React from 'react';
import { Send, HelpCircle, MessageSquare, Zap, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const ChatBox = ({ 
  messages, 
  input, 
  setInput, 
  isLoading, 
  tokenLimitExceeded, 
  chatBoxRef, 
  sendMessage, 
  handleKeyPress 
}) => {
  return (
    <div className="chat-container">
      <div className="header">
        <div className="logo">
          <h1>PBTech RAG</h1>
        </div>
      </div>
      
      {tokenLimitExceeded && (
        <div className="token-limit-message">
          <AlertCircle className="token-limit-icon" size={20} />
          <span>Token limit exceeded. Please try again later tomorrow or contact duynguyen290502@gmail.com for increased limits.</span>
        </div>
      )}
      
      <div className="chat-box" ref={chatBoxRef}>
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}-message`}>
            <div className="message-avatar">
              {message.role === 'user' ? 
                <MessageSquare size={20} /> : 
                message.role === 'assistant' ? 
                  <Zap size={20} /> : 
                  <HelpCircle size={20} />
              }
            </div>
            <div className="message-content">
              {message.role === 'tool' && (
                <div className="tool-header">
                  <span className="tool-name">{message.name || 'Tool'}</span>
                </div>
              )}
              {message.role === 'tool' ? (
                <div className="tool-content">{message.content}</div>
              ) : (
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm]}
                  className="markdown-content"
                >
                  {message.content}
                </ReactMarkdown>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message assistant-message">
            <div className="message-avatar">
              <Zap size={20} />
            </div>
            <div className="message-content typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
      </div>
      
      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask any question..."
          className="message-input"
          disabled={tokenLimitExceeded}
        />
        <button 
          onClick={sendMessage} 
          className="send-button"
          disabled={isLoading || input.trim() === '' || tokenLimitExceeded}
        >
          <Send size={20} />
        </button>
      </div>
    </div>
  );
};

export default ChatBox;