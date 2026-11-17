from degerlendirme_data import kullanilmis_menuler, degerlendirme_ekle


def kullanicinin_kullanilmis_menuleri(kullanici_id):
    return kullanilmis_menuler(kullanici_id)


def kullanici_degerlendirme_ekle(kullanici_id, menu_id, puan, yorum):
    return degerlendirme_ekle(kullanici_id, menu_id, puan, yorum)