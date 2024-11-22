from app import database, app

with app.app_context():
    database.create_all()
    print("Database tables created successfully")