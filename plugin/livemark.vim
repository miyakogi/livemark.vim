scriptencoding utf-8

if get(g:, 'loaded_livemark', 0)
  finish
else
  let g:loaded_livemark = 1
endif

" set default values
let g:livemark_python = get(g:, 'livemark_python', 'python3')
let g:livemark_browser = get(g:, 'livemark_browser', 'google-chrome')
let g:livemark_browser_port = get(g:, 'livemark_browser_port', 8089)
let g:livemark_vim_port = get(g:, 'livemark_vim_port', 8090)
let g:livemark_force_pysocket = get(g:, 'livemark_force_pysocket', 0)

let g:livemark_no_default_js = get(g:, 'livemark_no_default_js', 0)
let g:livemark_no_default_css = get(g:, 'livemark_no_default_css', 0)
let g:livemark_js_files = get(g:, 'livemark_js_files', [])
let g:livemark_css_files = get(g:, 'livemark_css_files', [])
let g:livemark_highlight_theme = get(g:, 'livemark_highlight_theme', '')

command! LiveMark call livemark#enable_livemark()
command! LiveMarkDisable call livemark#disable_livemark()

" vim set\ ts=2\ sts=2\ sw=2\ et
