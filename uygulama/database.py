import os
import mysql.connector


def okuma_baglantisi():
    return mysql.connector.connect(
        host=os.environ["DB_OKUMA_HOST"],
        port=int(os.environ.get("DB_PORT", "3306")),
        database=os.environ["DB_ADI"],
        user=os.environ["DB_KULLANICI"],
        password=os.environ["DB_SIFRE"],
        charset="utf8mb4",
    )
def yazma_baglantisi():
    return mysql.connector.connect(
        host=os.environ["DB_YAZMA_HOST"],
        port=int(os.environ.get("DB_PORT", "3306")),
        database=os.environ["DB_ADI"],
        user=os.environ["DB_KULLANICI"],
        password=os.environ["DB_SIFRE"],
        charset="utf8mb4",
        autocommit=True,
    )