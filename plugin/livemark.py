#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import path
import json
import asyncio
import webbrowser

from tornado import web
from tornado import websocket
from tornado.platform.asyncio import AsyncIOMainLoop
from tornado.ioloop import IOLoop

import misaka as m
from pygments import highlight
from pygments.styles import get_style_by_name
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name


connections = []
static_dir = path.join(path.dirname(__file__), 'static')
browser_port = 8089

css = HtmlFormatter(style='default').get_style_defs()
page = '''
<!DOCTYPE html>
<html>
<head>
<title>LiveMark</title>
<link rel="stylesheet" href="static/bootstrap.min.css">
<style>
{}
</style>
</head>
<body>
<div id="livemark" class="container"></div>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
<script type="text/javascript" src="static/bootstrap.min.js"></script>
<script type="text/javascript" src="static/livemark.js"></script>
</body>
</html>
'''.format(css)


class HighlighterRenderer(m.HtmlRenderer):
    def blockcode(self, text, lang):
        marker = '<span id="vimcursor"></span>'
        _cursor = False
        if marker in text:
            text = text.replace(marker, '')
            _cursor = True
        if not lang:
            return '\n<pre><code>{}</code></pre>\n'.format(text.strip())
        lexer = get_lexer_by_name(lang)
        formatter = HtmlFormatter()
        if _cursor:
            return marker + highlight(text, lexer, formatter)
        else:
            return highlight(text, lexer, formatter)


converter = m.Markdown(HighlighterRenderer(), extensions=('fenced-code',))


class MainHandler(web.RequestHandler):
    def get(self):
        self.write(page)


class WSHandler(websocket.WebSocketHandler):
    def open(self):
        connections.append(self)

    def on_close(self):
        connections.remove(self)


class VimListener(asyncio.Protocol):
    def data_received(self, data):
        msg = data.decode()
        text = '\n'.join(json.loads(msg)[1])
        html = converter(text)
        for conn in connections:
            conn.write_message(html)


def main():
    AsyncIOMainLoop().install()
    app = web.Application([
        ('/', MainHandler),
        ('/ws', WSHandler),
        ('/static/(.*)', web.StaticFileHandler, {'path':static_dir}),
    ])
    app.listen(browser_port)
    loop = asyncio.get_event_loop()
    coro = loop.create_server(VimListener, 'localhost', 8090)
    browser = webbrowser.get('google-chrome')
    browser.open('http://localhost:{}'.format(browser_port))
    loop.run_until_complete(coro)
    loop.run_forever()


if __name__ == '__main__':
    main()
