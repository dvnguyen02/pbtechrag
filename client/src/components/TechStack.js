import React, { useState, useEffect } from 'react';
import {Database, GitBranch, Code } from 'lucide-react';
import './TechStack.css';
const TechStack = () => {
  const [isVisible, setIsVisible] = useState(false);
  
  useEffect(() => {
    setTimeout(() => setIsVisible(true), 500);
  }, []);
  
  return (
    <div className={`tech-stack-footer ${isVisible ? 'visible' : ''}`}>
      <div className="tech-stack-container">
        <h3>Technical Implementation</h3>
        <div className="tech-stack-grid">
          <div className="tech-stack-section">
            <h4>Backend</h4>
            <ul>
              <li><span className="tech-icon"><Database size={16} /></span> Vector Database</li>
              <li><span className="tech-icon"><GitBranch size={16} /></span> Graph-based RAG Architecture</li>
            </ul>
          </div>
          <div className="tech-stack-section">
            <h4>Frontend</h4>
            <ul>
              <li><span className="tech-icon"><Code size={16} /></span> React & JavaScript</li>
              <li><span className="tech-icon"><Database size={16} /></span> Token Usage Tracking</li>
            </ul>
          </div>
        </div>
        
        <div className="footer-description">
          <p>
            This project demonstrates a production-ready RAG implementation using LangGraph with state management
            and conversation memory. The system routes queries through specialized tool functions for targeted 
            product discovery and comparison.
          </p>
          <p>
            If interested, please contact <a href="mailto:duynguyen290502@gmail.com">duynguyen290502@gmail.com</a> or contribute on  
            <a href="https://github.com/dvnguyen02/pbtechrag" target="_blank" rel="noopener noreferrer"> GitHub</a>.
          </p>
        </div>
        <div className="copyright">
          © 2025 PBTech RAG Demo. All rights reserved.
        </div>
      </div>
    </div>
  );
};

export default TechStack;