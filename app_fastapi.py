from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import openai
from faiss_search import search_faiss_index  # Import the updated function
import pickle
import faiss

app = FastAPI()

# OpenAI API key
openai.api_key = "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"

# Serve the frontend directory at "/static"
app.mount("/static", StaticFiles(directory="frontend", html=True), name="static")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load FAISS index and metadata
embedding_dim = 384
index = faiss.read_index("CITIZENAI/faiss_index.idx")  # Load the FAISS index
with open("CITIZENAI/metadata.pkl", "rb") as f:
    metadata = pickle.load(f)  # Load metadata

# Generate summary with clickable citations
def generate_summary_with_clickable_citations(query, context_with_links):
    messages = [
        {"role": "system", "content": "You are a knowledgeable assistant that provides answers with inline clickable citations."},
        {"role": "user", "content": f"Summarize the following information, embedding clickable citations as HTML links:\n\nQuery: {query}\n\nContext:\n{context_with_links}\n\nAnswer with inline clickable citations:"}
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=300,
            temperature=0.5
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error generating summary with clickable citations: {e}")
        return "Error generating summary with clickable citations."

# Search endpoint using the new search functionality
@app.get("/search")
async def search_query(query: str, top_k: int = 5):
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is missing")

    # Use the updated search function, which includes the Wikipedia fallback
    results = search_faiss_index(query, index, metadata, top_k=top_k)
    context_with_links = ""
    sources = []

    # Create the context with clickable links
    for doc in results:
        context_with_links += f"\nSource: <a href='{doc['url']}' target='_blank'>{doc['title']}</a>\nContent: {doc.get('summary', doc.get('extract', 'No summary available'))}\n"
        sources.append({"title": doc['title'], "url": doc['url']})

    summary_with_clickable_citations = generate_summary_with_clickable_citations(query, context_with_links)

    return {"summary": summary_with_clickable_citations, "sources": sources}
