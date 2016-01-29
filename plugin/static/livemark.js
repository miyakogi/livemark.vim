var ws = new WebSocket('ws://localhost:8089/ws')
  ws.onmessage = function(e) {
    var x = document.body.scrollLeft
    var y = document.body.scrollTop
    document.getElementById('livemark').innerHTML = e.data
    var cur = document.getElementById('vimcursor')
    if (cur) {
      pos = y + cur.getBoundingClientRect().bottom - 150
      // if (pos >= 0) {
        window.scrollTo(x, pos)
        console.log(pos);
      // } else {
        // console.log('pos negative');
        // console.log(pos);
        // window.scrollTo(x, y)
      // }
    } else {
      console.log('cursor not found');
      // window.scrollTo(x, y)
    }
  }
