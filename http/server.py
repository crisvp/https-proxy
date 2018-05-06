import cache
import BaseHTTPServer


class Server():
    def __init__(self, listen, **kwargs):
        self._server = BaseHTTPServer.HTTPServer(listen,
                                                 HandleRequest,
                                                 **kwargs)

    def serve(self):
        self._server.serve_forever()


class HandleRequest(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        request_url = self.headers['X-Original-Request']
        new_url = cache.cache.apply_rules(request_url)
        if new_url == request_url:
            self.send_response(304)
            self.send_header('Cache-Control', 'no-cache')
        else:
            self.send_response(302)
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Location', new_url)
        self.end_headers()
