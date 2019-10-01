#-*- coding:utf-8 -*-

import os
import sys
import json
import hashlib

from pathlib import Path
from pathlib import PurePath

from . import mdtools
from . import logging

TEMP_MD_FILE_NAME = 'tmp-mdcode.md'

def get_file_md5_hash(path, path2 = '') :
    target_path = str(PurePath(path).joinpath(path2))

    f = open(target_path, 'rb')
    data = f.read()
    f.close()

    return str(hashlib.md5(data).hexdigest())

def get_fileinfo_from_folder(path_folder, ext) :
    path = Path(path_folder)

    fileinfo_dic_arr = []

    for filename in path.glob('**/' + ext):

        findinfo_dic = {}

        findinfo_dic['file_name'] = str(PurePath(filename).stem)
        findinfo_dic['file_ext'] = str(PurePath(filename).suffix)
        findinfo_dic['file_full_name'] = findinfo_dic['file_name'] + findinfo_dic['file_ext'] 
        findinfo_dic['abpath_full'] = str(PurePath(str(Path(filename).resolve())))
        findinfo_dic['abpath_folder'] = str(PurePath(findinfo_dic['abpath_full']).parent)

        # filter skip files
        if findinfo_dic['abpath_full'].find(mdtools.TEMP_MD_FILE_NAME) != -1:
            continue

        fileinfo_dic_arr.append(findinfo_dic)
    return fileinfo_dic_arr

def get_fileinfo_dic(path, path2 = '') :
    findinfo_dic = {}

    target_path = str(PurePath(path).joinpath(path2))

    if Path(target_path).exists() == False :
        Path(target_path).touch()

    findinfo_dic['file_name'] = str(PurePath(target_path).stem)
    findinfo_dic['file_ext'] = str(PurePath(target_path).suffix)
    findinfo_dic['abpath_full'] = str(PurePath(str(Path(target_path).resolve())))
    findinfo_dic['abpath_folder'] = str(PurePath(findinfo_dic['abpath_full']).parent)

    return findinfo_dic
