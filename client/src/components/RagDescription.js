import React, { useState, useEffect } from 'react';
import './RagDescription.css'; // Make sure to create this CSS file for animations

const RagDescription = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [featuresVisible, setFeaturesVisible] = useState([false, false, false]);
  const [skillsVisible, setSkillsVisible] = useState(false);

  useEffect(() => {
    // Initial fade in for the main component
    setTimeout(() => setIsVisible(true), 300);
    
    // Sequentially reveal feature items
    setTimeout(() => setFeaturesVisible([true, false, false]), 600);
    setTimeout(() => setFeaturesVisible([true, true, false]), 900);
    setTimeout(() => setFeaturesVisible([true, true, true]), 1200);
    
    // Reveal skills section
    setTimeout(() => setSkillsVisible(true), 1500);
  }, []);

  return (
    <div className={`rag-description ${isVisible ? 'visible' : ''}`}>
      <h2 className="title-animation">Data Science-Powered RAG Implementation</h2>
      
      <div className="intro slide-in-animation">
        <p>
          An implementation demonstrating advanced vector search capabilities 
          with a graph-based RAG architecture.
        </p>
      </div>
      
      <div className="features">
        <div className={`feature-item ${featuresVisible[0] ? 'visible' : ''}`}>
          <h3>Retrieves</h3>
          <p>Searches databases for relevant information when questions are asked</p>
        </div>
        <div className={`feature-item ${featuresVisible[1] ? 'visible' : ''}`}>
          <h3>Augments</h3>
          <p>Enhances AI responses with retrieved data for factual accuracy</p>
        </div>
        <div className={`feature-item ${featuresVisible[2] ? 'visible' : ''}`}>
          <h3>Generates</h3>
          <p>Creates natural, helpful responses that sound human and conversational</p>
        </div>
      </div>
      
      <div className="benefits-section fade-in-animation">
        <h3 className="tool-section-title">Technical Implementation</h3>
        
        <p>
          This project demonstrates advanced LLM application engineering: 
          graph-based RAG architecture, specialized tool functions for targeted information retrieval,
          vector similarity matching, and state management for conversational memory across complex workflows.
        </p>
      </div>
      <div className="benefits-section fade-in-animation">
        <h3 className="tool-section-title">How it works?</h3>
        
        <p>
        When a user asks a question, the system first analyzes the query, then selects appropriate specialized function 
        calls/tool calls (such as retrieve, compare_products, get_price, etc.) to fetch relevant product information from a 
        vector database containing PBTech's laptop catalog. The retrieved product data is embedded using advanced embedding 
        models, allowing for semantic searching beyond simple keyword matching. 
        The system then augments the AI's knowledge with this retrieved information and generates a comprehensive response.
        </p>

        <p>
        What makes this system unique is the transparent display of both the raw tool results and the AI's 
        interpretation: you'll first see a "tool message" showing exactly what product data was retrieved 
        (technical specifications, pricing, etc.), followed by an "assistant message" where the LLM synthesizes 
        this information into a more helpful response. This approach ensures you receive up-to-date, factual 
        information about PBTech products rather than potentially outdated or hallucinated information that 
        might come from the AI's general training.

        </p>
      </div>
      <div className={`example-container ${skillsVisible ? 'skills-visible' : ''}`}>
        <h4>Example Queries:</h4>
        <ul className="example-list">
        <li><strong>Compare product A and B</strong> - Get detailed comparisons instantly</li>
        <li><strong>Find products matching specific criteria</strong> - Discover exactly what you need</li>
        <li><strong>Check Laptop compatibility with system requirements</strong> - Get reliable technical information</li>
        <li><strong>Show premium products</strong> - Find high-end alternatives quickly</li>
        <li><strong>What's been updated recently?</strong> - Stay informed on latest changes</li>
        </ul>
      </div>
    </div>
  );
};

export default RagDescription;