import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# =============================================================================
# Comparison 01: LangChain Implementation
# =============================================================================
#
# Task: Research -> Summarize -> Translate
# Approach: Linear Chain (LCEL)
#
# This represents the "Pipeline" mental model.
# A -> B -> C
# =============================================================================

def main():
    # 1. Setup LLM
    llm = ChatOllama(
        model="qwen3:8b",
        base_url="http://localhost:11434",
        temperature=0.7
    )

    # 2. Define Components
    
    # Step 1: Research (Mocked for consistency, or simple generation)
    # We'll ask the LLM to "generate" research to simulate a tool call or search
    research_prompt = ChatPromptTemplate.from_template(
        "Generate a brief research report about: {topic}. Include 3 key facts."
    )
    
    # Step 2: Summarize
    summarize_prompt = ChatPromptTemplate.from_template(
        "Summarize the following text into one concise sentence:\n\n{text}"
    )
    
    # Step 3: Translate
    translate_prompt = ChatPromptTemplate.from_template(
        "Translate the following sentence into Spanish:\n\n{text}"
    )

    # 3. Build the Chain (LCEL)
    # The output of one step becomes the input of the next
    
    chain = (
        {"topic": RunnablePassthrough()} 
        | research_prompt | llm | StrOutputParser() 
        | {"text": RunnablePassthrough()}
        | summarize_prompt | llm | StrOutputParser()
        | {"text": RunnablePassthrough()}
        | translate_prompt | llm | StrOutputParser()
    )

    # 4. Run
    topic = "The history of Pizza"
    print(f"\n🍝 Running LangChain Pipeline for topic: '{topic}'...\n")
    
    result = chain.invoke(topic)
    
    print("="*50)
    print("FINAL OUTPUT (Spanish Translation)")
    print("="*50)
    print(result)

if __name__ == "__main__":
    main()
