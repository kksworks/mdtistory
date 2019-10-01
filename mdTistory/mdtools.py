#-*- coding:utf-8 -*-

from pytistory import PyTistory

import sys
import codecs
import re

from pathlib import Path
from pathlib import PurePath

import markdown
from tomd import Tomd

import uuid
import requests
import subprocess
import shutil

import urllib.parse

from . import metatools
from . import logging

TEMP_HTML_FILE_NAME = 'tmp-htmlcode.html'
TEMP_HTML2_SUFFIX = '.remove-style.html'
TEMP_MD_FILE_NAME = 'tmp-mdcode.md'

def clean_text_1(read_data):
    #텍스트에 포함되어 있는 특수 문자 제거
    # text = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》;]', '_', read_data)
    text = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》;]', '_', read_data)
    return text

def clean_text_2(read_data):
    #텍스트에 포함되어 있는 특수 문자 제거
    # 카테고리의 경우 이름에 '/' 가 같이오기때문에.. 해당 문자는 path 로 활용함. 변환하지 않느다.
    text = re.sub('[-=+,#\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》;]', '_', read_data)
    return text

def save_from_target_url(target_url, target_path) :
    maxRetryCnt = 5

    for i in range(0, maxRetryCnt):
        logging.log_info ('    >> try to download cnt : ' + str(i) )
        web_response = requests.get(target_url, timeout=5)
        if web_response.status_code == 200:
            with open(target_path, 'wb') as f:
                f.write(web_response.content)
                logging.log_info ('    >> downlaod success')
                break
        logging.log_info ('    >> downloa fail.. retry')


def clean_escape_char(target_str):

    target_str = target_str.replace('\\#','#')
    target_str = target_str.replace('\\<','<')
    target_str = target_str.replace('\\>','>')
    target_str = target_str.replace('\\[','[')
    target_str = target_str.replace('\\]',']')
    target_str = target_str.replace('\\(',')')
    target_str = target_str.replace('\\)','(')

    target_str = target_str.replace('&quot;','\"')
    target_str = target_str.replace('&apos;','\'')
    target_str = target_str.replace('&gt;','>')
    target_str = target_str.replace('&lt;','<')

    return target_str

def html_to_markdown_proc_1(html_code_str, asset_folder_path) :

    markdown_str = ''

    target_html_file_path = str(PurePath(asset_folder_path).joinpath(TEMP_HTML_FILE_NAME))
    target_markdown_file_path = str(PurePath(asset_folder_path).joinpath(TEMP_MD_FILE_NAME))

    with open(target_html_file_path, 'w', encoding='utf-8') as html_file:
        html_file.write(html_code_str)
        html_file.close()

    # test script
    # cat tmp-htmlcode.html | pandoc --from html --to html -o test1.html -f html-native_divs-native_spans
    # cat test1.html | pandoc --from html --to markdown_github+all_symbols_escapable -o test1.md -f html-native_divs-native_spans --atx-header --language-prefix
    # pandoc --from html --to html -o test1.html -f html-native_divs-native_spans

    runPandocCmdLine = 'pandoc --from html --to html -f html-native_divs-native_spans ' + target_html_file_path + ' -o ' + target_html_file_path + TEMP_HTML2_SUFFIX
    subprocess.call (runPandocCmdLine, shell=True)

    runPandocCmdLine = 'pandoc --from html --to markdown_github+all_symbols_escapable -f html-native_divs-native_spans --atx-header ' + target_html_file_path + TEMP_HTML2_SUFFIX + ' -o ' + target_markdown_file_path
    subprocess.call (runPandocCmdLine, shell=True)

    with open(target_markdown_file_path, 'r', encoding='utf-8') as markdown_file:
        markdown_str = markdown_file.read()
        markdown_file.close()

    return markdown_str

def html_to_markdown_proc_2(html_code_str, asset_folder_path) :

    tmpHtmlCode = html_code_str

    target_html_file_path = str(PurePath(asset_folder_path).joinpath(TEMP_HTML_FILE_NAME))
    target_markdown_file_path = str(PurePath(asset_folder_path).joinpath(TEMP_MD_FILE_NAME))

    with open(target_html_file_path, 'w', encoding='utf-8') as html_file:
        html_file.write(tmpHtmlCode)
        html_file.close()

    markdown_str = Tomd(html_code_str).markdown

    return markdown_str

def convert_html_to_markdown_str(html_code_str, asset_folder_path) :

    markdown_str = html_to_markdown_proc_1(html_code_str, asset_folder_path)
    markdown_str = clean_escape_char(markdown_str)

    return markdown_str

