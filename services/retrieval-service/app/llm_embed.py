import os
import requests
from typing import List

def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed texts using the LLM gateway"""
    try:
        response = requests.post(
            f"{os.getenv('LLM_GATEWAY_URL', 'http://localhost:3000')}/embed",
            json={"texts": texts},
            timeout=30
        )
        response.raise_for_status()
        return response.json()["embeddings"]
    except Exception as e:
        print(f"Error embedding texts: {e}")
        # Fallback to mock embeddings
        return [[0.1] * 1536 for _ in texts]

def get_embedding_model() -> str:
    """Get the embedding model based on provider"""
    provider = os.getenv('LLM_PROVIDER', 'openai')
    if provider == 'openai':
        return 'text-embedding-3-small'
    elif provider == 'anthropic':
        return 'text-embedding-3'
    else:
        return 'llama2'  # For Ollama 