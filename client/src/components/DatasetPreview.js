import React from 'react';

const DatasetPreview = () => {
  return (
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
  );
};

export default DatasetPreview;