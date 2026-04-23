import os
import threading
from pathlib import Path

from flask import Flask

from dashboard.routes.api import api_bp, set_trader
from dashboard.routes.broker import broker_bp, set_broker_trader
from dashboard.routes.pages import pages_bp
from dashboard.routes.auth import auth_bp

app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
    static_folder=str(Path(__file__).parent / "static"),
)

# Use existing secret key or generate a random one for sessions
app.secret_key = os.getenv("FLASK_SECRET_KEY", os.urandom(24))

app.register_blueprint(api_bp)
app.register_blueprint(broker_bp)
app.register_blueprint(pages_bp)
app.register_blueprint(auth_bp)

def start_dashboard(trader, port=8080):
    set_trader(trader)
    set_broker_trader(trader)
    thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False),
        daemon=True,
    )
    thread.start()
    return thread
