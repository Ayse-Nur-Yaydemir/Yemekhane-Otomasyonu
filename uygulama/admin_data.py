from database import okuma_baglantisi, yazma_baglantisi


def yonetici_menuleri():
    baglanti = okuma_baglantisi()
    try:
        imlec = baglanti.cursor(dictionary=True)
        try:
            imlec.execute("""
                SELECT
                    d.menu_id,
                    CAST(d.tarih AS CHAR) AS tarih,
                    d.yemekhane_id,
                    d.yemekhane,
                    d.ogun_id,
                    d.ogun,
                    m.ogrenci_fiyati,
                    m.personel_fiyati,
                    d.kapasite,
                    d.rezerve,
                    d.bos_yer,
                    d.doluluk_yuzde,
                    p.oy_sayisi,
                    p.ortalama_puan,
                    (
                        SELECT GROUP_CONCAT(
                            my.yemek_id ORDER BY my.yemek_id
                        )
                        FROM menu_yemekleri AS my
                        WHERE my.menu_id = d.menu_id
                    ) AS yemek_idler
                FROM v_menu_doluluk AS d
                JOIN menuler AS m ON m.id = d.menu_id
                JOIN v_menu_puan AS p ON p.menu_id = d.menu_id
                ORDER BY d.tarih DESC, d.yemekhane_id, d.ogun_id
            """)
            return imlec.fetchall()
        finally:
            imlec.close()
    finally:
        baglanti.close()


def yonetici_secimleri():
    baglanti = okuma_baglantisi()
    try:
        imlec = baglanti.cursor(dictionary=True)

        imlec.execute("""
            SELECT id, ad
            FROM yemekhaneler
            ORDER BY id
        """)
        yemekhaneler = imlec.fetchall()

        imlec.execute("""
            SELECT id, ad
            FROM ogunler
            ORDER BY sira
        """)
        ogunler = imlec.fetchall()

        imlec.execute("""
            SELECT y.id, y.ad, k.ad AS kategori
            FROM yemekler AS y
            JOIN yemek_kategorileri AS k ON k.id = y.kategori_id
            ORDER BY k.sira, y.ad
        """)
        yemekler = imlec.fetchall()

        imlec.close()

        return {
            "yemekhaneler": yemekhaneler,
            "ogunler": ogunler,
            "yemekler": yemekler,
        }
    finally:
        baglanti.close()


def menu_olustur(menu):
    baglanti = yazma_baglantisi()
    imlec = None

    try:
        baglanti.start_transaction()
        imlec = baglanti.cursor()

        imlec.execute("""
            INSERT INTO menuler
                (yemekhane_id, tarih, ogun_id, ogrenci_fiyati, personel_fiyati)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            menu["yemekhane_id"],
            menu["tarih"],
            menu["ogun_id"],
            menu["ogrenci_fiyati"],
            menu["personel_fiyati"],
        ))

        menu_id = imlec.lastrowid
        imlec.executemany("""
            INSERT INTO menu_yemekleri (menu_id, yemek_id)
            VALUES (%s, %s)
        """, [(menu_id, yemek_id) for yemek_id in menu["yemek_ids"]])

        baglanti.commit()
        return menu_id
    except Exception:
        baglanti.rollback()
        raise
    finally:
        if imlec is not None:
            imlec.close()
        baglanti.close()


def menu_duzenle(menu_id, menu):
    baglanti = yazma_baglantisi()
    imlec = None

    try:
        baglanti.start_transaction()
        imlec = baglanti.cursor()

        imlec.execute(
            "SELECT id FROM menuler WHERE id = %s FOR UPDATE",
            (menu_id,),
        )
        if imlec.fetchone() is None:
            baglanti.rollback()
            return False

        imlec.execute("""
            UPDATE menuler
            SET yemekhane_id = %s,
                tarih = %s,
                ogun_id = %s,
                ogrenci_fiyati = %s,
                personel_fiyati = %s
            WHERE id = %s
        """, (
            menu["yemekhane_id"],
            menu["tarih"],
            menu["ogun_id"],
            menu["ogrenci_fiyati"],
            menu["personel_fiyati"],
            menu_id,
        ))

        imlec.execute(
            "DELETE FROM menu_yemekleri WHERE menu_id = %s",
            (menu_id,),
        )
        imlec.executemany("""
            INSERT INTO menu_yemekleri (menu_id, yemek_id)
            VALUES (%s, %s)
        """, [(menu_id, yemek_id) for yemek_id in menu["yemek_ids"]])

        baglanti.commit()
        return True
    except Exception:
        baglanti.rollback()
        raise
    finally:
        if imlec is not None:
            imlec.close()
        baglanti.close()