# backend/models.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    name: str
    email: str
    preferences: Optional[Dict] = {}
    progress: Optional[Dict] = {}

    class Config:
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True

class Chunk(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    subject: str
    chapter: str
    page: Optional[int]
    text: str
    metadata: Optional[Dict] = {}

    class Config:
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True
