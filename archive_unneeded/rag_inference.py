# src/rag_inference.py
import json
import sys
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

import os
BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
VECTOR_DIR = os.path.join(BASE_DIR, "vector_store")  # now using absolute path
EMB_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5


def load_vectorstore():
    emb = HuggingFaceEmbeddings(model_name=EMB_MODEL)
    try:
        vs = FAISS.load_local(VECTOR_DIR, emb, allow_dangerous_deserialization=True)
    except Exception as e:
        print("Error loading FAISS vector store:", e, file=sys.stderr)
        raise
    return vs


def enhance_query(query: str, user_profile: dict = None) -> str:
    """
    Enhance the query with relevant context and keywords.
    """
    enhanced = query
    
    # Add F1 visa specific context
    if "F1" in query or "Student" in query:
        f1_context = [
            "US F1 student visa requirements",
            "eligibility criteria",
            "academic admission requirements",
            "financial documentation",
            "proof of funds",
            "intent to return",
            "full course of study",
            "student visa interview",
            "I-20 form requirements",
            "SEVIS registration",
            "student employment restrictions"
        ]
        enhanced = f"{enhanced} {' '.join(f1_context)}"
    
    # Add profile-specific context if available
    if user_profile:
        relevant_fields = [
            ("nationality", "nationality citizenship country of origin residence"),
            ("education", "academic background education degree qualification previous study"),
            ("employment", "employment work status financial support sponsor"),
            ("visa_type", "visa category type class classification"),
            ("income", "financial resources bank statements support funds")
        ]
        for field, context in relevant_fields:
            if field in user_profile and user_profile[field] is not None:
                enhanced = f"{enhanced} {user_profile[field]} {context}"
    
    return enhanced

def retrieve(query, k=TOP_K, user_profile=None):
    """
    Returns a list of Document objects for the given query.
    Uses similarity_search on the FAISS vectorstore for compatibility.
    """
    enhanced_query = enhance_query(query, user_profile)
    print(f"\nDebug: Using enhanced query: {enhanced_query}")
    
    vs = load_vectorstore()
    try:
        # Try MMR search first with more aggressive parameters
        docs = vs.max_marginal_relevance_search(
            enhanced_query,
            k=k,
            fetch_k=k*4,  # Fetch more candidates for better diversity
            lambda_mult=0.5  # More emphasis on diversity vs relevance
        )
        
        # If we didn't get enough results, try a second search with different emphasis
        if len(docs) < k:
            additional_docs = vs.similarity_search(
                enhanced_query,
                k=(k - len(docs))
            )
            docs.extend(additional_docs)
            
    except Exception as e:
        print(f"Warning: MMR search failed ({e}), falling back to similarity search")
        docs = vs.similarity_search(enhanced_query, k=k)
    
    # Deduplicate results
    seen = set()
    unique_docs = []
    for doc in docs:
        doc_id = doc.metadata.get('id', doc.page_content[:100])
        if doc_id not in seen:
            seen.add(doc_id)
            unique_docs.append(doc)
    
    return unique_docs[:k]


if __name__ == "__main__":
    q = "student visa eligibility for Indian nationals"
    print("Running retrieval for query:", q)
    hits = retrieve(q, k=3)
    print(f"Returned {len(hits)} hits\n")
    for i, d in enumerate(hits, 1):
        meta = d.metadata if hasattr(d, "metadata") else {}
        text_preview = (
            d.page_content[:400] if hasattr(d, "page_content") else str(d)[:400]
        )
        print(f"--- Hit {i} ---")
        print("metadata:", meta)
        print("text preview:", text_preview.replace("\n", " "))
        print()
