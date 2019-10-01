#-*- coding:utf-8 -*-

import os
import sys
import json
import hashlib
import shutil

from pathlib import Path
from pathlib import PurePath

from . import filemgr
from . import mdtools
from . import logging

from datetime import datetime


POST_META_FILE_NAME='PostMeta.json'
ATTACH_META_FILE_NAME='AttachMeta.json'
FOLDER_META_FILE_NAME='FolderMeta.json'
TOTAL_FOLDER_META_FILE_NAME='TotalFolderMeta.json'

FUNC_RET_DEF_FALSE='False'
FUNC_RET_DEF_TRUE='True'

#####################################
# Meta files Path
#####################################

def get_fileinfo_meta_path(fileinfo_dic) :
	return str(PurePath(get_asset_folder_path(fileinfo_dic)).joinpath(POST_META_FILE_NAME))

def get_asset_folder_path(fileinfo_dic) :
	target_path = str(PurePath(fileinfo_dic['abpath_folder']).joinpath(fileinfo_dic['file_name'] + '.assets'))
	Path(target_path).mkdir(parents=True, exist_ok=True)
	return target_path

#####################################
# Post Meta files tools
#####################################

def get_post_meta_skel() :
	post_meta_dic = {}

	post_meta_dic['meta_ver'] = '1'
	post_meta_dic['file_md5'] = ''
	post_meta_dic['file_name'] = ''
	post_meta_dic['is_publish'] = ''
	post_meta_dic['publish_date'] = ''
	post_meta_dic['publish_id'] = ''
	post_meta_dic['publish_url'] = ''
	post_meta_dic['publish_category_id'] = ''

	return post_meta_dic


def init_post_meta_file(fileinfo_dic, init=False, file_md5_hash=None) :
	post_meta_dic = get_post_meta_skel()

	asset_folder_path = get_asset_folder_path(fileinfo_dic)
	fileinfo_meta_path = get_fileinfo_meta_path(fileinfo_dic)

	if init == True :
		post_meta_dic['meta_ver'] = '1'
		post_meta_dic['file_md5'] = get_file_md5_hash(fileinfo_dic['abpath_full'])
		post_meta_dic['file_name'] = fileinfo_dic['file_name']
		post_meta_dic['postTitle'] = FUNC_RET_DEF_FALSE
		post_meta_dic['is_publish'] = FUNC_RET_DEF_FALSE
		post_meta_dic['publish_date'] = FUNC_RET_DEF_FALSE
		post_meta_dic['publish_id'] = FUNC_RET_DEF_FALSE
		post_meta_dic['publish_url'] = FUNC_RET_DEF_FALSE
		post_meta_dic['publish_category_id'] = FUNC_RET_DEF_FALSE

		with open(fileinfo_meta_path, 'w', encoding='utf-8') as meta_file:
			json.dump(post_meta_dic, meta_file, indent="\t", ensure_ascii=False)
	else :
		with open(fileinfo_meta_path, 'r') as meta_data:
			post_meta_dic = json.load(meta_data)

	return post_meta_dic

def save_post_meta_file(fileinfo_dic, post_meta_dic) :

	asset_folder_path = get_asset_folder_path(fileinfo_dic)
	fileinfo_meta_path = get_fileinfo_meta_path(fileinfo_dic)

	with open(fileinfo_meta_path, 'w', encoding='utf-8') as meta_file:
		json.dump(post_meta_dic, meta_file, indent="\t", ensure_ascii=False)

	return post_meta_dic


def save_new_post_meta_file(fileinfo_dic, post_id, post_url, post_cateory) :
	post_meta_dic = get_post_meta_skel()
	post_meta_dic['meta_ver'] = '1'
	post_meta_dic['file_md5'] = filemgr.get_file_md5_hash(fileinfo_dic['abpath_full'])
	post_meta_dic['file_name'] = fileinfo_dic['file_full_name']
	post_meta_dic['is_publish'] = FUNC_RET_DEF_TRUE
	"""
	2012-08-15 11:31:57
	"""
	now = datetime.now()
	timestamp_str = "%s-%s-%s %s:%s:%s" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
	post_meta_dic['publish_date'] = timestamp_str
	post_meta_dic['publish_id'] = post_id
	post_meta_dic['publish_url'] = post_url
	post_meta_dic['publish_category_id'] = str(post_cateory)
	save_post_meta_file(fileinfo_dic, post_meta_dic)

def delete_post_meta_file(fileinfo_dic, post_id, post_url, post_cateory) :
	asset_folder_path = get_asset_folder_path(fileinfo_dic)
	fileinfo_meta_path = get_fileinfo_meta_path(fileinfo_dic)

	os.remove(fileinfo_dic['abpath_full'])
	shutil.rmtree(asset_folder_path)

def get_post_meta_file(fileinfo_dic) :
	post_meta_dic = get_post_meta_skel()

	asset_folder_path = get_asset_folder_path(fileinfo_dic)
	fileinfo_meta_path = get_fileinfo_meta_path(fileinfo_dic)

	if Path(fileinfo_meta_path).exists() == True :
		with open(fileinfo_meta_path, 'r', encoding='utf-8') as meta_file:
			post_meta_dic = json.load(meta_file)
			return post_meta_dic
	else :
		return None

	#return post_meta_dic

