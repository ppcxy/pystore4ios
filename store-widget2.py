#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : store-widget2.py
# @Author  : loli
# @Date    : 2018-03-15
# @Version : v0.1 bate
# @Contact : https://t.me/weep_x
# @tg group: https://t.me/pythonista3dalaoqun

import appex
import os


def main():
    widget_name = __file__ + str(os.stat(__file__).st_mtime)
    v = appex.get_widget_view()

    # Optimization: Don't create a new view if the widget already shows the launcher.
    if v is None or v.name != widget_name:
        from utils import py_utils
        from core.ui2.ui_widget import LauncherView

        # load global configs
        MAIN_CONFIG = py_utils.load_config()
        # getter index page buttons

        v = LauncherView(MAIN_CONFIG)
        v.name = widget_name
        appex.set_widget_view(v)


if __name__ == '__main__':
    main()
