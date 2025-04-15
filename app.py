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
import pandas as pd
from data_loader import load_product_data
# environment setup
load_dotenv()
df = load_product_data()
os.environ["LANGSMITH_TRACING"] = "true"

# init components
llm = ChatOpenAI(model = "gpt-4.1")
# prompt = hub.pull("rlm/rag-prompt") Not needed
 

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
@tool("retrieve",response_format="content_and_artifact")
def retrieve(query:str):
    """Retrieve a product related to a query."""
    retrieved_products = vector_store.similarity_search(query, k=2)
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
    retrieved_products = vector_store.similarity_search(query, k=2)
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
        serialized = "No products found within the budget. Here are some alternatives that are close:\n\n" + "\n\n".join(
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

@tool("get_products_total", response_format="content_and_artifact")
def get_products_total(): 
    """Get total number of products in the database"""
    try: 
        total_products = len(df)
        response = f"There are {total_products} laptops in stock."
        return response, []
    except Exception as e:
        return f"Error retrieving total amount of laptops", []
    
@tool("get_newest_product", response_format="content_and_artifact")
def get_newest_product():
    """Get the newest product in the database"""
    try: 
        latest_index = len(df)-1 # The last product in the database
        product_row = df.loc[latest_index]
        product_name = product_row.get('Product Name', 'Unknown Product')
        product_price = product_row.get('Price', 'Unknown Price')
        response = f"The newest product we have is {product_name} with the price of {product_price}"
        return response, [product_row]
    except Exception as e: 
        return f"Could not retrieve the product", []
    
@tool("filter_by_price_range", response_format="content_and_artifact")
def filter_by_price_range(query: str, min_price: float, max_price: float): 
    """Filter products by price range"""
    filtered_df = df[(df['Price'] >= min_price) & (df['Price'] <= max_price)]
    # Get top 5 products
    top_results = filtered_df.head(5)
    product_list = []
    for _, row in top_results.iterrows(): 
        product = {
            'Product Name': row.get('Product Name', 'Unknown Product'),
            'Price': row.get('Price', 'NA Price'),
            'Detailed Specs': row.get('Detailed Specs', 'NA Specs')
        }
        product_list.append(product)
    response = f"Found {len(filtered_df)} products between ${min_price} and ${max_price}. Here are the top matches:\n\n"
    response += "\n\n".join([f"- {p['Product Name']} ({p['Price']})" for p in product_list])

    return response, product_list

@tool("get_detailed_specs", response_format="content_and_artifact")
def get_detailed_specs(product_name: str):
    """Get detailed features for a specific product."""
    # Create a more targeted query to find detailed specifications
    if not product_name or product_name.strip() == "":
        return "Please provide a valid product name.", []
    
    # Create a query that specifically looks for specifications
    query = f"{product_name} technical specifications details features"
    
    try:
        # Retrieve relevant chunks without filtering by metadata
        retrieved_chunks = vector_store.similarity_search(
            query,
            k=2
        )
        
        if not retrieved_chunks:
            return f"No specifications found for {product_name}.", []
        
        # Format the results with clear section headers
        serialized = "\n\n".join(
            f"PRODUCT INFO: {chunk.metadata.get('product_name', product_name)}\n" 
            f"SOURCE: {chunk.metadata.get('source', 'Unknown')}\n"
            f"SPECIFICATIONS:\n{chunk.page_content}"
            for chunk in retrieved_chunks
        )
        
        return serialized, retrieved_chunks
        
    except Exception as e:
        error_msg = f"Error retrieving specifications: {str(e)}"
        return error_msg, []

@tool("get_most_expensive_product", response_format="content_and_artifact")
def get_most_expensive_product(query: str):
    """Get most expensive product"""
    max_price_idx = df['Price'].idxmax()
    product_row = df.loc[max_price_idx]
    product_name = product_row.get('Product Name', 'Unknown Product')
    price = product_row['Price']
    response = f"The most expensive product is {product_name}, and it costs {price}"
    return response, [product_row.to_dict()]

# Genearte AI Message that may include a tool-call to be sent

def query_or_respond(state: MessagesState):
    """Generate tool call for retrieval or respond."""
    llm_with_tools = llm.bind_tools([get_most_expensive_product, 
                                     get_newest_product,
                                     retrieve, 
                                     compare_products, 
                                     recommend_products, 
                                     get_detailed_specs, 
                                     get_products_total,
                                     filter_by_price_range])
    response = llm_with_tools.invoke(state["messages"])
    # MessagesState appends messages to state instead of overwriting
    return {"messages": [response]}

# Execute the tools
from langgraph.prebuilt import ToolNode
tools = ToolNode([get_most_expensive_product, 
                  get_newest_product,
                  compare_products, 
                  retrieve, 
                  recommend_products, 
                  get_detailed_specs, 
                  get_products_total,
                  filter_by_price_range])



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
    "You can not give any information of if you are/work for openAI."
    "You are a PBTech worker."
    "You are a helpful and knowledgeable assistant for PBTech, an electronics retailer. "
    "Your job is to answer customer queries using information retrieved from PB Tech’s website, "
    "which includes product descriptions, specifications, pricing. "
    "Always respond in a clear, friendly, and professional tone.\n\n"
    "If a user asks about a specific product (e.g., 'Is the Logitech MX Master 3 good for work?'), "
    "provide a concise and informative summary using the retrieved product information.\n\n"
    "If a user wants to compare products (e.g., 'What's better, the MacBook Air or Dell XPS 13?'), "
    "outline key differences based on features, performance, and pricing.\n\n"
    "If the question can't be answered from the available data, politely explain that and suggest the user "
    "check PB Tech’s website for the most up-to-date information.\n\n"
    "Use the following context to inform your answer:\n\n"
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
# """this does not work"""

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
    mermaid_markdown = graph.get_graph().draw_mermaid()
    # with open("graphs/rag_graph3.mmd", "w") as f:
    #     f.write(mermaid_markdown)
    # Test in terminals
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

