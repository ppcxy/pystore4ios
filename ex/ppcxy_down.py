#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : ppcy_down.py
# @Author  : loli
# @Date    : 2018-04-04
# @Version : 1.2
# @Contact : https://t.me/weep_x

'''
v1.2 2018-04-04 19:30
__处理重命名时自动获取扩展名
支持下载后手动输入重命名(直接确定不改名)
支持请求头的使用,支持连接中带请求头和手动输入请求头.
手动输入请求头请复制标准格式,如下:

Accept: */*
Accept-Encoding: br, gzip, deflate
Accept-Language: zh-cn
Connection: keep-alive
Cookie: buvid3=6ECDF61E-C916-41AD-AE13-80638BD9AA4012226infoc; finger=f001cced
Host: app.bilibili.com
User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_2 like Mac OS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0 Mobile/15C202 Safari/604.1

v0.2 2018-03-06 01:30
更新进度展示为行内

v0.1 2018-03-05 23:0
直链资源下载，默认检查共享(支持thor导出)，支持获取剪切板，支持手动输入
'''

import os
import urllib.request, urllib.parse, urllib.error
import base64, json
import appex, clipboard, re, console

# 资源保存文件夹
tmp_dir = os.path.expanduser('~/Documents/ppcxy_downloads')
if not os.path.exists(tmp_dir):
    os.mkdir(tmp_dir)


# 头信息处理
def req_header_build(url, use_header_str=''):
    req_header = []

    if use_header_str != '':
        use_req_header = re.split('([A-Za-z-]+):', use_header_str)
        for num in range(1, len(use_req_header), 2):
            req_header.append((use_req_header[num], use_req_header[1]))
    else:
        header_tag_index = url.find('#')
        if header_tag_index > 0:
            base64_header = url.split('#')[-1]
            if base64_header != '':
                head_json = json.loads(bytes.decode(base64.b64decode(base64_header)))
                for i, key in enumerate(head_json):
                    req_header.append((key, head_json[key]))

    # 绑定 header信息
    if len(req_header) == 0:
        req_header = [('User-Agent',
                       'Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_2 like Mac OS X) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0 Mobile/15C202 Safari/604.1')]
        print('使用默认 header\n')
    else:
        print('使用自定义header\n')

    opener = urllib.request.build_opener()
    opener.addheaders = req_header
    urllib.request.install_opener(opener)

    # for i, val in enumerate(req_header):
    #   print('%s: %s' % val)


# 进度跟踪
def Schedule(blocknum, blocksize, totalsize):
    per = 100.0 * blocknum * blocksize / totalsize
    if per > 100:
        per = 100
    print('\b\b\b\b\b\b\b%.2f%%' % per, end='')


# 下载方法
def download(url, req_header='', fileName='place_rename_me.ppcxy'):
    print('下载地址：\n' + url)
    print('\n')

    # 处理请求头
    # 处理请求头 begin -----------------------------------------
    print('请求头信息处理中...：')
    req_header_build(url, req_header)
    print('请求头信息处理完毕...：')
    # 处理请求头 end ------------------------------------------

    # 截取文件名
    # 截取文件名 begin -----------------------------------------
    url_file_name = url.split('/')[-1].split('?')[0].split('#')[0]

    if len(url_file_name) > 125 or url_file_name == 0:
        url_file_name = fileName
        print('未读取到文件名，下载后请自行修改：\n' + url_file_name)
    else:
        print('准备下载文件：\n' + url_file_name)
    url_file_name = os.path.join(tmp_dir, url_file_name)
    # 截取文件名 end ------------------------------------------

    print('\n努力下载中 ...      ', end=' ')
    urllib.request.urlretrieve(url, url_file_name, Schedule)

    new_file_name = console.input_alert('幸不辱命，下载完毕，如果要对文件重名请请输入(不修改不输入即可)：')

    # xxx 处理自定义重命名,如果命名后没有拓展名可能导致py编辑器崩溃,所以如果没有拓展名自动加.ppcxy
    if new_file_name != '':
        if new_file_name.find('.') < 0:
            if url_file_name.find('.') < 0:
                new_file_name = new_file_name + '.ppcxy'
            else:
                new_file_name = new_file_name + '.' + url_file_name.split('.')[-1]

        os.rename(url_file_name, os.path.join(tmp_dir, new_file_name))
        print('\n文件存储路径，去去看看吧：\n' + new_file_name)
    else:
        if url_file_name.find('.') < 0:
            new_file_name = url_file_name + '.ppcxy'
            os.rename(url_file_name, os.path.join(tmp_dir, new_file_name))
        print('\n文件存储路径，去去看看吧：\n' + url_file_name)


# 程序入口
def main():
    # 三种入口方式
    if appex.is_running_extension() and re.search('https*:\/\/[^\s]+', appex.get_attachments()[0]) is not None:
        url = appex.get_attachments()[0]
    else:
        clip = re.search('https*:\/\/[^\s]+', clipboard.get())

        if clip is None:
            url = console.input_alert('请输入直链或者资源地址：')
        else:
            url = clipboard.get()

    req_header = console.input_alert('请输入请求头，如果没有请不要输入(直接确定)：')

    download(url, req_header)


if __name__ == '__main__':
    main()
