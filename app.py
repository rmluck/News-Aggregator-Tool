"""
Main application file.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

database = SQLAlchemy(app)

from models import User, Feed, Category, Article, Bookmark, FeedForUser, FeedInCategory

@app.route("/")
def home():
    return "Welcome to RSS Aggregator!"

if __name__ == "__main__":
    app.run(debug=True)