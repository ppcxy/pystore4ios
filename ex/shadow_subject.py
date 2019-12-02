#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import common
import sys
import clipboard
import webbrowser

import urllib.request
from bs4 import BeautifulSoup
from utils import py_utils

# 构造http访问对象
req = urllib.request.Request('https://tool.ssrshare.com/tool/free_ssr')
req.add_header('User-Agent',
               'Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_6 like Mac OS X) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0 Mobile/15D100 Safari/604.1')

response = urllib.request.urlopen(req)
the_page = response.read()

# 解析返回的html
soup = BeautifulSoup(the_page, 'html.parser')

# input.mdui-textfield-input 获取
all_div = soup.find_all('input', attrs={'class': 'mdui-textfield-input'}, limit=3)

subjectUrl = all_div[1]
clipboard.set(subjectUrl['value'])

py_utils.send_message('订阅地址已复制到剪切板，请粘贴到支持订阅的app使用.')
# webbrowser.open('ssr://')
