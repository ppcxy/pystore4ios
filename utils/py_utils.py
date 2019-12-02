#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : py_utils.py
# @Author  : loli
# @Date    : 2018-03-15
# @Version : v0.1 bate(内部测试版)
# @Contact : https://t.me/weep_x
# @tg group: https://t.me/pythonista3dalaoqun
import common
import json
import os
from utils import notification


def load_base_dir(relative=True):
    base_path = __file__.split('utils')[0]

    if relative:
        return base_path.split('/')[-2]
    return base_path


def send_message(msg='', title='', d=1):
    x = notification.schedule(msg, delay=d, sound_name='arcade:Coin_2', action_url=None)
    # q.enqueue((msg,title,d))


def load_config(file='config.json', default=True):
    if default:
        file = os.path.join(load_base_dir(False), file)
    f = open(file, mode='r', encoding='utf-8')
    return json.load(f)


def save_config(config, file='config.json'):
    f = open(file, mode='w', encoding='utf-8')
    json.dump(config, f, ensure_ascii=False, indent=2)
