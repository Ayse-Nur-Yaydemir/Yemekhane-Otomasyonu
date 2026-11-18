from flask import Blueprint, current_app, jsonify, request, session
from mysql.connector import Error as MySQLError

from alerji_controller import (
    alerji_tercihi_guncelle,
    alerji_tercihi_listesi,
)


api = Blueprint("alerji_api", __name__)


def oturumdaki_kullanici():
    return session.get("kullanici")


@api.get("/api/alerji-tercihleri")
def alerji_tercihlerini_getir():
    kullanici = oturumdaki_kullanici()

    if kullanici is None:
        return jsonify({"hata": "Önce giriş yapmalısınız."}), 401

    return jsonify({
        "alerjenler": alerji_tercihi_listesi(kullanici["id"])
    })


@api.put("/api/alerji-tercihleri")
def alerji_tercihlerini_guncelle():
    kullanici = oturumdaki_kullanici()

    if kullanici is None:
        return jsonify({"hata": "Önce giriş yapmalısınız."}), 401

    veri = request.get_json(silent=True)

    if not isinstance(veri, dict):
        return jsonify({"hata": "Geçerli bir JSON gövdesi gerekli."}), 400

    alerjen_idler = veri.get("alerjen_idler")

    if not isinstance(alerjen_idler, list):
        return jsonify({
            "hata": "alerjen_idler bir liste olmalıdır."
        }), 400

    if any(
        isinstance(alerjen_id, bool)
        or not isinstance(alerjen_id, int)
        or alerjen_id <= 0
        for alerjen_id in alerjen_idler
    ):
        return jsonify({
            "hata": "Alerjen kimlikleri pozitif tam sayı olmalıdır."
        }), 400

    if len(set(alerjen_idler)) != len(alerjen_idler):
        return jsonify({
            "hata": "Aynı alerjen birden fazla seçilemez."
        }), 400

    try:
        sonuc = alerji_tercihi_guncelle(
            kullanici["id"],
            alerjen_idler,
        )
        return jsonify(sonuc)

    except ValueError as hata:
        return jsonify({"hata": str(hata)}), 400

    except MySQLError:
        current_app.logger.exception("Alerji tercihleri kaydedilemedi")
        return jsonify({
            "hata": "Alerji tercihleri kaydedilemedi."
        }), 500