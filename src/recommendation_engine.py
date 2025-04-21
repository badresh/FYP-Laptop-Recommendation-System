from typing import List, Dict, Optional, Any
from models import UsageType

class RecommendationEngine:
    """
    Engine responsible for recommending laptops based on user preferences.
    """
    
    def __init__(self, laptop_data: List[Dict[str, Any]]):
        """
        Initialize the recommendation engine with laptop data.
        
        Args:
            laptop_data: List of dictionaries containing laptop specifications
        """
        self.laptop_data = laptop_data
        
        # Define usage to hardware requirements mapping
        self.usage_requirements = {
            UsageType.GAMING: {
                "min_ram": 16,
                "min_storage": 512,
                "gpu_required": True,
                "processor_keywords": ["i7", "i9", "ryzen 7", "ryzen 9"],
                "importance": {
                    "gpu": 0.4,
                    "processor": 0.3,
                    "ram": 0.2,
                    "display": 0.1
                }
            },
            UsageType.BUSINESS: {
                "min_ram": 8,
                "min_storage": 256,
                "min_battery_life": 8,
                "processor_keywords": ["i5", "i7", "ryzen 5", "ryzen 7"],
                "importance": {
                    "battery_life": 0.4,
                    "weight": 0.3,
                    "processor": 0.2,
                    "ram": 0.1
                }
            },
            UsageType.STUDENT: {
                "min_ram": 8,
                "min_storage": 256,
                "min_battery_life": 6,
                "processor_keywords": ["i3", "i5", "ryzen 3", "ryzen 5"],
                "importance": {
                    "price": 0.4,
                    "battery_life": 0.3,
                    "weight": 0.2,
                    "storage": 0.1
                }
            },
            UsageType.CREATIVE: {
                "min_ram": 16,
                "min_storage": 512,
                "gpu_required": True,
                "processor_keywords": ["i7", "i9", "ryzen 7", "ryzen 9"],
                "importance": {
                    "display": 0.4,
                    "gpu": 0.3,
                    "ram": 0.2,
                    "processor": 0.1
                }
            },
            UsageType.PROGRAMMING: {
                "min_ram": 16,
                "min_storage": 512,
                "processor_keywords": ["i5", "i7", "ryzen 5", "ryzen 7"],
                "importance": {
                    "processor": 0.4,
                    "ram": 0.3, 
                    "battery_life": 0.2,
                    "storage": 0.1
                }
            },
            UsageType.GENERAL: {
                "min_ram": 8,
                "min_storage": 256,
                "processor_keywords": ["i5", "i7", "ryzen 5"],
                "importance": {
                    "price": 0.4,
                    "battery_life": 0.3,
                    "processor": 0.2,
                    "ram": 0.1
                }
            }
        }
    
    def get_recommendations(self, 
                          budget: float, 
                          usage_type: UsageType, 
                          brand_preference: Optional[str] = None,
                          min_ram: Optional[int] = None,
                          min_storage: Optional[int] = None,
                          prefer_gpu: bool = False,
                          limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get laptop recommendations based on user preferences.
        
        Args:
            budget: Maximum budget in dollars
            usage_type: Type of use (gaming, business, etc.)
            brand_preference: Preferred brand (optional)
            min_ram: Minimum RAM in GB (optional)
            min_storage: Minimum storage in GB (optional)
            prefer_gpu: Whether a dedicated GPU is preferred
            limit: Maximum number of recommendations to return
            
        Returns:
            List of recommended laptops as dictionaries
        """
        # Filter laptops based on preferences
        filtered_laptops = self._filter_laptops(
            budget=budget,
            usage_type=usage_type,
            brand_preference=brand_preference,
            min_ram=min_ram,
            min_storage=min_storage,
            prefer_gpu=prefer_gpu
        )
        
        # If no laptops match the criteria, relax constraints slightly
        if not filtered_laptops:
            filtered_laptops = self._filter_laptops(
                budget=budget * 1.1,  # Allow 10% higher budget
                usage_type=usage_type,
                brand_preference=None,  # Ignore brand preference
                min_ram=self.usage_requirements[usage_type].get("min_ram", 4),
                min_storage=self.usage_requirements[usage_type].get("min_storage", 128),
                prefer_gpu=prefer_gpu
            )
            
        # Score and rank the laptops
        scored_laptops = self._score_laptops(filtered_laptops, usage_type, budget)
        
        # Return top recommendations
        return scored_laptops[:limit]
        
    def _filter_laptops(self,
                       budget: float,
                       usage_type: UsageType,
                       brand_preference: Optional[str] = None,
                       min_ram: Optional[int] = None,
                       min_storage: Optional[int] = None,
                       prefer_gpu: bool = False) -> List[Dict[str, Any]]:
        """
        Filter laptops based on user preferences.
        
        Args:
            Same as get_recommendations
            
        Returns:
            List of laptops that match the criteria
        """
        # Get usage requirements
        usage_reqs = self.usage_requirements.get(usage_type, self.usage_requirements[UsageType.GENERAL])
        
        # Set default values from usage requirements if not specified
        if min_ram is None:
            min_ram = usage_reqs.get("min_ram", 4)
        if min_storage is None:
            min_storage = usage_reqs.get("min_storage", 128)
        
        # Filter by budget
        results = [laptop for laptop in self.laptop_data if laptop["price"] <= budget]
        
        # Filter by RAM
        results = [laptop for laptop in results if laptop["ram"] >= min_ram]
        
        # Filter by storage
        results = [laptop for laptop in results if laptop["storage"] >= min_storage]
        
        # Filter by brand if specified
        if brand_preference:
            results = [laptop for laptop in results if laptop["brand"].lower() == brand_preference.lower()]
        
        # Filter by GPU if required by usage type or preferred by user
        if usage_reqs.get("gpu_required", False) or prefer_gpu:
            results = [laptop for laptop in results if laptop.get("gpu") and laptop.get("gpu") != "None"]
        
        return results
    
    def _score_laptops(self, laptops: List[Dict[str, Any]], usage_type: UsageType, budget: float) -> List[Dict[str, Any]]:
        """
        Score and rank laptops based on usage preferences.
        
        Args:
            laptops: List of laptops to score
            usage_type: Type of usage for weighting features
            budget: Maximum budget for price efficiency scoring
            
        Returns:
            List of laptops sorted by score
        """
        if not laptops:
            return []
            
        # Get importance weights for this usage type
        importance = self.usage_requirements.get(usage_type, self.usage_requirements[UsageType.GENERAL])["importance"]
        
        # Calculate scores for each laptop
        scored_laptops = []
        for laptop in laptops:
            score = 0
            
            # Price efficiency score (higher is better)
            price_efficiency = 1 - (laptop["price"] / budget)
            score += importance.get("price", 0.25) * price_efficiency
            
            # RAM score
            ram_score = min(1.0, laptop["ram"] / 32)  # Normalize up to 32GB
            score += importance.get("ram", 0.15) * ram_score
            
            # Storage score
            storage_score = min(1.0, laptop["storage"] / 1000)  # Normalize up to 1TB
            score += importance.get("storage", 0.1) * storage_score
            
            # Processor score - based on keyword matching
            processor_keywords = self.usage_requirements.get(usage_type, self.usage_requirements[UsageType.GENERAL]).get("processor_keywords", [])
            processor_score = 0
            for keyword in processor_keywords:
                if keyword.lower() in laptop["processor"].lower():
                    processor_score = 1.0
                    break
            score += importance.get("processor", 0.2) * processor_score
            
            # GPU score
            if importance.get("gpu", 0) > 0:
                gpu_score = 1.0 if laptop.get("gpu") and laptop.get("gpu") != "None" else 0
                score += importance.get("gpu", 0) * gpu_score
            
            # Battery life score
            if "battery_life" in laptop and laptop["battery_life"] is not None:
                battery_score = min(1.0, laptop["battery_life"] / 15)  # Normalize up to 15 hours
                score += importance.get("battery_life", 0.1) * battery_score
            
            # Weight score (lower is better)
            if "weight" in laptop and laptop["weight"] is not None:
                weight_score = 1 - min(1.0, laptop["weight"] / 3)  # Normalize up to 3kg, but reverse (lower is better)
                score += importance.get("weight", 0.1) * weight_score
            
            # Add score to laptop object
            scored_laptop = laptop.copy()
            scored_laptop["score"] = score
            scored_laptops.append(scored_laptop)
        
        # Sort laptops by score (descending)
        return sorted(scored_laptops, key=lambda x: x["score"], reverse=True)
    

    # Inside recommendation_engine.py
from evaluation import evaluate_model

# Example function call - this should be replaced with real usage
def example_recommendation_and_evaluation():
    # Sample data (Replace these with actual labels and predictions)
    y_true = [0, 1, 0, 1, 1, 0, 1, 0]
    y_pred = [0, 1, 0, 0, 1, 0, 1, 1]
    y_scores = [0.1, 0.9, 0.2, 0.4, 0.85, 0.1, 0.75, 0.3]

    evaluate_model(y_true, y_pred, y_scores)

# You should call example_recommendation_and_evaluation() only as an example, 
# Ideally, locate where your recommendations are being made and pass the real data to evaluate_model
