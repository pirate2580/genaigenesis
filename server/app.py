from flask import Flask
from config import Config

# Import your blueprint from api/routes.py
from api.routes import api_blueprint

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # If using database or other extensions, you could initialize them here
    # db.init_app(app)

    # Register the blueprint for your API routes
    app.register_blueprint(api_blueprint, url_prefix="/api")

    return app
