import cache
import BaseHTTPServer
import logging
import socket

logger = logging.getLogger(__name__)


class Server(BaseHTTPServer.HTTPServer, object):
    def __init__(self, listen, **kwargs):
        sock = socket.getaddrinfo(listen[0], listen[1])
        self.address_family = sock[0][0]

        super(Server, self).__init__((sock[0][4][0], sock[0][4][1]),
                                     HandleRequest, **kwargs)
        logger.info('HTTP server listening on %s, port %d',
                    sock[0][4][0], sock[0][4][1])

    def serve(self):
        self.serve_forever()


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
