import os
import re
import json
import numpy as np
import faiss
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

class MarkdownChunker:
    """
    Custom heading-based chunker designed to parse markdown documents 
    into structured, metadata-rich sections for RAG.
    """
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Cleans whitespaces and removes redundant empty lines."""
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def chunk_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parses a single Markdown file and divides it using headings (# and ##).
        Preserves metadata: source filename, heading, section name, unique ID, and content.
        """
        filename = os.path.basename(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        chunks = []
        
        current_h1 = "General"
        current_h2 = ""
        current_section_lines = []
        chunk_idx = 0

        for line in lines:
            if line.startswith("# ") and not line.startswith("## "):
                if current_section_lines:
                    chunk_text = self.clean_text("\n".join(current_section_lines))
                    if chunk_text:
                        chunks.append(self._build_chunk_dict(
                            filename, current_h1, current_h2, chunk_text, chunk_idx
                        ))
                        chunk_idx += 1
                    current_section_lines = []
                
                current_h1 = line.replace("# ", "").strip()
                current_h2 = ""

            elif line.startswith("## "):
                if current_section_lines:
                    chunk_text = self.clean_text("\n".join(current_section_lines))
                    if chunk_text:
                        chunks.append(self._build_chunk_dict(
                            filename, current_h1, current_h2, chunk_text, chunk_idx
                        ))
                        chunk_idx += 1
                    current_section_lines = []
                
                current_h2 = line.replace("## ", "").strip()

            else:
                current_section_lines.append(line)

        if current_section_lines:
            chunk_text = self.clean_text("\n".join(current_section_lines))
            if chunk_text:
                chunks.append(self._build_chunk_dict(
                    filename, current_h1, current_h2, chunk_text, chunk_idx
                ))

        return chunks

    def _build_chunk_dict(self, filename: str, h1: str, h2: str, content: str, idx: int) -> Dict[str, Any]:
        """Helper to structure the extracted metadata uniformly."""
        section_name = h2 if h2 else h1
        return {
            "chunk_id": f"{filename.replace('.md', '')}_{idx}",
            "source_filename": filename,
            "heading": h1,
            "section_name": section_name,
            "original_content": f"### {section_name}\n{content}"
        }

    def process_knowledge_base(self, kb_dir: str) -> List[Dict[str, Any]]:
        """Loads and processes all markdown files in the target directory."""
        all_chunks = []
        if not os.path.exists(kb_dir):
            raise FileNotFoundError(f"Knowledge base directory '{kb_dir}' not found.")

        for file in os.listdir(kb_dir):
            if file.endswith(".md"):
                file_path = os.path.join(kb_dir, file)
                all_chunks.extend(self.chunk_file(file_path))
                
        return all_chunks


class RAGEngine:
    """
    Manages vector generation, local FAISS storage, 
    and semantic similarity search query routing.
    """
    def __init__(self, kb_dir: str, index_dir: str):
        self.kb_dir = kb_dir
        self.index_dir = index_dir
        self.index_path = os.path.join(index_dir, "clinic_index.faiss")
        self.metadata_path = os.path.join(index_dir, "clinic_metadata.json")
        
        # Load lightweight open-source embedder (384-dimensional outputs)
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.chunker = MarkdownChunker()
        
        # In-memory storage holders
        self.chunks_metadata: List[Dict[str, Any]] = []
        self.index: faiss.IndexFlatL2 = None

        # Build or load the vector space automatically
        os.makedirs(self.index_dir, exist_ok=True)
        self.initialize_vector_db()

    def initialize_vector_db(self, force_rebuild: bool = False):
        """Builds a new index from scratch or loads the cached local file."""
        if force_rebuild or not os.path.exists(self.index_path) or not os.path.exists(self.metadata_path):
            print("🔄 Building new FAISS Vector Index...")
            self.rebuild_index()
        else:
            print("💾 Loading existing FAISS index from disk...")
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self.chunks_metadata = json.load(f)

    def rebuild_index(self):
        """Parses documents, computes embeddings, and writes the FAISS state to disk."""
        # 1. Parse and chunk Markdown files
        raw_chunks = self.chunker.process_knowledge_base(self.kb_dir)
        if not raw_chunks:
            raise ValueError("The knowledge base has no readable chunks. Index building halted.")

        # 2. Extract contents and run embeddings inference
        texts_to_embed = [chunk["original_content"] for chunk in raw_chunks]
        embeddings = self.embedder.encode(texts_to_embed, convert_to_numpy=True)

        # 3. Initialize L2 Distance FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)

        # 4. Save to Disk
        faiss.write_index(self.index, self.index_path)
        self.chunks_metadata = raw_chunks
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.chunks_metadata, f, indent=2)

        print(f"✅ Vector Index completed. Indexed {self.index.ntotal} chunks.")

    def search(self, query: str, top_k: int = 3, distance_threshold: float = 1.4) -> List[Dict[str, Any]]:
        """
        Executes a semantic similarity query against the stored vector index.
        Applies a distance threshold to filter out unrelated results.
        """
        if not self.index:
            raise RuntimeError("Index is not initialized. Call initialize_vector_db first.")

        # Encode search query
        query_vector = self.embedder.encode([query], convert_to_numpy=True)
        
        # Search the FAISS index
        distances, indices = self.index.search(query_vector, top_k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            # Apply threshold to filter completely irrelevant hits
            if dist <= distance_threshold:
                match = self.chunks_metadata[idx].copy()
                match["score"] = float(dist)
                results.append(match)

        return results


# Quick Local Verification CLI Execution
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    kb_directory = os.path.join(current_dir, "../knowledge_base")
    index_directory = os.path.join(current_dir, "../storage")
    
    # Initialize index
    engine = RAGEngine(kb_dir=kb_directory, index_dir=index_directory)
    
    # Test semantic query search
    test_query = "What times is the clinic open on Saturdays?"
    print(f"\n🔍 Query: '{test_query}'")
    hits = engine.search(test_query, top_k=2)
    
    for rank, hit in enumerate(hits, 1):
        print(f"\n[Rank {rank}] {hit['source_filename']} - {hit['section_name']} (Score: {hit['score']:.4f})")
        print(f"Content:\n{hit['original_content']}")