from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import json
from typing_extensions import List, TypedDict, Annotated
from typing import Literal
from langchain_openai import OpenAIEmbeddings
#from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.vectorstores import FAISS
from langchain import hub
from langchain_core.documents import Document
from langgraph.graph import START, END, StateGraph, MessagesState
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, FunctionMessage
from langgraph.prebuilt import tools_condition

# environment setup
load_dotenv()
os.environ["LANGSMITH_TRACING"] = "true"

# init components
llm = ChatOpenAI(model = "gpt-4o")
prompt = hub.pull("rlm/rag-prompt")


# Load pre computed embeddings
embeddings_dir = "embeddings"
try:
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vector_store = FAISS.load_local(embeddings_dir, embeddings, allow_dangerous_deserialization=True)
    print(f"Successfully loaded embeddings from {embeddings_dir}")
except FileNotFoundError:
    raise FileNotFoundError(
        f"Embeddings directory {embeddings_dir} not found. "
        "Please run data_processing.py first."
    )

# search chema

# The Search class provides a type-safe way to create search parameters 
# that match these sections, enabling filtered searches like:
# search = Search(query="ASUS laptop", section="beginning") 
# -> this would only search for the ASUS laptops in the beginning section of the product catalog.

# class Search(TypedDict): 
#     query: Annotated[str, ... , "Search query to run"]
#     section: Annotated[
#         Literal["entry-level laptops", "mid-range laptops", "high-end/premium laptops", "all"], ... , 
#         "Section of the products to search"
#     ]



# retrieve function
from langchain_core.tools import tool
@tool("retrieve",response_format="content_and_artifact")
def retrieve(query:str):
    """Retrieve a product related to a query."""
    retrieved_products = vector_store.similarity_search(query, k=5)
    serialized = "\n\n".join(
        (f"Source: {product.metadata}\n" f"Content: {product.page_content}")
        for product in retrieved_products
    )
    return serialized, retrieved_products


# ------------------------- Maybe Unecessary ------------------------------------------
# @tool("retrieve_top_k_products", response_format="content_and_artifact")
# def retrieve_top_k_products(query: str, k:int):
#     """Retrieve top k products related to a query"""
#     if k > 5:
#         return f"Try the prompt again, we are not allowed to search more than 5 products"
#     else: 
#         retrieve_k_products = vector_store.similarity_search(query, k=k)
#         serialized_k_products = "\n\n".join(
#         (f"Source: {product.metadata}\n" f"Content: {product.page_content}")
#         for product in retrieve_k_products
#     )
#         return serialized_k_products, retrieve_k_products

# Compare product tool

@tool("recommend_products", response_format="content_and_artifact")
def recommend_products(query:str, budget: float, use_case: str): 
    """ Recommend a (list) product to a customer based on a query"""
    query = f"Recommend me a laptop for {use_case} under {budget}"
    retrieved_products = vector_store.similarity_search(query, k=5)
    budget_filtered = []
    
    for product in retrieved_products: 
        try:
            if 'Price' in product.metadata and product.metadata['Price']:
                price = float(product.metadata['Price'])

                
                if price <= budget:
                    budget_filtered.append(product)
        except (ValueError, IndexError) as e:
            # Skip products with parsing issues
            continue
    
    if budget_filtered: 
        serialized = "\n\n".join(
            f"Source: {product.metadata}\n" f"Content: {product.page_content}"
            for product in budget_filtered
        )
        return serialized, budget_filtered
    else:
        # If no products match budget, return original results with warning
        serialized = "No products found within your budget. Here are some alternatives:\n\n" + "\n\n".join(
            f"Source: {product.metadata}\n" 
            f"Content: {product.page_content}"
            for product in retrieved_products
        )
        return serialized, retrieved_products

@tool("compare_products", response_format="content_and_artifact")
def compare_products(product1: str, product2: str,query: str): 
    """Compare products related to a query"""
    product1_specs = vector_store.similarity_search(product1, k=1)
    product2_specs = vector_store.similarity_search(product2, k=1)
    if product1_specs and product2_specs: 
        p1_content = product1_specs[0].page_content
        p2_content = product2_specs[0].page_content
        comparision = { 
            f" Comparision between {product1} and {product2} based on {query}: \n\n"
             f"Product : {p1_content} \n\n"
            f"Product 2": {p2_content}
        }
        return comparision, [product1_specs[0], product2_specs[0]]
    else: 
        return f"Cound not find detailed specificaiton about one or another."


