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
    total_products = len(data)
    third = total_products // 3

    for i, product in enumerate(data): 
        if i < third: 
            product.metadata["section"] = "entry-level laptops"
        elif i < 2*third: 
            product.metadata["section"] = "mid-range laptops"
        else: 
            product.metadata["section"] = "high-end/premium laptops"

    # Create embeddings and vector store and save them to disk
    vector_store = FAISS.from_documents(data, embeddings)
    vector_store.save_local(folder_path=embeddings_dir)

    with open(f"{embeddings_dir}/documents.pkl", "wb") as f:
        pickle.dump(data, f)
    return vector_store

if __name__ == "__main__":
    process_and_save_data("pbtech_laptops_on_2025-04-08.csv")

