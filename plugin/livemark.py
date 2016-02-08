#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from os import path
import json
import asyncio
import webbrowser
from functools import partial

from tornado import web
from tornado import websocket
from tornado.platform.asyncio import AsyncIOMainLoop

import misaka as m
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, PythonLexer

current_dir = path.dirname(__file__)
sys.path.insert(0, path.join(current_dir, 'wdom'))

from wdom import options
from wdom.tag import Div, Style, H2, Script, WebElement
from wdom.document import get_document
from wdom.server import get_app, start_server
from wdom.parser import parse_html


connections = []
CURSOR_TAG = '<span id="vimcursor"></span>' 
static_dir = path.join(current_dir, 'static')
template_dir = path.join(current_dir, 'template')
css = HtmlFormatter(style='default').get_style_defs()

options.parser.define('browser', default='google-chrome', type=str)
options.parser.define('browser-port', default=8089, type=int)
options.parser.define('vim-port', default=8090, type=int)


class HighlighterRenderer(m.HtmlRenderer):
    def blockcode(self, text, lang):
        if not lang:
            return '\n<pre><code>{}</code></pre>\n'.format(text)
        else:
            lexer = get_lexer_by_name('python', stripall=True)
            lexer = PythonLexer()
            formatter = HtmlFormatter(linenos=True, cssclass="source")
            html = highlight(text, lexer, formatter)
            return html


converter = m.Markdown(HighlighterRenderer(), extensions=(
    'fenced-code',
    'tables',
))


class MainHandler(web.RequestHandler):
    def get(self):
        self.render('main.html', css=css, port=options.config.browser_port)


class WSHandler(websocket.WebSocketHandler):
    def open(self):
        connections.append(self)

    def on_close(self):
        connections.remove(self)


class VimListener(asyncio.Protocol):
    pass


class Server(object):
    def __init__(self, address='localhost', port=8090, loop=None, doc=None,
                 mount_point=None):
        self.address = address
        self.port = port
        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop

        self.doc = doc
        self.script = None
        self.mount_point = mount_point
        self.tlist = []

        self.listener = VimListener
        self.listener.connection_made = self.connection_made
        self.listener.data_received = self.data_received
        self._tasks = []
        self.transport = None

    def start(self):
        self.coro_server = self.loop.create_server(self.listener, self.address,
                                                   self.port)
        self.server_task = self.loop.run_until_complete(self.coro_server)
        return self.server_task

    def stop(self):
        self.server_task.close()

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        self.transport.close()
        for task in self._tasks:
            if not task.done() and not task.cancelled():
                task.cancel()
            self._tasks.remove(task)

        msg = json.loads(data.decode())[1]
        line = msg['line']
        event = msg['event']
        if event == 'update':
            self.tlist = msg['text']
            _task = self.update_preview
        elif event == 'move':
            _task = self.move_cursor
        else:
            raise ValueError('Get unknown event: {}'.format(event))

        try:
            self._tasks.append(asyncio.ensure_future(_task(line)))
        except asyncio.CancelledError:
            pass

    @asyncio.coroutine
    def update_preview(self, line):
        html = yield from self.convert_to_html(self.tlist)
        yield from self.mount_html(html)
        yield from self.move_cursor(line)

    @asyncio.coroutine
    def convert_to_html(self, tlist):
        md = '\n'.join(tlist)
        yield from asyncio.sleep(0.0)
        return converter(md)

    @asyncio.coroutine
    def mount_html(self, html):
        fragment = parse_html(html)
        if self.mount_point.length < 1:
            self.mount_point.appendChild(fragment)
        else:
            diff = yield from self.find_diff_node(fragment)
            for _i in diff['inserted']:
                self.mount_point.insertBefore(_i[1], _i[0])
            for _d in diff['deleted']:
                self.mount_point.removeChild(_d)
            for _a in diff['appended']:
                self.mount_point.appendChild(_a)

    @asyncio.coroutine
    def move_cursor(self, line):
        blank_lines = 0
        i = 1
        while i < len(self.tlist):
            if self.tlist[i] == '' and self.tlist[i - 1] == '':
                blank_lines += 1
                i += 1
                continue
            else:
                i += 1
        cur_line = line - blank_lines

        if self.mount_point is not None and self.mount_point.ownerDocument:
            _l = 0
            elm = self.mount_point.firstChild
            while elm is not None:
                yield from asyncio.sleep(0.0)
                _l += elm.textContent.count('\n')
                if _l >= cur_line:
                    break
                elm = elm.nextSibling

            if elm is not None:
                if isinstance(elm, WebElement):
                    self.move_to(elm.id)
                else:
                    while elm is not None:
                        elm = elm.previousSibling
                        if isinstance(elm, WebElement):
                            self.move_to(elm.id)
                            break

    def move_to(self, id):
        script = 'moveToElement("{}")'.format(id)
        self.mount_point.js_exec('eval', script=script)

    def _is_same_node(self, node1, node2):
        if node1.nodeType == node2.nodeType:
            if node1.nodeType == node1.TEXT_NODE:
                return node1.textContent == node2.textContent
            else:
                return node1.html_noid == node2.html_noid
        else:
            return False

    @asyncio.coroutine
    def find_diff_node(self, tree):
        _deleted = []
        _inserted = []

        node1 = self.mount_point.firstChild
        node2 = tree.firstChild
        last_node2 = node2
        while node1 is not None and node2 is not None:  # Loop over old html
            yield from asyncio.sleep(0.0)
            if self._is_same_node(node1, node2):
                node1 = node1.nextSibling
                node2 = node2.nextSibling
                last_node2 = node2
            else:
                _pending = [node2]
                while True:  # Loop over new html
                    node2 = node2.nextSibling
                    if node2 is None:
                        _deleted.append(node1)
                        node1 = node1.nextSibling
                        node2 = last_node2
                        break
                    elif self._is_same_node(node1, node2):
                        for n in _pending:
                            _inserted.append((node1, n))
                        node1 = node1.nextSibling
                        node2 = node2.nextSibling
                        last_node2 = node2
                        break
                    else:
                        _pending.append(node2)
        n = last_node2
        _appended = []
        while n is not None:
            _appended.append(n)
            n = n.nextSibling

        return {'deleted': _deleted, 'inserted': _inserted,
                'appended': _appended}

def main():
    AsyncIOMainLoop().install()

    doc = get_document()
    doc.add_jsfile(
        'https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js')
    doc.add_jsfile('static/bootstrap.min.js')
    doc.add_cssfile('static/bootstrap.min.css')
    doc.head.appendChild(Style(css))
    script = Script(parent=doc.body)
    script.innerHTML = '''
        function moveToElement(id) {
            var elm = document.getElementById(id)
            if (elm) {
                var x = window.scrollX
                var rect = elm.getBoundingClientRect()
                window.scrollTo(x, rect.top + window.scrollY)
                console.log(elm.textContent)
            }
        }
    '''
    mount_point = Div(parent=doc.body, class_='container')
    mount_point.appendChild(H2('LiveMark is running...'))
    app = get_app(doc, debug=True)
    app.add_static_path('static', static_dir)
    web_server = start_server(app, port=options.config.browser_port)

    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    vim_server = Server(port=options.config.vim_port, loop=loop, doc=doc,
                        mount_point=mount_point)
    browser = webbrowser.get(options.config.browser)
    browser.open('http://localhost:{}'.format(options.config.browser_port))
    try:
        vim_server.start()
        loop.run_forever()
    except KeyboardInterrupt:
        vim_server.stop()
        web_server.stop()


if __name__ == '__main__':
    options.parse_command_line()
    main()
