from decimal import Decimal, InvalidOperation

from flask import Blueprint, current_app, jsonify, request, session
from mysql.connector import Error as MySQLError

from bakiye_controller import kullanici_bakiyesi, kullanici_bakiye_yukle
from degerlendirme_controller import (
    kullanici_degerlendirme_ekle,
    kullanicinin_kullanilmis_menuleri,
)
from menu_controller import gunun_menuleri, haftalik_menuler, secilen_menu
from rezervasyon_controller import (
    kullanici_icin_iptal,
    kullanici_icin_rezervasyon,
    kullanici_rezervasyon_listesi,
)


api = Blueprint("api", __name__)


def oturumdaki_kullanici():
    return session.get("kullanici")


@api.get("/api/menuler")
def menuler():
    return jsonify(gunun_menuleri())


@api.get("/api/menuler/haftalik")
def haftalik_menu_listesi():
    return jsonify(haftalik_menuler())


@api.get("/api/menuler/<int:menu_id>")
def menu_detayi(menu_id):
    sonuc = secilen_menu(menu_id)

    if sonuc is None:
        return jsonify({"hata": "Menü bulunamadı."}), 404

    return jsonify(sonuc)


@api.post("/api/rezervasyonlar")
def rezervasyon_yap():
    kullanici = oturumdaki_kullanici()

    if kullanici is None:
        return jsonify({"hata": "Önce giriş yapmalısınız."}), 401

    veri = request.get_json(silent=True)

    if not isinstance(veri, dict):
        return jsonify({"hata": "Geçerli bir JSON gövdesi gerekli."}), 400

    menu_id = veri.get("menu_id")

    if (
        isinstance(menu_id, bool)
        or not isinstance(menu_id, int)
        or menu_id <= 0
    ):
        return jsonify({"hata": "Geçerli bir menu_id gerekli."}), 400

    yarim_porsiyon = veri.get("yarim_porsiyon", False)

    if not isinstance(yarim_porsiyon, bool):
        return jsonify({
            "hata": "yarim_porsiyon alanı doğru veya yanlış olmalıdır."
        }), 400

    try:
        sonuc = kullanici_icin_rezervasyon(
            kullanici["id"],
            menu_id,
            yarim_porsiyon,
        )
        return jsonify(sonuc), 201

    except MySQLError as hata:
        if hata.errno == 1644:
            return jsonify({"hata": hata.msg}), 400

        current_app.logger.exception("Rezervasyon oluşturulamadı")
        return jsonify({"hata": "Rezervasyon oluşturulamadı."}), 500


@api.get("/api/rezervasyonlar")
def rezervasyonlarim():
    kullanici = oturumdaki_kullanici()

    if kullanici is None:
        return jsonify({"hata": "Önce giriş yapmalısınız."}), 401

    return jsonify({
        "rezervasyonlar": kullanici_rezervasyon_listesi(kullanici["id"])
    })


@api.post("/api/rezervasyonlar/<int:rezervasyon_id>/iptal")
def rezervasyon_iptal(rezervasyon_id):
    kullanici = oturumdaki_kullanici()

    if kullanici is None:
        return jsonify({"hata": "Önce giriş yapmalısınız."}), 401

    try:
        sonuc = kullanici_icin_iptal(
            kullanici["id"],
            rezervasyon_id,
        )
        return jsonify(sonuc)

    except MySQLError as hata:
        if hata.errno == 1644:
            return jsonify({"hata": hata.msg}), 400

        current_app.logger.exception("Rezervasyon iptal edilemedi")
        return jsonify({"hata": "Rezervasyon iptal edilemedi."}), 500


@api.get("/api/bakiye")
def bakiye():
    kullanici = oturumdaki_kullanici()

    if kullanici is None:
        return jsonify({"hata": "Önce giriş yapmalısınız."}), 401

    return jsonify(kullanici_bakiyesi(kullanici["id"]))


@api.post("/api/bakiye/yukle")
def bakiye_yukle_rotasi():
    kullanici = oturumdaki_kullanici()

    if kullanici is None:
        return jsonify({"hata": "Önce giriş yapmalısınız."}), 401

    veri = request.get_json(silent=True)

    if not isinstance(veri, dict):
        return jsonify({"hata": "Geçerli bir JSON gövdesi gerekli."}), 400

    try:
        tutar = Decimal(str(veri.get("tutar")))

        if not tutar.is_finite():
            raise InvalidOperation

    except (InvalidOperation, ValueError):
        return jsonify({"hata": "Geçerli bir tutar girin."}), 400

    try:
        sonuc = kullanici_bakiye_yukle(kullanici["id"], tutar)
        return jsonify(sonuc), 201

    except MySQLError as hata:
        if hata.errno == 1644:
            return jsonify({"hata": hata.msg}), 400

        current_app.logger.exception("Bakiye yüklenemedi")
        return jsonify({"hata": "Bakiye yüklenemedi."}), 500


@api.get("/api/degerlendirmeler")
def degerlendirmelerim():
    kullanici = oturumdaki_kullanici()

    if kullanici is None:
        return jsonify({"hata": "Önce giriş yapmalısınız."}), 401

    return jsonify({
        "menuler": kullanicinin_kullanilmis_menuleri(kullanici["id"])
    })


@api.post("/api/degerlendirmeler")
def degerlendirme_yap():
    kullanici = oturumdaki_kullanici()

    if kullanici is None:
        return jsonify({"hata": "Önce giriş yapmalısınız."}), 401

    veri = request.get_json(silent=True)

    if not isinstance(veri, dict):
        return jsonify({"hata": "Geçerli bir JSON gövdesi gerekli."}), 400

    menu_id = veri.get("menu_id")
    puan = veri.get("puan")
    yorum = veri.get("yorum", "")

    if (
        isinstance(menu_id, bool)
        or not isinstance(menu_id, int)
        or menu_id <= 0
    ):
        return jsonify({"hata": "Geçerli bir menu_id gerekli."}), 400

    if (
        isinstance(puan, bool)
        or not isinstance(puan, int)
        or not 1 <= puan <= 5
    ):
        return jsonify({"hata": "Puan 1 ile 5 arasında olmalıdır."}), 400

    if yorum is None:
        yorum = ""

    if not isinstance(yorum, str) or len(yorum) > 500:
        return jsonify({
            "hata": "Yorum en fazla 500 karakter olabilir."
        }), 400

    yorum = yorum.strip() or None

    try:
        sonuc = kullanici_degerlendirme_ekle(
            kullanici["id"],
            menu_id,
            puan,
            yorum,
        )
        return jsonify(sonuc), 201

    except ValueError as hata:
        return jsonify({"hata": str(hata)}), 403

    except MySQLError as hata:
        if hata.errno == 1062:
            return jsonify({
                "hata": "Bu menüyü zaten değerlendirdiniz."
            }), 409

        current_app.logger.exception("Değerlendirme kaydedilemedi")
        return jsonify({"hata": "Değerlendirme kaydedilemedi."}), 500