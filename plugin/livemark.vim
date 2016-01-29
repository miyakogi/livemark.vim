
let g:livemark_python = 'python3'
let s:requred_modules = ['tornado', 'misaka', 'pygments']
let s:pyscript = expand('<sfile>:p:h') . '/run.py'
let s:server_pid = 0

function! s:get_text() abort
  let text_list = getline(0, '$')
  call insert(text_list, '<span id="vimcursor"></span>', line('.')-1)
  return text_list
endfunction

function! s:send_text() abort
  let handle = connect('localhost:8090', 'json')
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
  let cmd = g:livemark_python . ' ' . s:pyscript
  let s:server_pid = system(cmd)
endfunction

function! s:stop_server() abort
  if s:server_pid
    call system('kill ' . s:server_pid)
  endif
endfunction

function! s:enable_livemark() abort
  call s:start_server()
  augroup livemark
    autocmd!
    autocmd CursorMoved,TextChanged,TextChangedI <buffer> call s:send_text()
    autocmd VimLeave * call s:stop_server()
  augroup END
endfunction

function! s:disable_livemark() abort
  augroup livemark
    autocmd!
  augroup END
  call s:stop_server()
endfunction

command! LiveMark call s:enable_livemark()
command! LiveMarkDisable call s:disable_livemark()
