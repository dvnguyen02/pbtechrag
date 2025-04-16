import React from 'react';

const ExamplesPanel = ({ exampleQueries, tokenLimitExceeded, handleExampleClick }) => {
  return (
    <div className="examples-container">
      <h3>Common Questions</h3>
      <div className="examples-grid">
        {exampleQueries.map((query, index) => (
          <div 
            key={index} 
            className="example-card"
            onClick={() => !tokenLimitExceeded && handleExampleClick(query)}
          >
            {query}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ExamplesPanel;