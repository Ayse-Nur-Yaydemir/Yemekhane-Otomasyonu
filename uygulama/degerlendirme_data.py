from database import okuma_baglantisi, yazma_baglantisi


def kullanilmis_menuler(kullanici_id):
    baglanti = okuma_baglantisi()
    try:
        imlec = baglanti.cursor(dictionary=True)
        try:
            imlec.execute("""
                SELECT
                    m.id AS menu_id,
                    CAST(m.tarih AS CHAR) AS tarih,
                    yh.ad AS yemekhane,
                    o.ad AS ogun,
                    r.kullanma_zamani,
                    d.puan,
                    d.yorum
                FROM rezervasyonlar AS r
                JOIN menuler AS m ON m.id = r.menu_id
                JOIN yemekhaneler AS yh ON yh.id = m.yemekhane_id
                JOIN ogunler AS o ON o.id = m.ogun_id
                LEFT JOIN degerlendirmeler AS d
                    ON d.menu_id = r.menu_id
                    AND d.kullanici_id = r.kullanici_id
                WHERE r.kullanici_id = %s
                    AND r.durum = 'kullanildi'
                ORDER BY m.tarih DESC, o.sira
            """, (kullanici_id,))
            return imlec.fetchall()
        finally:
            imlec.close()
    finally:
        baglanti.close()


def degerlendirme_ekle(kullanici_id, menu_id, puan, yorum):
    baglanti = yazma_baglantisi()
    imlec = None

    try:
        baglanti.start_transaction()
        imlec = baglanti.cursor(dictionary=True)

        imlec.execute("""
            SELECT id
            FROM rezervasyonlar
            WHERE kullanici_id = %s
                AND menu_id = %s
                AND durum = 'kullanildi'
            FOR UPDATE
        """, (kullanici_id, menu_id))

        rezervasyon = imlec.fetchone()
        if rezervasyon is None:
            raise ValueError("Yalnızca kullanılmış menü değerlendirilebilir.")

        imlec.execute("""
            INSERT INTO degerlendirmeler
                (kullanici_id, menu_id, puan, yorum)
            VALUES (%s, %s, %s, %s)
        """, (kullanici_id, menu_id, puan, yorum))

        degerlendirme_id = imlec.lastrowid
        baglanti.commit()

        return {"degerlendirme_id": degerlendirme_id}
    except Exception:
        baglanti.rollback()
        raise
    finally:
        if imlec is not None:
            imlec.close()
        baglanti.close()