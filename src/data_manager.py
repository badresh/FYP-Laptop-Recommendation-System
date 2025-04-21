import os
import json
import csv
from typing import List, Dict, Optional, Any, Union
import uuid

from models import Laptop, LaptopBase

# Currency conversion utilities
class CurrencyConverter:
    """Utility class for currency conversion."""
    
    # Default conversion rates
    USD_TO_INR = 83.0
    
    @staticmethod
    def usd_to_inr(amount: Union[int, float]) -> float:
        """Convert USD to INR."""
        return amount * CurrencyConverter.USD_TO_INR
    
   

class DataManager:
    """
    Handles loading, processing, and managing laptop data for the recommendation system.
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the data manager.
        
        Args:
            data_path: Path to the data directory. If None, uses default paths.
        """
        self.data_path = data_path or os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        self.laptops: List[Dict[str, Any]] = []
        self._ensure_data_dir_exists()
        
    def _ensure_data_dir_exists(self):
        """Ensure data directory exists."""
        os.makedirs(self.data_path, exist_ok=True)
    
    def load_laptop_data(self) -> List[Dict[str, Any]]:
        """
        Load laptop data from JSON file. If no data file exists,
        returns a sample dataset for demonstration purposes.
        
        Returns:
            List of dictionaries containing laptop information
        """
        # Try loading from JSON
        json_path = os.path.join(self.data_path, "laptops.json")
        if os.path.exists(json_path):
            return self._load_from_json(json_path)
        
        # Create sample data file for testing if none exists
        return self._create_sample_data()
    
    def _load_from_json(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load laptop data from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            List of dictionaries containing laptop information
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            # Ensure each laptop has an ID
            for laptop in data:
                if 'id' not in laptop:
                    laptop['id'] = str(uuid.uuid4())
                    
            return data
            
        except Exception as e:
            print(f"Error loading JSON data: {e}")
            return self._create_sample_data()
    
    def _create_sample_data(self) -> List[Dict[str, Any]]:
        """
        Create a sample dataset for demonstration purposes.
        
        Returns:
            List of dictionaries containing sample laptop information
        """
        sample_data = [
            {
                "id": "1",
                "brand": "Dell", 
                "model": "XPS 13",
                "price": 1299,
                "processor": "Intel Core i7-1165G7",
                "ram": 16,
                "storage": 512,
                "gpu": None,
                "display": "13.4-inch FHD+ (1920 x 1200)",
                "battery_life": 12,
                "weight": 1.2,
                "os": "Windows 11"
            },
            {
                "id": "2",
                "brand": "Apple", 
                "model": "MacBook Air M2",
                "price": 1199,
                "processor": "Apple M2",
                "ram": 8,
                "storage": 256,
                "gpu": "Apple M2 GPU",
                "display": "13.6-inch Liquid Retina",
                "battery_life": 18,
                "weight": 1.24,
                "os": "macOS"
            }]
        """
        Create a sample dataset for demonstration purposes.
        
        Returns:
            List of dictionaries containing sample laptop information
        """
        # USD to INR conversion rate
        usd_to_inr = 83

        sample_data = [
            {
                "id": "1",
                "brand": "Dell", 
                "model": "XPS 13",
                "price": 107917,  # 1299 USD * 83
                "processor": "Intel Core i7-1165G7",
                "ram": 16,
                "storage": 512,
                "gpu": None,
                "display": "13.4-inch FHD+ (1920 x 1200)",
                "battery_life": 12,
                "weight": 1.2,
                "os": "Windows 11",
                "currency": "INR"
            },
            {
                "id": "2",
                "brand": "Apple", 
                "model": "MacBook Air M2",
                "price": 99517,  # 1199 USD * 83
                "processor": "Apple M2",
                "ram": 8,
                "storage": 256,
                "gpu": "Apple M2 GPU",
                "display": "13.6-inch Liquid Retina",
                "battery_life": 18,
                "weight": 1.24,
                "os": "macOS",
                "currency": "INR"
            },
            {
                "id": "3",
                "brand": "HP", 
                "model": "Spectre x360",
                "price": 116117,  # 1399 USD * 83
                "processor": "Intel Core i7-1255U",
                "ram": 16,
                "storage": 1000,
                "gpu": "Intel Iris Xe",
                "display": "14-inch 3K2K OLED",
                "battery_life": 10,
                "weight": 1.36,
                "os": "Windows 11",
                "currency": "INR"
            },
            {
                "id": "4",
                "brand": "Lenovo", 
                "model": "ThinkPad X1 Carbon",
                "price": 124417,  # 1499 USD * 83
                "processor": "Intel Core i7-1270P",
                "ram": 16,
                "storage": 512,
                "gpu": None,
                "display": "14-inch WUXGA IPS",
                "battery_life": 14,
                "weight": 1.12,
                "os": "Windows 11",
                "currency": "INR"
            },
            {
                "id": "5",
                "brand": "Asus", 
                "model": "ROG Zephyrus G14",
                "price": 136867,  # 1649 USD * 83
                "processor": "AMD Ryzen 9 6900HS",
                "ram": 16,
                "storage": 1000,
                "gpu": "NVIDIA RTX 3060",
                "display": "14-inch QHD 120Hz",
                "battery_life": 8,
                "weight": 1.6,
                "os": "Windows 11",
                "currency": "INR"
            },
            {
                "id": "6",
                "brand": "Acer", 
                "model": "Swift 5",
                "price": 91217,  # 1099 USD * 83
                "processor": "Intel Core i7-1165G7",
                "ram": 16,
                "storage": 512,
                "gpu": "Intel Iris Xe Graphics",
                "display": "14-inch FHD IPS",
                "battery_life": 10,
                "weight": 1.05,
                "os": "Windows 11",
                "currency": "INR"
            },
            {
                "id": "7",
                "brand": "MSI", 
                "model": "GS66 Stealth",
                "price": 157617,  # 1899 USD * 83
                "processor": "Intel Core i9-12900H",
                "ram": 32,
                "storage": 1000,
                "gpu": "NVIDIA RTX 3070",
                "display": "15.6-inch FHD 360Hz",
                "battery_life": 6,
                "weight": 2.1,
                "os": "Windows 11",
                "currency": "INR"
            },
            {
                "id": "8",
                "brand": "Microsoft", 
                "model": "Surface Laptop 4",
                "price": 107917,  # 1299 USD * 83
                "processor": "AMD Ryzen 5 4680U",
                "ram": 8,
                "storage": 256,
                "gpu": "AMD Radeon Graphics",
                "display": "13.5-inch PixelSense",
                "battery_life": 19,
                "weight": 1.3,
                "os": "Windows 11",
                "currency": "INR"
            },
            {
                "id": "9",
                "brand": "Razer",
                "model": "Blade 15",
                "price": 182517,  # 2199 USD * 83
                "processor": "Intel Core i7-12800H",
                "ram": 16,
                "storage": 1000,
                "gpu": "NVIDIA RTX 3080",
                "display": "15.6-inch QHD 240Hz",
                "battery_life": 5,
                "weight": 2.0,
                "os": "Windows 11",
                "currency": "INR"
            },
            {
                "id": "10",
                "brand": "LG",
                "model": "Gram 17",
                "price": 132717,  # 1599 USD * 83
                "processor": "Intel Core i7-1260P",
                "ram": 16,
                "storage": 512,
                "gpu": "Intel Iris Xe Graphics",
                "display": "17-inch WQXGA",
                "battery_life": 20,
                "weight": 1.35,
                "os": "Windows 11",
                "currency": "INR"
            }]
        try:
            json_path = os.path.join(self.data_path, "laptops.json")
            with open(json_path, 'w') as f:
                json.dump(laptops, f, indent=4)
        except Exception as e:
            print(f"Error saving laptop data: {e}")
        
        return Laptop(**new_laptop)
    
    def get_laptop_by_id(self, laptop_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a laptop by its ID.
        
        Args:
            laptop_id: ID of the laptop to retrieve
            
        Returns:
            Laptop data or None if not found
        """
        laptops = self.load_laptop_data()
        for laptop in laptops:
            if laptop.get("id") == laptop_id:
                return laptop
        return None
