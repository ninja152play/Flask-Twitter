from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@localhost:5432/twitter_db'
    #To prod postgresql://admin:admin@db:5432/twitter_db
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from .models import create_db

    def init_db():
        print("Инициализация базы данных")
        db.create_all()


    @app.cli.command("init-db")
    def init_once_per_process():
        """Команда для инициализации БД."""
        if not hasattr(g, "_db_initialized"):
            init_db()
            g._db_initialized = True
            print("База инициализирована.")

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    return app

