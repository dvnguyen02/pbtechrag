# PBTech RAG System

A Retrieval-Augmented Generation (RAG) implementation that helps users search, compare, and get recommendations for PBTech products. This system combines the power of large language models with vector search to provide accurate, data-driven answers about laptop products.

![PBTech RAG Demo](https://i.imgur.com/placeholder.png)

## 🌟 Features

- **Product Search**: Find laptops that match specific criteria
- **Product Comparison**: Compare two laptops side by side
- **Price Range Filtering**: Find products within a specific budget
- **Technical Specifications**: Get detailed specs for any laptop
- **Game Compatibility**: Check if a laptop can run specific games
- **Token Usage Tracking**: Monitor API token consumption

## 🛠️ Technology Stack

### Backend
- **Flask**: Web server framework
- **LangChain & LangGraph**: Orchestrating the RAG workflow
- **FAISS**: Vector storage for semantic search
- **OpenAI**: LLM integration with GPT-4.1
- **Tiktoken**: Token counting for usage tracking

### Frontend
- **React**: UI framework
- **CSS**: Custom styling with modern animations
- **Lucide React**: Icon library
- **React Markdown**: Formatting LLM responses

## 📊 Architecture

The system follows a graph-based RAG architecture:

1. User queries are processed and routed to appropriate specialized tool functions
2. Vector similarity search finds relevant products
3. Results are formatted and passed to the LLM
4. The LLM generates a comprehensive, natural language response
5. All interactions are tracked for token usage

## 🚀 Getting Started

### Prerequisites

- Node.js (v18+)
- Python (v3.8+)
- OpenAI API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pbtech-rag.git
   cd pbtech-rag
   ```

2. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:
   ```bash
   cd client
   npm install
   cd ..
   ```

4. Create a `.env` file in the root directory with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   SECRET_KEY=your_flask_secret_key
   LANGSMITH_TRACING=true
   DAILY_TOKEN_LIMIT=100000
   REQUEST_TOKEN_LIMIT=10000
   ```

### Running the Development Server

1. Start the Flask backend:
   ```bash
   python -m backend.server
   ```

2. In a separate terminal, start the React frontend:
   ```bash
   cd client
   npm start
   ```

3. Open your browser and navigate to `http://localhost:3000`

### Building for Production

1. Build the React frontend:
   ```bash
   cd client
   npm run build
   ```

2. Copy the build to the backend:
   ```bash
   # On Windows
   build_and_copy.bat
   
   # On Linux/Mac
   # Create an equivalent shell script or run manually:
   # cp -r client/build/ backend/build/
   ```

3. Run the production server:
   ```bash
   python -m backend.server
   ```

## 💾 Data Processing

The system uses a catalog of PBTech laptop products. The data processing pipeline:

1. Loads the CSV data from `backend/data/pbtech_computers_laptops_2025-04-14.csv`
2. Processes product information and adds metadata like use case categorization
3. Creates embeddings using OpenAI's embedding model
4. Stores the vectors in a FAISS index for efficient similarity search

To reprocess data (if the catalog is updated):
```bash
python -m backend.core.data_loader
```

## 📈 Token Usage Tracking

The system includes a token counter to track and limit API usage:

- Daily token limits to control costs
- Per-request limits for performance
- Visual tracking in the UI
- Resets automatically every 24 hours

## 📝 Project Structure

```
pbtech-rag/
├── backend/               # Flask server
│   ├── core/              # Core RAG functionality
│   │   ├── data_loader.py # Data processing
│   │   ├── rag.py         # LangGraph implementation
│   │   └── token_counter.py # Token usage tracking
│   ├── embeddings/        # Vector store and document data
│   ├── server.py          # Flask entry point
│   └── data/              # Product catalog data
├── client/                # React frontend
│   ├── public/            # Static files
│   └── src/               # React components
│       ├── components/    # UI components
│       └── App.js         # Main application
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## 🔍 Available Tool Functions

The RAG system implements several specialized tool functions:

- `retrieve`: Basic vector search for products
- `compare_products`: Compare two specific products
- `get_detailed_specs`: Get comprehensive specs for a product
- `filter_by_price_range`: Find products within a price range
- `get_price`: Get the price of a specific product
- `search_game_specs`: Check game compatibility with products
- `get_most_expensive_product`: Find premium options
- `get_newest_product`: Find the latest additions
- `get_products_total`: Count total available products

## 📋 Example Queries

- "Show me laptops for graphic design"
- "Can I run Black Myth Wukong on this laptop"
- "Compare MacBook Pro and Dell XPS 15"
- "What are the specifications of the Dell XPS 13?"
- "What laptops can I buy for over $500 and under $1500?"

## 📱 Contact

For questions or increased token limits, contact:
- Email: duynguyen290502@gmail.com
- GitHub: https://github.com/dvnguyen02

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
