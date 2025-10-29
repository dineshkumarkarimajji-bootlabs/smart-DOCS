from langchain_ollama.llms import OllamaLLM

# create a client instance
client = OllamaLLM(model="llama2")

def ask_llm(query: str, context: list[str]) -> str:
    # Combine only the first few chunks of context
    context_text = "\n\n".join(context[:5])

    prompt = f"""
    You are an AI assistant tasked with extracting information from documents.  
    Your goal is to answer the question using **only the information in the provided context**.  
    Do not hallucinate or add any information beyond what is in the context.  
    Return the answer in **clear sentence format**.  
    If the context does not contain information to answer a part of the question, say it is unknown.  

    Context:
    {context_text}

    Question:
    {query}

    Answer in sentences:
    """

    try:
        # Generate response using the client
        response = client.generate([prompt])
        return response.generations[0][0].text.strip()
    except Exception as e:
        return f"Error: {e}"