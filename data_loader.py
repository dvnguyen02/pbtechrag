from langchain_core.documents import Document
import os 
from langsmith import trace
from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import pickle
load_dotenv()
os.environ["LANGSMITH_TRACING"] = "true"


def process_and_save_data(csv_path = "pbtech_laptops_on_2025-04-08.csv", embeddings_dir = "embeddings"):
    
    os.makedirs(embeddings_dir, exist_ok=True)
    
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    loader = CSVLoader(
            file_path=csv_path,
            csv_args={
                "delimiter": ",",
                "quotechar": '"',
                "fieldnames": ['Product Name', 'Specification', 'Price']
            }
        )
    
    data = loader.load()
    # add metadata to each product


    for i, product in enumerate(data): 
        product.metadata["use_case"] = categorize_by_use_case(product)
        product.metadata["price"] = categorize_price(product)
        

    # Create embeddings and vector store and save them to disk
    vector_store = FAISS.from_documents(data, embeddings)
    vector_store.save_local(folder_path=embeddings_dir)

    with open(f"{embeddings_dir}/documents.pkl", "wb") as f:
        pickle.dump(data, f)
    return vector_store

def categorize_by_use_case(product): 
    """Determine the use case based on laptop"""
    specs = product.page_content.lower()
    
    if "gaming" in specs or "rtx" in specs or "rx" in specs or "nvidia" in specs:
        return "Gaming"
    elif "cad" in specs or "render" in specs or "studio" in specs or "workstation" in specs:
        return "Professional/Workstation"
    elif "business" in specs or "thinkpad" in specs or "elitebook" in specs or "latitude" in specs or "enterprise" in specs:
        return "Business"
    elif "thin" in specs or "light" in specs or "ultrabook" in specs or "slim" in specs:
        return "Ultraportable"
    elif "2-in-1" in specs or "convertible" in specs or "touch" in specs or "tablet" in specs:
        return "Convertible/2-in-1"
    elif "student" in specs or "education" in specs:
        return "Student"
    else:
        return "General Purpose"

def categorize_price(product): 
    """Determine price-range category"""
    try:
        page_content = product.page_content
        # Extract price from the content, accounting for different formats
        if "Price : " in page_content:
            price_str = page_content.split("Price : ")[1]
        elif "Price:" in page_content:
            price_str = page_content.split("Price:")[1]
        elif "Price" in page_content:
            price_str = page_content.split("Price")[1]
        else:
            return "unknown"
        
        # Extract numeric value (remove $ and other non-numeric characters)
        price_numeric = ''.join([c for c in price_str if c.isdigit() or c == '.'])
        
        # Convert to float for comparison
        price = float(price_numeric)
        
        if price < 600: 
            return "budget"
        elif price < 1000: 
            return "mid-range"
        elif price < 1500: 
            return "premium"
        else: 
            return "highend"
    except (ValueError, IndexError):
        return "unknown"

if __name__ == "__main__":
    process_and_save_data("pbtech_laptops_on_2025-04-08.csv")
    print("Finished Loading Data.")

