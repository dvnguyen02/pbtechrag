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
vector_store = None

def load_vector_store():
    """Load the vector store from disk"""
    global vector_store
    if vector_store is None:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        if os.path.exists(embeddings_dir):
            print(f"Loading embeddings from {embeddings_dir}")
            vector_store = FAISS.load_local(embeddings_dir, embeddings)
        else:
            raise FileNotFoundError(
                f"Embeddings directory {embeddings_dir} not found. "
                
            )
    return vector_store

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
    vector_store = load_vector_store()
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

@tool("compare_products", response_format="content_and_artifact")
def compare_products(product1: str, product2: str,query: str): 
    """Compare products related to a query"""
    vector_store = load_vector_store()
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

# Genearte AI Message that may include a tool-call to be sent

def query_or_respond(state: MessagesState):
    """Generate tool call for retrieval or respond."""
    llm_with_tools = llm.bind_tools([retrieve, compare_products])
    response = llm_with_tools.invoke(state["messages"])
    # MessagesState appends messages to state instead of overwriting
    return {"messages": [response]}

# Execute the tools
from langgraph.prebuilt import ToolNode
tools = ToolNode([compare_products, retrieve])



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

# Specify ID
config = {"configurable": {"thread_id": "test17"}}  # Example ID


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

input_message2 = "What are the prices of Lenovo IdeaPad 1 15AMN7 15.6"" FHD Laptop, HP 15-fc0432AU 15.6"" FHD, Dell Inspiron 3000 series 3520 15.6"" FHD, ASUS Vivobook Go E1504FA 15.6"" FHD, HP 15-fc0430AU 15.6"" FHD"
for step in graph.stream(
    {"messages": [{"role": "user", "content": input_message2}]},
    stream_mode="values",
    config=config
):
    step["messages"][-1].pretty_print()

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

