#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : devtools.py
# @Author  : loli
# @Date    : 2018-03-18
# @Version : 1.0
# @Contact : https://t.me/weep_x

import ui
from objc_util import UIApplication, ObjCInstance
from ctypes import cast, py_object, c_void_p
import clipboard, editor
import scene


class SideBar(ui.View):
    def __init__(self, width=30, *args, **kwargs):
        '''initialize the sidebar
        arguments:
        width (default = 30)
        '''
        app = UIApplication.sharedApplication()
        self.containerView = app.keyWindow().rootViewController(). \
            detailContainerView()
        # we will add ourself as a subview of the container view, on the right edge, and also resize the other subviews to fit.
        self.background_color = 'white'
        self.alpha = 1
        self.width = width
        self.y = 0

        self.height = self.containerView.frame().size.height
        self.siblings = self.containerView.subviews()
        close = ui.Button(image=ui.Image('iob:close_round_24'))
        close.frame = [2, 35, 24, 24]
        close.action = self._close
        self.add_subview(close)
        self.flex = 'LH'
        ObjCInstance(self).tag = hash('SideBar')

    def layout(self):
        '''resize other views when this view changes width'''
        for sib in self.siblings:
            f = sib.frame()
            if f.size.width + self._width == self.containerView.frame().size.width:
                f.size.width = self.containerView.frame().size.width - self.width
                sib.frame = f
            self._width = self.width
            self.x = self.containerView.frame().size.width - self.width

    def present(self):
        '''if another sidebar is being presented, close it first.  add to the editor window, shrinking other content'''
        if self.on_screen:
            return
        for sib in self.siblings:
            if sib.tag() == hash('SideBar'):
                sib.removeFromSuperview()
            else:
                f = sib.frame()
                if f.size.width == self.containerView.frame().size.width:
                    f.size.width -= self.width
                    sib.frame = f
            self.x = self.containerView.frame().size.width - self.width
            self.containerView.addSubview_(ObjCInstance(self))
            self._width = self.width

    def close(self):
        '''for programmatic close'''
        self._close(self)

    def _close(self, sender):
        ''' button callback. reset siblings, and close subview'''
        ObjCInstance(self).removeFromSuperview()
        for sib in self.siblings:
            f = sib.frame()
            if f.size.width == self.containerView.frame().size.width - self.width:
                f.size.width += self.width
                sib.frame = f
        if hasattr(self, 'will_close') and callable(self.will_close):
            self.will_close()


def select_action_r(self):
    i = editor.get_selection()
    editor.set_selection(i[0], i[1] + 1)


def select_action_l(self):
    i = editor.get_selection()
    editor.set_selection(i[0] - 1, i[1])


def copy_action(sender):
    i = editor.get_selection()
    t = editor.get_text()
    clipboard.set(t[i[0]:i[1]])


def paste_action(sender):
    i = editor.get_selection()
    t = editor.get_text()
    editor.replace_text(i[0], i[1], clipboard.get())
    editor.set_selection(i[0], i[1] - len(t) + len(editor.get_text()))


def cut_action(sender):
    i = editor.get_selection()
    t = editor.get_text()
    clipboard.set(t[i[0]:i[1]])
    editor.replace_text(i[0], i[1], '')
    editor.set_selection(i[0], i[0])


def indent(self):
    """indent selected lines by one tab"""
    import editor
    import re

    i = editor.get_line_selection()
    t = editor.get_text()
    # replace every occurance of newline with  newline plus indent, except last newline

    INDENTSTR = '    '
    editor.replace_text(i[0], i[1] - 1, INDENTSTR + re.sub(r'\n', r'\n' + INDENTSTR, t[i[0]:i[1] - 1]))

    editor.set_selection(i[0], i[1] - len(t) + len(editor.get_text()))


