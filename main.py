"""
URL Shortener - FastAPI Application
A lightweight, production-ready URL shortener
"""
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from database import db
from utils import (
    generate_short_code,
    is_valid_short_code,
    format_short_url,
    validate_url,
    sanitize_custom_code
)

# Load environment variables
load_dotenv()

# Configuration
BASE_DOMAIN = os.getenv("BASE_DOMAIN", "http://localhost:8000")
MAX_GENERATION_ATTEMPTS = 100  # Prevent infinite loops

# Setup FastAPI
app = FastAPI(
    title="URL Shortener",
    description="A lightweight URL shortener built with FastAPI and SQLite",
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main page"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "base_domain": BASE_DOMAIN
    })


@app.post("/shorten")
async def shorten_url(
    request: Request,
    url: str = Form(...),
    custom_code: Optional[str] = Form("")
):
    """
    Create a short URL
    - url: The long URL to shorten (required)
    - custom_code: Optional custom short code (5-10 chars, alphanumeric)
    """
    # Validate URL
    is_valid, result = validate_url(url)
    if not is_valid:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": result,
            "url": url,
            "custom_code": custom_code
        })
    
    original_url = result
    
    # Handle custom short code
    if custom_code:
        short_code = sanitize_custom_code(custom_code)
        
        # Validate custom code format
        if not is_valid_short_code(short_code):
            return templates.TemplateResponse("index.html", {
                "request": request,
                "error": "Custom code must be 5-10 characters long and contain only letters and numbers (a-z, A-Z, 0-9).",
                "url": original_url,
                "custom_code": custom_code
            })
        
        # Check if code already exists
        if db.url_exists(short_code):
            return templates.TemplateResponse("index.html", {
                "request": request,
                "error": f"This short URL already exists. Please choose another code.",
                "url": original_url,
                "custom_code": custom_code
            })
    else:
        # Generate random short code
        short_code = None
        for _ in range(MAX_GENERATION_ATTEMPTS):
            candidate = generate_short_code()
            if not db.url_exists(candidate):
                short_code = candidate
                break
        
        if not short_code:
            return templates.TemplateResponse("index.html", {
                "request": request,
                "error": "Unable to generate unique short code. Please try again or use a custom code.",
                "url": original_url
            })
    
    # Save to database
    success = db.create_url(short_code, original_url)
    
    if not success:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "Failed to create short URL. The code might already exist.",
            "url": original_url,
            "custom_code": custom_code
        })
    
    # Generate full short URL
    short_url = format_short_url(BASE_DOMAIN, short_code)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "short_url": short_url,
        "short_code": short_code,
        "original_url": original_url
    })


@app.get("/{short_code}")
async def redirect_to_url(short_code: str):
    """
    Redirect to original URL
    Returns 302 redirect if found, 404 if not
    """
    # Validate short code format
    if not is_valid_short_code(short_code):
        raise HTTPException(status_code=404, detail="Invalid short code")
    
    # Look up URL
    url_data = db.get_url(short_code)
    
    if not url_data:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    # Perform 302 redirect
    return RedirectResponse(url=url_data["original_url"], status_code=302)


@app.get("/api/stats")
async def get_stats():
    """Get statistics (optional endpoint for debugging)"""
    urls = db.get_all_urls(limit=100)
    return {
        "total_urls": len(urls),
        "urls": urls
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors with custom page"""
    if request.headers.get("accept", "").startswith("application/json"):
        return {"error": "Not found"}
    return templates.TemplateResponse("error.html", {
        "request": request,
        "status_code": 404,
        "message": "The short URL you're looking for doesn't exist."
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)