"""
Skill: retrieve_similar_cases

For the POC this uses lightweight TF-IDF + cosine similarity (scikit-learn)
instead of a vector DB, so there's nothing to stand up to run this end to
end. Swapping in pgVector/Chroma later means replacing this one function —
the agent and orchestrator don't need to change.
"""

from typing import Any, Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def retrieve_similar_cases(
    query_narrative: str,
    case_corpus: List[Dict[str, Any]],
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    """
    Return the top_k historical cases whose narrative most closely
    resembles query_narrative, each annotated with a similarity score.
    """
    if not case_corpus:
        return []

    corpus_texts = [c["narrative"] for c in case_corpus]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus_texts + [query_narrative])

    query_vec = tfidf_matrix[-1]
    corpus_vecs = tfidf_matrix[:-1]
    scores = cosine_similarity(query_vec, corpus_vecs).flatten()

    ranked = sorted(
        zip(case_corpus, scores), key=lambda pair: pair[1], reverse=True
    )

    results = []
    for case, score in ranked[:top_k]:
        results.append({**case, "similarity_score": round(float(score), 3)})
    return results
