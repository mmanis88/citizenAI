# citizen_ai/faiss_search.py

import faiss
import numpy as np
import requests
from sentence_transformers import SentenceTransformer

# Load the same model and FAISS index used in indexing
model = SentenceTransformer('all-MiniLM-L6-v2')

def search_faiss_index(query, index, metadata, top_k=5):
    # Convert the query to an embedding
    query_vector = model.encode(query).reshape(1, -1).astype('float32')
    faiss.normalize_L2(query_vector)  # Normalize for cosine similarity

    # Search FAISS index
    distances, indices = index.search(query_vector, top_k)

    # Retrieve top_k results
    results = []
    for idx in indices[0]:
        if idx < len(metadata):
            results.append(metadata[idx])

    # If FAISS results are insufficient, fetch from Wikipedia API as fallback
    if not results:
        print("No relevant FAISS results. Fetching data from Wikipedia API.")
        wiki_result = fetch_wikipedia_summary(query)
        if wiki_result:
            results.append(wiki_result)

    return results

def fetch_wikipedia_summary(query):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                "title": data.get("title"),
                "summary": data.get("extract"),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
            }
        else:
            print(f"Wikipedia API returned status code {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching data from Wikipedia API: {e}")
        return None


