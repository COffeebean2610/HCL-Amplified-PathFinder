import os
import json
import numpy as np
from typing import Optional

try:
    import pymongo
    from pymongo import MongoClient, ReplaceOne
except ImportError:
    pymongo = None
    MongoClient = None
    ReplaceOne = None

def get_mongodb_client(uri: Optional[str] = None) -> Optional[MongoClient]:
    """
    Initializes a PyMongo MongoClient using the provided URI or MONGO_URI env var.
    Returns None if no URI is configured or if pymongo is unavailable.
    """
    if pymongo is None:
        print("WARNING: pymongo is not installed. Database connection unavailable.")
        return None
        
    connection_uri = uri or os.environ.get("MONGO_URI")
    if not connection_uri:
        print("INFO: MONGO_URI is not set. Graceful local fallback will be used.")
        return None
        
    try:
        print(f"INFO: Connecting to MongoDB Atlas cluster...")
        # 5-second timeout to prevent blocking local startup if URI is invalid
        client = MongoClient(connection_uri, serverSelectionTimeoutMS=5000)
        # Trigger quick connection check
        client.admin.command("ping")
        print("SUCCESS: Connected to MongoDB Atlas cluster.")
        return client
    except Exception as e:
        print(f"WARNING: Failed to connect to MongoDB: {e}. Graceful local fallback active.")
        return None

def seed_collections(client: Optional[MongoClient], db_name: str, processed_dir: str, embeddings_dir: str, dry_run: bool = False) -> dict:
    """
    Seeds 'skills', 'careers', 'courses', and 'projects' collections by merging
    canonical JSON metadata records with their dense float32 Sentence Transformer embeddings.
    """
    entities = ["skills", "careers", "courses", "projects"]
    stats = {}
    
    id_keys = {
        "skills": "skill_id",
        "careers": "career_id",
        "courses": "course_id",
        "projects": "project_id"
    }

    for entity in entities:
        # Load metadata JSON
        json_path = os.path.join(processed_dir, f"{entity}.json")
        if not os.path.exists(json_path):
            print(f"WARNING: Metadata file '{json_path}' not found. Skipping {entity}.")
            continue
            
        with open(json_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        # Load NumPy embeddings
        npy_path = os.path.join(embeddings_dir, f"{entity}_embeddings.npy")
        ids_path = os.path.join(embeddings_dir, f"{entity}_ids.json")
        
        if not os.path.exists(npy_path) or not os.path.exists(ids_path):
            print(f"WARNING: Embedding assets for '{entity}' not found. Skipping {entity}.")
            continue
            
        embeddings = np.load(npy_path)
        with open(ids_path, "r", encoding="utf-8") as f:
            id_index_map = json.load(f)

        documents = []
        id_field = id_keys[entity]
        
        for rec in records:
            item_id = rec.get(id_field)
            if not item_id or item_id not in id_index_map:
                continue
                
            idx = id_index_map[item_id]
            vector = embeddings[idx].tolist()  # convert vector to list of floats
            
            # Combine record attributes with embedding
            doc = rec.copy()
            doc["embedding"] = vector
            # Set mongo primary key _id to the entity ID
            doc["_id"] = item_id
            documents.append(doc)

        stats[entity] = len(documents)

        if dry_run:
            print(f"DRY-RUN: Combined {len(documents)} records for '{entity}'. Preview of first doc:")
            if documents:
                preview = documents[0].copy()
                # Truncate vector representation for print readability
                preview["embedding"] = f"[{len(preview['embedding'])} dimensions...]"
                print(json.dumps(preview, indent=2))
            print("-" * 50)
        else:
            if not client:
                raise ValueError("Cannot seed database collections when MongoClient is None. Please set MONGO_URI.")
                
            db = client[db_name]
            col = db[entity]
            
            print(f"INFO: Seeding '{entity}' collection in database '{db_name}' ({len(documents)} docs)...")
            
            # Drops collection first to avoid duplicates and ensure fresh indices
            col.drop()
            if documents:
                col.insert_many(documents)
            print(f"SUCCESS: Seeded '{entity}' successfully.")

    return stats
