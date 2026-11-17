from menu_data import (
    bugunun_menuleri,
    menu_detay_satirlari,
    haftalik_menu_satirlari,
)


def gunun_menuleri():
    return {"menuler": bugunun_menuleri()}


def secilen_menu(menu_id):
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
def haftalik_menuler():
    return {"menuler": haftalik_menu_satirlari()}