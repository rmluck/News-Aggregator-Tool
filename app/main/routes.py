from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from app.main import main_blueprint, auth_blueprint
from app import database
from app.models import User, Feed, Category, Article, Bookmark, FeedForUser, FeedInCategory
import feedparser
from werkzeug.security import check_password_hash, generate_password_hash
import re

# Home route
@main_blueprint.route("/")
def home():
    if current_user.is_authenticated:
        user_feeds = FeedForUser.query.filter_by(user_id=current_user.id).all()
        feeds = []

        for feed_for_user in user_feeds:
            feeds.append((feed_for_user, feed_for_user.feed))

        return render_template("home.html", feeds=feeds)
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

# Route for account registration
@auth_blueprint.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]

        email_regex = r"[^@]+@[^@]+\.[^@]+"
        if not re.match(email_regex, email):
            flash("Invalid email format.")
            return redirect(url_for("auth.register"))

        existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            flash("Email or username already exists. Please log in.")
            return redirect(url_for("auth.register"))
        
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = User(email=email, username=username, password_hash=hashed_password)

        database.session.add(new_user)
        database.session.commit()

        login_user(new_user)
        flash("Account created successfully.")
        return redirect(url_for("main.home"))
    
    return render_template("register.html")

# Route for user logout
@auth_blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

# Route to add new feed
@main_blueprint.route("/add_feed", methods=["POST"])
@login_required
def add_feed():
    rss_url = request.form.get("rss_url")

    feed_data = feedparser.parse(rss_url)
    if feed_data.bozo:
        flash("Invalid RSS feed URL. Please try again.")
        return redirect(url_for("main.home"))
    
    existing_feed = Feed.query.filter_by(url=rss_url).first()
    if not existing_feed:
        feed_title = feed_data.feed.title
        feed_url = rss_url
        feed_description = feed_data.feed.description.strip() if getattr(feed_data.feed, "description", "").strip() else "N/A"

        new_feed = Feed(url=rss_url, title=feed_title, description=feed_description)
        database.session.add(new_feed)
        database.session.commit()
        flash(f"Added feed: {feed_data.feed.title}")
    else:
        new_feed = existing_feed

    user_feed = FeedForUser.query.filter_by(feed_id=new_feed.id, user_id=current_user.id).first()
    if not user_feed:
        user_feed = FeedForUser(feed_id=new_feed.id, user_id=current_user.id)
        database.session.add(user_feed)
        database.session.commit()
        flash(f"Feed successfully added to your account.")
    else:
        flash(f"Feed already added to your account.")
    
    return redirect(url_for("main.home"))

# Route to edit feed information
@main_blueprint.route("/feed/<int:feed_id>/edit_feed", methods=["GET", "POST"])
@login_required
def edit_feed(feed_id):
    feed = Feed.query.get_or_404(feed_id)
    feed_for_user = FeedForUser.query.filter_by(user_id=current_user.id, feed_id=feed.id).first()

    if request.method == "POST":
        custom_title = request.form.get("custom_feed_title")
        custom_description = request.form.get("custom_feed_description")

        if feed_for_user:
            if custom_title:
                feed_for_user.custom_title = custom_title
            if custom_description:
                feed_for_user.custom_description = custom_description
            database.session.commit()
            flash("Feed information updated successfully.")
        else:
            flash("Feed not associated with this user.")
        
        return redirect(url_for("main.home"))
    
    return render_template("edit_feed.html", feed=feed, feed_for_user=feed_for_user)


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