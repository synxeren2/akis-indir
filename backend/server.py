"""Personal, loopback-only yt-dlp server. Do not expose directly to the Internet."""
import json, os, time, uuid, shutil, tempfile, threading, socket, ipaddress
from pathlib import Path
from urllib.parse import urlparse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from concurrent.futures import ThreadPoolExecutor
import yt_dlp
ROOT = Path(__file__).resolve().parent.parent
POOL = ThreadPoolExecutor(max_workers=2)
JOBS = {}
TEMP = Path(tempfile.mkdtemp(prefix='akis-'))
BASE = {'quiet': True, 'no_warnings': True, 'noplaylist': True, 'socket_timeout': 25, 'retries': 3, 'concurrent_fragment_downloads': 4, 'js_runtimes': {'deno': {}}}
def validate(value):
    u = urlparse(value)
    if u.scheme not in ('http', 'https') or not u.hostname or u.username or u.password:
        raise ValueError('Geçerli bir HTTP(S) bağlantısı gir.')
    if any(not ipaddress.ip_address(x[4][0]).is_global for x in socket.getaddrinfo(u.hostname, u.port or 443)):
        raise ValueError('Yerel ağ bağlantıları desteklenmiyor.')
    return value

def extract(url):
    with yt_dlp.YoutubeDL(BASE) as ydl:
        data = ydl.extract_info(url, download=False)
    if data.get('_type') in ('playlist', 'multi_video') or data.get('is_live'):
        raise ValueError('Tek bir video bağlantısı kullan. Canlı yayın desteklenmiyor.')
    fs = data.get('formats', [])
    heights = sorted({int(f['height']) for f in fs if f.get('height') and f.get('vcodec') != 'none' and not f.get('has_drm')}, reverse=True)
    audio = any(f.get('acodec') not in (None, 'none') for f in fs)
    return {'url': url, 'title': data.get('title', 'İçerik'), 'duration': data.get('duration'), 'uploader': data.get('uploader', ''), 'video': [{'value': str(h), 'label': str(h)+'p'} for h in heights], 'audio': ([{'value':'original','label':'Orijinal · hızlı'}, {'value':'320','label':'MP3 · 320 kbps'}, {'value':'192','label':'MP3 · 192 kbps'}, {'value':'128','label':'MP3 · 128 kbps'}] if audio else [])}

def download(jid, url, mode, quality):
    job = JOBS[jid]
    directory = TEMP / jid
    directory.mkdir()
    def hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            job['progress'] = min(99, d.get('downloaded_bytes', 0)*100/total) if total else 0
        elif d['status'] == 'finished': job['state'] = 'processing'
    opts = {**BASE, 'outtmpl': str(directory/'%(title).120B.%(ext)s'), 'windowsfilenames': True, 'progress_hooks': [hook]}
    if mode == 'audio':
        opts['format'] = 'bestaudio/best'
        if quality != 'original':
            opts['postprocessors'] = [{'key':'FFmpegExtractAudio','preferredcodec':'mp3','preferredquality':quality}]
    else:
        h = int(quality)
        opts['format'] = f'bestvideo[height<={h}]+bestaudio/best[height<={h}]'
        opts['merge_output_format'] = 'mkv'
    try:
        with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([url])
        files = [p for p in directory.iterdir() if p.suffix not in ('.part', '.ytdl', '.temp')]
        if len(files) != 1: raise ValueError('Dosya birleştirilemedi. FFmpeg kurulumunu kontrol et.')
        job.update(state='done', progress=100, file=str(files[0]))
    except Exception as e: job.update(state='error', error=str(e))
    finally: job['finished'] = time.time()

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs): super().__init__(*args, directory=str(ROOT/'dist'), **kwargs)
    def allowed(self):
        return self.headers.get('Host') in ('127.0.0.1:8765', 'localhost:8765') and self.headers.get('Origin', 'http://127.0.0.1:8765') in ('http://127.0.0.1:8765','http://localhost:8765')
    def reply(self, value, code=200):
        b=json.dumps(value, ensure_ascii=False).encode(); self.send_response(code); self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(b))); self.end_headers();self.wfile.write(b)
    def do_POST(self):
        if not self.allowed(): return self.reply({'error':'Bu sunucu yalnızca yerel sayfadan kullanılabilir.'},403)
        try:
            n=int(self.headers.get('Content-Length',0))
            if n<=0 or n>16384: raise ValueError('Geçersiz istek.')
            data=json.loads(self.rfile.read(n)); url=validate(data.get('url',''))
            if self.path=='/api/info': return self.reply(extract(url))
            if self.path=='/api/download':
                mode=data.get('mode');q=str(data.get('quality',''))
                if mode not in ('audio','video') or (mode=='audio' and q not in ('original','320','192','128')) or (mode=='video' and (not q.isdigit() or not 1<=int(q)<=16384)): raise ValueError('Geçersiz kalite.')
                if sum(j['state'] not in ('done','error') for j in JOBS.values())>=2: return self.reply({'error':'İki işlem zaten çalışıyor. Biraz bekle.'},429)
                jid=uuid.uuid4().hex;JOBS[jid]={'state':'downloading','progress':0};POOL.submit(download,jid,url,mode,q);return self.reply({'id':jid})
            self.reply({'error':'Bulunamadı'},404)
        except Exception as e: self.reply({'error':str(e)},400)
    def do_GET(self):
        if not self.allowed(): return self.reply({'error':'Erişim reddedildi'},403)
        if self.path.startswith('/api/jobs/'):
            j=JOBS.get(self.path.rsplit('/',1)[-1]);return self.reply({k:v for k,v in j.items() if k!='file'} if j else {'error':'İş bulunamadı'},200 if j else 404)
        if self.path.startswith('/api/file/'):
            j=JOBS.get(self.path.rsplit('/',1)[-1])
            if not j or j['state']!='done': return self.reply({'error':'Dosya hazır değil'},404)
            from urllib.parse import quote
            p=Path(j['file']);self.send_response(200);self.send_header('Content-Type','application/octet-stream');self.send_header('Content-Length',str(p.stat().st_size));self.send_header('Content-Disposition',"attachment; filename*=UTF-8''"+quote(p.name));self.end_headers()
            with p.open('rb') as f: shutil.copyfileobj(f,self.wfile)
            return
        super().do_GET()

def cleanup():
    while True:
        time.sleep(60)
        for jid,j in list(JOBS.items()):
            if j.get('finished',time.time()) < time.time()-3600:
                JOBS.pop(jid,None);shutil.rmtree(TEMP/jid,ignore_errors=True)
if __name__=='__main__':
    import webbrowser
    threading.Thread(target=cleanup,daemon=True).start()
    print('Akış: http://127.0.0.1:8765 — Kapatmak için Ctrl+C')
    webbrowser.open('http://127.0.0.1:8765')
    try: ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
    finally: shutil.rmtree(TEMP,ignore_errors=True)
