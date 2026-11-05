# Akış
Sade, kişisel yt-dlp indirme arayüzü. Link → Ses / Video → gerçek kalite listesi → indir.

## Windows kurulumu
1. Python 3.11 veya üstünü python.org üzerinden kur.
2. PowerShell'de `winget install Gyan.FFmpeg` ve `winget install DenoLand.Deno` komutlarını çalıştır. Terminali kapatıp aç.
3. ZIP'i bir klasöre çıkar, `baslat.bat` dosyasını aç. İlk açılış internetten yt-dlp bağımlılıklarını yükler.
4. http://127.0.0.1:8765 açılır. Linkini yapıştır, Ses veya Video seç, kaliteyi seç ve indir.

## Diğer sistemler
Python 3.11+, FFmpeg ve Deno kurulu olmalı.
`python -m pip install -U -r backend/requirements.txt`
`python backend/server.py`

## Davranış ve sınırlar
- Yayımlanmış site arayüzdür; bu paketteki Python sunucusu kendi bilgisayarında gerçek indirmeleri yapar. Yerel sunucuyu kullanırken yerel sayfayı aç.
- Video seçenekleri kaynaktaki gerçek çözünürlüklerden gelir. Ayrı video ve ses FFmpeg ile MKV olarak birleştirilir; tek dosyalı kaynak kendi formatını korur.
- Orijinal ses dönüştürülmez; MP3 128/192/320 kbps seçenekleri dönüştürme hedefidir, kaynak kalitesini artırmaz.
- yt-dlp'nin desteklediği sitelerle çalışır. Her bağlantının çalışacağı garanti değildir. DRM, oturum açma, bölge ve bot koruması nedeniyle bazı bağlantılar başarısız olabilir. Çerez yükleme ve DRM aşma yoktur.
- Canlı yayın ve oynatma listesi yerine tek video bağlantısı kullan.
- Geçici dosyalar tamamlandıktan bir saat sonra temizlenir. En fazla iki indirme aynı anda çalışır. İndirme sırasında sayfa açık kalmalıdır.
- Sunucu yalnızca 127.0.0.1 üzerinde çalışır; doğrudan internete açma. Genel servis için kimlik doğrulama, indirme kotası, ağ izolasyonu/SSRF koruması ve HTTPS reverse proxy gerekir. Arayüzdeki harici sunucu alanı aynı API'yi sunan, CORS izinli ayrı bir servis içindir; bu paket böyle bir genel servis kurmaz.
- Kaynak: https://github.com/yt-dlp/yt-dlp
