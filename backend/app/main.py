from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine
from app.models.user import User
from app.api.auth import router as auth_router
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="NexCart AI API",
    description="Backend API for NexCart AI - Next Generation E-Commerce",
    version="0.1.0",
)

# Allow the React frontend (running on a different port) to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default dev port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "NexCart AI API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}  



