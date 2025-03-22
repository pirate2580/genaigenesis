# This file starts the Flask server using the app factory pattern
from app import create_app

app = create_app()

if __name__ == "__main__":
    # Default is http://127.0.0.1:5000
    app.run()
