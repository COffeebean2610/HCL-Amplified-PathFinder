import torch
import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer

class RouteMasterEmbedder:
    """
    Sentence Transformer wrapper for generating semantic representations of
    skills, courses, projects, and careers.
    """
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5", device: str = None):
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        print(f"INFO: Initializing RouteMasterEmbedder with model '{model_name}' on device '{self.device}'")
        self.model = SentenceTransformer(model_name, device=self.device)
        self.dimension = self.model.get_sentence_embedding_dimension()
        
    def encode(self, texts: Union[str, List[str]], batch_size: int = 32, show_progress_bar: bool = False) -> np.ndarray:
        """
        Encodes list of text items into dense float32 vectors.
        """
        if isinstance(texts, str):
            texts = [texts]
            
        embeddings = self.model.encode(
            texts, 
            batch_size=batch_size, 
            show_progress_bar=show_progress_bar,
            convert_to_numpy=True,
            normalize_embeddings=True  # BGE embeddings perform best when normalized
        )
        return embeddings

    def similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """
        Computes cosine similarity between two vectors.
        Since embeddings are normalized, this is simply the dot product.
        """
        # Ensure dimensions match
        if vec_a.ndim == 1:
            vec_a = vec_a.reshape(1, -1)
        if vec_b.ndim == 1:
            vec_b = vec_b.reshape(1, -1)
            
        # Standard dot product of normalized vectors
        sim = np.dot(vec_a, vec_b.T)[0, 0]
        return float(sim)
