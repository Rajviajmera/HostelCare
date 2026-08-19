# this is my initial folder
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return db.session.get(User, int(user_id))

    from app.routes import main

    app.register_blueprint(main)

    #with app.app_context():
    #   db.create_all()

    return app
