#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import ui


def load():
    v = ui.load_view()
    v.present('sheet')


if __name__ == '__main__':
    load()
