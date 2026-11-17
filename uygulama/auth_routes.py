from flask import Blueprint, current_app, jsonify, request, session
from auth_controller import kullaniciyi_dogrula

api = Blueprint("auth_api", __name__)


@api.post("/api/giris")
def giris():
    veri = request.get_json(silent=True) or {}
    eposta = veri.get("eposta")
    sifre = veri.get("sifre")

    if not isinstance(eposta, str) or not isinstance(sifre, str):
        return jsonify({"hata": "E-posta ve şifre gereklidir."}), 400

    kullanici = kullaniciyi_dogrula(eposta.strip().lower(), sifre)
    if kullanici is None:
        return jsonify({"hata": "E-posta veya şifre hatalı."}), 401

    session.clear()
    session.permanent = True
    session["kullanici"] = kullanici
    current_app.session_interface.regenerate(session)

    return jsonify({"kullanici": kullanici})


@api.get("/api/oturum")
def oturum():
    kullanici = session.get("kullanici")
    if kullanici is None:
        return jsonify({"hata": "Oturum açılmamış."}), 401
    return jsonify({"kullanici": kullanici})


@api.post("/api/cikis")
def cikis():
    session.clear()
    return jsonify({"mesaj": "Çıkış yapıldı."})