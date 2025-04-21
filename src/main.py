from fastapi import FastAPI, HTTPException, Body, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional, Dict, Any
import os
import logging
from datetime import datetime
import json

from models import (
    ChatRequest, 
    ChatResponse, 
    Laptop, 
    LaptopResponse, 
    UserPreference,
    UsageType,
    Health
)
from data_manager import DataManager
from recommendation_engine import RecommendationEngine
from chatbot import ChatBot

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("laptop-recommender")

# Initialize FastAPI app
app = FastAPI(
    title="Laptop Recommendation System",
    description="AI-powered chatbot for laptop recommendations",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize data manager and load data
data_manager = DataManager()
laptop_data = data_manager.load_laptop_data()
logger.info(f"Loaded {len(laptop_data)} laptops from data store")

# Initialize recommendation engine
recommendation_engine = RecommendationEngine(laptop_data)

# Initialize chatbot
chatbot = ChatBot(recommendation_engine)

# Base directory for static files (if needed)
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"Mounted static files from {static_dir}")


@app.get("/", tags=["General"])
async def root():
    """Root endpoint returning welcome message."""
    return {
        "message": "Welcome to the Laptop Recommendation API",
        "documentation": "/docs",
    }


@app.get("/health", tags=["General"], response_model=Health)
async def health_check():
    """Health check endpoint."""
    return Health(
        status="healthy",
        version="1.0.0",
    )


@app.post("/api/chat", tags=["Chat"], response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message and return a response.
    
    Args:
        request: Chat request with message and optional conversation ID
        
    Returns:
        ChatResponse with bot message and recommendations if available
    """
    logger.info(f"Received chat message: {request.message[:50]}...")
    try:
        response = chatbot.process_message(request)
        return response
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/recommendations", tags=["Recommendations"], response_model=LaptopResponse)
async def get_recommendations(preferences: UserPreference):
    """
    Get laptop recommendations based on explicit preferences.
    
    Args:
        preferences: User preferences for laptop recommendations
        
    Returns:
        LaptopResponse with recommendations
    """
    logger.info(f"Received recommendation request: {preferences}")
    try:
        # Get recommendations
        results = recommendation_engine.get_recommendations(
            budget=preferences.budget,
            usage_type=preferences.usage_type,
            brand_preference=preferences.brand_preference,
            min_ram=preferences.min_ram,
            min_storage=preferences.min_storage,
            prefer_gpu=preferences.prefer_gpu
        )
        
        # Convert to Laptop models
        laptop_models = [Laptop(**laptop) for laptop in results]
        
        return LaptopResponse(
            recommendations=laptop_models,
            count=len(laptop_models),
            message=f"Found {len(laptop_models)} laptops matching your criteria."
        )
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/laptops", tags=["Laptops"], response_model=List[Laptop])
async def get_all_laptops(
    limit: int = Query(50, gt=0, le=100, description="Maximum number of laptops to return"),
    brand: Optional[str] = Query(None, description="Filter by brand name")
):
    """
    Get all available laptops, optionally filtered by brand.
    
    Args:
        limit: Maximum number of laptops to return
        brand: Optional brand filter
        
    Returns:
        List of laptops
    """
    try:
        filtered_data = laptop_data
        
        # Apply brand filter if specified
        if brand:
            filtered_data = [
                laptop for laptop in filtered_data 
                if laptop.get("brand", "").lower() == brand.lower()
            ]
        
        # Limit results
        limited_data = filtered_data[:limit]
        
        # Convert to Laptop models
        return [Laptop(**laptop) for laptop in limited_data]
    except Exception as e:
        logger.error(f"Error getting all laptops: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/laptops/{laptop_id}", tags=["Laptops"], response_model=Laptop)
async def get_laptop_by_id(
    laptop_id: str = Path(..., description="ID of the laptop to retrieve")
):
    """
    Get a specific laptop by its ID.
    
    Args:
        laptop_id: ID of the laptop to retrieve
        
    Returns:
        Laptop details
    """
    try:
        laptop = data_manager.get_laptop_by_id(laptop_id)
        if not laptop:
            raise HTTPException(status_code=404, detail=f"Laptop with ID {laptop_id} not found")
        
        return Laptop(**laptop)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting laptop {laptop_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/brands", tags=["Metadata"])
async def get_available_brands():
    """Get a list of all available laptop brands."""
    try:
        # Extract unique brands
        brands = list(set(laptop["brand"] for laptop in laptop_data if "brand" in laptop))
        return {"brands": sorted(brands)}
    except Exception as e:
        logger.error(f"Error getting brands: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/usage-types", tags=["Metadata"])
async def get_usage_types():
    """Get all available usage types for laptops."""
    return {
        "usage_types": [
            {"value": usage_type.value, "name": usage_type.name.title(), "description": _get_usage_description(usage_type)}
            for usage_type in UsageType
        ]
    }


def _get_usage_description(usage_type: UsageType) -> str:
    """Get a human-readable description for a usage type."""
    descriptions = {
        UsageType.GAMING: "High-performance laptops for playing modern games",
        UsageType.BUSINESS: "Professional laptops for office and business tasks",
        UsageType.STUDENT: "Affordable and portable laptops for students",
        UsageType.CREATIVE: "Laptops for designers, video editors and creative professionals",
        UsageType.PROGRAMMING: "Laptops optimized for software development",
        UsageType.GENERAL: "Well-balanced laptops for everyday tasks"
    }
    return descriptions.get(usage_type, "")


@app.get("/api/conversations/{conversation_id}/history", tags=["Chat"])
async def get_conversation_history(
    conversation_id: str = Path(..., description="ID of the conversation")
):
    """
    Get the history of messages in a conversation.
    
    Args:
        conversation_id: ID of the conversation
        
    Returns:
        List of messages in the conversation
    """
    try:
        if conversation_id not in chatbot.conversations:
            raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
        
        return {
            "conversation_id": conversation_id,
            "messages": chatbot.conversations[conversation_id]["messages"],
            "preferences": chatbot.conversations[conversation_id]["preferences"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/conversations/{conversation_id}", tags=["Chat"])
async def delete_conversation(
    conversation_id: str = Path(..., description="ID of the conversation to delete")
):
    """
    Delete a conversation.
    
    Args:
        conversation_id: ID of the conversation to delete
        
    Returns:
        Success message
    """
    try:
        if conversation_id not in chatbot.conversations:
            raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
        
        del chatbot.conversations[conversation_id]
        return {"status": "success", "message": f"Conversation {conversation_id} deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}")
    return {"detail": "An unexpected error occurred. Please try again later."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
