# qian_rag_chatbot

This project essentially serves as sample code on using RAG to build GenAI chatbot. Advantages are:
* Best balance between accomodating GenAI with specified knowledge and minimizing additional effort (such as post-training)
* Proven technology demoing the power of GenAI

Things that can be improven:
* Agentic AI for better information retrieval, for instance, running SQL to get better result
* Model improvement, especially embedding model and chunking schema.
* Combination with Knowledge (GraphDB) and RLHF

Components of the system:
* Chainlit: a beautiful chatbot framework dealing with all chat part, such as UI, message management, etc
* LangChain: a popular GenAI framework orchestrating all calls
* Ollama: easy to run GenAI locally for testing
* ChromaDB: light-weight local VectorDB

Formal unit tests are ignored for the sake of time, which is not difficult to do:
* Test cases
  * add common questions
  * add "edge-case" questions
* Convert responses into embeddings
* Compute the cosine similarity between correct answers and embeddings from responses. Ideally, it should be 1.0
  * If it is within the error tolerance (say >0.9), it passes
  * Otherwise, throw error.

Depolyment on Mac:
* Ollama (Hosting LLM locally)
  1. brew install ollama (install Ollama framework)
  2. brew services start ollama (start Ollama)
  3. ollama pull deepseek-r1 (install LLM model - DeepSeek in this case)
  4. ollama pull nomic-embed-text (install embedding model)
* LangChain on Ollma:
  * Start a virtual enviornment (it can be further wrapped with Docker, then K8s for scalability)
  * pip3 install langchain, langchain-ollama (this can be further made into requirements.txt)
* Chainlit
  * pip install chainlit 
