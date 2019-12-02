#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : pystore.py
# @Author  : loli
# @Date    : 2018-03-15
# @Version : v0.1 bate(内部测试版)
# @Contact : https://t.me/weep_x
# @tg group: https://t.me/pythonista3dalaoqun
import common
import os
import appex
from utils import py_utils
from objc_util import *

_runas = 0

# load global configs
MAIN_CONFIG = py_utils.load_config()
# getter index page buttons
SHORTCUTS = MAIN_CONFIG['ibtns']
MAIN_CONFIG = None


def main():
    if appex.is_running_extension():
        from core.ui2 import ui_extension_menu
        ui_extension_menu.load()
    else:
        from core.ui2 import ui_sys_conf
        ui_sys_conf.load()


if __name__ == '__main__':
    main()
