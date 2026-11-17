from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, current_app, jsonify, request, session
from mysql.connector import Error as MySQLError

from admin_controller import (
    menu_guncelle,
    menu_listesi,
    yeni_menu,
    secim_listesi,
)

api = Blueprint("admin_api", __name__)


def yonetici_gerekli():
    kullanici = session.get("kullanici")
    if kullanici is None:
        return None, (jsonify({"hata": "Önce giriş yapmalısınız."}), 401)
    if kullanici.get("rol") != "yonetici":
        return None, (jsonify({"hata": "Bu işlem için yönetici yetkisi gerekli."}), 403)
    return kullanici, None


def menu_formunu_dogrula(veri):
    if not isinstance(veri, dict):
        return None, "Geçerli bir JSON gövdesi gerekli."

    for alan in ("yemekhane_id", "ogun_id"):
        deger = veri.get(alan)
        if isinstance(deger, bool) or not isinstance(deger, int) or deger <= 0:
            return None, f"{alan} pozitif bir tam sayı olmalıdır."

    try:
        menu_tarihi = date.fromisoformat(veri.get("tarih", ""))
    except (TypeError, ValueError):
        return None, "Tarih YYYY-AA-GG biçiminde olmalıdır."

    try:
        ogrenci_fiyati = Decimal(str(veri.get("ogrenci_fiyati")))
        personel_fiyati = Decimal(str(veri.get("personel_fiyati")))
        if (
            not ogrenci_fiyati.is_finite()
            or not personel_fiyati.is_finite()
            or ogrenci_fiyati < 0
            or personel_fiyati < 0
        ):
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        return None, "Fiyatlar sıfır veya daha büyük geçerli tutarlar olmalıdır."

    yemek_ids = veri.get("yemek_ids")
    if not isinstance(yemek_ids, list) or not yemek_ids:
        return None, "Menüde en az bir yemek seçmelisiniz."

    if any(
        isinstance(yemek_id, bool)
        or not isinstance(yemek_id, int)
        or yemek_id <= 0
        for yemek_id in yemek_ids
    ):
        return None, "Yemek seçimleri pozitif tam sayılardan oluşmalıdır."

    if len(set(yemek_ids)) != len(yemek_ids):
        return None, "Aynı yemek menüde birden fazla seçilemez."

    return {
        "yemekhane_id": veri["yemekhane_id"],
        "ogun_id": veri["ogun_id"],
        "tarih": menu_tarihi.isoformat(),
        "ogrenci_fiyati": ogrenci_fiyati,
        "personel_fiyati": personel_fiyati,
        "yemek_ids": yemek_ids,
    }, None


@api.get("/api/yonetici/secimler")
def yonetici_secimlerini_getir():
    _, hata = yonetici_gerekli()
    if hata:
        return hata
    return jsonify(secim_listesi())


@api.get("/api/yonetici/menuler")
def yonetici_menulerini_getir():
    _, hata = yonetici_gerekli()
    if hata:
        return hata
    return jsonify(menu_listesi())


@api.post("/api/yonetici/menuler")
def yonetici_menu_olustur():
    _, hata = yonetici_gerekli()
    if hata:
        return hata

    menu, dogrulama_hatasi = menu_formunu_dogrula(
        request.get_json(silent=True)
    )
    if dogrulama_hatasi:
        return jsonify({"hata": dogrulama_hatasi}), 400

    try:
        return jsonify(yeni_menu(menu)), 201
    except MySQLError as hata:
        if hata.errno == 1062:
            return jsonify({
                "hata": "Bu yemekhane, tarih ve öğün için menü zaten var."
            }), 409
        if hata.errno == 1452:
            return jsonify({
                "hata": "Yemekhane, öğün veya yemek seçimlerinden biri geçersiz."
            }), 400

        current_app.logger.exception("Menü oluşturulamadı")
        return jsonify({"hata": "Menü oluşturulamadı."}), 500


@api.put("/api/yonetici/menuler/<int:menu_id>")
def yonetici_menu_duzenle(menu_id):
    _, hata = yonetici_gerekli()
    if hata:
        return hata

    menu, dogrulama_hatasi = menu_formunu_dogrula(
        request.get_json(silent=True)
    )
    if dogrulama_hatasi:
        return jsonify({"hata": dogrulama_hatasi}), 400

    try:
        guncellendi = menu_guncelle(menu_id, menu)
        if not guncellendi:
            return jsonify({"hata": "Menü bulunamadı."}), 404
        return jsonify({"menu_id": menu_id, "mesaj": "Menü güncellendi."})
    except MySQLError as hata:
        if hata.errno == 1062:
            return jsonify({
                "hata": "Bu yemekhane, tarih ve öğün için başka bir menü var."
            }), 409
        if hata.errno == 1452:
            return jsonify({
                "hata": "Yemekhane, öğün veya yemek seçimlerinden biri geçersiz."
            }), 400

        current_app.logger.exception("Menü güncellenemedi")
        return jsonify({"hata": "Menü güncellenemedi."}), 500