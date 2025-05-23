from flask import Flask, render_template

def create_app():
    """
    Create and configure the Flask application for serving the frontend.
    """
    app = Flask(__name__, template_folder='templates', static_folder='static')

    @app.route('/')
    def index():
        """Render the dashboard page."""
        return render_template('dashboard.html')

    return app