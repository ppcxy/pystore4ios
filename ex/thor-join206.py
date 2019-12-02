#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : thor-join206.py
# @Author  : loli
# @Date    : 2018-03-15
# @Version : 1.0
# @Contact : https://t.me/weep_x
# @tg group: https://t.me/pythonista3dalaoqun
import json
from zipfile import ZipFile

import os, appex, console
import shutil

download_dir = os.path.expanduser('~/Documents/ppcxy_downloads/thor206')
if not os.path.exists(download_dir):
    os.makedirs(download_dir)
TEMP_PATH = 'temp'
TARGE_PATH = 'target'
PACKETS_NAME = 'packets'
PACKET_BODY = 'body'
INFO_JSON = 'info.json'
RESPONSE_JSON = 'response.json'
BODY_RAW_FILE_NAME = 'body_raw_file'

BODY_RAW_FILE = ''
packet_array = []

READ_SIZE = 1024


# 包信息封装
class Packet:
    path = None
    begin = 0
    end = 0

    def __init__(self, path, begin, end):
        self.path = path
        self.begin = begin
        self.end = end


# 解压缩文件到指定目录,目录不存在则创建
def unzip(src, path):
    if not os.path.exists(path):
        os.mkdir(path)

    zip_obj = ZipFile(src, mode='r')
    for info in zip_obj.filelist:
        zip_obj.extract(member=info, path=path)
    zip_obj.close()


# 加载配置文件
def load_config(file='config.json'):
    f = open(file, encoding='utf-8')
    return json.load(f)


# 包解析
def packet_parse(packet):
    print('parse packet :%s' % packet)
    print('============================')
    packet_response_json = load_config(os.path.join(TEMP_PATH, packet, RESPONSE_JSON))

    global BODY_RAW_FILE

    # 验证是否同一个文件

    if BODY_RAW_FILE == '':
        BODY_RAW_FILE = packet_response_json[BODY_RAW_FILE_NAME]
    elif BODY_RAW_FILE != packet_response_json[BODY_RAW_FILE_NAME]:
        return

    print('packet response status : %s' % packet_response_json['status'])

    if packet_response_json['status'] == 206:
        print(packet_response_json['headers_raw']['Content-Range'])

        body_raw_size = packet_response_json['body_raw_size']
        # bytes 0-12692139/12692140  => [0-12692139,12692140]
        respinse_infos = packet_response_json['headers_raw']['Content-Range'].split(' ')[-1].split('/')

        file_size = respinse_infos[-1]

        packet_infos = respinse_infos[0].split('-')
        packet_begin = int(packet_infos[0])
        packet_end = packet_begin + body_raw_size

        print('文件总大小 %s, 当前包大小%s字节, 当前包开始字节 %s ,结束字节 %s' % (
            file_size, packet_response_json['body_raw_size'], packet_begin, packet_end))
        print('============================')

        pack = Packet(packet, packet_begin, packet_begin + body_raw_size)

        packet_array.append(pack)


def join_file(base_path, files, target_file):
    output = open(target_file, 'wb')
    for file_name in files:
        file_path = os.path.join(base_path, str(file_name))
        file_obj = open(file_path, 'rb')
        while 1:
            file_bytes = file_obj.read(READ_SIZE)
            if not file_bytes:
                break
            output.write(file_bytes)
        file_obj.close()
    output.close()


# TODO 需要算法升级
def split_file(file, begin, despath):
    input_file = open(file, 'rb')  # rb 读二进制文件
    file_obj = open(despath, 'wb')

    try:
        # 去掉差值
        input_file.read(begin)
        while 1:
            chunk = input_file.read(READ_SIZE)
            if not chunk:  # 文件块是空的
                break

            file_obj.write(chunk)
    finally:
        input_file.close()
        file_obj.flush()


# 解析thor p4包
def p4thor_parse(p4thor_file, download_dir):
    # 解压到临时工作目录
    unzip(p4thor_file, TEMP_PATH)

    # 解析包信息
    p4json = load_config(os.path.join(TEMP_PATH, INFO_JSON))

    # 读取packets
    packets = p4json[PACKETS_NAME]

    # 解析所有packets
    for i, v in enumerate(packets):
        packet_parse(v)
    files = []

    tail_byte = 0
    # 首先按开始字节排序
    packet_array.sort(key=lambda x: x.begin)

    # 遍历处理多余字节
    for i, v in enumerate(packet_array):

        file_name = os.path.join(TEMP_PATH, v.path, PACKET_BODY, BODY_RAW_FILE)
        if v.begin < tail_byte:
            if v.end < tail_byte:
                continue
            tem_file = os.path.join(TEMP_PATH, v.path, PACKET_BODY, 'ls')
            split_file(file_name, tail_byte - v.begin, tem_file)
            os.rename(tem_file, os.path.join(TARGE_PATH, str(v.begin)))
        else:
            os.rename(file_name, os.path.join(TARGE_PATH, str(v.begin)))
        tail_byte = v.end
        files.append(v.begin)

    # 排序文件顺序进行拼接
    files.sort()
    join_file(TARGE_PATH, files, os.path.join(download_dir, BODY_RAW_FILE))


def main():
    if appex.is_running_extension():
        get_path = appex.get_file_path()
        file_name = os.path.basename(get_path)
        file_ext = os.path.splitext(file_name)[-1]
        if os.path.exists(TEMP_PATH):
            shutil.rmtree(TEMP_PATH)
        os.mkdir(TEMP_PATH)
        if os.path.exists(TARGE_PATH):
            shutil.rmtree(TARGE_PATH)
        os.mkdir(TARGE_PATH)

        if file_ext == '.p4thor':
            dstpath = os.path.join(TEMP_PATH, '666.p4thor')
            try:
                shutil.copy(get_path, dstpath)
                p4thor_parse(dstpath, os.path.join(TARGE_PATH, str(download_dir)))

            except Exception as eer:
                print(eer)
                console.hud_alert('解析失败！', 'error', 1)
            finally:
                # 清理临时文件
                shutil.rmtree(TARGE_PATH)
                shutil.rmtree(TEMP_PATH)
        else:
            console.hud_alert('非 p4thor 文件无法解析', 'error', 2)
        # appex.finish()
    else:
        console.hud_alert('请在分享扩展中打开本脚本', 'error', 2)


if __name__ == '__main__':
    main()
