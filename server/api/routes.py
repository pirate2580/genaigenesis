from flask import Blueprint, jsonify, request

api_blueprint = Blueprint("api", __name__)

@api_blueprint.route("/", methods=["GET"])
def home():
    """
    A simple API home endpoint to verify that the service is up.
    Example: GET /api/
    """
    return jsonify({"message": "Welcome to the API!"})

@api_blueprint.route("/users", methods=["GET"])
def get_users():
    """
    Dummy route to demonstrate retrieving a list of users.
    Example: GET /api/users
    """
    # In a real app, you'd probably call a service or query the database
    dummy_users = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]
    return jsonify(dummy_users), 200

@api_blueprint.route("/users", methods=["POST"])
def create_user():
    """
    Dummy route to demonstrate creating a new user.
    Example: POST /api/users
    {
      "name": "Charlie"
    }
    """
    data = request.get_json()
    name = data.get("name")
    if not name:
        return jsonify({"error": "Name is required"}), 400

    # In a real app, you'd save to the database and return the new user
    new_user = {"id": 3, "name": name}
    return jsonify(new_user), 201
