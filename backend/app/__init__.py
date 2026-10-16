from flask import Flask
from .extensions import db, migrate
from .routes import bp as routes_bp
from .receipts import bp as receipts_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(routes_bp)
    app.register_blueprint(receipts_bp)

    return app
