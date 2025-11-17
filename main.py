import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Article, Category, Author, Comment

app = FastAPI(title="News API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "News API is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# -----------------------------
# News API Endpoints
# -----------------------------

# Bootstrap defaults if empty
@app.post("/api/bootstrap")
def bootstrap_defaults():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    # Seed categories
    existing_categories = list(db["category"].find({}))
    if not existing_categories:
        defaults = [
            {"name": "Top Stories", "slug": "top-stories", "description": "Latest headlines"},
            {"name": "Technology", "slug": "technology", "description": "Tech news and analysis"},
            {"name": "Business", "slug": "business", "description": "Market and company news"},
            {"name": "Sports", "slug": "sports", "description": "Scores and highlights"},
            {"name": "World", "slug": "world", "description": "Global news"},
        ]
        for c in defaults:
            create_document("category", c)

    # Seed author
    existing_authors = list(db["author"].find({}))
    if not existing_authors:
        create_document("author", {"name": "Staff Reporter", "bio": "Newsroom", "avatar_url": None})

    # If no articles, create sample
    if db["article"].count_documents({}) == 0:
        create_document("article", {
            "title": "Welcome to Your News Site",
            "slug": "welcome-to-your-news-site",
            "summary": "This is a sample article to get you started.",
            "content": "<p>Use the editor to publish your first story. This sample shows the layout.</p>",
            "category": "top-stories",
            "author_name": "Staff Reporter",
            "cover_image": None,
            "tags": ["news", "sample"],
            "published": True,
            "published_at": datetime.utcnow(),
            "view_count": 0
        })

    return {"status": "ok"}

# Categories
@app.get("/api/categories", response_model=List[Category])
def list_categories():
    items = get_documents("category")
    return [Category(**{k: v for k, v in item.items() if k != "_id"}) for item in items]

# Articles
@app.get("/api/articles", response_model=List[Article])
def list_articles(category: Optional[str] = None, limit: int = 20):
    filter_q = {"published": True}
    if category:
        filter_q["category"] = category
    items = get_documents("article", filter_q, limit)
    return [Article(**{k: v for k, v in item.items() if k != "_id"}) for item in items]

@app.get("/api/articles/{slug}", response_model=Article)
def get_article(slug: str):
    items = get_documents("article", {"slug": slug}, limit=1)
    if not items:
        raise HTTPException(status_code=404, detail="Article not found")
    doc = items[0]
    return Article(**{k: v for k, v in doc.items() if k != "_id"})

class ArticleCreate(BaseModel):
    title: str
    summary: str
    content: str
    category: str
    author_name: str
    cover_image: Optional[str] = None
    tags: Optional[List[str]] = []

@app.post("/api/articles", response_model=Article)
def create_article(payload: ArticleCreate):
    slug = "-".join(payload.title.lower().split())
    data = payload.model_dump()
    data.update({
        "slug": slug,
        "published": True,
        "published_at": datetime.utcnow(),
        "view_count": 0,
    })
    create_document("article", data)
    return Article(**data)

# Comments
class CommentCreate(BaseModel):
    article_slug: str
    name: str
    message: str

@app.post("/api/comments")
def post_comment(payload: CommentCreate):
    create_document("comment", payload.model_dump())
    return {"status": "ok"}

@app.get("/api/comments/{article_slug}", response_model=List[Comment])
def list_comments(article_slug: str):
    items = get_documents("comment", {"article_slug": article_slug})
    return [Comment(**{k: v for k, v in item.items() if k != "_id"}) for item in items]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
