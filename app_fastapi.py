import os
import pickle

import faiss
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from openai import AuthenticationError, OpenAI

from faiss_search import search_faiss_index  # Import the updated function

load_dotenv()

# Configuration using environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "faiss_index.idx")
METADATA_PATH = os.getenv("METADATA_PATH", "metadata.pkl")
FRONTEND_DIR = os.getenv("FRONTEND_DIR", "frontend")

# Validate API key
if not OPENAI_API_KEY:
    raise RuntimeError(
        "OpenAI API key is not set. Ensure OPENAI_API_KEY is passed as an environment variable."
    )


# Initialize the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


# FastAPI app initialization
app = FastAPI()

# Serve the frontend directory at "/static"
static_dir = os.path.join(FRONTEND_DIR, "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Jinja2 template setup
templates = Jinja2Templates(directory=FRONTEND_DIR)

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load FAISS index and metadata
def load_resources(faiss_path: str, metadata_path: str):
    """Load the FAISS index and metadata."""
    try:
        index = faiss.read_index(faiss_path)
        with open(metadata_path, "rb") as f:
            metadata = pickle.load(f)
        return index, metadata
    except Exception as e:
        raise RuntimeError(f"Error loading FAISS index or metadata: {e}")


index, metadata = load_resources(FAISS_INDEX_PATH, METADATA_PATH)


# Function to generate summary with clickable citations
def generate_summary_with_clickable_citations(
    query: str,
    context_with_links: str,
    model: str = "gpt-4",
    max_tokens: int = 300,
    temperature: float = 0.5,
) -> str:
    """
    Generates a summary with clickable HTML citations.

    Args:
        query (str): The user's query.
        context_with_links (str): Context including clickable HTML links.
        model (str): Model to use. Default is "gpt-4".
        max_tokens (int): Maximum tokens in the response. Default is 300.
        temperature (float): Sampling temperature. Default is 0.5.

    Returns:
        str: Summary with clickable citations or error message.
    """
    messages = [
        {
            "role": "system",
            "content": "You are a knowledgeable assistant that provides answers with inline clickable citations.",
        },
        {
            "role": "user",
            "content": f"Summarize the following information, embedding clickable citations as HTML links:\n\nQuery: {query}\n\nContext:\n{context_with_links}\n\nAnswer with inline clickable citations:",
        },
    ]
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
    except AuthenticationError:
        return "Authentication failed. Please check your API key."
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "An error occurred while generating the summary. Please try again later."


# Root endpoint to serve HTML
security = HTTPBasic()


@app.get("/", response_class=HTMLResponse)
async def serve_html(
    request: Request,
    credentials: HTTPBasicCredentials = Depends(security),
):
    """Serve the main HTML page at the root endpoint."""

    # Hardcoded example credentials - replace this with secure verification logic
    valid_username = "admin"
    valid_password = "citizenai"

    if credentials.username != valid_username or credentials.password != valid_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return templates.TemplateResponse("index.html", {"request": request})


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    return {"status": "healthy", "message": "Service is up and running!"}


# Search endpoint
@app.get("/search")
async def search_query(query: str, top_k: int = 5):
    """
    Handles search requests by querying the FAISS index and returning
    a summary with clickable citations.
    """
    if not query.strip():
        raise HTTPException(
            status_code=400, detail="Query parameter is missing or empty."
        )

    try:
        # Query the FAISS index
        results = search_faiss_index(query, index, metadata, top_k=top_k)
        if not results:
            raise HTTPException(
                status_code=404, detail="No results found for the query."
            )

        context_with_links = ""
        sources = []

        # Construct context with clickable links
        for doc in results:
            context_with_links += (
                f"\nSource: <a href='{doc['url']}' target='_blank'>{doc['title']}</a>\n"
                f"Content: {doc.get('summary', doc.get('extract', 'No summary available'))}\n"
            )
            sources.append({"title": doc["title"], "url": doc["url"]})

        # Generate summary with citations
        summary_with_clickable_citations = generate_summary_with_clickable_citations(
            query, context_with_links
        )

        return {"summary": summary_with_clickable_citations, "sources": sources}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error processing search query: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the search request.",
        )
