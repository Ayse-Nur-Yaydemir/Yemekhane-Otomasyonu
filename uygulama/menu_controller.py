from datetime import date

from menu_cache import onbellegin_getir_veya_yukle
from menu_data import (
    bugunun_menuleri,
    haftalik_menu_satirlari,
    menu_detay_satirlari,
)


def gunun_menuleri():
    bugun = date.today().isoformat()
    anahtar = f"yemekhane:menu:gun:{bugun}"

    return onbellegin_getir_veya_yukle(
        anahtar,
        lambda: {"menuler": bugunun_menuleri()},
    )


def _secilen_menu_verisini_yukle(menu_id):
    satirlar = menu_detay_satirlari(menu_id)

    if not satirlar:
        return None

    ilk = satirlar[0]
    tarih = ilk["tarih"]
    tarih_iso = tarih.isoformat() if hasattr(tarih, "isoformat") else tarih
    yemekler = []

    for satir in satirlar:
        alerjenler = satir["alerjenler"]
        alerjen_idler = satir["alerjen_idler"]

        yemekler.append({
            "ad": satir["yemek"],
            "kategori": satir["kategori"],
            "kalori": satir["kalori"],
            "vejetaryen": bool(satir["vejetaryen"]),
            "alerjenler": alerjenler.split(", ") if alerjenler else [],
            "alerjen_idler": [
                int(x) for x in alerjen_idler.split(",")
            ] if alerjen_idler else [],
        })

    return {
        "menu_id": ilk["menu_id"],
        "tarih": tarih_iso,
        "yemekhane": ilk["yemekhane"],
        "ogun": ilk["ogun"],
        "ogrenci_fiyati": ilk["ogrenci_fiyati"],
        "personel_fiyati": ilk["personel_fiyati"],
        "toplam_kalori": sum(yemek["kalori"] for yemek in yemekler),
        "yemekler": yemekler,
    }


def secilen_menu(menu_id):
    anahtar = f"yemekhane:menu:detay:{menu_id}"

    return onbellegin_getir_veya_yukle(
        anahtar,
        lambda: _secilen_menu_verisini_yukle(menu_id),
    )


def haftalik_menuler():
    bugun = date.today().isoformat()
    anahtar = f"yemekhane:menu:hafta:{bugun}"

    return onbellegin_getir_veya_yukle(
        anahtar,
        lambda: {"menuler": haftalik_menu_satirlari()},
    )