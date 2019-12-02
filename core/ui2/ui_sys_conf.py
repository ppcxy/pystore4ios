#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import common
import ui

from core.db import sys_config_dao
from core.service import widget_handler

_UPDATE_STORE = 'update_store'
_UPDATE_SCRIPT = 'update_script'
_notifications = 'notifications'


def pystore_action(sender):
    widget_handler.open_script('', oper_param='core/ui2/ui_widget_setter')


def table_action(sender):
    print(sender.selected_row)


def switch_store_update_action(sender):
    sys_config_dao.setter(_UPDATE_STORE, str(sender.value))


def switch_script_update_action(sender):
    sys_config_dao.setter(_UPDATE_SCRIPT, str(sender.value))


def switch_notifications_action(sender):
    sys_config_dao.setter(_notifications, str(sender.value))


def load():
    v = ui.load_view()
    sv = v.subviews[0]

    tv = sv['tv']
    tv.allows_selection = False
    sv[_UPDATE_STORE].value = sys_config_dao.load_config(_UPDATE_STORE) == 'True'
    sv[_UPDATE_SCRIPT].value = sys_config_dao.load_config(_UPDATE_SCRIPT) == 'True'
    sv[_notifications].value = sys_config_dao.load_config(_notifications) == 'True'

    v.present('sheet')


if __name__ == '__main__':
    load()
