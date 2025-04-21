import re
import uuid
import json
from datetime import datetime
from typing import Dict, Optional, List, Tuple, Any

from models import UsageType, ChatRequest, ChatResponse, UserPreference, Laptop


class ChatBot:
    """
    ChatBot class for processing user input and extracting preferences.
    """
    
    def __init__(self, recommendation_engine):
        """
        Initialize the chatbot with a recommendation engine.
        
        Args:
            recommendation_engine: Engine providing laptop recommendations
        """
        self.recommendation_engine = recommendation_engine
        self.conversations: Dict[str, Dict[str, Any]] = {}
        
        # Define regular expressions for information extraction
        self.regex_patterns = {
            "budget": [
                r"\$?(\d{3,5}(?:,\d{3})*)(?:\s*(?:dollars|USD|bucks))?",
                r"budget\s*(?:is|of)?\s*\$?(\d{3,5}(?:,\d{3})*)",
                r"spend\s*(?:up to)?\s*\$?(\d{3,5}(?:,\d{3})*)",
                r"(?:under|below|less than)\s*\$?(\d{3,5}(?:,\d{3})*)",
                r"(?:max|maximum)?\s*(?:budget|price)?\s*(?:of)?\s*\$?(\d{3,5}(?:,\d{3})*)"
            ],
            "usage": {
                UsageType.GAMING: [
                    r"(?:gaming|games|gamer|play games)",
                    r"(?:fps|shooter|mmo|rpg|strategy|simulation)"
                ],
                UsageType.BUSINESS: [
                    r"(?:business|work|office|professional|corporate)",
                    r"(?:presentations|spreadsheets|documents|meetings)"
                ],
                UsageType.STUDENT: [
                    r"(?:student|school|college|university|campus|education)",
                    r"(?:study|studying|coursework|assignments|homework)"
                ],
                UsageType.CREATIVE: [
                    r"(?:creative|design|art|artist|creator)",
                    r"(?:photo|video|editing|photoshop|illustrator|premiere|after effects)"
                ],
                UsageType.PROGRAMMING: [
                    r"(?:programming|coding|development|developer|software)",
                    r"(?:code|compile|development|IDE|programming)"
                ]
            },
            "brand": r"(?:prefer|want|like)\s+(?:a\s+)?(\w+)(?:\s+laptop)?",
            "ram": r"(\d+)\s*(?:GB|gigs?)?\s*(?:of)?\s*(?:RAM|memory)",
            "storage": r"(\d+)\s*(?:GB|TB|gigs?)?\s*(?:of)?\s*(?:storage|SSD|hard drive|HDD)"
        }
        
        # Define greeting patterns
        self.greeting_patterns = [
            r"\b(?:hi|hello|hey|greetings|howdy)\b",
            r"\b(?:good\s+(?:morning|afternoon|evening))\b",
            r"^(?:start|begin|help)$"
        ]
        
        # Define keywords for extracting preferences
        self.preference_keywords = {
            "laptop_type": {
                "thin": ["thin", "slim", "light", "portable", "ultrabook"],
                "gaming": ["gaming", "game", "powerful"],
                "business": ["business", "professional", "work"],
                "budget": ["cheap", "affordable", "budget", "inexpensive"]
            },
            "os": {
                "windows": ["windows"],
                "macos": ["mac", "macos", "apple"],
                "linux": ["linux", "ubuntu", "debian", "fedora"]
            }
        }
        
    def process_message(self, request: ChatRequest) -> ChatResponse:
        """
        Process a message from the user and generate a response.
        
        Args:
            request: Chat request containing the message and conversation ID
            
        Returns:
            ChatResponse with bot message and recommendations if available
        """
        message = request.message.strip()
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Initialize conversation state if it doesn't exist
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = {
                "preferences": {},
                "messages": [],
                "stage": "greeting"
            }
        
        # Add user message to conversation history
        self.conversations[conversation_id]["messages"].append({
            "text": message,
            "sender": "user",
            "timestamp": datetime.now().isoformat()
        })
        
        # Process the message based on conversation stage
        conversation = self.conversations[conversation_id]
        extracted_preferences = self._extract_preferences(message)
        
        # Update preferences with extracted values
        conversation["preferences"].update(extracted_preferences)
        preferences = conversation["preferences"]
        
        # Check if this is a greeting
        if conversation["stage"] == "greeting" or self._is_greeting(message):
            conversation["stage"] = "getting_preferences"
            response_text = (
                "Hello! I'm your laptop recommendation assistant. "
                "I can help you find the perfect laptop based on your needs. "
                "What's your budget for a new laptop?"
            )
        
        # Check if we have enough information for recommendations
        elif self._has_sufficient_preferences(preferences):
            recommendations = self._get_recommendations(preferences)
            
            if recommendations:
                conversation["stage"] = "recommendations"
                
                # Format recommendations into a readable message
                recommendation_text = self._format_recommendations(recommendations[:3])
                
                response_text = (
                    f"Based on your preferences, here are some recommended laptops:\n\n"
                    f"{recommendation_text}\n\n"
                    f"Would you like more details about any of these options? Or would you like to refine your search?"
                )
                
                # Create response with recommendations
                return ChatResponse(
                    message=response_text,
                    recommendations=[Laptop(**laptop) for laptop in recommendations[:3]],
                    conversation_id=conversation_id,
                    extracted_preferences=preferences
                )
            else:
                response_text = (
                    "I couldn't find any laptops matching your exact criteria. "
                    "Would you like to adjust your budget or requirements?"
                )
        
        # If we don't have enough information, ask for what's missing
        else:
            response_text = self._ask_for_missing_preferences(preferences)
        
        # Add bot response to conversation history
        conversation["messages"].append({
            "text": response_text,
            "sender": "bot",
            "timestamp": datetime.now().isoformat()
        })
        
        # Return chat response
        return ChatResponse(
            message=response_text,
            conversation_id=conversation_id,
            extracted_preferences=preferences
        )
    
    def _extract_preferences(self, message: str) -> Dict[str, Any]:
        """
        Extract user preferences from a message.
        
        Args:
            message: User message
            
        Returns:
            Dictionary of extracted preferences
        """
        preferences = {}
        
        # Extract budget
        for pattern in self.regex_patterns["budget"]:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                budget_str = match.group(1).replace(',', '')
                try:
                    preferences["budget"] = float(budget_str)
                    break
                except ValueError:
                    pass
        
        # Extract usage type
        for usage_type, patterns in self.regex_patterns["usage"].items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    preferences["usage_type"] = usage_type
                    break
            if "usage_type" in preferences:
                break
        
        # Extract brand preference
        brand_match = re.search(self.regex_patterns["brand"], message, re.IGNORECASE)
        if brand_match:
            brand = brand_match.group(1).lower()
            common_brands = ["dell", "hp", "lenovo", "asus", "acer", "apple", "microsoft", "msi", "razer"]
            if brand in common_brands:
                preferences["brand_preference"] = brand
        
        # Extract RAM requirement
        ram_match = re.search(self.regex_patterns["ram"], message, re.IGNORECASE)
        if ram_match:
            try:
                preferences["min_ram"] = int(ram_match.group(1))
            except ValueError:
                pass
        
        # Extract storage requirement
        storage_match = re.search(self.regex_patterns["storage"], message, re.IGNORECASE)
        if storage_match:
            try:
                storage_value = int(storage_match.group(1))
                # Convert to GB if specified in TB
                if "TB" in storage_match.group(0).upper():
                    storage_value *= 1000
                preferences["min_storage"] = storage_value
            except ValueError:
                pass
        
        # Extract GPU preference
        if re.search(r"(?:dedicated|good|gaming)\s+(?:GPU|graphics)", message, re.IGNORECASE):
            preferences["prefer_gpu"] = True
            
        return preferences
    
    def _is_greeting(self, message: str) -> bool:
        """Check if the message is a greeting."""
        for pattern in self.greeting_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        return False
    
    def _has_sufficient_preferences(self, preferences: Dict[str, Any]) -> bool:
        """
        Check if we have sufficient preferences to make recommendations.
        
        Args:
            preferences: Extracted user preferences
            
        Returns:
            True if we have enough information, False otherwise
        """
        # At minimum, we need budget and usage type
        return "budget" in preferences and "usage_type" in preferences
    
    def _ask_for_missing_preferences(self, preferences: Dict[str, Any]) -> str:
        """
        Generate a message asking for missing preferences.
        
        Args:
            preferences: Current preferences
            
        Returns:
            Message asking for missing information
        """
        if "budget" not in preferences:
            return "What's your budget for a new laptop?"
        
        if "usage_type" not in preferences:
            return f"Thanks for providing your budget (${preferences['budget']}). What will you primarily use this laptop for? (e.g., gaming, business, student, creative work, programming)"
        
        # If we have the basics but want to refine further
        if "brand_preference" not in preferences:
            return "Do you have a preferred brand? (e.g., Dell, HP, Lenovo, Asus, Apple)"
        
        # Fallback
        return "Can you tell me more about what you're looking for in a laptop? Any specific features that are important to you?"
    
    def _get_recommendations(self, preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get laptop recommendations based on preferences.
        
        Args:
            preferences: User preferences
            
        Returns:
            List of recommended laptops
        """
        # Convert to appropriate types
        budget = float(preferences.get("budget", 1000))
        usage_type = preferences.get("usage_type", UsageType.GENERAL)
        brand_preference = preferences.get("brand_preference")
        min_ram = preferences.get("min_ram")
        min_storage = preferences.get("min_storage")
        prefer_gpu = preferences.get("prefer_gpu", False)
        
        # Get recommendations
        return self.recommendation_engine.get_recommendations(
            budget=budget,
            usage_type=usage_type,
            brand_preference=brand_preference,
            min_ram=min_ram,
            min_storage=min_storage,
            prefer_gpu=prefer_gpu
        )
    
    def _format_recommendations(self, recommendations: List[Dict[str, Any]]) -> str:
        """
        Format recommendations into a readable string.
        
        Args:
            recommendations: List of recommended laptops
            
        Returns:
            Formatted string with recommendations
        """
        if not recommendations:
            return "No laptops found matching your criteria."
        
        result = ""
        for i, laptop in enumerate(recommendations, 1):
            result += f"{i}. {laptop['brand']} {laptop['model']}\n"
            result += f"   Price: ${laptop['price']:.2f}\n"
            result += f"   Specs: {laptop['processor']}, {laptop['ram']}GB RAM, {laptop['storage']}GB storage\n"
            if laptop.get('gpu') and laptop['gpu'] != "None":
                result += f"   GPU: {laptop['gpu']}\n"
            if laptop.get('battery_life'):
                result += f"   Battery: {laptop['battery_life']} hours\n"
            result += "\n"
        
        return result

