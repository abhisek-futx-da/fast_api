"""Simple test application to verify FastAPI installation and basic functionality."""

from fastapi import FastAPI

# Create FastAPI app
app = FastAPI(
    title="Test FastAPI App",
    description="Simple test application to verify FastAPI is working",
    version="1.0.0"
)

@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "Hello, FastAPI is working!"}

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Test app is running"}

@app.get("/test/{item_id}")
def read_item(item_id: int, q: str = None):
    """Test endpoint with path and query parameters."""
    return {"item_id": item_id, "q": q}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
