from flask import Flask, request, jsonify, render_template, abort
import os
import logging
import json
import importlib.metadata
from datetime import datetime
from pathlib import Path

# Import models
from models import Laptop, LaptopResponse, UserPreference, ChatRequest, ChatResponse, UsageType

# Import application components
from data_manager import DataManager
from recommendation_engine import RecommendationEngine
from chatbot import ChatBot

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("laptop-recommender")

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Initialize data manager and load data
data_manager = DataManager()
laptop_data = data_manager.load_laptop_data()
logger.info(f"Loaded {len(laptop_data)} laptops from data store")

# Initialize recommendation engine
recommendation_engine = RecommendationEngine(laptop_data)

# Initialize chatbot
chatbot = ChatBot(recommendation_engine)

# Helper functions for response handling
def serialize_model(obj):
    """Convert Pydantic models to dictionaries for Flask's jsonify."""
    if hasattr(obj, 'dict'):
        return obj.dict()
    elif isinstance(obj, list):
        return [serialize_model(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: serialize_model(v) for k, v in obj.items()}
    elif isinstance(obj, UsageType):
        return obj.value
    return obj

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"detail": str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"detail": "Resource not found"}), 404

@app.errorhandler(500)
def internal_server_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({"detail": "An internal server error occurred"}), 500

