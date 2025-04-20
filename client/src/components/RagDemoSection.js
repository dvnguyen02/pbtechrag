import React, { useEffect, useRef } from 'react';
import DatasetPreview from './DatasetPreview';

const RagDemoSection = () => {
  const demoRef = useRef(null);
  
  useEffect(() => {
    // Set up intersection observer for scroll animation
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            // Once it's been revealed, no need to watch anymore
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1 } // Trigger when 10% of the element is visible
    );
    
    // Start observing the demo section
    if (demoRef.current) {
      observer.observe(demoRef.current);
    }
    
    // Clean up
    return () => {
      if (demoRef.current) {
        observer.unobserve(demoRef.current);
      }
    };
  }, []);

  return (
    <div className="demo-section">
      <h3>See The Knowledge Behind the RAG</h3>
      
      <div className="demo-container scroll-reveal" ref={demoRef}>
        <div className="demo-question">
          "What's the battery life of the Lenovo 300e G4?"
        </div>
        
        <div className="demo-columns">
          <div className="demo-col">
            <h4>What RAG sees:</h4>
            <div className="data-sample">
              <DatasetPreview limitRows={3} showHeader={true} />
            </div>
          </div>
          
          <div className="demo-col">
            <h4>What You Receive:</h4>
            <div className="response-sample">
              <div className="sample-message assistant-message">
                <div className="message-avatar">AI</div>
                <div className="message-content">
                  "The Lenovo 300e G4 11.6" HD Touch Chromebook offers up to 16 hours of battery life, based on testing with the Google Power Load Test Tool. Individual results may vary depending on usage. If you have any more questions about this model or need more details, feel free to ask!"
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* New call-to-action section */}
      <div className="rag-explanation">
        <p>
          What makes RAG unique is the transparent display of both the raw tool results and the AI's 
          interpretation. 
        </p>
        <p>
        You'll first see a tool message showing what product data was retrieved,
          followed by the RAG messages where the LLM synthesizes this information into a more helpful response. 
          <p>
          This approach ensures you receive factual information about PBTech products rather than potentially 
          outdated or hallucinated information that might come from the AI's general training.
          </p>
          
        </p>
      </div>

      <div className="try-it-cta">
        <h4>Ready to Try It Yourself?</h4>
        <p>Ask your own questions about our products in the chatbox below.</p>
        <div className="dataset-link-container">
          <p>
            Not sure about the AI's knowledge? Check out <a 
              href='https://docs.google.com/spreadsheets/d/1SDhHi2_sJkzhY9_LESBFzNB94bT9n0kaIGnEKC7741Y/edit?usp=sharing'
              target="_blank"
              rel="noopener noreferrer"
            >
              the complete dataset
            </a> that produces the responses.
          </p>
        </div>
      </div>
    </div>
  );
};

export default RagDemoSection;