from langchain_ollama.llms import OllamaLLM

# create a client instance
client = OllamaLLM(model="llama2")

def ask_llm(query: str, context: list[str]) -> str:
    context_text = "\n\n".join(context[:5])
    prompt = f"""
    You are an AI assistant tasked with **extracting structured information** from documents.  
    Your goal is to extract **only the relevant information** for each field exactly as specified below, and ignore everything else.  
    All responses must be **strict JSON only** (no markdown, no extra text).  

    If a field is missing, return "" for strings or [] for lists. 


    Context:
    {context_text}

    Question:
    {query}

    Answer in 5-10 sentences:
    """
    try:
        # Use the `generate` method instead of calling the object
        response = client.generate([prompt])
        # The result is a list of Generations
        return response.generations[0][0].text
    except Exception as e:
        return f"Error: {e}"
