import os
from app.rag_engine import RAGEngine

# Get the absolute path of the backend directory
current_dir = os.path.dirname(os.path.abspath(__file__))
kb_dir = os.path.join(current_dir, "knowledge_base")
storage_dir = os.path.join(current_dir, "storage")

# Force rebuild the index
engine = RAGEngine(kb_dir=kb_dir, index_dir=storage_dir)
engine.initialize_vector_db(force_rebuild=True)
print("✨ FAISS index successfully rebuilt!")