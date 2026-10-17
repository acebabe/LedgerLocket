"""
Application factory and top-level app package initialization.
"""
from flask import Flask
from config import Config
from app.extensions import db, migrate, mail


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # register blueprints
    from app.api.router import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # health
    @app.route('/health')
    def health():
        return {'status':'ok'}

    return app
