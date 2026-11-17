from database import okuma_baglantisi, yazma_baglantisi


def guncel_bakiye(kullanici_id):
    baglanti = yazma_baglantisi()
    try:
        imlec = baglanti.cursor(dictionary=True)
        try:
            imlec.execute(
                "SELECT bakiye FROM kullanicilar WHERE id = %s",
                (kullanici_id,),
            )
            sonuc = imlec.fetchone()
            return sonuc["bakiye"] if sonuc else None
        finally:
            imlec.close()
    finally:
        baglanti.close()


def bakiye_hareketleri(kullanici_id):
    baglanti = okuma_baglantisi()
    try:
        imlec = baglanti.cursor(dictionary=True)
        try:
            imlec.execute("""
                SELECT
                    tur,
                    tutar,
                    aciklama,
                    CAST(olusturma AS CHAR) AS olusturma
                FROM bakiye_hareketleri
                WHERE kullanici_id = %s
                ORDER BY olusturma DESC, id DESC
            """, (kullanici_id,))
            return imlec.fetchall()
        finally:
            imlec.close()
    finally:
        baglanti.close()


def bakiye_yukle(kullanici_id, tutar):
    baglanti = yazma_baglantisi()
    imlec = None

    try:
        imlec = baglanti.cursor(dictionary=True)
        imlec.execute(
            "CALL sp_bakiye_yukle(%s, %s)",
            (kullanici_id, tutar),
        )
        sonuc = imlec.fetchone()

        while imlec.nextset():
            pass

        return sonuc
    finally:
        if imlec is not None:
            imlec.close()
        baglanti.close()