# Routes
@app.route("/", methods=["GET"])
def root():
    """Root endpoint returning welcome message."""
    return jsonify({
        "message": "Welcome to the Laptop Recommendation API",
        "documentation": "/docs"
    })

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    try:
        flask_version = importlib.metadata.version('flask')
    except:
        flask_version = "unknown"
        
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "flask_version": flask_version
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Process a chat message and return a response.
    
    Request body:
        message: User message text
        conversation_id: Optional conversation ID
    """
    try:
        data = request.json
        if not data or not isinstance(data, dict):
            return jsonify({"detail": "Invalid request body"}), 400
            
        if "message" not in data:
            return jsonify({"detail": "Message field is required"}), 400
            
        chat_request = ChatRequest(
            message=data["message"],
            conversation_id=data.get("conversation_id")
        )
        
        response = chatbot.process_message(chat_request)
        return jsonify(serialize_model(response))
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        return jsonify({"detail": str(e)}), 500

@app.route("/api/recommendations", methods=["POST"])
def get_recommendations():
    """
    Get laptop recommendations based on explicit preferences.
    
    Request body:
        UserPreference object with:
            budget: Maximum budget
            usage_type: Primary usage type
            brand_preference: Optional preferred brand
            min_ram: Optional minimum RAM
            min_storage: Optional minimum storage
            prefer_gpu: Optional GPU preference
    """
    try:
        data = request.json
        if not data or not isinstance(data, dict):
            return jsonify({"detail": "Invalid request body"}), 400
            
        if "budget" not in data or "usage_type" not in data:
            return jsonify({"detail": "Budget and usage_type are required fields"}), 400
            
        try:
            # Validate usage_type
            usage_type = UsageType(data["usage_type"])
            data["usage_type"] = usage_type
        except ValueError:
            valid_types = [t.value for t in UsageType]
            return jsonify({
                "detail": f"Invalid usage_type. Must be one of: {', '.join(valid_types)}"
            }), 400
            
        try:
            preferences = UserPreference(**data)
        except Exception as e:
            return jsonify({"detail": f"Invalid preferences: {str(e)}"}), 400
            
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
        
        response = LaptopResponse(
            recommendations=laptop_models,
            count=len(laptop_models),
            message=f"Found {len(laptop_models)} laptops matching your criteria."
        )
        
        return jsonify(serialize_model(response))
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return jsonify({"detail": str(e)}), 500

@app.route("/api/laptops", methods=["GET"])
def get_all_laptops():
    """
    Get all available laptops, optionally filtered by brand.
    
    Query parameters:
        limit: Maximum number of laptops to return (default: 50)
        brand: Optional brand filter
    """
    try:
        limit = request.args.get("limit", 50, type=int)
        if limit <= 0 or limit > 100:
            limit = 50
            
        brand = request.args.get("brand")
        
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
        laptop_models = [Laptop(**laptop) for laptop in limited_data]
        
        return jsonify(serialize_model(laptop_models))
        
    except Exception as e:
        logger.error(f"Error getting all laptops: {e}")
        return jsonify({"detail": str(e)}), 500

@app.route("/api/laptops/<laptop_id>", methods=["GET"])
def get_laptop_by_id(laptop_id):
    """
    Get a specific laptop by its ID.
    
    Path parameters:
        laptop_id: ID of the laptop to retrieve
    """
    try:
        laptop = data_manager.get_laptop_by_id(laptop_id)
        if not laptop:
            return jsonify({"detail": f"Laptop with ID {laptop_id} not found"}), 404
        
        laptop_model = Laptop(**laptop)
        return jsonify(serialize_model(laptop_model))
        
    except Exception as e:
        logger.error(f"Error getting laptop {laptop_id}: {e}")
        return jsonify({"detail": str(e)}), 500

@app.route("/api/brands", methods=["GET"])
def get_available_brands():
    """Get a list of all available laptop brands."""
    try:
        # Extract unique brands
        brands = list(set(laptop["brand"] for laptop in laptop_data if "brand" in laptop))
        return jsonify({"brands": sorted(brands)})
        
    except Exception as e:
        logger.error(f"Error getting brands: {e}")
        return jsonify({"detail": str(e)}), 500

@app.route("/api/usage-types", methods=["GET"])
def get_usage_types():
    """Get all available usage types for laptops."""
    usage_descriptions = {
        UsageType.GAMING: "High-performance laptops for playing modern games",
        UsageType.BUSINESS: "Professional laptops for office and business tasks",
        UsageType.STUDENT: "Affordable and portable laptops for students",
        UsageType.CREATIVE: "Laptops for designers, video editors and creative professionals",
        UsageType.PROGRAMMING: "Laptops optimized for software development",
        UsageType.GENERAL: "Well-balanced laptops for everyday tasks"
    }
    
    usage_types = [
        {
            "value": usage_type.value, 
            "name": usage_type.name.title(), 
            "description": usage_descriptions.get(usage_type, "")
        }
        for usage_type in UsageType
    ]
    
    return jsonify({"usage_types": usage_types})

@app.route("/api/conversations/<conversation_id>/history", methods=["GET"])
def get_conversation_history(conversation_id):
    """
    Get the history of messages in a conversation.
    
    Path parameters:
        conversation_id: ID of the conversation
    """
    try:
        if conversation_id not in chatbot.conversations:
            return jsonify({"detail": f"Conversation {conversation_id} not found"}), 404
        
        return jsonify({
            "conversation_id": conversation_id,
            "messages": chatbot.conversations[conversation_id]["messages"],
            "preferences": chatbot.conversations[conversation_id]["preferences"]
        })
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        return jsonify({"detail": str(e)}), 500

@app.route("/api/conversations/<conversation_id>", methods=["DELETE"])
def delete_conversation(conversation_id):
    """
    Delete a conversation.
    
    Path parameters:
        conversation_id: ID of the conversation to delete
    """
    try:
        if conversation_id not in chatbot.conversations:
            return jsonify({"detail": f"Conversation {conversation_id} not found"}), 404
        
        del chatbot.conversations[conversation_id]
        return jsonify({
            "status": "success", 
            "message": f"Conversation {conversation_id} deleted"
        })
        
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        return jsonify({"detail": str(e)}), 500

# Simple template for a basic web interface
@app.route("/ui", methods=["GET"])
def ui():
    """Simple web interface for the chatbot."""
    return render_template("index.html")

# Function to set up template and static directories
def setup_dirs():
    """Set up template and static directories."""
    # Create templates directory and index.html if it doesn't exist
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    os.makedirs(template_dir, exist_ok=True)
    
    index_file = os.path.join(template_dir, "index.html")
    if not os.path.exists(index_file):
        with open(index_file, 'w') as f:
            f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Laptop Recommendation Chatbot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .chat-container {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            height: 400px;
            overflow-y: auto;
            margin-bottom: 20px;
            background-color: #f9f9f9;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 8px;
        }
        .user-message {
            background-color: #e3f2fd;
            margin-left: 50px;
            text-align: right;
        }
        .bot-message {
            background-color: #f1f1f1;
            margin-right: 50px;
        }
        .input-container {
            display: flex;
        }
        #message-input {
            flex-grow: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            margin-left: 10px;
            border-radius: 4px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <h1>AI-powered Laptop Recommendation Chatbot</h1>
    <div class="chat-container" id="chat-container">
        <div class="message bot-message">
            Hello! I'm your laptop recommendation assistant. I can help you find the perfect laptop based on your needs. Let's start with your budget. How much are you looking to spend?
        </div>
    </div>
    <form class="input-container" id="chat-form">
        <input type="text" id="message-input" placeholder="Type your message here..." required>
        <button type="submit">Send</button>
    </form>

    <script>
        let conversationId = null;
        
        document.getElementById('chat-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const messageInput = document.getElementById('message-input');
            const message = messageInput.value;
            if (!message) return;
            
            // Add user message to chat
            addMessage(message, 'user-message');
            
            // Clear input
            messageInput.value = '';
            
            try {
                // Send message to server
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        conversation_id: conversationId
                    })
                });
                
                const data = await response.json();
                
                // Store conversation ID for future messages
                if (data.conversation_id) {
                    conversationId = data.conversation_id;
                }
                
                // Add bot response to chat
                addMessage(data.message, 'bot-message');
                
                // If there are recommendations, show them
                if (data.recommendations && data.recommendations.length > 0) {
                    const recsEl = document.createElement('div');
                    recsEl.className = 'recommendations';
                    recsHtml = '<strong>Recommendations:</strong><ul>';
                    
                    for (let i = 0; i < data.recommendations.length; i++) {
                        const rec = data.recommendations[i];
                        recsHtml += `<li>
                            <strong>${rec.brand} ${rec.model}</strong><br>
                            Price: $${rec.price}<br>
                            Specs: ${rec.processor}, ${rec.ram}GB RAM, ${rec.storage}GB storage
                            ${rec.gpu ? '<br>GPU: ' + rec.gpu : ''}
                        </li>`;
                    }
                    
                    recsHtml += '</ul>';
                    recsEl.innerHTML = recsHtml;
                    document.getElementById('chat-container').appendChild(recsEl);
                }
                
            } catch (error) {
                console.error('Error:', error);
                addMessage('Sorry, there was an error processing your request.', 'bot-message');
            }
        });
        
        function addMessage(text, className) {
            const chatContainer = document.getElementById('chat-container');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${className}`;
            messageDiv.textContent = text;
            chatContainer.appendChild(messageDiv);
            
            // Scroll to bottom
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    </script>
</body>
</html>
        ''')

# Add main execution block
if __name__ == "__main__":
    # Set up required directories and files before starting the app
    setup_dirs()
    
    # Create static directory if it doesn't exist
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    os.makedirs(static_dir, exist_ok=True)
    
    # Announce the application startup
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("DEBUG", "False").lower() == "true"
    
    print(f"Starting Flask application on http://localhost:{port}")
    print(f"Debug mode: {debug_mode}")
    print("Press Ctrl+C to quit")
    
    # Run the application
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