def save_markdown_file(markdown_str, target_path, markdown_header_yml_dic) :

    markdown_str = covert_markdown_header_to_str(markdown_header_yml_dic) + markdown_str
    with open(target_path, 'w', encoding='utf-8') as target_file:
        target_file.write(markdown_str)
        target_file.close()

def convert_markdown_to_html_str(markdown_str, attach_meta_dic_arr) :

    # replace attach info : local file to attach url
    if attach_meta_dic_arr != None :
        logging.log_info(attach_meta_dic_arr)
        for attach_meta_dic in attach_meta_dic_arr :

            replace_str = './' + attach_meta_dic['attach_folder'] + '/' + attach_meta_dic['file_name']
            markdown_str = markdown_str.replace(replace_str, attach_meta_dic['file_url'] )
            replace_str = urllib.parse.quote_plus(replace_str).replace('%2F','/')
            markdown_str = markdown_str.replace(replace_str, attach_meta_dic['file_url'] )

            replace_str = '.' + attach_meta_dic['attach_folder'] + '/' + attach_meta_dic['file_name']
            markdown_str = markdown_str.replace(replace_str, attach_meta_dic['file_url'] )
            replace_str = urllib.parse.quote_plus(replace_str).replace('%2F','/')
            markdown_str = markdown_str.replace(replace_str, attach_meta_dic['file_url'] )

            replace_str = attach_meta_dic['attach_folder'] + '/' + attach_meta_dic['file_name']
            markdown_str = markdown_str.replace(replace_str, attach_meta_dic['file_url'] )
            replace_str = urllib.parse.quote_plus(replace_str).replace('%2F','/')
            markdown_str = markdown_str.replace(replace_str, attach_meta_dic['file_url'] )

            replace_str = attach_meta_dic['attach_folder'] + attach_meta_dic['file_name']
            markdown_str = markdown_str.replace(replace_str, attach_meta_dic['file_url'] )
            replace_str = urllib.parse.quote_plus(replace_str).replace('%2F','/')
            markdown_str = markdown_str.replace(replace_str, attach_meta_dic['file_url'] )

    md = markdown.Markdown(extensions=['markdown.extensions.fenced_code', 'markdown.extensions.meta', 'markdown.extensions.attr_list', 'markdown_captions'], tab_length=2)

    md_conv_html = {}

    md_conv_html['html'] = md.convert(markdown_str)
    md_conv_html['meta'] = md.Meta

    return md_conv_html

def convert_markdown_to_html_file(markdown_file_path, attach_meta_dic_arr) :
    input_file = codecs.open(markdown_file_path, mode="r", encoding="utf-8")
    markdown_str = input_file.read()


    return convert_markdown_to_html_str(markdown_str, attach_meta_dic_arr)

def convert_markdown_tistory_attach_str(markdown_str, target_asset_folder) :

    # convert attach type 1
    markdown_str = tistory_attach_str_proc1_1(markdown_str, target_asset_folder)

    # convert attach type 2
    markdown_str = tistory_attach_str_proc2_1(markdown_str, target_asset_folder)

    return markdown_str

# step 1 : [## ~ ##] filter
def tistory_attach_str_proc1_1(markdown_str, target_asset_folder) :
    attach_meta_dic_arr = []

    p = re.compile('(\[##).*(##\])')
    m = p.search(markdown_str)

    while m is not None:
        pattern_str = str(m.group())
        attach_meta_dic = tistory_attach_str_proc1_2(pattern_str, target_asset_folder)
        attach_meta_dic_arr.append(attach_meta_dic)
        markdown_str = markdown_str.replace(pattern_str,tistory_attach_str_proc0_1(attach_meta_dic))
        m = p.search(markdown_str)

    metatools.save_attach_meta_file(target_asset_folder, attach_meta_dic_arr)

    return markdown_str
    '''
	regular expression ==> (\[##).*(##\])
    tistory attach file example ==> [##_Image|kage@FhehS/btqxDuJc8hK/JsrkrI1uaRE2YLoKhQmrt0/img.png|alignCenter|data-filename="2019-07-21-00-23-58.png"|_##]
    '''

