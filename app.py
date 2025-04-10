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

def analyze_query(state: MessagesState):
    # Extract the question from the last human message
    messages = state["messages"]
    last_human_message = next((m for m in reversed(messages) if m.type == "human"), None)
    
    if not last_human_message:
        return {"messages": [AIMessage(content="I couldn't find a question to answer.")]}
    
    question = last_human_message.content
    
    response = llm.invoke(
        f"Analyze the question: {question}. "
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
            "query": question,
            "section": "all"
        }
    
    # Add a system message containing the query information
    return {"messages": [SystemMessage(content=json.dumps(query_data))]}

# retrieve using semantic search 
def retrieve(state: MessagesState):
    messages = state["messages"]
    
    # Get the query data from the last system message
    query_message = next((m for m in reversed(messages) if m.type == "system"), None)
    last_human_message = next((m for m in reversed(messages) if m.type == "human"), None)
    
    if not query_message or not last_human_message:
        return {"messages": [AIMessage(content="Missing query information.")]}
    
    try:
        query = json.loads(query_message.content)
        question = last_human_message.content
        
        if query["section"] != "all":
            def metadata_filter(doc: Document) -> bool:
                return doc.metadata.get("section") == query["section"]
                
            retrieved_products = vector_store.similarity_search(
                query["query"],
                k=3,
                filter=metadata_filter  
            )
        else:
            retrieved_products = vector_store.similarity_search(query["query"], k=3)
        
        # Create a context message with the retrieved products
        context_content = "\n\n".join([doc.page_content for doc in retrieved_products])
        
        # Store the retrieved context as a FunctionMessage
        return {"messages": [FunctionMessage(name="retrieve", content=context_content)]}
    
    except Exception as e:
        return {"messages": [AIMessage(content=f"Error retrieving information: {str(e)}")]}


def generation(state: MessagesState):
    messages = state["messages"]
    
    # Get the context from the last function message
    context_message = next((m for m in reversed(messages) if m.type == "function" and m.name == "retrieve"), None)
    last_human_message = next((m for m in reversed(messages) if m.type == "human"), None)
    
    if not context_message or not last_human_message:
        return {"messages": [AIMessage(content="Missing context or question.")]}
    
    context = context_message.content
    question = last_human_message.content
    
    prompt_messages = prompt.invoke(
        {"context": context, "question": question}
    )
    
    response = llm.invoke(prompt_messages)
    
    # Return the AI's response as an AIMessage
    return {"messages": [response]}


# image_data = graph.get_graph().draw_mermaid_png(output_file_path="graphs/rag_graph.png") 
# """this does not work""

# control flow using graph object
# connecting retrieval and generation steps
from langgraph.graph import START, StateGraph

graph_builder = StateGraph(state_schema=MessagesState)
graph_builder.add_node("analyze_query", analyze_query)
graph_builder.add_node("retrieve", retrieve)
graph_builder.add_node("generation", generation)

# connect nodes in sq
graph_builder.add_edge(START, "analyze_query")
graph_builder.add_edge("analyze_query", "retrieve")
graph_builder.add_edge("retrieve", "generation")
graph_builder.add_edge("generation", END)


graph = graph_builder.compile()


#mermaid_markdown = graph.get_graph().draw_mermaid()


# with open("graphs/rag_graph.mmd", "w") as f:
#     f.write(mermaid_markdown)
input_message = "Could you recommend me some good gaming laptops?"

for step in graph.stream(
    {"messages": [{"role": "user", "content": input_message}]},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()


# # # test run
# user_question = input("Enter your question: ")
# result = graph.invoke(
#     {"messages": [HumanMessage(content=user_question)]}
# )

# # Print results
# print("Question:", user_question)
# print("Answer:", result["messages"][-1].content)

