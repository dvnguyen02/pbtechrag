import React from 'react';
import { Send, HelpCircle, MessageSquare, Cpu, AlertCircle } from 'lucide-react'; 
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
  // Add this wrapper function to ensure proper parameter handling
  const handleSendClick = (e) => {
    e.preventDefault();
    sendMessage(input); // Pass the input value explicitly
  };

  return (
    <div className="chat-container">
      <div className="header">
        <div className="logo">
        </div>
      </div>
      
      {tokenLimitExceeded && (
        <div className="token-limit-message">
          <AlertCircle className="token-limit-icon" size={20} />
          <span>Token limit exceeded. Please try again later tomorrow or contact duynguyen290502@gmail.com for increased limits.</span>
        </div>
      )}
      
      <div 
        className="chat-box custom-scrollbar" 
        ref={chatBoxRef}
        style={{
          height: "60vh",
          maxHeight: "calc(100vh - 200px)",
          overflowY: "auto",
          padding: "10px",
        }}
      >
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}-message`}>
            <div className="message-avatar">
              {message.role === 'user' ? 
                <MessageSquare size={20} /> : 
                message.role === 'assistant' ? 
                  <Cpu size={20} /> : // Changed Zap to Cpu
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
              <Cpu size={20} /> {/* Changed Zap to Cpu */}
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
          placeholder="Ask any relating to products on PBTech.."
          className="message-input"
          disabled={tokenLimitExceeded}
        />
        <button 
          onClick={handleSendClick} 
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