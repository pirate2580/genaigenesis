from flask import Flask

# Import your blueprint from api/routes.py
# from api.routes import api_blueprint
from routes.agent_route import api_blueprint
from routes import agent_route
def create_app():
    app = Flask(__name__)
    # app.config.from_object(Config)

    # If using database or other extensions, you could initialize them here
    # db.init_app(app)

    # Register the blueprint for your API routes
    app.register_blueprint(agent_route.api_blueprint, url_prefix="/agent")

    return app
