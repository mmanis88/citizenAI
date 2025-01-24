import os
import pickle

import faiss
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from openai import AuthenticationError, OpenAI
from passlib.context import CryptContext
from fastapi import Cookie
from sqlalchemy.future import select

from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db, init_db
from models.user import User

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

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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


# Hash password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# User authentication dependency
def get_current_user(session: str = Cookie(None)):
    if not session:
        return None
    return session  # Replace with a database lookup if needed


# Root endpoint to serve HTML
@app.get("/", response_class=HTMLResponse)
async def serve_html(request: Request, current_user: str = Depends(get_current_user)):
    """Serve the main HTML page at the root endpoint."""
    if not current_user:
        return RedirectResponse(url="/signin")
    return templates.TemplateResponse(
        "index.html", {"request": request, "user": current_user}
    )


@app.get("/signup", response_class=HTMLResponse)
async def show_signup(request: Request):
    """Render the signup page."""
    return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/signup")
async def signup(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Handle user signup."""
    # Check if user or email already exists
    query = select(User).where((User.username == username) | (User.email == email))
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists.")

    # Add new user
    hashed_password = hash_password(password)
    new_user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(new_user)
    await db.commit()
    return RedirectResponse(url="/signin", status_code=303)


@app.get("/signin", response_class=HTMLResponse)
async def show_signin(request: Request):
    """Render the signin page."""
    return templates.TemplateResponse("signin.html", {"request": request})


@app.post("/signin")
async def signin(
    username_or_email: str = Form(...),  # Accept either username or email
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Handle user signin."""
    # Query for the user based on username or email
    query = select(User).where(
        (User.username == username_or_email) | (User.email == username_or_email)
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=400, detail="Invalid username/email or password."
        )

    # Set the session cookie and redirect to the home page
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="session", value=user.username)  # Set session cookie
    return response


@app.get("/signout")
async def signout():
    """Handle user signout."""
    response = RedirectResponse(url="/signin", status_code=303)
    response.delete_cookie("session")
    return response


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


@app.on_event("startup")
async def startup_event():
    await init_db()
