var ws = new WebSocket('ws://localhost:8089/ws')
  ws.onmessage = function(e) {
    var x = document.body.scrollLeft
    var y = document.body.scrollTop
    document.getElementById('livemark').innerHTML = e.data
    var cur = document.getElementById('vimcursor')
    if (cur) {
      pos = y + cur.getBoundingClientRect().bottom - 150
      window.scrollTo(x, pos)
    }
  }
