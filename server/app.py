from flask import Flask

# Import your blueprint from api/routes.py
# from api.routes import api_blueprint
from routes.agent_route import agent_blueprint
from routes.transcribe_route import transcribe_blueprint
from routes import agent_route
from routes import transcribe_route
def create_app():
    app = Flask(__name__)
    # app.config.from_object(Config)

    # If using database or other extensions, you could initialize them here
    # db.init_app(app)

    # Register the blueprint for your API routes
    app.register_blueprint(agent_route.agent_blueprint, url_prefix="/agent")
    # app.register_blueprint(transcribe_route.transcribe_blueprint, url_prefix="/transcribe")

    return app
