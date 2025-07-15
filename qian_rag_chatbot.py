# Ollama model 
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain_ollama import OllamaEmbeddings

# RAG related 
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

# Chatbot
import chainlit as cl

# System
import json, os, shutil

# Constants
CHROMA_PATH = "./financial_news_db"
COLLECTION_NAME = "stock_news"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:
{context}
 - -
Answer the question based on the above context: {question}
"""

EMBEDDING_MODEL = OllamaEmbeddings(model='nomic-embed-text')


@cl.on_chat_start
async def load_news():
    """
    When initiating chatbot, build the vectorDB based on news in json file.
    """

    # Remove existing DB to avoid duplication problem. Easiest way.
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Chunk text. TODO: Should add ticker, link, source, etc into metadata. 
    data = []
    with open('stock_news.json') as f:
        d = json.load(f)
        for _, value in d.items():
            for news in value:
                text = news['full_text']
                #doc = Document(page_content=text, metadata={"ticker": news['ticker'], "link": news['link']})
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                texts = text_splitter.create_documents([text])
                data = data + texts

    # Upload all chunks with embedding
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=EMBEDDING_MODEL,
        persist_directory=CHROMA_PATH,  
    )

    vector_store.add_documents(documents=data)

def query_rag(query_text):
    """
    Query a Retrieval-Augmented Generation (RAG) system using Chroma database and Ollma.
    Args:
        - query_text (str): The text to query the RAG system with.
    Returns:
        - response_text (str): The generated response text.
    """
    
    # Initiate VectorDB access
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=EMBEDDING_MODEL,
        persist_directory=CHROMA_PATH,  
    )
  
    # Retrieving the context from the DB using similarity search
    results = vector_store.similarity_search_with_score(query_text, k=3)

    # Check if there are any matching results or if the relevance score is too low
    if len(results) == 0 or results[0][1] < 0.5:
        print(f"Debug: length: {len(results)}.")
        if len(results) > 0 and results[0][1] < 0.7:
            print(f"Debug: score: {results[0][1]}.")
            print(f"Debug: content: {results[0][0]}.")
        return "Unable to find matching results."

    # Combine context from matching documents
    context_text = "\n\n - -\n\n".join([doc.page_content for doc, _score in results])
 
    # Create prompt template using context and query text
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
  
    # Initialize Ollama chat model
    model = OllamaLLM(model="deepseek-r1")

    # Generate response text based on the prompt
    response_text = model.invoke(prompt)
    return response_text

@cl.on_message
async def main(message: cl.Message):
    question = message.content

    answer = query_rag(question)

    # Send a response back to the user
    await cl.Message(
        content=f"Answer: {answer}",
    ).send()