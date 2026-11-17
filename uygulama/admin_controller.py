from admin_data import (
    menu_duzenle,
    menu_olustur,
    yonetici_menuleri,
    yonetici_secimleri,
)


def menu_listesi():
    return {"menuler": yonetici_menuleri()}


def secim_listesi():
    return yonetici_secimleri()


def yeni_menu(menu):
    return {"menu_id": menu_olustur(menu)}


def menu_guncelle(menu_id, menu):
    return menu_duzenle(menu_id, menu)