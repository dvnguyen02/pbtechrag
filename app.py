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
    query: Search
    answer: str


# nodes (application steps) 

# retrieve using semantic search 
def retrieve(state: State): 
    """Retrieve products from the vector store based on the question."""
    query = state["query"]
    if query["section"] != "all": 
        filter_dict = {"metadata": {"section": query["section"]}}
        retrieved_products = vector_store.similarity_search_with_score(
            query["query"], 
            k=3, 
            filter=filter_dict
        )
    else: 
        retrieved_products = vector_store.similarity_search(query["query"], k=3)
    return {"context": retrieved_products}
            
def generation(state: State): 
    product_contents = "\n\n".join([doc.page_content for doc in state["context"]])
    messages = prompt.invoke(
        {"context": product_contents, "question": state["question"]}
    )
    response = llm.invoke(messages)
    return {"answer": response}



# image_data = graph.get_graph().draw_mermaid_png(output_file_path="graphs/rag_graph.png") """this does not work""


# #Run test
# result = graph.invoke({"question": "How much is ASUS Vivobook Go E1504FA 15.6 FHD Laptop?"})
# print(result["answer"].content)

# query analysis could optimized search queries from raw user input
total_products = len(data)
third = total_products // 3

for i, product in enumerate(data): 
    if i < third: 
        product.metadata["section"] = "entry-level laptops"
    elif i < 2: 
        product.metadata["section"] = "mid-range laptops"
    else: 
        product.metadata["section"] = "high-end/premium laptops"

# with metadata, we could now use metadata to filter the search results.
from langchain_core.vectorstores import InMemoryVectorStore
vector_store = InMemoryVectorStore(embedding=embeddings)
_ = vector_store.add_documents(documents=data)

# schema

from typing import Literal
from typing_extensions import Annotated


class Search(TypedDict): 
    query: Annotated[str, ... , "Search query to run"]
    section: Annotated[
        Literal["entry-level laptops", "mid-range laptops", "high-end/premium laptops"], ... , "Section of the products to search"
    ]

# The Search class provides a type-safe way to create search parameters 
# that match these sections, enabling filtered searches like:
# search = Search(query="ASUS laptop", section="beginning") 
# -> this would only search for the ASUS laptops in the beginning section of the product catalog.

def analyze_query(state: State): 
    """Analyze the question and determine the section to search."""
    response = llm.invoke(
        f"Analyze the question: {state['question']}. "
        "Determine if it is related to entry-level, mid-range, or high-end laptops."
    )
    import json # for error handling

    try: 
        query_data = json.loads(response.content)
        # check if we have valid section value 
        if query_data["section"] not in ["entry-level laptops", "mid-range laptops", "high-end/premium laptops"]: 
            query_data["section"] = "entry-level laptops"
    except: 
        query_data = {
            "query": state["question"],
            "section": "entry-level laptops"
        }
    return {"query": query_data}

# control flow using graph object
# connecting retrieval and generation steps
from langgraph.graph import START, StateGraph

graph_builder = StateGraph(State)
graph_builder.add_node("analyze_query", analyze_query)
graph_builder.add_node("retrieve", retrieve)
graph_builder.add_node("generation", generation)

# connect nodes in sq
graph_builder.add_edge(START, "analyze_query")
graph_builder.add_edge("analyze_query", "retrieve")
graph_builder.add_edge("retrieve", "generation")
