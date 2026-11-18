from rezervasyon_data import (
    rezervasyon_olustur,
    kullanicinin_rezervasyonlari,
    rezervasyon_iptal_et,
)


def kullanici_icin_rezervasyon(
    kullanici_id,
    menu_id,
    yarim_porsiyon=False,
):
    return rezervasyon_olustur(
        kullanici_id,
        menu_id,
        yarim_porsiyon,
    )


def kullanici_rezervasyon_listesi(kullanici_id):
    return kullanicinin_rezervasyonlari(kullanici_id)


def kullanici_icin_iptal(kullanici_id, rezervasyon_id):
    return rezervasyon_iptal_et(kullanici_id, rezervasyon_id)