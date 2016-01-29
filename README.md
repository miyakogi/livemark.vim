# Livemark.vim

Real-time markdown preview vim plugin.
This plugin requires vim version 7.4.1191+ and `+channel` feature.

## Install

Python 3.4+ and some libraries (misaka, pygments, tornado) are required.

To install them;

```
pip3 install misaka pygments tornado
```

## Usage

Open markdown file and execute `:LiveMark`.
This command open browser (google-chrome) and real-time preview on browser.

To stop preview, execute `:LiveMarkDisable`.

## Screen cast

<img src="https://raw.githubusercontent.com/miyakogi/livemark.vim/master/sample.gif">

## License

[MIT License](https://github.com/miyakogi/livemark.vim/blob/master/LICENSE)

This plugin includes [Honoka](http://honokak.osaka/) (bootstrap theme optimized for Japanese).
