from bakiye_data import (
    guncel_bakiye,
    bakiye_hareketleri,
    bakiye_yukle,
)


def kullanici_bakiyesi(kullanici_id):
    return {
        "bakiye": guncel_bakiye(kullanici_id),
        "hareketler": bakiye_hareketleri(kullanici_id),
    }


def kullanici_bakiye_yukle(kullanici_id, tutar):
    return bakiye_yukle(kullanici_id, tutar)