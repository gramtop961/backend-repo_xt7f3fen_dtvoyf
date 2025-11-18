import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

from database import create_document, get_documents, db
from schemas import Service, Booking, ContactMessage

app = FastAPI(title="Prestige Beauty Salon API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Prestige Beauty Salon Backend Running"}


# ---------- Services ----------
@app.get("/api/services")
def list_services() -> List[dict]:
    try:
        services = get_documents("service")
        # Seed with a few defaults if empty
        if len(services) == 0:
            defaults = [
                Service(title="Haircut & Styling", description="Prerje profesionale, stilim dhe këshillim personal.", price=25.0, duration_minutes=45, category="Hair").model_dump(),
                Service(title="Manicure & Gel", description="Manikyr me gel, forma natyrale dhe ngjyra premium.", price=20.0, duration_minutes=60, category="Nails").model_dump(),
                Service(title="Facial Glow", description="Trajtim fytyre për lëkurë të shëndetshme dhe të ndritshme.", price=35.0, duration_minutes=50, category="Skin").model_dump(),
            ]
            for s in defaults:
                create_document("service", s)
            services = get_documents("service")
        # Convert ObjectId to str if present
        for s in services:
            if "_id" in s:
                s["id"] = str(s.pop("_id"))
        return services
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Bookings ----------
@app.post("/api/bookings")
def create_booking(payload: Booking):
    try:
        booking_id = create_document("booking", payload)
        return {"success": True, "id": booking_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bookings")
def list_bookings(limit: int = 20):
    try:
        docs = get_documents("booking")[:limit]
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Contact ----------
@app.post("/api/contact")
def create_contact(payload: ContactMessage):
    try:
        msg_id = create_document("contactmessage", payload)
        return {"success": True, "id": msg_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Social (best-effort placeholders) ----------
class SocialConfig(BaseModel):
    instagram_username: Optional[str] = None
    facebook_page: Optional[str] = None

@app.get("/api/social/config")
def social_config():
    return {
        "instagram_username": os.getenv("INSTAGRAM_USERNAME"),
        "facebook_page": os.getenv("FACEBOOK_PAGE"),
    }

@app.get("/api/social/instagram")
def instagram_feed():
    # Real Instagram Graph API requires tokens; return empty list if not configured
    username = os.getenv("INSTAGRAM_USERNAME")
    if not username:
        return []
    # In this environment, skip external calls and return placeholder items
    return [
        {"id": "1", "image_url": "https://images.unsplash.com/photo-1519681393784-d120267933ba?q=80&w=1200&auto=format&fit=crop", "caption": "Stilime moderne tek Prestige ✨", "permalink": "https://instagram.com/"+username},
        {"id": "2", "image_url": "https://images.unsplash.com/photo-1517167685284-96dd43deca1d?q=80&w=1200&auto=format&fit=crop", "caption": "Ngjyra të buta, estetikë minimale.", "permalink": "https://instagram.com/"+username},
    ]

@app.get("/api/social/facebook")
def facebook_feed():
    page = os.getenv("FACEBOOK_PAGE")
    if not page:
        return []
    return [
        {"id": "1", "message": "Mirë se erdhët tek Prestige Beauty Salon!", "permalink": "https://facebook.com/"+page},
    ]


# ---------- Health & DB Test ----------
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
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