# step 2 : convert attach string
def tistory_attach_str_proc1_2(tag_str, target_asset_folder) :
    attach_meta_dic = metatools.get_attach_meta_skel()

    spilt_str = tag_str.split('|')

    # replace for tistory attachfile
    target_url = spilt_str[1]
    target_url = target_url.replace('kage@', 'https://k.kakaocdn.net/dn/') # image path
    target_url = target_url.replace('t/cfile@', 'https://t1.daumcdn.net/cfile/tistory/') # image path

    target_file =  uuid.uuid4().hex[:8] + '.png'

    target_file_full_path = str(PurePath(target_asset_folder).joinpath(target_file))

    logging.log_info(' -- download files : ' + target_url + '-->' + target_file_full_path)

    save_from_target_url(target_url, target_file_full_path)
    logging.log_info('\n...')

    attach_meta_dic['file_name'] = target_file
    attach_meta_dic['file_url'] = target_url
    attach_meta_dic['attach_folder'] = str(PurePath(target_asset_folder).name)

    return attach_meta_dic

# step2-1 : convert attach string :: images
def tistory_attach_str_proc2_1(markdown_str, target_asset_folder) :
    '''
    ![img](http://cfile22.uf.tistory.com/image/99B0D7335A0EEEC41864F7) 의 스트링을 필터링
    '''

    attach_meta_dic_arr = []

    p = re.compile('(\[\!\[.*\].*\(http.*\))')
    m = p.search(markdown_str)
    while m is not None:
        pattern_str = str(m.group())
        attach_meta_dic = tistory_attach_str_proc2_2(pattern_str[1:], target_asset_folder)
        attach_meta_dic_arr.append(attach_meta_dic)
        markdown_str = markdown_str.replace(pattern_str,tistory_attach_str_proc0_1(attach_meta_dic))
        m = p.search(markdown_str)

    p = re.compile('(\!\[.*\].*\(http.*\))')
    m = p.search(markdown_str)
    while m is not None:
        pattern_str = str(m.group())
        attach_meta_dic = tistory_attach_str_proc2_2(pattern_str, target_asset_folder)
        attach_meta_dic_arr.append(attach_meta_dic)
        markdown_str = markdown_str.replace(pattern_str,tistory_attach_str_proc0_1(attach_meta_dic))
        m = p.search(markdown_str)

    metatools.save_attach_meta_file(target_asset_folder, attach_meta_dic_arr)

    return markdown_str

def tistory_attach_str_proc2_2(tag_str, target_asset_folder) :
    attach_meta_dic = metatools.get_attach_meta_skel()
    picture_file_ext_list = '(\.jpg$|\.png$|\.bmp$)'

    spilt_str = re.split('!|\[|\]|\(|\)',tag_str)
    # ['', '', 'img', '', 'http://cfile22.uf.tistory.com/image/99B0D7335A0EEEC41864F7', '']

    target_file = uuid.uuid4().hex[:8]
    target_url = spilt_str[4]

    if target_url.find('.jpg') == -1 :
        target_file = target_file + '.jpg'
    elif target_url.find('.png') == -1 :
        target_file = target_file + '.png'
    elif target_url.find('.bmp') == -1 :
        target_file = target_file + '.bmp'
    else :
        # default : non ext file
        target_file = target_file + '.png'

    # replace for tistory attachfile

    target_file_full_path = str(PurePath(target_asset_folder).joinpath(target_file))

    logging.log_info(' -- download files : ' + target_url + ' --> ' + target_file_full_path)
    # wget.download(target_url, target_file_full_path)
    save_from_target_url(target_url, target_file_full_path)

    logging.log_info('\n...')

    attach_meta_dic['file_name'] = target_file
    attach_meta_dic['file_url'] = target_url
    attach_meta_dic['attach_folder'] = str(PurePath(target_asset_folder).name)

    return attach_meta_dic

# step3 : markdown attach string
def tistory_attach_str_proc0_1(attach_meta_dic) :
    picture_file_ext_list = '(\.jpg$|\.png$|\.bmp$)'

    markdown_attach_pic_str = ''
    # check images
    p = re.compile(picture_file_ext_list)
    m = p.search(attach_meta_dic['file_name'])

    if m != None:
        markdown_attach_pic_str = "![](./" + attach_meta_dic['attach_folder'] + "/" + attach_meta_dic['file_name'] + ")"

    return markdown_attach_pic_str

def covert_markdown_header_to_str(markdown_header_yml_dic) :
    markdown_yml_str = ''

    markdown_yml_str += '---\n'
    markdown_yml_str += 'title: ' + clean_escape_char(markdown_header_yml_dic['title']) + '\n'
    markdown_yml_str += 'publish: ' + markdown_header_yml_dic['publish'] + '\n'
    markdown_yml_str += 'tags: ' + markdown_header_yml_dic['tags'] + '\n'
    markdown_yml_str += '--- \n\n\n\n'

    return markdown_yml_str

