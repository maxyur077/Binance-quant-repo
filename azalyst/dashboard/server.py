import threading
from pathlib import Path

from flask import Flask, jsonify, render_template, request

app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
    static_folder=str(Path(__file__).parent / "static"),
)

_trader_instance = None


def set_trader(trader):
    global _trader_instance
    _trader_instance = trader


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/test_ping")
def test_ping():
    return jsonify({"status": "healthy", "message": "pong"})


@app.route("/api/status")
def api_status():
    if _trader_instance is None:
        return jsonify({"error": "Trader not initialized"}), 503
    return jsonify(_trader_instance.get_status())


@app.route("/api/trades/open")
def api_open_trades():
    if _trader_instance is None:
        return jsonify([])
    return jsonify(_trader_instance.get_open_trades())


@app.route("/api/trades/closed")
def api_closed_trades():
    if _trader_instance is None:
        return jsonify([])
    return jsonify(_trader_instance.get_closed_trades())


@app.route("/api/equity")
def api_equity():
    if _trader_instance is None:
        return jsonify([])
    return jsonify(_trader_instance.get_equity_curve())


@app.route("/api/trades/close", methods=["POST"])
def api_close_trade():
    if _trader_instance is None:
        return jsonify({"error": "Trader not initialized"}), 503
    data = request.get_json(silent=True) or {}
    symbol = data.get("symbol", "")
    if not symbol:
        return jsonify({"error": "symbol is required"}), 400
    result = _trader_instance.manual_close_trade(symbol)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)


@app.route("/api/daily_target", methods=["POST"])
def api_set_daily_target():
    if _trader_instance is None:
        return jsonify({"error": "Trader not initialized"}), 503
    data = request.get_json(silent=True) or {}
    target = data.get("target", 0)
    try:
        target = float(target)
    except (ValueError, TypeError):
        return jsonify({"error": "target must be a number"}), 400
    _trader_instance.set_daily_profit_target(target)
    return jsonify({"success": True, "daily_profit_target": target})


def start_dashboard(trader, port=8080):
    set_trader(trader)
    thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False),
        daemon=True,
    )
    thread.start()
    return thread
