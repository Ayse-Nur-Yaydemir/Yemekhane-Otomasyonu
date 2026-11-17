import os
from datetime import timedelta

import redis
from flask import Flask, jsonify
from flask_session import Session

app = Flask(__name__)

app.config.update(
    SECRET_KEY=os.environ["SESSION_SECRET_KEY"],
    SESSION_TYPE="redis",
    SESSION_REDIS=redis.Redis(
        host=os.environ["REDIS_HOST"],
        port=int(os.environ.get("REDIS_PORT", "6379")),
    ),
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
    SESSION_SERIALIZATION_FORMAT="json",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

Session(app)

from menu_routes import api as menu_api
from auth_routes import api as auth_api
from admin_routes import api as admin_api

app.register_blueprint(menu_api)
app.register_blueprint(auth_api)
app.register_blueprint(admin_api)


@app.get("/api/")
def ana_sayfa():
    return jsonify({
        "durum": "çalışıyor",
        "mesaj": "Yemekhane API hazır."
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)