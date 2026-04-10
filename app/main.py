from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import user, task, dashboard, api_keys
from app.database import init_db

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Task Manager API",
    description="A RESTful API for managing tasks",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user.router, prefix="/api/users", tags=["users"])
app.include_router(task.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(api_keys.router, prefix="/api", tags=["api-keys"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Task Manager API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
