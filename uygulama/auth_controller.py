import bcrypt
from auth_data import epostayla_kullanici_bul


def kullaniciyi_dogrula(eposta, sifre):
    kullanici = epostayla_kullanici_bul(eposta)

    if kullanici is None:
        return None

    sifre_hash = kullanici["sifre_hash"].encode("utf-8")
    girilen_sifre = sifre.encode("utf-8")

    if not bcrypt.checkpw(girilen_sifre, sifre_hash):
        return None

    return {
        "id": kullanici["id"],
        "ad": kullanici["ad"],
        "soyad": kullanici["soyad"],
        "eposta": kullanici["eposta"],
        "rol": kullanici["rol"],
    }