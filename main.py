import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

from schemas import Appointment, ContactMessage
from database import create_document, get_documents, db

app = FastAPI(title="Salon de Coiffure API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API du salon de coiffure"}

@app.get("/api/services")
def get_services() -> List[Dict[str, Any]]:
    """Liste des services proposés par le salon"""
    return [
        {"id": "cut", "title": "Coupe", "price": 35, "duration": 30, "description": "Coupe personnalisée pour femmes et hommes."},
        {"id": "color", "title": "Coloration", "price": 60, "duration": 90, "description": "Coloration complète ou mèches."},
        {"id": "blowout", "title": "Brushing", "price": 25, "duration": 30, "description": "Brushing soigné pour toutes les occasions."},
        {"id": "treatment", "title": "Soin", "price": 30, "duration": 30, "description": "Soin nourrissant et réparateur."},
    ]

@app.post("/api/appointments")
def create_appointment(appointment: Appointment):
    """Créer une demande de rendez-vous"""
    try:
        inserted_id = create_document("appointment", appointment)
        return {"status": "success", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/appointments")
def list_appointments(limit: int = 50):
    """Lister les derniers rendez-vous (limités)"""
    try:
        docs = get_documents("appointment", limit=limit)
        # Convert ObjectId and datetime for JSON safety
        for d in docs:
            if "_id" in d:
                d["_id"] = str(d["_id"])
            for k, v in list(d.items()):
                if isinstance(v, datetime):
                    d[k] = v.isoformat()
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contact")
def create_contact(msg: ContactMessage):
    """Envoyer un message de contact"""
    try:
        inserted_id = create_document("contactmessage", msg)
        return {"status": "success", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    """Vérifie l'accès à la base de données"""
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
            response["database_name"] = getattr(db, 'name', None) or ("✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set")
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
