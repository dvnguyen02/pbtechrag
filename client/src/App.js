import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import { Send, HelpCircle, MessageSquare, Zap, Database, Server, Code, Globe, Cpu, Book } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatBoxRef = useRef(null);
  
  const exampleQueries = [
    "Recommend me a laptop for gaming under $1500",
    "Compare Acer Chromebook C734 11.6'' HD and Lenovo ThinkPad T14s G5 14",
    "What does CPU mean?",
    "What is the price of Acer Swift?",
    "What's a good laptop for uni?",
    "In a range of 2000 to 2500, suggest me some laptops"
  ];

  useEffect(() => {
    // Add welcome message when component mounts
    setMessages([
      { role: 'assistant', content: 'Welcome to PBTech! How can I help you today?' }
    ]);
  }, []);

  useEffect(() => {
    // Scroll to bottom whenever messages change
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async (messageToSend = null) => {
    const messageText = messageToSend || input;
    if (messageText.trim() === '') return;
    
    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: messageText }]);
    setInput('');
    setIsLoading(true);
    
    try {
      const response = await fetch('/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: messageText }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log("API Response:", data); // Debug logging
      
      if (data.responses && Array.isArray(data.responses)) {
        // Add each response to messages sequentially
        for (const item of data.responses) {
          if (item.type === 'answer') {
            setMessages(prev => [...prev, { 
              role: 'assistant', 
              content: item.content 
            }]);
          } else if (item.type === 'tool') {
            setMessages(prev => [...prev, { 
              role: 'tool', 
              name: item.name || 'Unknown Tool', 
              content: item.content 
            }]);
          }
        }
      } else if (data.response) {
        // Fallback for original API format
        if (data.response.type === 'answer') {
          setMessages(prev => [...prev, { 
            role: 'assistant', 
            content: data.response.content 
          }]);
        } else if (data.response.type === 'tool') {
          setMessages(prev => [...prev, { 
            role: 'tool', 
            name: data.response.name || 'Unknown Tool', 
            content: data.response.content 
          }]);
        }
      } else {
        // No proper response format
        throw new Error('Invalid response format from server');
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `Sorry, there was an error processing your request: ${error.message}` 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExampleClick = (query) => {
    setInput(query);
    // Send the query directly rather than relying on state update
    sendMessage(query);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };


  return (
    <div className="app-container">
      <div className="tech-stack-preview">
        <h2>PBTech RAG Dataset Preview</h2>
        <div className="dataset-preview">
          <table>
            <thead>
              <tr>
                <th>Product Name</th>
                <th>Category</th>
                <th>General Specs</th>
                <th>Detailed Specs</th>
                <th>Price</th>
                <th>Product URL</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>ASUS Vivobook Go E1504FA 15.6" FHD</td>
                <td>computers/laptops</td>
                <td>AMD Ryzen 5 7520U - 16GB RAM - 512GB SSD - Win 11 Home - 1yr warranty - AC WiFi 5 + BT4.1 - Webcam - USB-C & HDMI</td>
                <td>...</td>
                <td>$1078.75</td>
                <td>
                  <a href="https://www.pbtech.co.nz/product/NBKASU1504274/ASUS-Vivobook-Go-E1504FA-156-FHD-AMD-Ryzen-5-7520U" target='_blank' rel="noopener noreferrer">
                  Product Page
                  </a>
                </td>
              </tr>
            </tbody>
          </table>
          <div className="dataset-note">* Sample data from PBTech product catalog</div>
          <div className="dataset-link">
            <a href="https://docs.google.com/spreadsheets/d/1SDhHi2_sJkzhY9_LESBFzNB94bT9n0kaIGnEKC7741Y/edit?usp=sharing" target="_blank" rel="noopener noreferrer">
              View Dataset
            </a>
          </div>
        </div>
      </div>
      
      <div className="chat-container">
        <div className="header">
          <div className="logo">
            <h1>PBTech RAG</h1>
          </div>
        </div>
        
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
          />
          <button 
            onClick={sendMessage} 
            className="send-button"
            disabled={isLoading || input.trim() === ''}
          >
            <Send size={20} />
          </button>
        </div>
      </div>
      
      <div className="examples-container">
        <h3>Common Questions</h3>
        <div className="examples-grid">
          {exampleQueries.map((query, index) => (
            <div 
              key={index} 
              className="example-card"
              onClick={() => handleExampleClick(query)}
            >
              {query}
            </div>
          ))}
        </div>
      </div>
      
      {/* New Tech Stack Footer */}
      <div className="tech-stack-footer">
        <div className="tech-stack-container">
          <h3>Tech Stack</h3>
          <div className="tech-stack-grid">
            <div className="tech-stack-section">
              <h4>LLM Framework</h4>
              <ul>
                <li><span className="tech-icon"><Code size={16} /></span> LangChain</li>
                <li><span className="tech-icon"><Cpu size={16} /></span> LangGraph</li>
                <li><span className="tech-icon"><Book size={16} /></span> GPT-4.1 API</li>
              </ul>
            </div>
            <div className="tech-stack-section">
              <h4>Backend</h4>
              <ul>
                <li><span className="tech-icon"><Server size={16} /></span> Flask</li>
                <li><span className="tech-icon"><Database size={16} /></span> FAISS Vector DB</li>
                <li><span className="tech-icon"><Code size={16} /></span> OpenAI Embeddings</li>
              </ul>
            </div>
            <div className="tech-stack-section">
              <h4>Data Processing</h4>
              <ul>
                <li><span className="tech-icon"><Database size={16} /></span> Pandas</li>
                <li><span className="tech-icon"><Code size={16} /></span> CSV Loader</li>
                <li><span className="tech-icon"><Cpu size={16} /></span> RecursiveCharacterTextSplitter</li>
              </ul>
            </div>
            <div className="tech-stack-section">
              <h4>Frontend</h4>
              <ul>
                <li><span className="tech-icon"><Code size={16} /></span> React.js</li>
                <li><span className="tech-icon"><Globe size={16} /></span> JavaScript</li>
                <li><span className="tech-icon"><Code size={16} /></span> Lucide Icons</li>
              </ul>
            </div>
          </div>
          <div className="copyright">
            © 2025 PBTech RAG Demo. All rights reserved.
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;