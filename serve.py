import http.server
import socketserver
import os
import urllib.parse
import json

PORT = int(os.environ.get("PORT", 3000))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class SyncBubblesHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_POST(self):
        # Handle presence or demand pings
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(b'{"ok": true}')

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Handle API routes
        api_map = {
            '/api/public/snapshot': 'api/public/snapshot_k_boot.json',
            '/api/public/fn/api/leaderboard': 'api/public/fn/api/leaderboard_data.json',
            '/api/public/fn/api/feed/copies': 'api/public/fn/api/feed_copies.json',
            '/api/public/fn/api/kol/transactions': 'api/public/fn/api/kol_transactions.json',
            '/api/public/live': 'api/public/live_data.json',
            '/api/public/fn/api/tokens': 'api/public/fn/api/tokens',
            '/api/public/fn/api/copy/last': 'api/public/fn/api/copy/last'
        }

        for api_prefix, target_file in api_map.items():
            if path == api_prefix:
                full_target = os.path.join(BASE_DIR, target_file)
                if os.path.exists(full_target):
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    with open(full_target, 'rb') as f:
                        self.wfile.write(f.read())
                    return

        # Handle clean URLs for SPA
        if path.startswith('/app') and not os.path.exists(os.path.join(BASE_DIR, path.lstrip('/'))):
            app_html = os.path.join(BASE_DIR, 'app', 'index.html')
            if os.path.exists(app_html):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                with open(app_html, 'rb') as f:
                    self.wfile.write(f.read())
                return

        return super().do_GET()

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), SyncBubblesHandler) as httpd:
        print(f"🚀 SyncBubbles server running on http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