@tool("explain_specs", response_format="content_and_artifact")
def explain_specs(spec_query: str):
    """
    Explain technical specifications in simple terms refer to the product that a customer asks.
    
    """
    explanation = { 
        "cpu": "The CPU is the brain of the computer. Higher numbers generally mean better performance",
        "ram": "RAM is computer's short term memory, 8GB is good, 16GB is recommended to most users, and 32GB is for demanding tasks like gaming or video editing",
        "ssd": "SSDs store your files and program. They're are faster than normal HHD",
        "hhd": "HHDS also store your files and program but it is slower than SSDs.",
        "gpu": "The GPU handles graphic processing. Integrated graphics are OK for basic tasks like office tasks, but for tasks like training AI Models or gaming may require dedicated GPUS.",
        "display": "Display quality affects what you see. FHD is standard resolution, IPS panels generally have better colors than the standard displays."
    }
    # check common terms that might be in the query
    spec_query_lower = spec_query.lower()
    
    if "processor" in spec_query_lower or "cpu" in spec_query_lower: 
        spec_type = "processor"
        return explanation["cpu"], []
    elif "ram" in spec_query_lower or "memory" in spec_query_lower: 
        spec_type = "ram"
        return explanation["ram"], []
    elif "ssd" in spec_query_lower or "solid state drive" in spec_query_lower:
        spec_type = "ssd"
        return explanation["ssd"], []
    elif "hhd" in spec_query_lower or "hard drive": 
        spec_type = "hhd"
        return explanation["hhd"], []
    elif "gpu" in spec_query_lower or "graphic card" in spec_query_lower: 
        spec_type = "gpu"
        return explanation["gpu"], []
    elif "display" in spec_query_lower:
        spec_type = "display"
        return explanation["display"], []
    
    value_terms = {
        "cpu": ["ryzen", "intel", "core i7", "core i5", "core i3", "amd"],
        "ram": ["8gb", "16gb", "32gb", "ddr4", "ddr5"],
        "ssd": ["256gb", "512gb", "1tb", "nvme"],
        "hdd": ["1tb", "2tb"],
        "gpu": ["rtx", "gtx", "radeon", "nvidia", "integrated"],
        "display": ["fhd", "uhd", "4k", "ips", "oled"]
    }
    specific_value = None
    if spec_type in value_terms: 
        for term in value_terms[spec_type]: 
            if term in spec_query_lower: 
                specific_value = term

    if specific_value: 
        search_term = f"{specific_value} {search_term}"
        relevant_products = vector_store.similarity_search(search_term, k=2)
        return relevant_products

@tool("get_detailed_features", response_format="content_and_artifact")
def get_detailed_features(product_name: str):
    """Get detailed features for a specific product."""
    query = product_name if product_name else "laptop features"
    filter_dict = {"chunk_type": "Detailed Features"}
    
    retrieved_chunks = vector_store.similarity_search(
        query, 
        k=5,
        filter=filter_dict
    )
    
    serialized = "\n\n".join(
        f"Source: {chunk.metadata}\n" 
        f"Features: {chunk.page_content}"
        for chunk in retrieved_chunks
    )
    return serialized, retrieved_chunks

# Genearte AI Message that may include a tool-call to be sent

def query_or_respond(state: MessagesState):
    """Generate tool call for retrieval or respond."""
    llm_with_tools = llm.bind_tools([retrieve, compare_products, explain_specs, recommend_products, get_detailed_features])
    response = llm_with_tools.invoke(state["messages"])
    # MessagesState appends messages to state instead of overwriting
    return {"messages": [response]}

# Execute the tools
from langgraph.prebuilt import ToolNode
tools = ToolNode([compare_products, retrieve, explain_specs, recommend_products, get_detailed_features])



# generate reponse using tool
def generate(state: MessagesState):
    """Generate answer."""
    # Get generated ToolMessages
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]

    # Format into prompt
    docs_content = "\n\n".join(doc.content for doc in tool_messages)
    system_message_content = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        f"{docs_content}"
    )
    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
        or (message.type == "ai" and not message.tool_calls)
    ]
    prompt = [SystemMessage(system_message_content)] + conversation_messages

    # Run
    response = llm.invoke(prompt)
    return {"messages": [response]}



# image_data = graph.get_graph().draw_mermaid_png(output_file_path="graphs/rag_graph.png") 
# """this does not work""

# control flow using graph object
# connecting retrieval and generation steps

def build_langgraph(): 
    graph_builder = StateGraph(state_schema=MessagesState)


    graph_builder.add_node(query_or_respond)
    graph_builder.add_node(tools)
    graph_builder.add_node(generate)

    graph_builder.set_entry_point("query_or_respond")
    graph_builder.add_conditional_edges(
        "query_or_respond",
        tools_condition,
        {END: END, "tools": "tools"},
    )
    graph_builder.add_edge("tools", "generate")
    graph_builder.add_edge("generate", END)

    graph = graph_builder.compile()

    from langgraph.checkpoint.memory import MemorySaver
    checkpoint = MemorySaver()
    graph = graph_builder.compile(checkpointer=checkpoint)
    return graph

if __name__ == "__main__": 
        
    
    graph = build_langgraph()
    import uuid
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower().strip() == "exit":
            print("Exiting conversation. Goodbye!")
            break
        
        # Process the user input through the graph
        for step in graph.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            stream_mode="values",
            config=config
        ):
            print("\nAssistant:", end=" ")
            step["messages"][-1].pretty_print()


    # Pipeline Graph
    # mermaid_markdown = graph.get_graph().draw_mermaid()
    # with open("graphs/rag_graph2.mmd", "w") as f:
    #     f.write(mermaid_markdown)
        
    # input_message = "Compare between Acer NZ Remanufactured NX.VR3SA.005 Flip 2in1 Edu Laptop 11.6"" FHD Touch and Lenovo 500e Yoga G4 12.2"" WUXGA Touch Chromebook?"

    # for step in graph.stream(
    #     {"messages": [{"role": "user", "content": input_message}]},
    #     stream_mode="values",
    #     config=config
    # ):
    #     step["messages"][-1].pretty_print()

    # for step in graph.stream(
    #     {"messages": [{"role": "user", "content": input_message}]},
    #     stream_mode="values",
    # ):
    #     step["messages"][-1].pretty_print()




    # # # test run
    # user_question = input("Enter your question: ")
    # result = graph.invoke(
    #     {"messages": [HumanMessage(content=user_question)]}
    # )

    # # Print results
    # print("Question:", user_question)
    # print("Answer:", result["messages"][-1].content)