def unindent(self):
    """unindent selected lines all the way"""
    import editor
    import textwrap

    i = editor.get_line_selection()
    t = editor.get_text()

    editor.replace_text(i[0], i[1], textwrap.dedent(t[i[0]:i[1]]))

    editor.set_selection(i[0], i[1] - len(t) + len(editor.get_text()))


def comment_action(sender):
    """" comment out selected lines"""
    import re
    COMMENT = '#'
    i = editor.get_line_selection()
    t = editor.get_text()
    # replace every occurance of newline with  ewline plus COMMENT, except last newline
    editor.replace_text(i[0], i[1] - 1, COMMENT + re.sub(r'\n', r'\n' + COMMENT, t[i[0]:i[1] - 1]))
    editor.set_selection(i[0], i[1] - len(t) + len(editor.get_text()))


def uncomment_action(self):
    """" uncomment selected lines"""
    import re
    COMMENT = '#'
    i = editor.get_line_selection()
    t = editor.get_text()
    # replace every occurance of newline # with newline, except last newline
    if all([x.startswith('#') for x in t[i[0]:i[1] - 1].split(r'\n')]):
        editor.replace_text(i[0], i[1] - 1, re.sub(r'^' + COMMENT, r'', t[i[0]:i[1] - 1], flags=re.MULTILINE))
    editor.set_selection(i[0], i[1] - len(t) + len(editor.get_text()))


def execlines_action(self):
    """execute selected lines in console.   """
    import textwrap
    a = editor.get_text()[editor.get_line_selection()[0]:editor.get_line_selection()[1]]
    exec(textwrap.dedent(a))


if __name__ == '__main__':
    v = SideBar()

    s = ui.ScrollView()
    s.always_bounce_vertical = True
    s.height = 350
    s.y = 64
    s.x = 3
    s.border_width = 1
    s.border_color = '#cccccc'

    px = 0
    ps = 40
    b02 = ui.Button(image=ui.Image('iow:chevron_right_24'))
    b02.action = select_action_r
    s.add_subview(b02)
    b02.y = px = px + 0
    b02.x = 0

    b02_1 = ui.Button(image=ui.Image('iow:chevron_left_24'))
    b02_1.action = select_action_l
    s.add_subview(b02_1)
    b02_1.y = px = px + ps
    b02_1.x = 0

    b03 = ui.Button(image=ui.Image('iob:ios7_copy_outline_32'))
    b03.action = copy_action
    s.add_subview(b03)
    b03.y = px = px + ps
    b03.x = 0

    b04 = ui.Button(image=ui.Image('iob:ios7_trash_outline_32'))
    b04.action = cut_action
    s.add_subview(b04)
    b04.y = px = px + ps
    b04.x = 0

    b05 = ui.Button(image=ui.Image('iob:clipboard_32'))
    b05.action = paste_action
    s.add_subview(b05)
    b05.y = px = px + ps
    b05.x = 0

    b06 = ui.Button(image=ui.Image('iob:ios7_skipforward_outline_32'))
    b06.action = indent
    s.add_subview(b06)
    b06.y = px = px + ps
    b06.x = 0

    b07 = ui.Button(image=ui.Image('iob:ios7_skipbackward_outline_32'))
    b07.action = unindent
    s.add_subview(b07)
    b07.y = px = px + ps
    b07.x = 0

    b08 = ui.Button(image=ui.Image('iob:pound_24'))
    b08.action = comment_action
    s.add_subview(b08)
    b08.y = px = px + ps
    b08.x = 0

    b09 = ui.Button(image=ui.Image('iow:pound_24'))
    b09.action = uncomment_action

    # b09.tint_color = 'green'
    b09.title = '-'
    b09.tint_color = '#cccccc'
    s.add_subview(b09)
    b09.y = px = px + ps
    b09.x = 0

    b10 = ui.Button(image=ui.Image('iow:flash_24'))
    b10.action = execlines_action
    b10.title = '-'
    s.add_subview(b10)
    b10.y = px = px + ps
    b10.x = 0

    s.content_size = (0, px + 40)
    v.add_subview(s)
    v.present()
