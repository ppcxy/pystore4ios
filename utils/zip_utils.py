#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @File    : zip_utils.py
# @Author  : loli
# @Date    : 2018-03-15
# @Version : v0.1 bate(内部测试版)
# @Contact : https://t.me/weep_x
# @tg group: https://t.me/pythonista3dalaoqun

import zipfile


# 解压缩文件到指定目录,目录不存在则创建
def unzip(src, path):
    if not os.path.exists(path):
        os.mkdir(path)

    zip_obj = ZipFile(src, mode='r')
    for info in zip_obj.filelist:
        zip_obj.extract(member=info, path=path)
    zip_obj.close()


def zip(startdir, file_news):
    z = zipfile.ZipFile(file_news, 'w', zipfile.ZIP_DEFLATED)  # 参数一：文件夹名
    for dirpath, dirnames, filenames in os.walk(startdir):
        fpath = dirpath.replace(startdir, '')  # 这一句很重要，不replace的话，就从根目录开始复制
        fpath = fpath and fpath + os.sep or ''  # 这句话理解我也点郁闷，实现当前文件夹以及包含的所有文件的压缩
        for filename in filenames:
            z.write(os.path.join(dirpath, filename), fpath + filename)
            print('压缩成功')
    z.close()
