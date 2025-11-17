"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime

# -----------------------------
# NEWS WEBSITE SCHEMAS
# -----------------------------

class Author(BaseModel):
    """Author profile stored in "author" collection"""
    name: str = Field(..., description="Display name of the author")
    bio: Optional[str] = Field(None, description="Short bio")
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    twitter: Optional[str] = Field(None)
    website: Optional[str] = Field(None)

class Category(BaseModel):
    """News category stored in "category" collection"""
    name: str = Field(..., description="Category name, e.g., Technology")
    slug: str = Field(..., description="URL-friendly slug, e.g., technology")
    description: Optional[str] = Field(None)

class Article(BaseModel):
    """News article stored in "article" collection"""
    title: str = Field(..., description="Headline")
    slug: str = Field(..., description="URL slug derived from title")
    summary: str = Field(..., description="Short summary/dek")
    content: str = Field(..., description="Full article HTML/Markdown")
    category: str = Field(..., description="Category slug")
    author_name: str = Field(..., description="Author display name")
    cover_image: Optional[HttpUrl] = Field(None, description="Hero/cover image URL")
    tags: List[str] = Field(default_factory=list)
    published: bool = Field(default=True)
    published_at: Optional[datetime] = Field(default=None)
    view_count: int = Field(default=0)

class Comment(BaseModel):
    """Article comments stored in "comment" collection"""
    article_slug: str = Field(..., description="Related article slug")
    name: str = Field(..., description="Commenter name")
    message: str = Field(..., description="Comment text")
    likes: int = Field(default=0)

# Example schemas retained for reference (not used by news app)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
