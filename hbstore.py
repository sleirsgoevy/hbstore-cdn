import os.path, sys, http.server, socketserver, re, json
from collections import OrderedDict as odict

pkgs = [i for i in os.listdir(sys.argv[1]) if i.endswith('.pkg')]

def pkg_titleid(name):
    match = re.match('[A-Z]{2}[0-9]{4}-([A-Z]{4}[0-9]{5})_[0-9]{2}-[A-Z0-9]{16}(-A[0-9]{4}-V[0-9]{4})?.pkg', name)
    if match: return match.group(1)
    return None

def pkg_name(name):
    titleid = pkg_titleid(name)
    if titleid != None: return titleid
    return name[:9]

class Handler(http.server.BaseHTTPRequestHandler):
    def send_file(self, path):
        path = path.replace('/', os.path.sep)
        try: f = open(path, 'rb')
        except IOError:
            self.send_error(404)
            return
        with f:
            f.seek(0, os.SEEK_END)
            self.send_response(200)
            self.send_header('Content-Length', f.tell())
            self.end_headers()
            f.seek(0)
            while True:
                chk = f.read(1048576)
                self.wfile.write(chk)
                if not chk: break
    def send_data(self, data):
        if isinstance(data, str): data = data.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Length', len(data))
        self.end_headers()
        self.wfile.write(data)
    def send_page(self, i):
        host = self.headers.get('host', 'orbismandl.darksoftware.xyz')
        pkgs1 = []
        for i in range(8*i, min(len(pkgs), 8*i+8)):
            titleid = pkg_titleid(pkgs[i])
            if titleid == None: titleid = 'UNKN%05d'%i
            name = pkg_name(pkgs[i])
            pkgs1.append(odict((
                ('id', titleid),
                ('name', name),
                ('desc', pkgs[i][46:]),
                ('image', 'http://'+host+'/storedata/icon0.png'),
                ('package', 'http://'+host+'/pkgs/%d.pkg'%i),
                ('version', ''),
                ('picpath', '/user/app/NPXS39041/storedata/icon0.png'),
                ('desc_1', pkgs[i][:23]),
                ('desc_2', pkgs[i][23:46]),
                ('ReviewStars', ''),
                ('Size', ''), # ignored
                ('Author', ''),
                ('apptype', ''),
                ('pv', ''),
                ('main_icon_path', 'http://'+host+'/storedata/main.png'),
                ('main_menu_pic', '/user/app/NPXS39041/storedata/main.png'),
                ('releaseddate', ''),
            )))
        self.send_data(json.dumps({'packages': pkgs1}))
    def send_main_app(self):
        host = self.headers.get('host', 'orbismandl.darksoftware.xyz')
        self.send_data(json.dumps({'packages': [odict((
            ('name', 'Main_App'),
            ('main_bg', 'http://'+host+'/storedata/store_background.dat'),
            ('main_bg_local', '/user/app/NPXS39041/storedata/store_background.dat'),
            ('default_dl', 'http://'+host+'/storedata/nondf.png'),
            ('default_dl_local', '/user/app/NPXS39041/storedata/nondf.png'),
            ('dl_bg', 'http://'+host+'/storedata/dl_bg.dat'),
            ('dl_bg_local', '/user/app/NPXS39041/storedata/dl_bg.dat'),
        ))]}))
    def do_GET(self):
        path = self.path
        if path.startswith('http://'): # proxy request
            path = '/' + path.split('/', 3)[3]
        if path == '/':
            self.send_data(b'')
        elif path in (
            '/homebrew.elf',
            '/storedata/dl_bg.dat',
            '/storedata/icon0.png',
            '/storedata/main.png',
            '/storedata/nondf.png',
            '/storedata/store_background.dat'
        ):
            self.send_file('images/'+path.split('/')[-1])
        elif path == '/main_app.json':
            self.send_main_app()
        elif path.startswith('/homebrew-page') and path.endswith('.json'):
            try: idx = int(path[14:-5]) - 1
            except ValueError:
                self.send_error(404)
                return
            if idx < 0 or 8 * idx >= len(pkgs):
                self.send_error(404)
                return
            self.send_page(idx)
        elif path.startswith('/pkgs/') and path.endswith('.pkg'):
            try: idx = int(path[6:-4])
            except ValueError:
                self.send_error(404)
                return
            if idx not in range(len(pkgs)):
                self.send_error(404)
                return
            self.send_file(sys.argv[1]+'/'+pkgs[idx])

http.server.HTTPServer(('', 80), Handler).serve_forever()
