# -*- coding: utf-8 -*- 
# Author: J. Lee
# Python 2.7.12 on Linux Mint 18

import re, os, requests, pickle, shutil, urllib
from bs4 import BeautifulSoup
from urlparse import urlparse
from os.path import splitext, basename

dir_name='collect' # 파일을 저장할 폴더의 이름
gall_id='tree' # 식물 갤러리
domain='http://gall.dcinside.com'
recommend_url='/board/lists/?id='+gall_id+'&page=1&exception_mode=recommend'

done_list = [] # 한번 다운받은 페이지는 skip

def init():
	global done_list
	try: 
		done_list=pickle.load(open('done_list.log','r')) # 여러 번 실행하는 경우 한번만 scrap
	except:
		pass
	try:
		os.makedirs(dir_name+'/images') # 처음 실행하는 경우, 폴더를 구성
	except:
		pass

def cleanup():
	pickle.dump(done_list,open('done_list.log','w'))

def get_html(url):
	return requests.get(url).text

def save_page(url):
	page_no=re.findall(r'\d+', url)[0] # 글 번호

	html=get_html(url)
	soup=BeautifulSoup(html,'lxml')

	for link in soup.select('img'):
		try:
			img_src=link.get('src')
			filename=basename(urlparse(img_src).path)
			if filename=='viewimage.php': # 이미지 다운로드
				img=urllib.urlopen(img_src.replace('dcimg1','dcimg2'))
				img_name=img.info().getheader('Content-Disposition')[21:]
				open(dir_name+'/images/'+img_name, 'wb').write(img.read())
				html=html.replace(img_src,'images/'+img_name)
		except:
			print img_src

	open(dir_name+'/['+str(page_no)+'] '+soup.title.string+'.html','w').write(html.encode('utf8'))
	print "save: "+page_no


def scrap():
	html=get_html(domain+recommend_url)
	soup=BeautifulSoup(html,'lxml')

	for link in soup.select('td > a'): # 개념글들의 url을 추출
		if link.get('class')==['icon_pic_b']:
			href=link.get('href')
			if not href in done_list:
				save_page(domain+href)
				done_list.append(href)


init()
scrap()
cleanup()

