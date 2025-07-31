from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
import chromadb
import os
import uuid

app = FastAPI(title="Retrieval Service", version="1.0.0")

# Initialize ChromaDB client
client = chromadb.Client(
    host=os.getenv('CHROMA_HOST', 'localhost'),
    port=int(os.getenv('CHROMA_PORT', '8000'))
)

# Get or create collection
collection = client.get_or_create_collection("docs")

class SearchRequest(BaseModel):
    query: str
    k: int = 5

class SearchResponse(BaseModel):
    documents: List[dict]
    metadata: List[dict]
    distances: List[List[float]]

class EmbedRequest(BaseModel):
    texts: List[str]

class EmbedResponse(BaseModel):
    embeddings: List[List[float]]

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "retrieval-service"}

@app.post("/search")
async def search(request: SearchRequest):
    """Search for relevant document chunks"""
    try:
        results = collection.query(
            query_texts=[request.query],
            n_results=request.k
        )
        
        return {
            "documents": [
                {
                    "text": doc,
                    "source": meta.get("source", "unknown"),
                    "timestamp": meta.get("timestamp", "")
                }
                for doc, meta in zip(results['documents'][0], results['metadatas'][0])
            ]
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/embed")
async def embed_texts(request: EmbedRequest):
    """Embed texts using the configured embedding model"""
    try:
        # For now, we'll use a simple approach
        # In production, you'd call the LLM gateway for embeddings
        embeddings = []
        for text in request.texts:
            # Placeholder - replace with actual embedding call
            embedding = [0.1] * 1536  # Mock embedding
            embeddings.append(embedding)
        
        return {"embeddings": embeddings}
    except Exception as e:
        return {"error": str(e)}

@app.post("/add")
async def add_documents(texts: List[str], metadata: Optional[List[dict]] = None):
    """Add documents to the vector store"""
    try:
        if metadata is None:
            metadata = [{"source": "unknown"} for _ in texts]
        
        ids = [str(uuid.uuid4()) for _ in texts]
        
        collection.add(
            documents=texts,
            metadatas=metadata,
            ids=ids
        )
        
        return {"status": "success", "added": len(texts)}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 