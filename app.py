from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import json
from typing_extensions import List, TypedDict, Annotated
from typing import Literal
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import CSVLoader
from langchain import hub
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
# environment setup
load_dotenv()
os.environ["LANGSMITH_TRACING"] = "true"

# init components
llm = ChatOpenAI(model = "gpt-3.5-turbo")
embeddings = OpenAIEmbeddings(model = "text-embedding-3-large")
prompt = hub.pull("rlm/rag-prompt")

# search chema

# The Search class provides a type-safe way to create search parameters 
# that match these sections, enabling filtered searches like:
# search = Search(query="ASUS laptop", section="beginning") 
# -> this would only search for the ASUS laptops in the beginning section of the product catalog.

class Search(TypedDict): 
    query: Annotated[str, ... , "Search query to run"]
    section: Annotated[
        Literal["entry-level laptops", "mid-range laptops", "high-end/premium laptops", "all"], ... , 
        "Section of the products to search"
    ]

from langchain_core.documents import Document

class State(TypedDict):
    question: str
    context: List[Document]
    query: Search
    answer: str

# Load and process data
from langsmith import trace
with trace("rag_pipline", projectname="simplerag") as tracer:
    from langchain_community.document_loaders import CSVLoader
    loader = CSVLoader(file_path = "pbtech_laptops_on_2025-04-08.csv",
                    csv_args= {"delimiter": ",",
                                'quotechar': '"',
                                'fieldnames': ['Product Name', 'Specification', 'Price']})

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
    vector_store = InMemoryVectorStore(embeddings)
    data_ids = vector_store.add_documents(documents=data)


# nodes for pipeline

def analyze_query(state: State): 
    """Analyze the question and determine the section to search."""
    response = llm.invoke(
        f"Analyze the question: {state['question']}. "
        "Determine if it is related to entry-level, mid-range, or high-end laptops. "
        "Return your answer as a JSON object with 'query' (the search query) and 'section' "
        "(one of: 'entry-level laptops', 'mid-range laptops', 'high-end/premium laptops', or 'all') fields."
    )
    
    try: 
        query_data = json.loads(response.content)
        # Check if we have valid section value 
        if query_data["section"] not in ["entry-level laptops", "mid-range laptops", "high-end/premium laptops", "all"]: 
            query_data["section"] = "all"
    except: 
        query_data = {
            "query": state["question"],
            "section": "all"
        }
    return {"query": query_data}

# retrieve using semantic search 
def retrieve(state: State): 
    """Retrieve products from the vector store based on the question."""
    query = state["query"]
    if query["section"] != "all": 
        filter_dict = {"metadata": {"section": query["section"]}}
        retrieved_products = vector_store.similarity_search_with_metadata(
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


# image_data = graph.get_graph().draw_mermaid_png(output_file_path="graphs/rag_graph.png") 
# """this does not work""

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
graph = graph_builder.compile()


# test run
result = graph.invoke(
    {"question": input("What product do you want to know about? ")}
)
print("Question:", result["question"])
print("Analyzed Query:", result["query"])
print("Answer:", result["answer"].content)