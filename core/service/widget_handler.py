#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author  : loli
# @Date    : 2018-03-15
# @Contact : https://t.me/weep_x
# @tg group: https://t.me/pythonista3dalaoqun

import common
import os

import webbrowser
from utils import py_utils

BASE_DIR = py_utils.load_base_dir(False).split('Documents')[-1]


def open_script(oper, oper_param):
    oper_param = oper_param.replace(' ', '%20')
    args = ''
    if len(oper_param.split('|')) >= 2:
        args = '&args=' + ('%20'.join(oper_param.split('|')[1:]))
        oper_param = oper_param.split('|')[0]

    try:
        webbrowser.open('pythonista3://' + os.path.join(BASE_DIR, oper_param) + '?action=run' + args)
    except:
        py_utils.send_message('启动参数错误，请检查.')


def open_app(oper, oper_param):
    webbrowser.open(oper_param)


def update_store(oper, oper_param):
    if oper == 'update_store':
        py_utils.send_message('正在更新商店,请不要关闭py主程序,等待更新完毕后操作.')


def restart(oper, oper_param):
    os.abort()


def no_thing(oper, oper_param):
    py_utils.send_message(oper_param)


def execute(oper=None, oper_param=''):
    switcher = {
        'update_store': update_store,
        'open_script': open_script,
        'open_app': open_app,
        'restart': restart,
    }
    # Get the function from switcher dictionary
    func = switcher.get(oper, no_thing)
    # Execute the function
    return func(oper, oper_param)


import hashlib
import os


def load_help(file_path):
    help = None
    if os.path.isfile(file_path):
        f = open(file_path, 'rb')
        help_obj = hashlib.md5()
        help_obj.update(f.read())
        hash_code = help_obj.hexdigest()
        f.close()
        help = str(hash_code).lower()
    return help


def pystore_valid():
    return True

# if not pystore_valid():
#    py_utils.send_message('监测到非官方分发版本,可能存在第三方修改或者恶意脚本,请慎用,如有任何问题与原作者无关,另外请大家支持正版app',d=(172800))
