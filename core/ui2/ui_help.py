#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : ui_help.py
# @Author  : loli
# @Date    : 2018-03-15
# @Version : 1.0
# @Contact : https://t.me/weep_x
# @tg group: https://t.me/pythonista3dalaoqun

import ui

v = ui.load_view()
vv = v.subviews[0]
vv.load_url(__file__[:-10] + 'ui_help.html')
v.present('sheet')
