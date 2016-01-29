# Livemark.vim

Real-time markdown preview vim plugin.

## Requirements

Vim version 7.4.1191+ with `+channel` feature.

Python 3.4+ (3.5+ is better) and some libraries (misaka, pygments, tornado) are also required to be installed in your `$PATH`.

To install them:

```
pip3 install misaka pygments tornado
```

Thanks to the new channel feature, this plugin does not requre `+python`, `+python3`, or any other process control plugins.
Simply use python in your system path.

## Usage

Open markdown file and execute `:LiveMark`.
This command opens browser (google-chrome by default) and starts real-time previewing on browser.

To stop previewing, execute `:LiveMarkDisable` command.

## Configuration

#### Python binary

This plugin uses python3 installed in your path by default.
If you want to use another python, you can specify the path as follows:

```vim
let g:livemark_python = '/path/to/python/binary'
```

#### Browser

By default, this plugin use `google-chrome` to show preview.
To use other browser, for example, firefox, set `g:livemark_browser` variable in your vimrc.

```vim
let g:livemark_browser = 'firefox'
```

This value is passed to python's webbrowser module.
Available browsers and corresponding values are listed [here](https://docs.python.org/3/library/webbrowser.html#webbrowser.register).

#### Port

For now, this plugin uses two ports; one for tornado web-server (8089), and the other for sending markdown texts from vim (8090).
If you want to change these ports, add the following lines to your vimrc and change values as you like.

```vim
let g:livemark_browser_port = 8089
let g:livemark_vim_port = 8090
```

## Screen cast

<img src="https://raw.githubusercontent.com/miyakogi/livemark.vim/master/sample.gif">

## License

[MIT License](https://github.com/miyakogi/livemark.vim/blob/master/LICENSE)

This plugin includes [Honoka](http://honokak.osaka/) (bootstrap theme optimized for Japanese).
