import React from 'react';
import { Code, Cpu, Book, Server, Database, Globe } from 'lucide-react';

const TechStack = () => {
  return (
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
  );
};

export default TechStack;