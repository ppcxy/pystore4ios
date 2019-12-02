#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : ui_widget_setter.py
# @Author  : loli
# @Date    : 2018-03-15
# @Version : 1.0
# @Contact : https://t.me/weep_x
# @tg group: https://t.me/pythonista3dalaoqun

import common
import os
import shutil
import ui
import _ui
import console
from utils import py_utils, file_picker
import css_color_selector, icon_selector

config = py_utils.load_config(os.path.join(py_utils.load_base_dir(False), 'config.json'))
mc = None


def color_callback(color):
    scrv['color'].text = color
    scrv.alpha = 1
    scrv.remove_subview(mc)
    selecter_v.alpha = 0


def font_color_callback(color):
    scrv['t_font_color'].text = color
    scrv.alpha = 1
    scrv.remove_subview(mc)
    selecter_v.alpha = 0


def icon_callback(icon):
    scrv['icon'].text = icon
    scrv.alpha = 1
    scrv.remove_subview(mc)


def selecter(sender):
    _ui.end_editing()
    global mc

    if sender.name == 'btn_color':
        mc = colorsv
        mc.callback = color_callback
    elif sender.name == 'btn_icon':
        mc = iconsv
    elif sender.name == 'btn_font_color':
        mc = colorsv
        mc.callback = font_color_callback
    # selecter.present('sheet', animated=False)
    selecter_v.add_subview(mc)
    selecter_v.alpha = 1


def tcc_action(sender):
    if sender.name == 'tcquxiao':
        pass
    else:
        global py_files

        oper_param = scrv['t_open_param'].text

        if oper_param == '':
            console.alert('请选择脚本或者输入urlscheme')
            return
        title = scrv['title'].text
        color = scrv['color'].text if scrv['color'].text != '' else '#3b73ff'
        font_color = scrv['t_font_color'].text if scrv['t_font_color'].text != '' else '#ffffff'
        icon = scrv['icon'].text
        if icon != '':
            if scrv['icon_iob'] == 0:
                icon = 'iow:' + icon
            else:
                icon = 'iob:' + icon

        btn = {'title': title, 'id': '', 'oper': 'open_script', 'oper_param': '', 'color': color,
               'font_color': font_color, 'icon': icon}

        if type_btn.selected_index == 0:
            try:
                shutil.copyfile(py_files, os.path.join(py_utils.load_base_dir(False), 'ex', py_files.split('/')[-1]))
            except:
                pass
            btn['oper_param'] = os.path.join('ex', py_files.split('/')[-1])
        elif type_btn.selected_index == 1:
            btn['oper_param'] = py_files.split('Documents')[-1]
        elif type_btn.selected_index == 2:
            btn['oper_param'] = scrv['t_open_param'].text
            btn['oper'] = 'open_app'

        tv.data_source.items.append(btn)
    scrv['title'].text = ''
    scrv['color'].text = ''
    scrv['icon'].text = ''
    scrv.alpha = 0
    py_files = None


def edit(sender):
    tv.editing = not tv.editing


def save_config(sender):
    config['btn-h'] = int(v['rh'].text)
    config['btn-c'] = int(v['cc'].text)

    config['ibtns'] = tv.data_source.items
    py_utils.save_config(config, os.path.join(py_utils.load_base_dir(False), 'config.json'))
    console.alert('通知', '保存配置成功.', '确定', hide_cancel_button=True)
    v.close()


def add_jb(sender):
    global py_files
    py_files = file_picker.file_picker_dialog('请选择文件', multiple=False, select_dirs=False, file_pattern=r'^.*\.py$')

    if py_files != None:
        scrv['t_open_param'].text = py_files.split('Documents')[-1]


def add_ex(sender):
    scrv.alpha = 1


py_files = None

v = ui.load_view()
tv = v['data_table']
scrv = v['scrv']
type_btn = scrv['btn_add_type']
tv.data_source.items.clear()
tv.data_source.items.extend(config['ibtns'])
v['rh'].text = str(config['btn-h'])
v['cc'].text = str(config['btn-c'])

w, h = ui.get_screen_size()

if w > 490:
    w = 324
    h = 260
else:
    h = h - 318
    w = w - 23
selecter_v = scrv['selecter_v']
f = (0, 0, w, h)
colorsv = css_color_selector.ColorClass(name='颜色选择器', frame=f, bg_color='white', callback=color_callback)

iconsv = icon_selector.IconClass(name='图标选择器', frame=f, bg_color='white', callback=icon_callback)

v.present('sheet')
