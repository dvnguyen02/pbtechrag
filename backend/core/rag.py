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
from backend.core.data_loader import load_product_data
# environment setup
load_dotenv()
df = load_product_data(filepath="backend/data/pbtech_computers_laptops_2025-04-14.csv")
os.environ["LANGSMITH_TRACING"] = "true"

# init components
llm = ChatOpenAI(model = "gpt-4.1")
# prompt = hub.pull("rlm/rag-prompt") Not needed
 

# Load pre computed embeddings
embeddings_dir = "backend/embeddings"
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
    """
    Retrieve products related to a query using vector similarity search.
    
    Args:
        query (str): The search query to find relevant products.
        
    Returns:
        tuple: A tuple containing:
            - str: Formatted product information with metadata and content
            - list: List of Document objects containing the retrieved products
            
    Example:
        >>> retrieve("gaming laptop")
        ("Source: {...}\nContent: {...}", [Document1, Document2])
    """
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

# --------------------Need to work more on -------------------------
# @tool("recommend_products", response_format="content_and_artifact")
# def recommend_products(query:str, budget: float, use_case: str): 
#     """
#     Recommend products to a customer based on query, budget constraints and intended use case.
    
#     Args:
#         query (str): The search query describing desired product features
#         budget (float): Maximum price the customer is willing to pay
#         use_case (str): Description of how the customer intends to use the product
        
#     Returns:
#         tuple: A tuple containing:
#             - str: Formatted product recommendations with metadata and content
#             - list: List of Document objects containing the recommended products that fit within budget
            
#     Example:
#         >>> recommend_products("laptop", 1500.0, "video editing")
#         ("Source: {...}\nContent: {...}", [Document1, Document2])
#     """
#     query = f"Recommend me a laptop for {use_case} under {budget}"
#     retrieved_products = vector_store.similarity_search(query, k=2)
#     budget_filtered = []
    
#     for product in retrieved_products: 
#         try:
#             if 'Price' in product.metadata and product.metadata['Price']:
#                 price = float(product.metadata['Price'])

                
#                 if price <= budget:
#                     budget_filtered.append(product)
#         except (ValueError, IndexError) as e:
#             # Skip products with parsing issues
#             continue
    
#     if budget_filtered: 
#         serialized = "\n\n".join(
#             f"Source: {product.metadata}\n" f"Content: {product.page_content}"
#             for product in budget_filtered
#         )
#         return serialized, budget_filtered
#     else:
#         # If no products match budget, return original results with warning
#         serialized = "No products found within the budget. Here are some alternatives that are close:\n\n" + "\n\n".join(
#             f"Source: {product.metadata}\n" 
#             f"Content: {product.page_content}"
#             for product in retrieved_products
#         )
#         return serialized, retrieved_products

@tool("compare_products", response_format="content_and_artifact")
def compare_products(product1: str, product2: str,query: str): 
    """
    Compare two products based on their specifications and a specific comparison query.
    
    Args:
        product1 (str): Name or description of the first product to compare
        product2 (str): Name or description of the second product to compare
        query (str): The specific aspect or criteria to focus on for comparison
        
    Returns:
        tuple: A tuple containing:
            - dict: Dictionary with formatted comparison information between the two products
            - list: List containing Document objects for both products
            
    Example:
        >>> compare_products("MacBook Pro", "Dell XPS 15", "performance")
        ({"Comparison between MacBook Pro and Dell XPS 15 based on performance: ...": ...}, [Document1, Document2])
    """
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
    """
    Get the total number of laptop products available in the database.
    
    Returns:
        tuple: A tuple containing:
            - str: A response string indicating the total number of laptops in stock
            - list: An empty list (no additional data needed for this function)
            
    Example:
        >>> get_products_total()
        ("There are 152 laptops in stock.", [])
    """
    try: 
        total_products = len(df)
        response = f"There are {total_products} laptops in stock."
        return response, []
    except Exception as e:
        return f"Error retrieving total amount of laptops", []
    
