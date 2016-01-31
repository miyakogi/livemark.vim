#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import path
import json
import asyncio
import webbrowser

from tornado import web
from tornado import websocket
from tornado import options
from tornado.platform.asyncio import AsyncIOMainLoop
from tornado.ioloop import IOLoop

import misaka as m
from pygments import highlight
from pygments.styles import get_style_by_name
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name


connections = []
CURSOR_TAG = '<span id="vimcursor"></span>' 
static_dir = path.join(path.dirname(__file__), 'static')
template_dir = path.join(path.dirname(__file__), 'template')
css = HtmlFormatter(style='default').get_style_defs()

options.define('browser', default='google-chrome')
options.define('browser-port', default=8089)
options.define('vim-port', default=8090)


class HighlighterRenderer(m.HtmlRenderer):
    def blockcode(self, text, lang):
        global CURSOR_TAG
        _cursor = False

        if CURSOR_TAG in text:
            # When cursor tag is inserted, one extra \n is inserted
            text = text.replace(CURSOR_TAG + '\n', '')
            _cursor = True

        CURSOR_TAG = CURSOR_TAG.replace('\n', '')
        head = CURSOR_TAG if _cursor else ''

        if not lang:
            return head + '\n<pre><code>{}</code></pre>\n'.format(text)
        else:
            lexer = get_lexer_by_name(lang)
            formatter = HtmlFormatter()
            return head + highlight(text, lexer, formatter)


converter = m.Markdown(HighlighterRenderer(), extensions=('fenced-code',))


class MainHandler(web.RequestHandler):
    def get(self):
        self.render('main.html', css=css, port=options.options.browser_port)


class WSHandler(websocket.WebSocketHandler):
    def open(self):
        connections.append(self)

    def on_close(self):
        connections.remove(self)


class VimListener(asyncio.Protocol):
    def data_received(self, data):
        msg = json.loads(data.decode())[1]
        tlist = msg['text']
        line = msg['line']

        global CURSOR_TAG
        if tlist[line - 1].startswith('```'):
            # previous line of the code block must be blank line.
            CURSOR_TAG += '\n'
        tlist.insert(line - 1, CURSOR_TAG)

        html = converter('\n'.join(tlist))
        # Remove paragraph which only includes cursor tag
        html = html.replace('<p>' + CURSOR_TAG + '</p>', CURSOR_TAG)

        for conn in connections:
            conn.write_message(html)
        CURSOR_TAG = CURSOR_TAG.replace('\n', '')


def main():
    AsyncIOMainLoop().install()
    app = web.Application(
        [('/', MainHandler), ('/ws', WSHandler),
         ('/static/(.*)', web.StaticFileHandler, {'path':static_dir}), ],
        template_path=template_dir,
    )
    app.listen(options.options.browser_port)
    loop = asyncio.get_event_loop()
    coro = loop.create_server(VimListener, 'localhost',
                              options.options.vim_port)
    browser = webbrowser.get(options.options.browser)
    browser.open('http://localhost:{}'.format(options.options.browser_port))
    loop.run_until_complete(coro)
    loop.run_forever()


if __name__ == '__main__':
    options.parse_command_line()
    main()
