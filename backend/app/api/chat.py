from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.chat_agent import run_chat
from app.core.security import get_current_user
from app.db.database import get_db

router = APIRouter(prefix="/chat", tags=["Chat"])

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Tum NexCart ke shopping assistant ho. User ki madad karo products "
        "dhoondhne aur cart mein add karne mein. Sirf search_products aur "
        "add_to_cart tools use karo jab zaroorat ho. Order place karna "
        "tumhara kaam nahi hai — user khud checkout karega apni marzi se."
    ),
}


@router.post("/assistant")
def chat_assistant(payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    history = payload.get("history", [])
    message = payload["message"]

    messages = [SYSTEM_PROMPT] + history + [{"role": "user", "content": message}]
    result = run_chat(db, user.id, messages)
    return {"reply": result["reply"], "history": result["messages"][1:]}