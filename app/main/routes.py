from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from app.main import main_blueprint, auth_blueprint
from app import database
from app.models import User, Feed, Category, Article, Bookmark, FeedForUser, FeedInCategory
import feedparser
from werkzeug.security import check_password_hash

# Home route
@main_blueprint.route("/")
def home():
    if current_user.is_authenticated:
        return render_template("home.html")
    else:
        return redirect(url_for("auth.login"))

# Route for user login
@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("main.home"))
        else:
            flash("Login failed. Check username and/or password.")
    
    return render_template("login.html")

# Route for user logout
@auth_blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

# Route to fetch and display articles for specific feed
@main_blueprint.route("/feed/<int:feed_id>/articles")
@login_required
def get_articles_for_feed(feed_id):
    feed = Feed.query.get_or_404(feed_id)
    feed_data = feedparser.parse(feed.url)

    articles = []
    for entry in feed_data.entries:
        article = {
            "title": entry.title,
            "link": entry.link,
            "summary": entry.summary,
            "published": entry.published
        }
        articles.append(article)
    
    return jsonify(articles)

# Route to fetch and display articles across all feeds
@main_blueprint.route("/articles")
@login_required
def get_all_articles():
    articles = Article.query.all()
    return jsonify([{
        "title": article.title,
        "link": article.link,
        "summary": article.url,
        "date": article.published
    } for article in articles])