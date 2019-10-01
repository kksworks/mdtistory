#-*- coding:utf-8 -*-
from pytistory import PyTistory

import sys
import codecs
import json

from pathlib import Path
from pathlib import PurePath

import html

#from metatools import mdTistory
from . import metatools
from . import filemgr
from . import mdtools
from . import logging

import re


FUNC_RET_DEF_FALSE='False'
FUNC_RET_DEF_TRUE='True'

class TistoryTools :

    accessToken = ""
    pyTistory = {}
    categoryInfo = {}

    default_folder_path = ''

    foler_meta_dic_arr = []

    def __init__(self, accessToken) :
        self.accessToken = accessToken
        self.pyTistory = PyTistory()
        self.pyTistory.configure(access_token=accessToken)

    def get_category_folder_info(self, blog_name, base_folder) :
        self.foler_meta_dic_arr = metatools.get_folder_meta_total_file(base_folder)

        if self.foler_meta_dic_arr == None :
            tistory_api_res = self.pyTistory.category.list(blog_name=blog_name)
            self.foler_meta_dic_arr = self.make_category_folder_info(tistory_api_res, base_folder, blog_name)

        self.default_folder_path = base_folder

        return True

    def get_category_folder_path(self, blog_name, category_id, base_folder) :
        if self.foler_meta_dic_arr == None :
            return None

        for folder_meta_dic in self.foler_meta_dic_arr :
            if folder_meta_dic['folder_code'] == category_id :
                return str(PurePath(base_folder).joinpath(folder_meta_dic['target_folder_path']))

        return base_folder

    def make_category_folder_info(self, tistory_api_res, target_folder_path, blog_name) :
        tistory_api_category_info_arr = tistory_api_res['item']['categories']
        logging.log_debug(tistory_api_category_info_arr)
        tmp_folder_meta_dic_arr = []

        listCount = len(tistory_api_category_info_arr)

        while (listCount > 0):
            for tistory_api_category_info in tistory_api_category_info_arr :
                # 1. parents item filter
                '''
                {'parent': '157165', 'id': '183301', 'name': 'GCC', 'entries': '3', 'entriesInLogin': '3', 'label': 'Compiler/GCC'}
                '''
                tistory_api_category_info['label'] = html.unescape(tistory_api_category_info['label'])
                tistory_api_category_info['label'] = mdtools.clean_text_2(tistory_api_category_info['label'])

                if tistory_api_category_info['parent'] == '':
                    folder_meta_dic = metatools.save_folder_meta_one_file(target_folder_path, tistory_api_category_info['label'].replace(' ','_'), tistory_api_category_info['id'], blog_name)
                    tistory_api_category_info_arr.remove(tistory_api_category_info)
                    tmp_folder_meta_dic_arr.append(folder_meta_dic)
                else :
                    for categoryMakeInfo in tmp_folder_meta_dic_arr :
                        if tistory_api_category_info['parent'] == categoryMakeInfo['folder_code'] :
                            folder_meta_dic = metatools.save_folder_meta_one_file(target_folder_path, tistory_api_category_info['label'].replace(' ','_'), tistory_api_category_info['id'], blog_name)
                            tistory_api_category_info_arr.remove(tistory_api_category_info)
                            tmp_folder_meta_dic_arr.append(folder_meta_dic)

                listCount = len(tistory_api_category_info_arr)

        # non category make..

        folder_meta_dic = metatools.save_folder_meta_one_file(target_folder_path, 'non_category/type-non', '', blog_name)
        tmp_folder_meta_dic_arr.append(folder_meta_dic)

        for i in range(-10, 1):
            folder_meta_dic = metatools.save_folder_meta_one_file(target_folder_path, 'non_category/type' + str(i), str(i), blog_name)
            tmp_folder_meta_dic_arr.append(folder_meta_dic)

        metatools.save_folder_meta_total_file(target_folder_path, tmp_folder_meta_dic_arr)
        return tmp_folder_meta_dic_arr

    def writePost(self,blog_name, post_title = 'title', category_name = '', category_id = 0, content_html = '', tags = []) :
        tistory_api_res = self.pyTistory.post.write(post_title,
                            blog_name=blog_name,
                            visibility=1,
                            category=category_id,
                            content=content_html,
                            tag=tags)

    def read_post(self, id, blog_name, base_folder) :
        logging.log_info("read post : target id => " + str(id))

        try :
            tistory_api_res = self.pyTistory.post.read(id, blog_name=blog_name)
        except Exception as ex:
            logging.log_info("    - Oops!  valid read target skip read post")
            return None

        # 1. markdown yml generate
        markdown_header_yml_dic = metatools.get_markdown_header_yml_skel()
        markdown_header_yml_dic['title'] = tistory_api_res['item']['title']
        markdown_header_yml_dic['publish'] = FUNC_RET_DEF_TRUE

        if tistory_api_res['item']['tags'] != '' :
            markdown_header_yml_dic['tags'] = ','.join(tistory_api_res['item']['tags']['tag'])

        # 2. file name generate
        tistory_post_date = tistory_api_res['item']['date'].replace("-","")
        tistory_post_date = tistory_post_date[0:8]  + "_"

        # 2-1. post title
        markdown_post_title = tistory_api_res['item']['title']
        markdown_post_title = markdown_post_title.replace(" ","_")
        markdown_post_title = markdown_post_title.replace("/","|")
        markdown_post_title = markdown_post_title.replace("\\","|")
        markdown_post_title = html.unescape(markdown_post_title)
        markdown_post_title = mdtools.clean_text_1(markdown_post_title)

        # 2-2. make file name
        markdown_file_name = tistory_post_date + markdown_post_title + ".md"

        # 3. post meta generate
        post_meta_dic = metatools.get_post_meta_skel()
        post_meta_dic['meta_ver'] = '1'
        post_meta_dic['file_md5'] = ''
        post_meta_dic['file_name'] = markdown_file_name
        post_meta_dic['is_publish'] = FUNC_RET_DEF_TRUE
        post_meta_dic['publish_date'] = tistory_api_res['item']['date']
        post_meta_dic['publish_id'] = tistory_api_res['item']['id']
        post_meta_dic['publish_url'] = tistory_api_res['item']['postUrl']
        post_meta_dic['publish_category_id'] = tistory_api_res['item']['categoryId']

        # 4. get save target (category <-> folder)
        target_path = self.get_category_folder_path(blog_name, post_meta_dic['publish_category_id'], base_folder)

        logging.log_info ('   + target_path : ' + target_path)
        logging.log_info ('   + targetfilename : ' + markdown_file_name)

        # set file info
        fileinfo_dic = filemgr.get_fileinfo_dic(target_path, markdown_file_name)
        asset_folder_path = metatools.get_asset_folder_path(fileinfo_dic)

        # convert html to markdown
        tistory_api_res['item']['content'] = html.unescape(tistory_api_res['item']['content'])
        markdown_str = mdtools.convert_html_to_markdown_str(tistory_api_res['item']['content'], asset_folder_path)

        # convert tistory attach url str to local attach (save to local)
        markdown_str = mdtools.convert_markdown_tistory_attach_str(markdown_str,asset_folder_path)

        mdtools.save_markdown_file(markdown_str, fileinfo_dic['abpath_full'], markdown_header_yml_dic)

        post_meta_dic['file_md5'] = filemgr.get_file_md5_hash(target_path, markdown_file_name)

        metatools.save_post_meta_file(fileinfo_dic, post_meta_dic)

    def getPostList(self, blog_name) :
        tistory_api_res = self.pyTistory.post.list(blog_name=blog_name)

    def editPost(self,blog_name, post_title = 'title', category_name = '', category_id = 0, content_html = '', tags = []) :
        tistory_api_res = self.pyTistory.post.write(post_title,
                            blog_name=blog_name,
                            visibility=1,
                            category=category_id,
                            content=content_html,
                            tag=tags)# tistory api

    def check_post_files(self, blog_name, base_folder) : 

        post_info_arr = {}

        new_post_fileinfo_dic_arr = []
        del_post_fileinfo_dic_arr = []
        update_post_fileinfo_dic_arr = []

        fileinfo_dic_arr = filemgr.get_fileinfo_from_folder(base_folder, '*.md')

        for fileinfo_dic in fileinfo_dic_arr :
            post_meta_dic = metatools.get_post_meta_file(fileinfo_dic)

            # new post : 기존 md post meta 파일이 없다.
            if post_meta_dic == None :
                new_post_fileinfo_dic_arr.append(fileinfo_dic)
                continue

            if post_meta_dic['file_md5'] != filemgr.get_file_md5_hash(fileinfo_dic['abpath_full']) :
                update_post_fileinfo_dic_arr.append(fileinfo_dic)
                continue

        post_info_arr['new_post_fileinfo'] = new_post_fileinfo_dic_arr
        post_info_arr['update_post_fileinfo'] = update_post_fileinfo_dic_arr

        return post_info_arr


    def new_post_markdown_file(self, blog_name, fileinfo_dic) :
        attach_meta_dic_arr = self.attach_meta_chk(blog_name, metatools.get_asset_folder_path(fileinfo_dic))

        post_tags = []
        post_title = ''
        post_cateory = 0

        """
        0: 비공개
        1: 보호
        2: 공개
        3: 발행
        """
        post_publish = 0
        folder_meta_dic = metatools.get_folder_meta_one_file(fileinfo_dic)

        md_conv_html = mdtools.convert_markdown_to_html_file(fileinfo_dic['abpath_full'], attach_meta_dic_arr)

        if md_conv_html['meta'] != None and len(md_conv_html['meta']) > 0 and md_conv_html['meta']['title'] != None and md_conv_html['meta']['title'] != '' :
            post_title = md_conv_html['meta']['title']
        else :
            post_title = fileinfo_dic['file_name']

        if md_conv_html['meta'] != None and len(md_conv_html['meta']) > 0  and md_conv_html['meta']['tags'] != None and md_conv_html['meta']['tags'] != '' :
            spilt_target = str(md_conv_html['meta']['tags'])
            spilt_target = spilt_target.replace('[','')
            spilt_target = spilt_target.replace(']','')
            spilt_target = spilt_target.replace('\'','')
            spilt_target = spilt_target.replace('\"','')

            spilt_str = re.split(', "\[\]',spilt_target)
            for keyword in spilt_str :
                if len(str(keyword)) > 0 :
                    post_tags.append(str(keyword))

        if md_conv_html['meta'] != None and len(md_conv_html['meta']) > 0  and md_conv_html['meta']['publish'] != None and md_conv_html['meta']['publish'] != '' :
            if str(md_conv_html['meta']['publish']).find('True') != -1 :
                post_publish = 3

        if folder_meta_dic['folder_code'] != None and len(folder_meta_dic['folder_code'] ) :
            post_cateory = int(folder_meta_dic['folder_code'] )

        logging.log_debug('--- post info ----------')
        logging.log_debug('  > post_title : ' + str(post_title))
        logging.log_debug('  > post_tags : ' + str(post_tags))
        logging.log_debug('  > post_cateory : ' + str(post_cateory))
        logging.log_debug('  > post_publish : ' + str(post_publish))

        tistory_api_res = self.pyTistory.post.write(post_title,
                                             blog_name=blog_name,
                                             visibility=post_publish,
                                             category=post_cateory,
                                             content=md_conv_html['html'],
                                             tag=post_tags)

        logging.log_debug('server res : ' + str(tistory_api_res))

        if tistory_api_res['status'] == '200' :
            metatools.save_new_post_meta_file(fileinfo_dic, tistory_api_res['postId'], tistory_api_res['url'], str(post_cateory))


    def edit_post_markdown_file(self, blog_name, fileinfo_dic) :
        attach_meta_dic_arr = self.attach_meta_chk(blog_name, metatools.get_asset_folder_path(fileinfo_dic))

        post_tags = []
        post_title = ''
        post_cateory = 0
        """
        0: 비공개
        1: 보호
        2: 공개
        3: 발행
        """
        post_publish = 0
        post_delete = False
        folder_meta_dic = metatools.get_folder_meta_one_file(fileinfo_dic)

        md_conv_html = mdtools.convert_markdown_to_html_file(fileinfo_dic['abpath_full'], attach_meta_dic_arr)

        if md_conv_html['meta'] != None and len(md_conv_html['meta']) > 0 and md_conv_html['meta'].get('title') != None and md_conv_html['meta']['title'] != None and md_conv_html['meta']['title'] != '' :
            post_title = md_conv_html['meta']['title']
        else :
            post_title = fileinfo_dic['file_name']

        if md_conv_html['meta'] != None and len(md_conv_html['meta']) > 0 and md_conv_html['meta'].get('tags') != None and md_conv_html['meta']['tags'] != None and md_conv_html['meta']['tags'] != '' :
            spilt_target = str(md_conv_html['meta']['tags'])
            spilt_target = spilt_target.replace('[','')
            spilt_target = spilt_target.replace(']','')
            spilt_target = spilt_target.replace('\'','')
            spilt_target = spilt_target.replace('\"','')

            spilt_str = re.split(', "\[\]',spilt_target)
            for keyword in spilt_str :
                if len(str(keyword)) > 0 :
                    post_tags.append(str(keyword))

        if md_conv_html['meta'] != None and len(md_conv_html['meta']) > 0 and  md_conv_html['meta'].get('publish') != None and md_conv_html['meta']['publish'] != None and md_conv_html['meta']['publish'] != '' :
            if str(md_conv_html['meta']['publish']).find('True') != -1 :
                post_publish = 3

        # 강제로 삭제는 못하고, 그냥 비공개로 처리한다.
        if md_conv_html['meta'] != None and len(md_conv_html['meta']) > 0 and  md_conv_html['meta'].get('delete') != None and md_conv_html['meta']['delete'] != None and md_conv_html['meta']['delete'] != '' :
             logging.log_debug(md_conv_html['meta']['delete'])
             if str(md_conv_html['meta']['delete']).find('True') != -1 :
                 post_publish = 0
                 post_delete = True

        if folder_meta_dic['folder_code'] != None and len(folder_meta_dic['folder_code'] ) :
            post_cateory = int(folder_meta_dic['folder_code'] )
        logging.log_debug('--- post info ----------')
        logging.log_debug('  > post_title : ' + str(post_title))
        logging.log_debug('  > post_tags : ' + str(post_tags))
        logging.log_debug('  > post_cateory : ' + str(post_cateory))
        logging.log_debug('  > post_publish : ' + str(post_publish))

        post_meta_dic = metatools.get_post_meta_file(fileinfo_dic)

        tistory_api_res = self.pyTistory.post.modify(post_title,
                                            int(post_meta_dic['publish_id']),
                                            blog_name=blog_name,
                                            visibility=post_publish,
                                            category=post_cateory,
                                            content=md_conv_html['html'],
                                            tag=post_tags)

        logging.log_debug(logging.log_debug('server res : ' + str(tistory_api_res)))

        if tistory_api_res['status'] == '200' :
            metatools.save_new_post_meta_file(fileinfo_dic, tistory_api_res['postId'], tistory_api_res['url'], str(post_cateory))

            # 이후에 삭제옵션이 켜져있으면 그냥 해당 게시물은 로컬에서만 삭제하자
            if post_delete == True :
                logging.log_info(' !!!! delete Target : ' + post_meta_dic['file_name'] )
                metatools.delete_post_meta_file(fileinfo_dic, tistory_api_res['postId'], tistory_api_res['url'], str(post_cateory))

    def attach_meta_chk(self, blog_name, asset_path) :

        attach_meta_update_need = False
        upload_target_fileinfo_dic_arr = metatools.check_attach_meta_file(asset_path)

        logging.log_info('target upload files')
        logging.log_info(upload_target_fileinfo_dic_arr)
        attach_meta_dic_arr = []

        for upload_target_fileinfo_dic in upload_target_fileinfo_dic_arr :
            # upload to tistory
            tistory_api_res = self.pyTistory.post.attach(upload_target_fileinfo_dic['abpath_full'], blog_name=blog_name)
            logging.log_debug(logging.log_debug('server res : ' + str(tistory_api_res)))
            """
            {'url': 'http://cfile24.uf.tistory.com/image/999BEE435D80AFA42A5A39', 'status': '200', 'replacer': '[##_1N|cfile24.uf@999BEE435D80AFA42A5A39.png|width="430" height="121" filename="2019-09-17-17-14-30.png" filemime="image/png"|_##]'}
            """
            attach_meta_dic = {}

            # if tistory_api_res check
            if tistory_api_res['status'] == '200' :
                attach_meta_dic['file_name'] = upload_target_fileinfo_dic['file_full_name']
                attach_meta_dic['file_url'] = tistory_api_res['url']
                attach_meta_dic['attach_folder'] = str(PurePath(asset_path).name)

            logging.log_debug(attach_meta_dic)
            attach_meta_dic_arr.append(attach_meta_dic)
            attach_meta_update_need = True

        if attach_meta_update_need == True :
            metatools.save_attach_meta_file(asset_path, attach_meta_dic_arr)

        return metatools.get_attach_meta_file(asset_path)
