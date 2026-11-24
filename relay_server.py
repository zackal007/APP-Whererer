#!/usr/bin/env python3
import json, ssl, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

AUTH = 'Bearer RlyBearer-7c1d9e2a4b6f'
ALLOWED_HOST = 'api.weixin.qq.com'

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        if self.path != '/call':
            self.send_response(404); self.end_headers(); return
        if self.headers.get('Authorization') != AUTH:
            self.send_response(403); self.end_headers(); return
        try:
            n = int(self.headers.get('Content-Length', 0))
            req = json.loads(self.rfile.read(n) or b'{}')
            url = req['url']
            from urllib.parse import urlparse
            if urlparse(url).hostname != ALLOWED_HOST:
                self.send_response(400); self.end_headers(); return
            import base64
            body = base64.b64decode(req['body_b64']) if req.get('body_b64') else None
            r = urllib.request.Request(url, data=body, method=req.get('method','GET'))
            for k, v in (req.get('headers') or {}).items():
                r.add_header(k, v)
            try:
                with urllib.request.urlopen(r, timeout=60) as resp:
                    data = resp.read(); status = resp.status
                    ctype = resp.headers.get('Content-Type','application/octet-stream')
            except urllib.error.HTTPError as e:
                data = e.read(); status = e.code
                ctype = e.headers.get('Content-Type','application/octet-stream') if e.headers else 'application/octet-stream'
            out = json.dumps({'status': status, 'content_type': ctype,
                              'body_b64': base64.b64encode(data).decode()}).encode()
            self.send_response(200)
            self.send_header('Content-Type','application/json')
            self.send_header('Content-Length', str(len(out)))
            self.end_headers(); self.wfile.write(out)
        except Exception as e:
            msg = str(e).encode()
            self.send_response(500); self.send_header('Content-Length', str(len(msg)))
            self.end_headers(); self.wfile.write(msg)

ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ctx.load_cert_chain('/etc/letsencrypt/live/relayhost/fullchain.pem',
                    '/etc/letsencrypt/live/relayhost/privkey.pem')
srv = ThreadingHTTPServer(('0.0.0.0', 443), H)
srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
print('relay listening on 443')
srv.serve_forever()
