from database import okuma_baglantisi


def epostayla_kullanici_bul(eposta):
    baglanti = okuma_baglantisi()
    try:
        imlec = baglanti.cursor(dictionary=True)
        try:
            imlec.execute("""
                SELECT id, ad, soyad, eposta, sifre_hash, rol
                FROM kullanicilar
                WHERE eposta = %s AND aktif = 1
            """, (eposta,))
            return imlec.fetchone()
        finally:
            imlec.close()
    finally:
        baglanti.close()