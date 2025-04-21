import json
from recommendation_engine import RecommendationEngine
from models import UsageType

# Load dataset
with open("laptop_dataset.json", "r") as f:
    laptop_data = json.load(f)

# Initialize the recommendation engine
engine = RecommendationEngine(laptop_data)

# Example user preferences
budget = 80000  # INR or USD depending on your dataset
usage_type = UsageType.STUDENT
brand_preference = "Dell"
min_ram = 8
min_storage = 256
prefer_gpu = False

# Get recommendations
recommendations = engine.get_recommendations(
    budget=budget,
    usage_type=usage_type,
    brand_preference=brand_preference,
    min_ram=min_ram,
    min_storage=min_storage,
    prefer_gpu=prefer_gpu,
    limit=5
)

# Print results
for idx, laptop in enumerate(recommendations, 1):
    print(f"{idx}. {laptop['brand']} - {laptop['model']} | Score: {round(laptop['score'], 2)}")
