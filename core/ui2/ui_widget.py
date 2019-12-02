#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : loli
# @Date    : 2018-03-15
# @Contact : https://t.me/weep_x
# @tg group: https://t.me/pythonista3dalaoqun

import common
import ui
from math import ceil, floor

from core.service import widget_handler


# UI layout
class LauncherView(ui.View):
    # layout basic param
    cols = 3
    rows = 0
    row_height = 54

    def __init__(self, main_config, *args, **kwargs):
        shortcuts = main_config['ibtns']
        self.row_height = main_config['btn-h']
        self.cols = main_config['btn-c']
        self.rows = ceil(len(shortcuts) / self.cols)

        super().__init__(self, frame=(0, 0, 800, self.rows * self.row_height), *args, **kwargs)

        self.buttons = []
        for s in shortcuts:
            iconstr = s.get('icon', '')

            if iconstr != '':
                try:
                    img = ui.Image(s.get('icon', 'iow:bag_24'))
                except Exception as e:
                    img = None
            else:
                img = None
            btn = ui.Button(title=s['title'], image=img, action=self.button_action, bg_color=s.get('color', '#55bcff'),
                            tint_color=s.get('font_color', '#000000'), corner_radius=5)

            btn.oper = s['oper']
            btn.oper_param = s['oper_param']

            self.add_subview(btn)
            self.buttons.append(btn)

    def layout(self):
        self.height = (self.row_height + 3) * self.rows
        bw = self.width / self.cols
        bh = self.row_height

        for i, btn in enumerate(self.buttons):
            btn.frame = ui.Rect(i % self.cols * bw, i // self.cols * bh, bw, bh).inset(3, 3)
            btn.alpha = 0.7  # if btn.frame.max_y < self.height else 0

    def button_action(self, sender):
        executeOper(sender)


def executeOper(action):
    widget_handler.execute(action.oper, action.oper_param)
