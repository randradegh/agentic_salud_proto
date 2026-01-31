"""Sistema RAG con ChromaDB."""
import os
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings
from app.rag.embeddings import embedding_model


class RAGRetriever:
    """Sistema de recuperación de información usando RAG."""
    
    def __init__(self):
        self.db_path = settings.chroma_db_path
        self.collection_name = settings.chroma_collection_name
        self._client: Optional[chromadb.ClientAPI] = None
        self._collection: Optional[chromadb.Collection] = None
    
    @property
    def client(self) -> chromadb.ClientAPI:
        """Lazy loading del cliente ChromaDB."""
        if self._client is None:
            os.makedirs(self.db_path, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=self.db_path,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
        return self._client
    
    @property
    def collection(self) -> chromadb.Collection:
        """Lazy loading de la colección."""
        if self._collection is None:
            try:
                self._collection = self.client.get_collection(name=self.collection_name)
            except Exception:
                # Crear colección si no existe
                self._collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
        return self._collection
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Divide texto en chunks."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk.strip())
            start = end - overlap
        
        return chunks
    
    def ingest_documents(self, documents: List[Dict[str, str]]) -> int:
        """Ingiere documentos en ChromaDB."""
        all_chunks = []
        all_metadatas = []
        all_ids = []
        
        for doc_idx, doc in enumerate(documents):
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            
            chunks = self.chunk_text(content)
            
            for chunk_idx, chunk in enumerate(chunks):
                chunk_id = f"{doc.get('id', doc_idx)}_{chunk_idx}"
                all_chunks.append(chunk)
                all_metadatas.append({
                    **metadata,
                    "chunk_index": chunk_idx,
                    "document_id": doc.get("id", str(doc_idx))
                })
                all_ids.append(chunk_id)
        
        if not all_chunks:
            return 0
        
        # Generar embeddings
        embeddings = embedding_model.encode(all_chunks)
        
        # Añadir a ChromaDB
        self.collection.add(
            ids=all_ids,
            embeddings=embeddings,
            documents=all_chunks,
            metadatas=all_metadatas
        )
        
        return len(all_chunks)
    
    def search(self, query: str, top_k: int = 3, similarity_threshold: float = 0.7) -> List[Dict]:
        """Busca información relevante."""
        if self.collection.count() == 0:
            return []
        
        # Generar embedding de la query
        query_embedding = embedding_model.encode_single(query)
        
        # Buscar en ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Formatear resultados
        formatted_results = []
        if results["documents"] and len(results["documents"][0]) > 0:
            for i, doc in enumerate(results["documents"][0]):
                distance = results["distances"][0][i] if results.get("distances") else None
                similarity = 1 - distance if distance is not None else 1.0
                
                if similarity >= similarity_threshold:
                    formatted_results.append({
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                        "similarity": similarity
                    })
        
        return formatted_results
    
    def load_documents_from_directory(self, directory: str) -> int:
        """Carga documentos desde un directorio."""
        doc_path = Path(directory)
        if not doc_path.exists():
            return 0
        
        documents = []
        
        # Buscar archivos .md
        for md_file in doc_path.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                relative_path = md_file.relative_to(doc_path)
                
                documents.append({
                    "id": str(relative_path),
                    "content": content,
                    "metadata": {
                        "source": str(relative_path),
                        "category": relative_path.parts[0] if len(relative_path.parts) > 1 else "general"
                    }
                })
            except Exception as e:
                print(f"Error leyendo {md_file}: {e}")
        
        if documents:
            return self.ingest_documents(documents)
        return 0


rag_retriever = RAGRetriever()
