"""
Database Schemas for Prestige Beauty Salon

Each Pydantic model below maps to a MongoDB collection. The collection name is the
lowercased class name. Example: Booking -> "booking".
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class Service(BaseModel):
    title: str = Field(..., description="Service name (e.g., Haircut, Manicure)")
    description: Optional[str] = Field(None, description="Short description of the service")
    price: float = Field(..., ge=0, description="Price in EUR")
    duration_minutes: Optional[int] = Field(None, ge=0, description="Estimated duration in minutes")
    category: Optional[str] = Field(None, description="Category, e.g., Hair, Nails, Skin")

class Booking(BaseModel):
    full_name: str = Field(..., description="Client full name")
    phone: str = Field(..., description="Client phone number")
    email: Optional[EmailStr] = Field(None, description="Client email address")
    service_title: str = Field(..., description="Selected service title")
    preferred_date: str = Field(..., description="Preferred date in ISO format (YYYY-MM-DD)")
    preferred_time: str = Field(..., description="Preferred time (e.g., 14:30)")
    notes: Optional[str] = Field(None, description="Additional notes from client")
    status: str = Field("pending", description="Booking status: pending/confirmed/cancelled")

class ContactMessage(BaseModel):
    full_name: str = Field(..., description="Sender full name")
    email: Optional[EmailStr] = Field(None, description="Sender email")
    phone: Optional[str] = Field(None, description="Sender phone")
    subject: str = Field(..., description="Message subject")
    message: str = Field(..., description="Message body")

# Optional future blog schema
class BlogPost(BaseModel):
    title: str
    slug: str
    excerpt: Optional[str] = None
    content: str
    cover_image_url: Optional[str] = None
    published_at: Optional[datetime] = None
    is_published: bool = True
