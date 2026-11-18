from database import okuma_baglantisi, yazma_baglantisi


def kullanicinin_alerji_tercihleri(kullanici_id):
    baglanti = okuma_baglantisi()

    try:
        imlec = baglanti.cursor(dictionary=True)

        try:
            imlec.execute("""
                SELECT
                    a.id AS alerjen_id,
                    a.ad,
                    (kat.alerjen_id IS NOT NULL) AS secili
                FROM alerjenler AS a
                LEFT JOIN kullanici_alerjen_tercihleri AS kat
                    ON kat.alerjen_id = a.id
                    AND kat.kullanici_id = %s
                ORDER BY a.ad
            """, (kullanici_id,))

            return imlec.fetchall()

        finally:
            imlec.close()

    finally:
        baglanti.close()


def alerji_tercihlerini_kaydet(kullanici_id, alerjen_idler):
    baglanti = yazma_baglantisi()
    imlec = None

    try:
        baglanti.start_transaction()
        imlec = baglanti.cursor()

        if alerjen_idler:
            yer_tutucular = ", ".join("%s" for _ in alerjen_idler)
            imlec.execute(
                f"SELECT id FROM alerjenler WHERE id IN ({yer_tutucular})",
                tuple(alerjen_idler),
            )
            bulunan_idler = {satir[0] for satir in imlec.fetchall()}

            if bulunan_idler != set(alerjen_idler):
                raise ValueError("Alerjen seçimlerinden biri geçersiz.")

        imlec.execute("""
            DELETE FROM kullanici_alerjen_tercihleri
            WHERE kullanici_id = %s
        """, (kullanici_id,))

        if alerjen_idler:
            imlec.executemany("""
                INSERT INTO kullanici_alerjen_tercihleri
                    (kullanici_id, alerjen_id)
                VALUES (%s, %s)
            """, [
                (kullanici_id, alerjen_id)
                for alerjen_id in alerjen_idler
            ])

        baglanti.commit()

    except Exception:
        baglanti.rollback()
        raise

    finally:
        if imlec is not None:
            imlec.close()

        baglanti.close()