"""
Local Ollama model (llama3.2) ko "tools" deta hai — products search karna
aur cart mein add karna — taake AI khud decide kare kab konsa tool use
karna hai user ki request ke hisaab se.

⚠️ Ye SIRF localhost pe kaam karta hai (Ollama chal raha hona chahiye
tumhare laptop pe) — Render pe deploy nahi hota.
"""

import json

import numpy as np
import ollama
from sqlalchemy.orm import Session

from app.api.search import get_cached_vectors
from app.core.embeddings import embed_query
from app.models.cart import CartItem
from app.models.product import Product

MODEL = "llama3.2"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Products dhoondhta hai jab user kisi cheez ki tarif ya category bataye",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query, jaise 'comfortable running shoes'"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_to_cart",
            "description": "Ek product ko user ke cart mein add karta hai",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer"},
                    "quantity": {"type": "integer"},
                },
                "required": ["product_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_cart",
            "description": "User ka current cart dikhata hai",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def tool_search_products(db: Session, query: str, limit: int = 5):
    query_vector = np.array(embed_query(query), dtype=np.float32)
    ids, vectors = get_cached_vectors(db)
    if not ids:
        return []
    pv = vectors.astype(np.float32)
    qn = query_vector / (np.linalg.norm(query_vector) + 1e-8)
    vn = pv / (np.linalg.norm(pv, axis=1, keepdims=True) + 1e-8)
    scores = vn @ qn
    top = np.argsort(-scores)[:limit]
    top_ids = [ids[i] for i in top]
    products = db.query(Product).filter(Product.id.in_(top_ids)).all()
    by_id = {p.id: p for p in products}
    return [
        {"id": by_id[i].id, "name": by_id[i].name, "price": float(by_id[i].price)}
        for i in top_ids
        if i in by_id
    ]


def tool_add_to_cart(db: Session, user_id: int, product_id: int, quantity: int = 1):
    existing = (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id, CartItem.product_id == product_id)
        .first()
    )
    if existing:
        existing.quantity += quantity
    else:
        db.add(CartItem(user_id=user_id, product_id=product_id, quantity=quantity))
    db.commit()
    return {"status": "added", "product_id": product_id, "quantity": quantity}


def tool_get_cart(db: Session, user_id: int):
    items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    return [{"product_id": i.product_id, "quantity": i.quantity} for i in items]


def run_chat(db: Session, user_id: int, messages: list[dict]) -> dict:
    response = ollama.chat(model=MODEL, messages=messages, tools=TOOLS)
    msg = response["message"]

    tool_calls = msg.get("tool_calls")
    if not tool_calls:
        return {"reply": msg["content"], "messages": messages + [dict(msg)]}

    messages = messages + [dict(msg)]
    for call in tool_calls:
        name = call["function"]["name"]
        args = call["function"]["arguments"]

        if name == "search_products":
            result = tool_search_products(db, args.get("query", ""))
        elif name == "add_to_cart":
            result = tool_add_to_cart(db, user_id, args["product_id"], args.get("quantity", 1))
        elif name == "get_cart":
            result = tool_get_cart(db, user_id)
        else:
            result = {"error": "unknown tool"}

        messages.append({"role": "tool", "content": json.dumps(result)})

    final = ollama.chat(model=MODEL, messages=messages, tools=TOOLS)
    messages.append(dict(final["message"]))
    return {"reply": final["message"]["content"], "messages": messages}