# AI-powered Laptop Recommendation System

A chatbot-based system that recommends laptops based on user preferences and budget constraints. The system uses natural language processing to understand user requirements and provides personalized laptop recommendations.

## Features

- Interactive chatbot interface to collect user preferences
- Natural language processing to understand user requirements
- Smart recommendation engine that filters and ranks laptops based on user criteria
- Comprehensive database of laptop specifications and prices
- RESTful API endpoints for programmatic access

## Project Structure

```
laptop-recommender/
├── data/               # Dataset and data processing scripts
├── docs/               # Documentation
├── src/                # Source code
│   ├── main.py         # FastAPI application entry point
│   ├── chatbot.py      # Chatbot logic
│   ├── recommendation_engine.py  # Recommendation system logic
│   ├── data_manager.py # Data handling utilities
│   └── models.py       # Data models and schemas
├── tests/              # Test files
├── .gitignore          # Git ignore file
├── README.md           # Project documentation
└── requirements.txt    # Project dependencies
```

## Installation

### Prerequisites

- Python 3.9+ (tested with Python 3.13)
- pip (Python package installer)

### Setup

1. Clone the repository

2. Create a virtual environment
   ```
   python -m venv venv
   ```

3. Activate the virtual environment
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required packages
   ```
   pip install -r requirements.txt
   ```

## Usage

### Running the API Server

```bash
cd src
uvicorn main:app --reload
```

The API server will be available at http://localhost:8000

### API Endpoints

- `GET /`: Welcome page
- `GET /health`: Health check endpoint
- `POST /api/chat`: Process chat messages
- `POST /api/recommendations`: Get recommendations based on preferences
- `GET /api/laptops`: List all available laptops
- `GET /api/laptops/{laptop_id}`: Get details of a specific laptop
- `GET /api/brands`: Get list of available laptop brands
- `GET /api/usage-types`: Get list of available usage types

### Chatbot Interaction

Start a conversation by sending a POST request to `/api/chat` with a message. The chatbot will extract preferences from your message and eventually provide laptop recommendations.

Example:
```json
{
  "message": "I need a gaming laptop under $1500",
  "conversation_id": null
}
```

## Deployment

To deploy and share your project, you can upload it to GitHub. Follow these steps:

1. **Initialize a Git Repository**
   - Navigate to the project root directory:
     ```
     cd C:\Users\BadvigBros\laptop-recommender
     ```
   - Initialize a git repository (if not already initialized):
     ```
     git init
     ```

2. **Commit Your Project Files**
   - Stage all your files:
     ```
     git add .
     ```
   - Commit your changes with an appropriate message:
     ```
     git commit -m "Initial commit of laptop recommendation project"
     ```

3. **Create a New Repository on GitHub**
   - Visit [GitHub New Repository](https://github.com/new) and create a new repository.
   - For example, name it `recommendation-agent` and do NOT initialize it with a README (since your project already contains one).

4. **Add the Remote Repository and Push Your Code**
   - Add your new GitHub repository as a remote (replace `yourusername` with your GitHub username):
     ```
     git remote add origin https://github.com/yourusername/recommendation-agent.git
     ```
   - Push your commits to GitHub (assuming your branch is `main`):
     ```
     git push -u origin main
     ```

5. **Verify Your Repository**
   - Visit your GitHub repository URL to see your project files.

For more information, refer to the [GitHub documentation](https://docs.github.com/en/get-started/quickstart/create-a-repo).

### Adding New Laptop Data

To add new laptop data, modify or replace the sample data in `data_manager.py`, or create a JSON file at `data/laptops.json` with the appropriate structure.

### Extending the Chatbot

The chatbot uses regular expressions for information extraction. To improve its capabilities, update the patterns in `chatbot.py`.

## License

MIT

