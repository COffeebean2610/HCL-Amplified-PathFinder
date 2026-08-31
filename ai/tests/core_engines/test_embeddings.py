import os
import json
import numpy as np
import pytest

from src.embeddings.embedder import RouteMasterEmbedder
from src.embeddings.pipeline import EmbeddingPipeline

@pytest.fixture(scope="module")
def embedder():
    """Cache embedder instance for testing."""
    return RouteMasterEmbedder(model_name="BAAI/bge-small-en-v1.5")

def test_embedder_initialization(embedder):
    assert embedder.model is not None
    assert embedder.dimension == 384
    assert embedder.device in ["cuda", "cpu"]

def test_embedder_encoding(embedder):
    text = "Machine learning models and deep neural networks."
    vec = embedder.encode(text)
    
    assert isinstance(vec, np.ndarray)
    assert vec.shape == (1, 384)
    # Check normalization: dot product with itself should be approx 1.0
    self_similarity = embedder.similarity(vec, vec)
    assert pytest.approx(self_similarity, abs=1e-4) == 1.0

def test_semantic_similarity_rankings(embedder):
    # Proves semantic representation draws correct relative alignments
    anchor = embedder.encode("Python programming language syntax and scripts")
    close_match = embedder.encode("C++ software coding structure and functions")
    distant_match = embedder.encode("Corporate balance sheet audits and double-entry bookkeeping")
    
    sim_close = embedder.similarity(anchor, close_match)
    sim_distant = embedder.similarity(anchor, distant_match)
    
    print(f"DEBUG: sim_close={sim_close}, sim_distant={sim_distant}")
    assert sim_close > sim_distant, \
        f"Semantic ranking error: Close match ({sim_close}) should be greater than distant match ({sim_distant})"

def test_pipeline_persistence_loading():
    # If the pipeline has run and files are persisted, verify their structure
    embeddings_dir = "model/embeddings"
    
    for entity in ["skills", "careers", "courses", "projects"]:
        npy_path = os.path.join(embeddings_dir, f"{entity}_embeddings.npy")
        json_path = os.path.join(embeddings_dir, f"{entity}_ids.json")
        
        # If files exist (which they will after running pipeline), check them
        if os.path.exists(npy_path) and os.path.exists(json_path):
            # Load npy
            mat = np.load(npy_path)
            assert mat.ndim == 2
            assert mat.shape[1] == 384
            
            # Load JSON map
            with open(json_path, "r", encoding="utf-8") as f:
                id_map = json.load(f)
                
            assert isinstance(id_map, dict)
            assert len(id_map) == mat.shape[0]
            # Verify each index is within bound
            for item_id, index in id_map.items():
                assert 0 <= index < mat.shape[0]
