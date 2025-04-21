from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from enum import Enum


class UsageType(str, Enum):
    """Enum for different laptop usage types."""
    GAMING = "gaming"
    BUSINESS = "business"
    STUDENT = "student"
    CREATIVE = "creative"
    PROGRAMMING = "programming"
    GENERAL = "general"


class LaptopBase(BaseModel):
    """Base model for laptop data."""
    brand: str
    model: str
    price: float
    processor: str
    ram: int = Field(..., description="RAM in GB")
    storage: int = Field(..., description="Storage in GB")
    gpu: Optional[str] = None
    display: Optional[str] = None
    battery_life: Optional[float] = None  # hours
    weight: Optional[float] = None  # kg
    os: Optional[str] = None

    class Config:
        extra = "ignore"


class Laptop(LaptopBase):
    """Complete laptop model with id."""
    id: str = Field(..., description="Unique identifier for the laptop")
    score: Optional[float] = None

    class Config:
        extra = "ignore"


class LaptopResponse(BaseModel):
    """Response model for laptop recommendations."""
    recommendations: List[Laptop]
    count: int
    message: Optional[str] = None

    class Config:
        extra = "ignore"


class UserPreference(BaseModel):
    """User preferences for laptop recommendations."""
    budget: float = Field(..., description="Maximum budget for laptop")
    usage_type: UsageType = Field(..., description="Primary usage type")
    brand_preference: Optional[str] = None
    min_ram: Optional[int] = Field(None, description="Minimum RAM in GB")
    min_storage: Optional[int] = Field(None, description="Minimum storage in GB")
    prefer_gpu: bool = False
    weight_preference: Optional[str] = None
    os_preference: Optional[str] = None

    @validator('budget')
    def budget_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('budget must be greater than 0')
        return v

    @validator('min_ram')
    def ram_must_be_valid(cls, v):
        if v is not None and v < 4:
            raise ValueError('min_ram must be at least 4 GB')
        return v

    @validator('min_storage')
    def storage_must_be_valid(cls, v):
        if v is not None and v < 128:
            raise ValueError('min_storage must be at least 128 GB')
        return v

    class Config:
        extra = "ignore"


class ChatMessage(BaseModel):
    """Chat message model for request/response."""
    text: str
    sender: str = Field(..., description="'user' or 'bot'")
    timestamp: Optional[str] = None

    class Config:
        extra = "ignore"


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="User message text")
    conversation_id: Optional[str] = None

    @validator('message')
    def message_must_not_be_empty(cls, v):
        if len(v) < 1:
            raise ValueError('message must not be empty')
        return v

    class Config:
        extra = "ignore"


class ChatResponse(BaseModel):
    """Chat response model."""
    message: str
    recommendations: Optional[List[Laptop]] = None
    conversation_id: str
    extracted_preferences: Optional[Dict[str, Any]] = None

    class Config:
        extra = "ignore"


class Health(BaseModel):
    """Health check response model."""
    status: str
    version: str

    class Config:
        extra = "ignore"
