from flask import Flask
from .extensions import db, login_manager, mail, migrate
from .main.routes import main
from .auth.routes import auth


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()

    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app
