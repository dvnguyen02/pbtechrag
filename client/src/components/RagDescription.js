import React from 'react';

const RagDescription = () => {
  return (
    <div className="rag-description">
      <h2>How It Works</h2>
      <p>
        This system uses Retrieval Augmented Generation (RAG) to provide accurate and relevant 
        information about PBTech products. When you ask a question, the system:
      </p>
      <div className="features">
        <div className="feature-item">
          <h3>Retrieves</h3>
          <p>Searches through a database of product information to find relevant details</p>
        </div>
        <div className="feature-item">
          <h3>Augments</h3>
          <p>Enhances the AI's knowledge with the retrieved information</p>
        </div>
        <div className="feature-item">
          <h3>Generates</h3>
          <p>Creates accurate and helpful responses based on the combined knowledge</p>
        </div>
      </div>
      
      <h3 className="tool-section-title">Special Tools & Function Calls</h3>
      <p>
        When you ask a complex question, the system may use specialized tools to provide better answers:
      </p>
      
      <div className="tool-workflow">
        <div className="workflow-step">
          <h4>1. Query Analysis</h4>
          <p>The system analyzes your question to determine if it needs specific product data</p>
        </div>
        
        <div className="workflow-step">
          <h4>2. Tool Selection</h4>
          <p>If needed, it selects the appropriate tool (e.g., product search, comparison, price check)</p>
        </div>
        
        <div className="workflow-step">
          <h4>3. Tool Execution</h4>
          <p>The selected tool retrieves structured data about products from our database</p>
        </div>
        
        <div className="workflow-step">
          <h4>4. Response Integration</h4>
          <p>You'll see both the raw tool results and a helpful summary in your conversation</p>
        </div>
      </div>
      
      <div className="example-container">
        <h4>Example:</h4>
        <p>If you ask <strong>"Compare MacBook Pro and Dell XPS 15"</strong>, you'll see:</p>
        <ul className="example-list">
          <li>A tool call that fetches detailed specs for both products</li>
          <li>The raw comparison data (RAM, CPU, price, etc.)</li>
          <li>A summarized, easy-to-understand comparison from the AI</li>
        </ul>
      </div>
    </div>
  );
};

export default RagDescription;