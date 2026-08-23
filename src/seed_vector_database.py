import os
import sys
import argparse

# Ensure project CWD is on PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vector_search.database import get_mongodb_client, seed_collections

def main():
    parser = argparse.ArgumentParser(description="Seed RouteMaster MongoDB Atlas collections with Phase 5 dense embeddings.")
    parser.add_argument("--dry-run", action="store_true", help="Merge and preview documents without inserting into MongoDB.")
    parser.add_argument("--db-name", default="routemaster", help="MongoDB database name.")
    parser.add_argument("--processed-dir", default="data/processed", help="Path to processed JSON registries.")
    parser.add_argument("--embeddings-dir", default="model/embeddings", help="Path to generated embedding matrices.")
    
    args = parser.parse_args()

    print("INFO: Initializing RouteMaster Seeding Pipeline...")
    
    client = None
    if not args.dry_run:
        client = get_mongodb_client()
        if client is None:
            print("ERROR: MONGO_URI environment variable not configured or connection failed.")
            print("To verify seeder document generation offline, run with the '--dry-run' flag.")
            sys.exit(1)
            
    try:
        stats = seed_collections(
            client=client,
            db_name=args.db_name,
            processed_dir=args.processed_dir,
            embeddings_dir=args.embeddings_dir,
            dry_run=args.dry_run
        )
        print("SUCCESS: Seeding pipeline run completed successfully. Statistics:")
        for col_name, count in stats.items():
            print(f"  - Collection '{col_name}': {count} documents ready.")
            
    except Exception as e:
        print(f"ERROR: Seeding pipeline execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
