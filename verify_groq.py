import os
import sys

try:
    from langchain_groq import ChatGroq
    print("Successfully imported ChatGroq")
    
    # Mock instantiation
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key="mock_key",
        temperature=0
    )
    print("Successfully instantiated ChatGroq")
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