@tool("get_newest_product", response_format="content_and_artifact")
def get_newest_product():
    """
    Retrieve information about the most recently added product in the database.
    
    Returns: 
        tuple: A tuple containing: 
            - str: A response with the newest product's name and price
            - list: A list containing the product data as a pandas Series
            
    Example:
        >>> get_newest_product()
        ("The newest product we have is ASUS ROG Zephyrus with the price of $2499.99", [Series(...)])
    """
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
def filter_by_price_range(min_price: float, max_price: float): 
    """
    Filter products by a specified price range and return top matches.
    
    Args:
        min_price (float): The minimum price threshold (inclusive)
        max_price (float): The maximum price threshold (inclusive)
        
    Returns: 
        tuple: A tuple containing: 
            - str: A formatted response with the count of matching products and top results
            - list: A list of dictionaries containing product details for the top matches
            
    Example:
        >>> filter_by_price_range(800.0, 1200.0)
        ("Found 15 products between $800.0 and $1200.0. Here are the top matches:\n\n- HP Pavilion (999.99)\n- Lenovo IdeaPad (849.99)\n...", [{...}, {...}, ...])
    """
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
### Need more work on this 
def get_detailed_specs(product_name: str):
    """
    Get detailed specifications for a specific product.
    
    Args:
        product_name (str): The name of the product to retrieve specifications for
        
    Returns:
        tuple: A tuple containing:
            - str: Formatted string with detailed specifications from retrieved documents
            - list: List of Document objects containing the retrieved specification data
            
    Example:
        >>> get_detailed_specs("Dell XPS 13")
        ("PRODUCT INFO: Dell XPS 13\nSOURCE: Product Database\nSPECIFICATIONS:\nProcessor: Intel Core i7-1165G7\nRAM: 16GB LPDDR4x\n...", [Document1, Document2])
    """    # Create a more targeted query to find detailed specifications
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

@tool("search_game_specs", response_format="content_and_artifact")
def search_game_specs(query:str, game:str, product:str): 
    """
    Search for game specifications and check if a product is compatible with the game.
    """
    from langchain_community.tools import BraveSearch
    import json
    
    search = BraveSearch.from_search_kwargs(search_kwargs={"count": 10})
    
    # Search for game requirements
    game_search_query = f"{game} system requirements"
    game_specs_results_str = search.run(game_search_query)
    
    # Parse the string results - you may need to adjust this based on the actual format
    # Or use search._search_fn(game_search_query) to get raw results
    
    # Get product specs from vector store
    product_specs = vector_store.similarity_search(product, k=2)
    product_details = ""
    if product_specs:
        product_details = product_specs[0].page_content
    
    response = (
        f"# Game Compatibility Info: {game} and {product}\n\n"
        f"## Game Requirements\n{game_specs_results_str}...\n\n"
        f"## Product Specifications\n{product_details}...\n\n"
        f"Based on the above information, you can determine if {product} is compatible with {game}."
    )
    
    return response, [{"game_specs": game_specs_results_str, "product_specs": product_details}]


@tool("get_price", response_format="content_and_artifact")
def get_price(product:str): 
    """Get the price of a specific product"""
    # First try exact match
    product_row = df[df["Product Name"] == product]
    
    # If no exact match, try partial match
    if product_row.empty:
        # Case-insensitive partial match
        product_row = df[df["Product Name"].str.lower().str.contains(product.lower())]
    
    if product_row.empty:
        return f"Product '{product}' not found.", []
    
    if len(product_row) > 1:
        products_info = []
        response = f"Found multiple products matching '{product}':\n\n"
        
        for idx, row in product_row.iterrows():
            product_name = row.get('Product Name', 'Unknown Product')
            product_specs = row.get('Detailed Specs', 'Unknown Specs')
            price_value = row.get('Price', 'Unknown Price')
            response += f"- {product_name}: ${price_value}, Specs: {product_specs}\n"
            products_info.append(row.to_dict())
        
        return response, products_info
    
    # Single match found
    price_value = product_row['Price'].iloc[0]
    product_name = product_row['Product Name'].iloc[0]
    response = f"The price of {product_name} is ${price_value}"
    
    # Convert DataFrame row to dictionary for serialization
    product_data = product_row.iloc[0].to_dict()
    
    return response, [product_data]

@tool("get_most_expensive_product", response_format="content_and_artifact")
def get_most_expensive_product(query: str):
    """
    Retrieve information about the most expensive product in the database.
    
    Args:
        query (str): Optional query parameter to provide context for the request
        
    Returns: 
        tuple: A tuple containing: 
            - str: A response string identifying the most expensive product and its price
            - list: A list containing a dictionary with the product's data
            
    Example:
        >>> get_most_expensive_product("gaming laptop")
        ("The most expensive product is Alienware m18 R2, and it costs $4999.99", [{"Product Name": "Alienware m18 R2", "Price": 4999.99, ...}])
    """
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
                                     get_detailed_specs, 
                                     get_products_total,
                                     filter_by_price_range,
                                     get_price,
                                     search_game_specs])
    response = llm_with_tools.invoke(state["messages"])
    # MessagesState appends messages to state instead of overwriting
    return {"messages": [response]}

# Execute the tools
from langgraph.prebuilt import ToolNode
tools = ToolNode([get_most_expensive_product, 
                  get_newest_product,
                  compare_products, 
                  retrieve, 
                  get_detailed_specs, 
                  get_products_total,
                  filter_by_price_range,
                  get_price,
                  search_game_specs])



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



# For testing purpose
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