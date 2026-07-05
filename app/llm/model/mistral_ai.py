from langchain_mistralai import ChatMistralAI

def get_llm():
    llm = ChatMistralAI(
        model_name="devstral-small-latest",
        temperature=0,
        timeout=120,    
        max_retries=3   
    )
    return llm