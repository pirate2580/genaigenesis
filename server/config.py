import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    DEBUG = True
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    # Example of a database URI if you decide to add a database
    # SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///example.db")