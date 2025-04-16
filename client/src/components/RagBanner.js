import React from 'react';

const RagBanner = ({ 
  title = "PBTech RAG (Unofficial)", 
  subtitle = "A product recommendation system powered by Retrieval Augmented Generation" 
}) => {
  return (
    <div className="rag-banner">
      <h1>{title}</h1>
      <p className="rag-banner-subtitle">{subtitle}</p>
    </div>
  );
};

export default RagBanner;