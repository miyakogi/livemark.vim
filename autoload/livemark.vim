scriptencoding utf-8

let s:requred_modules = ['tornado', 'misaka', 'pygments']
let s:pyscript = expand('<sfile>:p:h:h') . '/plugin/run.py'
let s:server_pid = 0

function! s:get_text() abort
  let msg = {}
  let msg.text = getline(0, '$')
  let msg.line = line('.')
  let msg.ext = &filetype
  return msg
endfunction

function! s:send_text() abort
  let handle = connect('localhost:' . g:livemark_vim_port, 'json')
  call sendexpr(handle, s:get_text(), 0)
  call disconnect(handle)
endfunction

function! s:check_pymodule(module) abort
  let cmd = system(g:livemark_python . ' -c "import ' . a:module . '"')
  if len(cmd) > 0
    return 1
  else
    return 0
  endif
endfunction

function! s:start_server() abort
  if !has('channel')
    echoerr 'LiveMark.vim requires +channel feature'
    return 0
  endif

  let _error_modules = []
  for m in s:requred_modules
    let _err = s:check_pymodule(m)
    if _err
      echoerr 'Module ' . m . ' is not installed.'
      call add(_error_modules, m)
    endif
  endfor
  if len(_error_modules)
    return 0
  endif

  let l:options = ' --browser=' . g:livemark_browser
        \     . ' --browser-port=' . g:livemark_browser_port
        \     . ' --vim-port=' . g:livemark_vim_port
  let cmd = g:livemark_python . ' ' . s:pyscript . l:options
  let s:server_pid = system(cmd)
endfunction

function! s:stop_server() abort
  if s:server_pid
    call system('kill ' . s:server_pid)
  endif
endfunction

function! livemark#enable_livemark() abort
  call s:start_server()
  augroup livemark
    autocmd!
    autocmd CursorMoved,TextChanged,TextChangedI <buffer> call s:send_text()
    autocmd VimLeave * call s:stop_server()
  augroup END
endfunction

function! livemark#disable_livemark() abort
  augroup livemark
    autocmd!
  augroup END
  call s:stop_server()
endfunction

" vim set\ ts=2\ sts=2\ sw=2\ et
