import os
import re
from datetime import timedelta

import redis
from flask import Flask, jsonify, request
from flask_session import Session

from menu_cache import menu_onbellegini_temizle


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


@app.after_request
def menu_degisiminde_onbellegi_temizle(response):
    basarili = 200 <= response.status_code < 300
    yol = request.path
    yontem = request.method

    rezervasyon_olustu = (
        yontem == "POST"
        and yol == "/api/rezervasyonlar"
    )
    rezervasyon_iptal_edildi = (
        yontem == "POST"
        and re.fullmatch(r"/api/rezervasyonlar/\d+/iptal", yol)
    )
    menu_olusturuldu = (
        yontem == "POST"
        and yol == "/api/yonetici/menuler"
    )
    menu_guncellendi = (
        yontem == "PUT"
        and re.fullmatch(r"/api/yonetici/menuler/\d+", yol)
    )

    if basarili and (
        rezervasyon_olustu
        or rezervasyon_iptal_edildi
        or menu_olusturuldu
        or menu_guncellendi
    ):
        menu_onbellegini_temizle()

    return response


from menu_routes import api as menu_api
from auth_routes import api as auth_api
from admin_routes import api as admin_api
from alerji_routes import api as alerji_api

app.register_blueprint(menu_api)
app.register_blueprint(auth_api)
app.register_blueprint(admin_api)
app.register_blueprint(alerji_api)


@app.get("/api/")
def ana_sayfa():
    return jsonify({
        "durum": "çalışıyor",
        "mesaj": "Yemekhane API hazır.",
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)