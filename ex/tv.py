import ui
import time, console

v = ui.load_view()
v['wv'].load_url('http://www.82190555.com/index.php?url=http://m.iqiyi.com/v_19rr0nztrg.html')
v.present('sheet')
time.sleep(3)
v['wv'].eval_js('window.location.href=document.getElementsByTagName("iframe")[2].src;')
