from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import getpass
import os

load_dotenv()
os.environ["LANGSMITH_TRACING"] = "true"

llm = ChatOpenAI(model = "gpt-3.5-turbo")

# Use trace context manager for the RAG pipeline
from langsmith import trace
with trace("rag_pipline", projectname="simplerag") as tracer:
    # Embeddings

    from langchain_openai import OpenAIEmbeddings
    embeddings = OpenAIEmbeddings(model = "text-embedding-3-large")

    # Vector Store
    from langchain_core.vectorstores import InMemoryVectorStore
    vector_store = InMemoryVectorStore(embeddings)

    # Load data
    from langchain_community.document_loaders import CSVLoader

    loader = CSVLoader(file_path = "pbtech_laptops_on_2025-04-08.csv",
                    csv_args= {"delimiter": ",",
                                'quotechar': '"',
                                'fieldnames': ['Product Name', 'Specification', 'Price']})

    data = loader.load()

    # Store documents
    data_ids = vector_store.add_documents(documents=data)

    # Building retrieval and genearation (rag)
    from langchain import hub

    prompt = hub.pull("rlm/rag-prompt")
    # example_messages = prompt.invoke(
    #     {"context": "Product Name: HP Pavilion 15, Specification: Intel Core i5, 8GB RAM, 512GB SSD, Price: $799.99",
    #     "question": "What is the price of the HP Pavilion 15?"}
    # )
    # example_messages= example_messages.to_messages()


# Using langGraph
from langchain_core.documents import Document
from typing_extensions import List, TypedDict

class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


# nodes (application steps) 

# retrieve using semantic search 
def retrieve(state: State): 
    """Retrieve products from the vector store based on the question."""
    retrieved_products = vector_store.similarity_search(state["question"], k=3)
    return {"context": retrieved_products}
            
def generation(state: State): 
    product_contents = "\n\n".join([doc.page_content for doc in state["context"]])
    messages = prompt.invoke(
        {"context": product_contents, "question": state["question"]}
    )
    response = llm.invoke(messages)
    return {"answer": response}


# control flow using graph object
# connecting retrieval and generation steps
from langgraph.graph import START, StateGraph

graph_builder = StateGraph(State).add_sequence([retrieve, generation])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()
result = graph.invoke({"question": "How much is ASUS Vivobook Go E1504FA 15.6"" FHD Laptop?"})
print(result["answer"])