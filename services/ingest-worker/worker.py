#!/usr/bin/env python3
"""
Document ingestion worker for the Telegram coaching bot.
Scans a directory for documents, processes them, and adds to vector store.
"""

import os
import glob
import uuid
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Any
import requests
from unstructured.partition.auto import partition
import chromadb

class IngestWorker:
    def __init__(self):
        self.corpus_dir = os.getenv("CORPUS_DIR", "./corpus")
        self.chroma_host = os.getenv("CHROMA_HOST", "localhost")
        self.chroma_port = int(os.getenv("CHROMA_PORT", "8000"))
        self.retrieval_url = os.getenv("RETRIEVAL_URL", "http://localhost:8080")
        
        # Initialize ChromaDB client
        self.client = chromadb.Client(
            host=self.chroma_host,
            port=self.chroma_port
        )
        self.collection = self.client.get_or_create_collection("docs")
        
        # Track processed files
        self.processed_files = set()
        self.load_processed_files()

    def load_processed_files(self):
        """Load list of already processed files"""
        try:
            # In a real implementation, you'd store this in a database
            # For now, we'll use a simple file
            if os.path.exists("processed_files.txt"):
                with open("processed_files.txt", "r") as f:
                    self.processed_files = set(f.read().splitlines())
        except Exception as e:
            print(f"Error loading processed files: {e}")

    def save_processed_files(self):
        """Save list of processed files"""
        try:
            with open("processed_files.txt", "w") as f:
                for file_path in self.processed_files:
                    f.write(f"{file_path}\n")
        except Exception as e:
            print(f"Error saving processed files: {e}")

    def get_file_hash(self, file_path: str) -> str:
        """Get SHA256 hash of file"""
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

    def process_document(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a single document and return chunks"""
        try:
            print(f"Processing: {file_path}")
            
            # Use unstructured to partition the document
            elements = partition(filename=file_path)
            
            chunks = []
            for i, element in enumerate(elements):
                if hasattr(element, 'text') and element.text.strip():
                    chunk = {
                        'text': element.text.strip(),
                        'source': file_path,
                        'chunk_id': f"{file_path}_{i}",
                        'timestamp': time.time()
                    }
                    chunks.append(chunk)
            
            print(f"Extracted {len(chunks)} chunks from {file_path}")
            return chunks
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return []

    def add_chunks_to_store(self, chunks: List[Dict[str, Any]]):
        """Add chunks to the vector store via retrieval service"""
        try:
            for chunk in chunks:
                response = requests.post(
                    f"{self.retrieval_url}/add",
                    json={
                        "texts": [chunk['text']],
                        "metadata": [{
                            "source": chunk['source'],
                            "chunk_id": chunk['chunk_id'],
                            "timestamp": chunk['timestamp']
                        }]
                    }
                )
                response.raise_for_status()
                
        except Exception as e:
            print(f"Error adding chunks to store: {e}")

    def scan_and_process(self):
        """Scan corpus directory and process new files"""
        print(f"Scanning directory: {self.corpus_dir}")
        
        # Supported file extensions
        extensions = ['*.pdf', '*.docx', '*.txt', '*.md', '*.html', '*.pptx']
        
        for ext in extensions:
            pattern = os.path.join(self.corpus_dir, ext)
            files = glob.glob(pattern)
            
            for file_path in files:
                file_hash = self.get_file_hash(file_path)
                file_key = f"{file_path}:{file_hash}"
                
                if file_key not in self.processed_files:
                    print(f"Found new file: {file_path}")
                    
                    chunks = self.process_document(file_path)
                    if chunks:
                        self.add_chunks_to_store(chunks)
                        self.processed_files.add(file_key)
                        print(f"Successfully processed: {file_path}")
                else:
                    print(f"Already processed: {file_path}")
        
        self.save_processed_files()
        print(f"Scan complete. Total processed files: {len(self.processed_files)}")

    def run_once(self):
        """Run ingestion once"""
        self.scan_and_process()

    def run_continuous(self, interval: int = 300):
        """Run ingestion continuously with given interval (seconds)"""
        print(f"Starting continuous ingestion with {interval}s interval")
        
        while True:
            try:
                self.run_once()
                print(f"Sleeping for {interval} seconds...")
                time.sleep(interval)
            except KeyboardInterrupt:
                print("Stopping ingestion worker...")
                break
            except Exception as e:
                print(f"Error in continuous run: {e}")
                time.sleep(60)  # Wait before retrying

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Document ingestion worker")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--interval", type=int, default=300, help="Interval in seconds for continuous mode")
    
    args = parser.parse_args()
    
    worker = IngestWorker()
    
    if args.once:
        worker.run_once()
    else:
        worker.run_continuous(args.interval)

if __name__ == "__main__":
    main() 