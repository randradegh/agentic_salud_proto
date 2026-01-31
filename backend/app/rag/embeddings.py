"""Utilidades para embeddings."""
from typing import List
from sentence_transformers import SentenceTransformer
from app.config import settings


class EmbeddingModel:
    """Modelo para generar embeddings."""
    
    def __init__(self):
        self.model_name = settings.embedding_model
        self._model: SentenceTransformer | None = None
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy loading del modelo."""
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model
    
    def encode(self, texts: List[str]) -> List[List[float]]:
        """Genera embeddings para una lista de textos."""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def encode_single(self, text: str) -> List[float]:
        """Genera embedding para un solo texto."""
        embedding = self.model.encode([text], convert_to_numpy=True)
        return embedding[0].tolist()


embedding_model = EmbeddingModel()
