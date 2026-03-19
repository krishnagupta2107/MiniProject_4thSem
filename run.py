"""
run.py
Entry point for the Flask development server.
Run with: python run.py
"""

from app import create_app
from config import Config

app = create_app(Config)

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=Config.PORT,
        debug=Config.DEBUG,
    )
