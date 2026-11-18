import redis
from flask import current_app


MENU_CACHE_PATTERN = "yemekhane:menu:*"
MENU_CACHE_TTL_SECONDS = 300


def onbellegin_getir_veya_yukle(
    anahtar,
    veri_yukle,
    sure=MENU_CACHE_TTL_SECONDS,
):
    istemci = current_app.config.get("SESSION_REDIS")

    if istemci is None:
        return veri_yukle()

    try:
        kayit = istemci.get(anahtar)

        if kayit is not None:
            try:
                return current_app.json.loads(kayit)
            except (TypeError, ValueError):
                istemci.delete(anahtar)

    except redis.RedisError:
        current_app.logger.warning(
            "Redis menü önbelleği okunamadı; veritabanı kullanılacak.",
            exc_info=True,
        )
        return veri_yukle()

    veri = veri_yukle()

    if veri is None:
        return None

    try:
        json_verisi = current_app.json.dumps(veri)
        istemci.set(anahtar, json_verisi, ex=sure)
    except (redis.RedisError, TypeError, ValueError):
        current_app.logger.warning(
            "Redis menü önbelleğine yazılamadı.",
            exc_info=True,
        )

    return veri


def menu_onbellegini_temizle():
    istemci = current_app.config.get("SESSION_REDIS")

    if istemci is None:
        return

    try:
        silinecekler = []

        for anahtar in istemci.scan_iter(
            match=MENU_CACHE_PATTERN,
            count=100,
        ):
            silinecekler.append(anahtar)

            if len(silinecekler) >= 100:
                istemci.delete(*silinecekler)
                silinecekler.clear()

        if silinecekler:
            istemci.delete(*silinecekler)

    except redis.RedisError:
        current_app.logger.warning(
            "Redis menü önbelleği temizlenemedi.",
            exc_info=True,
        )