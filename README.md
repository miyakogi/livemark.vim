# Livemark.vim

Real-time markdown preview plugin for vim.

## Requirements

Vim which has `+channel with patch7.4.1263` **or** `+python` feature.

Python 3.4+ (3.5+ is better) and some libraries (misaka, pygments, tornado) are also required to be installed in your `$PATH`.

To install them:

```
pip3 install misaka pygments tornado
```

Thanks to the new channel feature, this plugin does not requre `+python`, `+python3`, or any other process control plugins.
But if `+channel` is not available, this plugin uses `:python` for socket connection.

## Install

This plugin is using git submodule.

If you are using [NeoBundle](https://github.com/Shougo/neobundle.vim) to manage plugins, it will automatically enable submodules by default. So you can install this plugin by simply adding `NeoBundle 'miyakogi/livemark.vim'` in your vimrc and then execute `:NeoBundleInstall`.

However, if you are using other plugin manager which does not support submodules, or installing manually, you need to update submodule after installation. To manually install this plugin, please execute `git clone --recursive https://github.com/miyakogi/livemark.vim`.

## Usage

Open markdown file and execute `:LiveMark`.
This command opens browser (google-chrome by default) and starts real-time previewing on browser.

To stop previewing, execute `:LiveMarkDisable` command.

## Configuration

#### Python binary

This plugin uses python3 installed in your path by default.
If you want to use another python, you can specify the path as follows:

```vim
let g:livemark_python = '/path/to/python/binary'  " default 'python3'
```

#### Browser

By default, this plugin use `google-chrome` to show preview.
To use other browser, for example, firefox, set `g:livemark_browser` variable in your vimrc.

```vim
let g:livemark_browser = 'firefox'  "default: 'google-chrome'
```

This value is passed to python's webbrowser module.
Available browsers and corresponding names are listed [here](https://docs.python.org/3/library/webbrowser.html#webbrowser.register).

#### Connections

For now, this plugin uses two ports; one for tornado web-server (8089), and the other for sending markdown texts from vim (8090).
If you want to change these port numbers, add the following lines to your vimrc and change values as you like.

```vim
let g:livemark_browser_port = 8089
let g:livemark_vim_port = 8090
```

The following setting forces to use `python` to send markdown text, instead of `channel`:

```vim
let g:livemark_force_pysocket = 1  "default: 0
```

#### CSS/JS files

By default, [Honoka](http://honokak.osaka/) bootstrap theme is used for preview. If you want to use other css/js, use these options.

```vim
let g:livemark_js_files = [expand('~/path/to/your/js_file.js')]     " default []
let g:livemark_css_files = [expand('~/path/to/your/css_file.css')]  " default []
```

If you don't want to include defualt css/js files (jQuery, bootstrap.js and bootstrap.css), use these options.

```vim
let g:livemark_no_default_js = 1   " default 0
let g:livemark_no_default_css = 1  " default 0
```

#### Syntax highlighting

Livemark.vim supports code blocks and syntax highlighting.
If you change theme of the code block, add the below option.

```vim
let g:livemark_highlight_theme = 'friendly'  " default ''
```

To list all available themes, run below command in shell.

```sh
python3 -c "import pygments.styles; print(pygments.styles.STYLE_MAP.keys())"
```

## Screen cast

<img src="https://raw.githubusercontent.com/miyakogi/livemark.vim/master/sample.gif">

## License

[MIT License](https://github.com/miyakogi/livemark.vim/blob/master/LICENSE)

This plugin includes [Honoka](http://honokak.osaka/) (bootstrap theme optimized for Japanese).
