from alerji_data import (
    kullanicinin_alerji_tercihleri,
    alerji_tercihlerini_kaydet,
)


def alerji_tercihi_listesi(kullanici_id):
    return kullanicinin_alerji_tercihleri(kullanici_id)


def alerji_tercihi_guncelle(kullanici_id, alerjen_idler):
    alerji_tercihlerini_kaydet(kullanici_id, alerjen_idler)
    return {
        "mesaj": "Alerji tercihleri kaydedildi.",
        "alerjen_idler": alerjen_idler,
    }