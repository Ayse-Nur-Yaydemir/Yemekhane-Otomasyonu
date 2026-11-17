from database import okuma_baglantisi


def bugunun_menuleri():
    baglanti = okuma_baglantisi()
    try:
        imlec = baglanti.cursor(dictionary=True)
        try:
            imlec.execute("""
                SELECT
                    m.id AS menu_id,
                    DATE_FORMAT(m.tarih, '%Y-%m-%d') AS tarih,
                    yh.ad AS yemekhane,
                    o.ad AS ogun,
                    m.ogrenci_fiyati,
                    m.personel_fiyati
                FROM menuler AS m
                JOIN yemekhaneler AS yh ON yh.id = m.yemekhane_id
                JOIN ogunler AS o ON o.id = m.ogun_id
                WHERE m.tarih = CURDATE()
                ORDER BY yh.ad, o.sira
            """)
            return imlec.fetchall()
        finally:
            imlec.close()
    finally:
        baglanti.close()


def menu_detay_satirlari(menu_id):
    baglanti = okuma_baglantisi()
    try:
        imlec = baglanti.cursor(dictionary=True)
        try:
            imlec.execute("""
                SELECT
                    menu_id, tarih, yemekhane, ogun,
                    ogrenci_fiyati, personel_fiyati,
                    yemek, kategori, kalori, vejetaryen,
                    alerjenler, alerjen_idler, kategori_sira
                FROM v_menu_detay
                WHERE menu_id = %s
                ORDER BY kategori_sira, yemek
            """, (menu_id,))
            return imlec.fetchall()
        finally:
            imlec.close()
    finally:
        baglanti.close()
def haftalik_menu_satirlari():
    baglanti = okuma_baglantisi()
    try:
        imlec = baglanti.cursor(dictionary=True)
        try:
            imlec.execute("""
                SELECT
                    d.menu_id,
                    DATE_FORMAT(d.tarih, '%Y-%m-%d') AS tarih,
                    d.yemekhane,
                    d.ogun,
                    m.ogrenci_fiyati,
                    m.personel_fiyati,
                    d.kapasite,
                    d.rezerve,
                    d.bos_yer,
                    d.doluluk_yuzde,
                    DATE_FORMAT(
                        d.rezervasyon_son,
                        '%Y-%m-%dT%H:%i:%s+03:00'
                    ) AS rezervasyon_son
                FROM v_menu_doluluk AS d
                JOIN menuler AS m ON m.id = d.menu_id
                WHERE d.tarih BETWEEN CURDATE()
                    AND DATE_ADD(CURDATE(), INTERVAL 6 DAY)
                ORDER BY d.tarih, d.yemekhane_id, d.ogun_id
            """)
            return imlec.fetchall()
        finally:
            imlec.close()
    finally:
        baglanti.close()       