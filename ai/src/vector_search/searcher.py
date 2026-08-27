import os
import json
import numpy as np
from typing import List, Dict, Any, Optional

from src.embeddings.embedder import RouteMasterEmbedder
from .database import get_mongodb_client
from src.path_utils import resolve_path

class RouteMasterVectorSearch:
    """
    Search orchestrator performing semantic retrieval against MongoDB Atlas Vector Search
    or falling back gracefully to local in-memory cosine similarities.
    """
    def __init__(self, processed_dir="data/processed", model_dir="model", db_name="routemaster"):
        self.processed_dir = str(resolve_path(processed_dir))
        self.model_dir = str(resolve_path(model_dir))
        self.embeddings_dir = os.path.join(self.model_dir, "embeddings")
        self.db_name = db_name
        
        # 1. Initialize embedder
        self.embedder = RouteMasterEmbedder(device="cpu")  # run search encodings on CPU
        
        # 2. Setup MongoDB connection
        self.client = get_mongodb_client()
        
        # 3. Load local fallback caches
        self._load_local_metadata()

    def _load_local_metadata(self):
        """Loads canonical databases and JSON maps to support offline fallback search."""
        self.local_metadata = {}
        self.local_embeddings = {}
        self.local_id_maps = {}
        self.local_reverse_id_maps = {}

        entities = ["skills", "careers", "courses", "projects"]
        id_keys = {
            "skills": "skill_id",
            "careers": "career_id",
            "courses": "course_id",
            "projects": "project_id"
        }

        for entity in entities:
            # Metadata JSON
            json_path = os.path.join(self.processed_dir, f"{entity}.json")
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    records = json.load(f)
                id_field = id_keys[entity]
                self.local_metadata[entity] = {r[id_field]: r for r in records}
            
            # Embeddings NPY
            npy_path = os.path.join(self.embeddings_dir, f"{entity}_embeddings.npy")
            ids_path = os.path.join(self.embeddings_dir, f"{entity}_ids.json")
            
            if os.path.exists(npy_path) and os.path.exists(ids_path):
                self.local_embeddings[entity] = np.load(npy_path)
                with open(ids_path, "r", encoding="utf-8") as f:
                    id_map = json.load(f)
                self.local_id_maps[entity] = id_map
                
                # Reverse mapping
                rev_map = [None] * len(id_map)
                for item_id, index in id_map.items():
                    if index < len(rev_map):
                        rev_map[index] = item_id
                self.local_reverse_id_maps[entity] = rev_map

    def search(self, entity_type: str, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Executes semantic retrieval.
        Returns:
            List of dictionaries matching:
            {
                "entity_id": str,
                "metadata": dict,
                "similarity_score": float
            }
        """
        valid_entities = ["skills", "careers", "courses", "projects"]
        if entity_type not in valid_entities:
            raise ValueError(f"Invalid entity type '{entity_type}'. Must be one of {valid_entities}.")
            
        if not query_text or not query_text.strip():
            return []

        # Step 1: Query embedding generation (normalized unit vector)
        q_vec = self.embedder.encode(query_text)[0]

        # Step 2: Database vs local fallback branch
        if self.client:
            return self._search_mongodb(entity_type, q_vec, top_k)
        else:
            return self._search_local(entity_type, q_vec, top_k)

    def _search_mongodb(self, entity_type: str, q_vec: np.ndarray, top_k: int) -> List[Dict[str, Any]]:
        """Queries MongoDB Atlas Vector Search using the aggregate pipeline stage."""
        db = self.client[self.db_name]
        col = db[entity_type]
        
        # Build aggregation pipeline
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": q_vec.tolist(),
                    "numCandidates": 100,
                    "limit": top_k
                }
            },
            {
                "$project": {
                    "embedding": 0,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]
        
        results = list(col.aggregate(pipeline))
        
        formatted_matches = []
        for doc in results:
            doc_id = doc.get("_id")
            # Clean Mongo system tags
            meta = doc.copy()
            if "_id" in meta:
                del meta["_id"]
            if "score" in meta:
                del meta["score"]
                
            formatted_matches.append({
                "entity_id": doc_id,
                "metadata": meta,
                "similarity_score": float(doc.get("score", 0.0))
            })
            
        return formatted_matches

    def _search_local(self, entity_type: str, q_vec: np.ndarray, top_k: int) -> List[Dict[str, Any]]:
        """Performs fast in-memory cosine similarity search using dot-product multiplication."""
        if entity_type not in self.local_embeddings or entity_type not in self.local_id_maps:
            print(f"WARNING: Fallback assets missing for '{entity_type}'. Returning empty.")
            return []
            
        embeddings_matrix = self.local_embeddings[entity_type]
        reverse_map = self.local_reverse_id_maps[entity_type]
        metadata_map = self.local_metadata.get(entity_type, {})

        # Compute dot products of unit normalized vectors (equal to cosine similarity)
        similarities = np.dot(embeddings_matrix, q_vec)
        
        # Get top K indices sorted descending
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        formatted_matches = []
        for idx in top_indices:
            score = float(similarities[idx])
            item_id = reverse_map[idx]
            if not item_id:
                continue
                
            rec = metadata_map.get(item_id, {}).copy()
            if "embedding" in rec:
                del rec["embedding"]
                
            formatted_matches.append({
                "entity_id": item_id,
                "metadata": rec,
                "similarity_score": score
            })
            
        return formatted_matches
