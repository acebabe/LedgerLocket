from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_socketio import SocketIO

from config import Config
from models import db

socketio = SocketIO(cors_allowed_origins="*", async_mode="eventlet")
migrate = Migrate()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    socketio.init_app(app)
    CORS(app)

    from routes.auth import bp as auth_bp
    from routes.wallets import bp as wallets_bp
    from routes.transactions import bp as tx_bp
    from routes.notifications import bp as notif_bp
    from receipts.receipt_routes import bp as receipt_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(wallets_bp, url_prefix="/wallets")
    app.register_blueprint(tx_bp, url_prefix="/transactions")
    app.register_blueprint(notif_bp, url_prefix="/notifications")
    app.register_blueprint(receipt_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
