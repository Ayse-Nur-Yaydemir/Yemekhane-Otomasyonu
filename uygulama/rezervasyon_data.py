
from database import okuma_baglantisi, yazma_baglantisi


def rezervasyon_olustur(kullanici_id, menu_id):
    baglanti = yazma_baglantisi()
    imlec = None

    try:
        imlec = baglanti.cursor(dictionary=True)

        imlec.execute(
            "CALL sp_rezervasyon_yap(%s, %s)",
            (kullanici_id, menu_id)
        )

        sonuc = imlec.fetchone()

        while imlec.nextset():
            pass

        return sonuc

    finally:
        if imlec is not None:
            imlec.close()

        baglanti.close()


def kullanicinin_rezervasyonlari(kullanici_id):
    baglanti = okuma_baglantisi()

    try:
        imlec = baglanti.cursor(dictionary=True)

        try:
            imlec.execute("""
                SELECT
                    r.id AS rezervasyon_id,
                    r.menu_id,
                    CAST(m.tarih AS CHAR) AS tarih,
                    yh.ad AS yemekhane,
                    o.ad AS ogun,
                    r.durum,
                    r.ucret,
                    CAST(r.olusturma AS CHAR) AS olusturma,
                    d.bos_yer,
                    CONCAT(
                        CAST(d.rezervasyon_son AS CHAR),
                        '+03:00'
                    ) AS rezervasyon_son,
                    (
                        r.durum = 'aktif'
                        AND NOW() < d.rezervasyon_son
                    ) AS iptal_edilebilir

                FROM rezervasyonlar AS r

                JOIN menuler AS m
                    ON m.id = r.menu_id

                JOIN yemekhaneler AS yh
                    ON yh.id = m.yemekhane_id

                JOIN ogunler AS o
                    ON o.id = m.ogun_id

                JOIN v_menu_doluluk AS d
                    ON d.menu_id = r.menu_id

                WHERE r.kullanici_id = %s

                ORDER BY m.tarih DESC, o.sira
            """, (kullanici_id,))

            return imlec.fetchall()

        finally:
            imlec.close()

    finally:
        baglanti.close()


def rezervasyon_iptal_et(kullanici_id, rezervasyon_id):
    baglanti = yazma_baglantisi()
    imlec = None

    try:
        imlec = baglanti.cursor(dictionary=True)

        imlec.execute(
            "CALL sp_rezervasyon_iptal(%s, %s)",
            (kullanici_id, rezervasyon_id)
        )

        sonuc = imlec.fetchone()

        while imlec.nextset():
            pass

        return sonuc

    finally:
        if imlec is not None:
            imlec.close()

        baglanti.close()