#####################################
# folder Meta files tools
#####################################

def get_folder_meta_skel() :
	folder_meta_dic = {}

	folder_meta_dic['folder_name'] = ''
	folder_meta_dic['folder_code'] = ''
	folder_meta_dic['target_folder_path'] = ''
	folder_meta_dic['blog_name'] = ''

	return folder_meta_dic

def save_folder_meta_total_file(makePath, folder_meta_dic_arr) :

	with open(str(PurePath(makePath).joinpath(TOTAL_FOLDER_META_FILE_NAME)), 'w', encoding='utf-8') as meta_file:
		json.dump(folder_meta_dic_arr, meta_file, indent="\t", ensure_ascii=False)

def get_folder_meta_total_file(makePath) :
	folder_meta_dic_arr = {}
	target_path = str(PurePath(makePath).joinpath(TOTAL_FOLDER_META_FILE_NAME))

	if Path(target_path).exists() == True :
		with open(target_path, 'r', encoding='utf-8') as meta_file:
			return json.load(meta_file)
	else :
		return None

def get_folder_meta_one_file(fileinfo_dic) :
	folder_meta_dic_arr = {}
	target_path = str(PurePath(fileinfo_dic['abpath_folder']).joinpath(FOLDER_META_FILE_NAME))

	logging.log_info('folder meta path : ' + target_path)
	if Path(target_path).exists() == True :
		with open(target_path, 'r', encoding='utf-8') as meta_file:
			return json.load(meta_file)
	else :
		return None


def save_folder_meta_one_file(target_folder_path, folder_name, folder_code, blog_name) :
	target_folder_path = str(PurePath(target_folder_path).joinpath(folder_name))

	Path(target_folder_path).mkdir(parents=True, exist_ok=True)
	folder_meta_dic = get_folder_meta_skel()

	folder_meta_dic['folder_name'] = folder_name
	folder_meta_dic['folder_code'] = folder_code
	folder_meta_dic['target_folder_path'] = folder_name
	folder_meta_dic['blog_name'] = blog_name

	with open(str(PurePath(target_folder_path).joinpath(FOLDER_META_FILE_NAME)), 'w', encoding='utf-8') as meta_file:
		json.dump(folder_meta_dic, meta_file, indent="\t", ensure_ascii=False)

	return folder_meta_dic

#####################################
# attach Meta files tools
#####################################
def get_attach_meta_skel() :
	attach_meta_dic = {}

	attach_meta_dic['file_name'] = ''
	attach_meta_dic['file_url'] = ''
	attach_meta_dic['attach_folder'] = ''

	return attach_meta_dic

def save_attach_meta_file(makePath, attach_meta_dic) :

	with open(str(PurePath(makePath).joinpath(ATTACH_META_FILE_NAME)), 'w', encoding='utf-8') as meta_file:
		json.dump(attach_meta_dic, meta_file, indent="\t", ensure_ascii=False)

def get_attach_meta_file(makePath) :

	attach_meta_dic = get_attach_meta_skel()
	target_path = str(PurePath(makePath).joinpath(ATTACH_META_FILE_NAME))

	if Path(target_path).exists() == True :
		with open(target_path, 'r', encoding='utf-8') as meta_file:
			attach_meta_dic = json.load(meta_file)
			return attach_meta_dic
	else :
		return None

def check_attach_meta_file(asset_path) :
	attach_meta_dic_arr = get_attach_meta_file(asset_path)

	upload_target_fileinfo_dic_arr = []

	fileinfo_dic_arr = []
	fileinfo_dic_arr += filemgr.get_fileinfo_from_folder(asset_path, '*.jpg')
	logging.log_debug(fileinfo_dic_arr)
	fileinfo_dic_arr += filemgr.get_fileinfo_from_folder(asset_path, '*.png')
	logging.log_debug(fileinfo_dic_arr)
	# 기존에 upload 이력없으면 전체 파일이 모두 업로드 대상
	if attach_meta_dic_arr == None :
		return fileinfo_dic_arr

	for fileinfo_dic in fileinfo_dic_arr :
		found_attach_file = False

		for attach_meta_dic in attach_meta_dic_arr :
			if attach_meta_dic['file_name'] == fileinfo_dic['file_full_name'] :
				found_attach_file = True
				break;

		# 기존 meta 에서 파일을 찾지 못했으므로 업로드 대상
		if found_attach_file == False :
			upload_target_fileinfo_dic_arr.append(fileinfo_dic)

	logging.log_info('-- upload target file list ---')
	logging.log_info(upload_target_fileinfo_dic_arr)
	return upload_target_fileinfo_dic_arr

#####################################
# markdown Meta files tools
#####################################
def get_markdown_header_yml_skel() :
	markdown_header_yml_dic = {}

	markdown_header_yml_dic['title'] = ''
	markdown_header_yml_dic['publish'] = ''
	markdown_header_yml_dic['tags'] = ''

	return markdown_header_yml_dic

