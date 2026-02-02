from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Annotated
from datetime import datetime
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "doc2deck")

client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]

class User(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    
    id: Optional[str] = Field(default=None, alias="_id")
    username: str
    email: str
    hashed_password: str
    notes: Optional[str] = None
    pdf_filename: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Presentation(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    title: str
    notes: Optional[str] = None
    pdf_filename: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

async def get_database():
    return database