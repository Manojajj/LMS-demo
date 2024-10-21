from flask import Flask
from .models import db  # Importing db from models


def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object('config')

    # Initialize the database
    db.init_app(app)

    # Import routes here to avoid circular import
    from .routes import routes as routes_blueprint
    app.register_blueprint(routes_blueprint)

    # Create the database tables
    with app.app_context():
        db.create_all()  # Ensure all tables are created

    return app
