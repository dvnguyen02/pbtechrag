import React from 'react';

const DatasetPreview = ({ limitRows = null, showHeader = true }) => {
  // More realistic sample data with actual specs
  const allRows = [
    {
      productName: "Lenovo 300e G4 11.6\" HD Touch Chromebook",
      category: "Chromebook",
      generalSpecs: "MediaTek MT8183, 4GB RAM, 32GB eMMC",
      detailedSpecs: "11.6\" HD Touchscreen, Chrome OS, 16hr battery life",
      price: "$349.99",
      productUrl: "https://www.pbtech.co.nz/product/..."
    },
    {
      productName: "ASUS Vivobook Go E1504FA",
      category: "Ultrabook",
      generalSpecs: "AMD Ryzen 5 7520U, 16GB RAM, 512GB SSD",
      detailedSpecs: "15.6\" FHD Display, Windows 11, 10hr battery life",
      price: "$899.00",
      productUrl: "https://www.pbtech.co.nz/product/NBKASU1504274/..."
    },
    {
      productName: "MSI Katana 15 B13VFK",
      category: "Gaming Laptop",
      generalSpecs: "Intel i7-13620H, 16GB RAM, 1TB SSD",
      detailedSpecs: "15.6\" FHD 144Hz, RTX 4060 8GB, Windows 11",
      price: "$1,899.00",
      productUrl: "https://www.pbtech.co.nz/product/..."
    }
  ];

  const displayRows = limitRows ? allRows.slice(0, limitRows) : allRows;

  return (
    <div className="dataset-container">
      {showHeader && <h4 className="dataset-header">Retrieved Products</h4>}
      
      <div className="product-cards">
        {displayRows.map((product, index) => (
          <div key={index} className="product-card">
            <div className="product-header">
              <h5 className="product-name">{product.productName}</h5>
              <div className="product-price">{product.price}</div>
            </div>
            
            <div className="product-details">
              <div className="spec-row">
                <span className="spec-label">Category:</span>
                <span className="spec-value">{product.category}</span>
              </div>
              
              <div className="spec-row">
                <span className="spec-label">Specs:</span>
                <span className="spec-value">{product.generalSpecs}</span>
              </div>
              
              <div className="spec-row">
                <span className="spec-label">Display:</span>
                <span className="spec-value">{product.detailedSpecs.split(',')[0]}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="dataset-footer">
        <span className="dataset-note">Sample data from PBTech product catalog</span>
        <a href="https://docs.google.com/spreadsheets/d/1SDhHi2_sJkzhY9_LESBFzNB94bT9n0kaIGnEKC7741Y/edit?usp=sharing" 
           target="_blank" 
           rel="noopener noreferrer"
           className="dataset-link">
          View Full Dataset
        </a>
      </div>
    </div>
  );
};

export default DatasetPreview;