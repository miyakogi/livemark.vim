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
from wdom.tag import Div, Style, H2
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
        # global CURSOR_TAG
        # _cursor = False

        # if CURSOR_TAG in text:
        #     # When cursor tag is inserted, one extra \n is inserted
        #     text = text.replace(CURSOR_TAG + '\n', '')
        #     _cursor = True

        # CURSOR_TAG = CURSOR_TAG.replace('\n', '')
        # head = CURSOR_TAG if _cursor else ''

        if not lang:
            # return head + '\n<pre><code>{}</code></pre>\n'.format(text)
            return '\n<pre><code>{}</code></pre>\n'.format(text)
        else:
            lexer = get_lexer_by_name('python', stripall=True)
            lexer = PythonLexer()
            formatter = HtmlFormatter(linenos=True, cssclass="source")
            # return head + highlight(text, lexer, formatter)
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
    _mount_point = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tasks = []

    def data_received(self, data):
        msg = json.loads(data.decode())[1]
        tlist = msg['text']
        line = msg['line']

        for task in self._tasks:
            if not task.done() and not task.cancelled():
                task.cancel()
            self._tasks.remove(task)
        try:
            self._tasks.append(asyncio.ensure_future(self._update(tlist, line)))
        except asyncio.CancelledError:
            pass

    @asyncio.coroutine
    def _update(self, tlist, line):
        _l = []
        self._blank_lines = 0
        i = 1
        while i < len(tlist):
            if tlist[i] == '' and tlist[i - 1] == '':
                self._blank_lines += 1
                i += 1
                continue
            else:
                _l.append(tlist[i])
                i += 1

        self.cur_line = line - self._blank_lines
        html = yield from self.convert_to_html(tlist, self.cur_line)
        yield from self.mount_html(html)
        yield from self._move_to_cursor()

    @asyncio.coroutine
    def convert_to_html(self, tlist, line):
        # global CURSOR_TAG
        # if tlist[line - 1].startswith('```'):
        #     # previous line of the code block must be blank line.
        #     CURSOR_TAG += '\n'
        # tlist.insert(line - 1, CURSOR_TAG)

        _html = converter('\n'.join(tlist))
        # self._mount_point.innerHTML = _html
        # Remove paragraph which only includes cursor tag
        # html = html.replace('<p>' + CURSOR_TAG + '</p>', CURSOR_TAG)
        # CURSOR_TAG = CURSOR_TAG.replace('\n', '')

        html_list = _html.splitlines()
        html_list.insert(line - 1, CURSOR_TAG)
        html = '\n'.join(html_list)
        return html

    @asyncio.coroutine
    def mount_html(self, html):
        fragment = parse_html(html)
        if self._mount_point.length < 1:
            self._mount_point.appendChild(fragment)
        else:
            diff = yield from self.find_diff_node(fragment)
            for _i in diff['inserted']:
                self._mount_point.insertBefore(_i[1], _i[0])
                print('insert:', _i[1].html)
            for _d in diff['deleted']:
                self._mount_point.removeChild(_d)
                print('delete:', _d.html)
            for _a in diff['appended']:
                self._mount_point.appendChild(_a)
                print('append:', _a.html)

    @asyncio.coroutine
    def _move_to_cursor(self):
        print('cursor move called')
        if self._mount_point is not None and self._mount_point.ownerDocument:
            cursor = self._mount_point.ownerDocument.getElementById('vimcursor')
            body = self._mount_point.ownerDocument.body
            try:
                fs = asyncio.gather(cursor.getBoundingClientRect(),
                                    cursor.scrollY())
                done = yield from asyncio.wait_for(fs, 0.1)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                return
            print(done)
            _rect = done[0]
            _y = done[1]
            if _rect is None or _y is None:
                return
            cursor_top = _rect.get('top')
            body_y = _y.get('y')
            if cursor_top is None or body_y is None:
                return
            cursor.scrollTo(0, body_y + cursor_top)
            print('cursor move done')
        else:
            print('cursor not found')

    def _is_same_node(self, node1, node2):
        if node1.nodeType == node2.nodeType:
            if node1.nodeType == node1.TEXT_NODE:
                return node1.textContent == node2.textContent
            else:
                return node1.tagName == node2.tagName \
                    and node1.attributes == node2.attributes \
                    and node1.classList == node2.classList \
                    and node1.innerHTML == node2.innerHTML
        else:
            return False

    @asyncio.coroutine
    def find_diff_node(self, tree):
        _deleted = []
        _inserted = []

        node1 = self._mount_point.firstChild
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
    VimListener._mount_point = Div(parent=doc.body, class_='container')
    VimListener._mount_point.appendChild(H2('LiveMark is running...'))
    app = get_app(doc)
    app.add_static_path('static', static_dir)
    server = start_server(app, port=options.config.browser_port)

    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    coro = loop.create_server(VimListener, 'localhost',
                              options.config.vim_port)
    browser = webbrowser.get(options.config.browser)
    browser.open('http://localhost:{}'.format(options.config.browser_port))
    try:
        asyncio.ensure_future(coro)
        # loop.run_until_complete(coro)
        loop.run_forever()
    except KeyboardInterrupt:
        server.stop()


if __name__ == '__main__':
    options.parse_command_line()
    main()
