from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.api.auth import router as auth_router
from app.api.categories import router as categories_router
from app.api.products import router as products_router
from app.models.cart import CartItem
from app.api.cart import router as cart_router
from app.models.order import Order, OrderItem
from app.api.orders import router as orders_router
from app.models.wishlist import WishlistItem
from app.api.wishlist import router as wishlist_router
from app.models.review import Review
from app.api.reviews import router as reviews_router

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
    expose_headers=["X-Total-Count"],
)

app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(wishlist_router)
app.include_router(reviews_router)

@app.get("/")
def read_root():
    return {"message": "NexCart AI API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}  



