# Akış — Ses ve video indir

Canlı arayüz: https://akis-indir.vercel.app
İndirme motoru: https://akis-indir-api.onrender.com

Tarayıcıya kurulum gerekmez. Bağlantı → Ses / Video → gerçek kalite listesi → İndir.

## Bulut kurulumu
Dockerfile Python, FFmpeg ve Deno kurar. Render ücretsiz web servisi `main` dalını otomatik dağıtır.
`RENDER=true`, `PORT` ve `RENDER_EXTERNAL_URL` Render tarafından sağlanır.
`ALLOWED_ORIGINS` virgülle ayrılmış izinli arayüz adresleridir. `/health` bağımlılık durumunu gösterir.

Ücretsiz sunucu 15 dakika boşta kaldığında uyuyabilir. İlk istekte yaklaşık bir dakika bekleme olabilir.
En fazla iki işlem, istek başına 30 dakika içerik ve 250 MB indirme sınırı vardır. Geçici dosyalar 15 dakika sonra temizlenir. Saatlik istemci işlem sınırı 30'dur.
Kaynak sitelerin bot/oturum/bölge kontrolleri bazı bağlantıları engelleyebilir; her sitenin çalışacağı garanti edilmez. DRM veya bot koruması aşılmaz.

## Yerel kullanım
Python 3.11+, FFmpeg ve Deno kur. Windows için `baslat.bat`; diğer sistemlerde:
```
python -m pip install -U -r backend/requirements.txt
python backend/server.py
```

Orijinal ses dönüştürülmez. MP3 seçenekleri dönüştürme hedefidir, kaynak kalitesini artırmaz.
Ayrı ses ve video MKV olarak birleştirilir. Tek dosya kaynak formatını korur.
Kaynak: https://github.com/yt-dlp/yt-dlp
