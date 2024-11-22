"""
Defines SQLAlchemy models corresponding to database tables.
"""

from app import database as db
from flask_login import UserMixin

# Users table
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)

    feeds = db.relationship("FeedForUser", back_populates="user", lazy=True)
    categories = db.relationship("Category", back_populates="user", lazy=True)
    bookmarks = db.relationship("Bookmark", back_populates="user", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

    @staticmethod
    def get(user_id):
        return User.query.get(int(user_id))

# Feeds table
class Feed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(512), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    users = db.relationship("FeedForUser", back_populates="feed", lazy=True)
    categories = db.relationship("FeedInCategory", back_populates="feed", lazy=True)
    articles = db.relationship("Article", back_populates="feed", lazy=True)

# Categories table
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)

    user = db.relationship("User", back_populates="categories")
    feeds = db.relationship("FeedInCategory", back_populates="category", lazy=True)

# Feed in category table
class FeedInCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feed_id = db.Column(db.Integer, db.ForeignKey("feed.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)

    feed = db.relationship("Feed", back_populates="categories")
    category = db.relationship("Category", back_populates="feeds")

# Articles table
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feed_id = db.Column(db.Integer, db.ForeignKey("feed.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.Text)
    date = db.Column(db.DateTime)
    url = db.Column(db.String(512), nullable=False)

    feed = db.relation("Feed", back_populates="articles")

# Bookmarks table
class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey("article.id"), nullable=False)

    user = db.relationship("User", back_populates="bookmarks")
    article = db.relationship("Article")

# Feed for user table
class FeedForUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    feed_id = db.Column(db.Integer, db.ForeignKey("feed.id"), nullable=False)

    user = db.relationship("User", back_populates="feeds")
    feed = db.relationship("Feed", back_populates="users")