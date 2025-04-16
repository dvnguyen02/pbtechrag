import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import TokenUsageDisplay from './components/TokenUsageDisplay';
import DatasetPreview from './components/DatasetPreview';
import ChatBox from './components/ChatBox';
import ExamplesPanel from './components/ExamplesPanel';
import TechStack from './components/TechStack';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [tokenUsage, setTokenUsage] = useState(null);
  const [tokenLimitExceeded, setTokenLimitExceeded] = useState(false);
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
    
    // Fetch initial token usage
    fetchTokenUsage();
  }, []);

  useEffect(() => {
    // Scroll to bottom whenever messages change
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  const fetchTokenUsage = async () => {
    try {
      const response = await fetch('/token-usage');
      if (response.ok) {
        const data = await response.json();
        setTokenUsage(data);
      }
    } catch (error) {
      console.error('Error fetching token usage:', error);
    }
  };

  const sendMessage = async (messageToSend = null) => {
    const messageText = messageToSend || input;
    if (messageText.trim() === '') return;
    
    // Reset token limit exceeded state
    setTokenLimitExceeded(false);
    
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
      
      // Update token usage data if available
      if (data.token_usage) {
        setTokenUsage(data.token_usage);
      }
      
      // Check if token limit was exceeded
      if (data.token_limit_exceeded) {
        setTokenLimitExceeded(true);
      }
      
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
      <DatasetPreview />
      
      <div className="main-content">
        <ChatBox 
          messages={messages}
          input={input}
          setInput={setInput}
          isLoading={isLoading}
          tokenLimitExceeded={tokenLimitExceeded}
          chatBoxRef={chatBoxRef}
          sendMessage={sendMessage}
          handleKeyPress={handleKeyPress}
        />
        
        <div className="side-content">
          <ExamplesPanel 
            exampleQueries={exampleQueries}
            tokenLimitExceeded={tokenLimitExceeded}
            handleExampleClick={handleExampleClick}
          />
          
          {/* Token Usage Display */}
          {tokenUsage && <TokenUsageDisplay tokenUsage={tokenUsage} />}
        </div>
      </div>
      
      {/* Tech Stack Footer */}
      <TechStack />
    </div>
  );
}

export default App;