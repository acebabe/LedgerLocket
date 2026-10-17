from flask import jsonify


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error':'not_found'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error':'internal_server_error'}), 500
