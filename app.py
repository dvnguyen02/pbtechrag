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
from langgraph.graph import START, END, StateGraph, MessagesState
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, FunctionMessage
# environment setup
load_dotenv()
os.environ["LANGSMITH_TRACING"] = "true"

# init components
llm = ChatOpenAI(model = "gpt-4o")
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


# retrieve function
from langchain_core.tools import tool

@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Retrieve information related to a query."""
    retrieved_products = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {product.metadata}\n" f"Content: {product.page_content}")
        for product in retrieved_products
    )
    return serialized, retrieved_products

# Step 1: Genearte AI Message that may include a tool-call to be sent

def query_or_respond(state: MessagesState):
    """Generate tool call for retrieval or respond."""
    llm_with_tools = llm.bind_tools([retrieve])
    response = llm_with_tools.invoke(state["messages"])
    # MessagesState appends messages to state instead of overwriting
    return {"messages": [response]}

# Step 2: Execute the Retrieval
from langgraph.prebuilt import ToolNode
tools = ToolNode([retrieve])



# Step 3: Generate reponse using retrieved product
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

from langgraph.graph import END
from langgraph.prebuilt import ToolNode, tools_condition

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
config = {"configurable": {"thread_id": "test10"}}  # Example ID

#mermaid_markdown = graph.get_graph().draw_mermaid()


# with open("graphs/rag_graph.mmd", "w") as f:
#     f.write(mermaid_markdown)
input_message = "Could you recommend me a laptop that is cheapest?"

for step in graph.stream(
    {"messages": [{"role": "user", "content": input_message}]},
    stream_mode="values",
    config=config
):
    step["messages"][-1].pretty_print()

input_message2 = "What was its specification again?"

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

