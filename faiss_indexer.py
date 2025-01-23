# CITIZENAI/faiss_indexer.py

import os
import pickle
import time

import faiss
import numpy as np
import requests
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def create_faiss_index(embedding_dim=384):
    return faiss.IndexFlatIP(embedding_dim)


def fetch_category_articles(category, num_articles=30):
    """
    Fetch a specified number of articles from a Wikipedia category.
    """
    search_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category}",
        "format": "json",
        "cmlimit": num_articles,
    }
    response = requests.get(search_url, params=params)
    data = response.json()
    return [item["title"] for item in data.get("query", {}).get("categorymembers", [])]


def fetch_article_summary(title):
    """
    Fetches a summary of a Wikipedia article by title.
    """
    summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    response = requests.get(summary_url)
    if response.status_code == 200:
        data = response.json()
        return {
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "extract": data.get("extract", ""),
            "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
        }
    else:
        print(f"Error fetching article: {title}")
        return None


def fetch_and_index_articles(titles, index):
    doc_vectors = []
    metadata = []

    for i, title in enumerate(titles):
        article = fetch_article_summary(title)
        if article:
            print(f"Indexing article {i+1}/{len(titles)}: {title}")
            vector = model.encode(article["extract"]).reshape(1, -1)
            doc_vectors.append(vector)
            metadata.append(article)

    if doc_vectors:
        doc_vectors = np.vstack(doc_vectors).astype("float32")
        faiss.normalize_L2(doc_vectors)
        index.add(doc_vectors)

    return metadata


if __name__ == "__main__":
    start_time = time.time()

    # Create FAISS index
    index = create_faiss_index()

    # Category-Based Hybrid Approach
    categories = ["Science", "Technology", "Health", "Philosophy", "History"]
    all_titles = set()  # Use a set to avoid duplicates

    # Step 1: Fetch articles based on categories
    for category in categories:
        print(f"Fetching articles from category: {category}")
        all_titles.update(fetch_category_articles(category, num_articles=30))

    # Step 2: Incrementally expand index as needed
    metadata = fetch_and_index_articles(all_titles, index)

    # Save FAISS index and metadata to disk
    os.makedirs("CITIZENAI", exist_ok=True)
    faiss.write_index(index, os.path.join("CITIZENAI", "faiss_index.idx"))
    with open(os.path.join("CITIZENAI", "metadata.pkl"), "wb") as f:
        pickle.dump(metadata, f)

    print(
        f"FAISS index and metadata saved using category-based and incremental approach."
    )
    print(f"Total time taken: {time.time() - start_time:.2f} seconds")
