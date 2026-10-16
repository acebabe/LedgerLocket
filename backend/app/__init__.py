from flask import Flask
from .extensions import db, migrate, socketio
from .routes import bp as routes_bp
from .receipts import bp as receipts_bp
from .auth import bp as auth_bp
from .notifications import bp as notifications_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins="*")

    app.register_blueprint(routes_bp)
    app.register_blueprint(receipts_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(notifications_bp, url_prefix='/ws')

    return app
