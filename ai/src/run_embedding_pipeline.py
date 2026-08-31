import os
import sys

# Ensure project CWD is on PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.embeddings.pipeline import EmbeddingPipeline

def main():
    pipeline = EmbeddingPipeline(
        processed_dir="data/processed", 
        model_dir="model", 
        model_name="BAAI/bge-small-en-v1.5"
    )
    pipeline.run(batch_size=64)

if __name__ == "__main__":
    main()
