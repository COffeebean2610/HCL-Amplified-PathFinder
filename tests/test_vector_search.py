import os
import json
import pytest
from unittest.mock import MagicMock, patch

from src.vector_search.searcher import RouteMasterVectorSearch
from src.vector_search.database import seed_collections

@pytest.fixture(scope="module")
def searcher():
    """Cache vector searcher instance (ensures offline mode is default)."""
    # Force connection client to None by removing MONGO_URI from env
    with patch.dict(os.environ, {"MONGO_URI": ""}):
        return RouteMasterVectorSearch()

def test_local_search_fallback_courses(searcher):
    # Ensure offline mode is active
    assert searcher.client is None
    
    # Query related to React/web development
    results = searcher.search("courses", "React web development and frontend interface", top_k=3)
    
    assert len(results) == 3
    # Check output contract structure
    for r in results:
        assert "entity_id" in r
        assert "metadata" in r
        assert "similarity_score" in r
        assert isinstance(r["similarity_score"], float)
        assert 0.0 <= r["similarity_score"] <= 1.0
        
    # Top results should match frontend/React/web
    top_titles = [r["metadata"]["course_name"].lower() for r in results]
    assert any("react" in t or "web" in t or "frontend" in t or "developer" in t for t in top_titles)

def test_local_search_fallback_careers(searcher):
    # Query related to artificial intelligence
    results = searcher.search("careers", "Deep learning models, natural language processing and neural networks", top_k=3)
    
    assert len(results) == 3
    top_titles = [r["metadata"]["career_title"].lower() for r in results]
    assert any("ai" in t or "machine learning" in t or "engineer" in t for t in top_titles)

def test_mongodb_query_pipeline_construction():
    """
    Mocks a MongoDB connection client and aggregate call to verify
    that the pipeline contains the standard $vectorSearch aggregations.
    """
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_col = MagicMock()
    
    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_col
    
    # Return mock results for collection aggregate
    mock_col.aggregate.return_value = [
        {"_id": "CRS_001", "course_name": "Mock Course", "score": 0.95}
    ]
    
    with patch("src.vector_search.searcher.get_mongodb_client", return_value=mock_client):
        vs = RouteMasterVectorSearch()
        assert vs.client is mock_client
        
        results = vs.search("courses", "React test query", top_k=5)
        
        assert len(results) == 1
        assert results[0]["entity_id"] == "CRS_001"
        assert results[0]["similarity_score"] == 0.95
        
        # Verify aggregate call pipeline layout
        mock_col.aggregate.assert_called_once()
        pipeline = mock_col.aggregate.call_args[0][0]
        
        assert "$vectorSearch" in pipeline[0]
        v_search_params = pipeline[0]["$vectorSearch"]
        assert v_search_params["index"] == "vector_index"
        assert v_search_params["path"] == "embedding"
        assert len(v_search_params["queryVector"]) == 384  # bge-small output dimension
        assert v_search_params["limit"] == 5

def test_seeder_dry_run():
    # Execute seeder in dry_run mode (which doesn't require a MongoClient connection)
    stats = seed_collections(
        client=None,
        db_name="routemaster",
        processed_dir="data/processed",
        embeddings_dir="model/embeddings",
        dry_run=True
    )
    
    assert "skills" in stats
    assert "careers" in stats
    assert "courses" in stats
    assert "projects" in stats
    
    assert stats["skills"] == 8908
    assert stats["careers"] == 122
    assert stats["courses"] == 3416
    assert stats["projects"] == 251
