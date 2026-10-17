from flask import request, g

# placeholder middleware example

def simple_middleware(app):
    @app.before_request
    def attach_request_id():
        g.request_id = request.headers.get('X-Request-Id')
