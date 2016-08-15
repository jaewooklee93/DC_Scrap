# -*- coding: utf-8 -*- 
# Author: J. Lee
# Python 2.7.12 on Linux Mint 18

import re, os, requests, pickle, urllib
from bs4 import BeautifulSoup
from urlparse import urlparse
from os.path import splitext, basename
from selenium import webdriver # install selenium nodejs phantomjs 

dir_name='collect' # 파일을 저장할 폴더의 이름
gall_id='tree' # 식물 갤러리
domain='http://gall.dcinside.com'
recommend_url='/board/lists/?id='+gall_id+'&page=1&exception_mode=recommend'

done_list = [] # 한번 다운받은 페이지는 skip

def init():
	global done_list
	try: 
		done_list=pickle.load(open(dir_name+'/images/common/done_list.log','r')) # 여러 번 실행하는 경우 한번만 scrap
	except:
		pass
	try:
		os.makedirs(dir_name+'/images/common') # 처음 실행하는 경우, 폴더를 구성
	except:
		pass
	global driver
	driver=webdriver.PhantomJS()

def cleanup():
	pickle.dump(done_list,open(dir_name+'/images/common/done_list.log','w'))

def save_page(url):
	page_no=re.findall(r'\d+', url)[-2] # 글 번호
	print "page_no: "+page_no,

	driver.get(url) # 병목 구간
	html=driver.page_source
	soup=BeautifulSoup(html,'lxml')

	for link in soup.select('img'): # 이미지 다운로드
		try:
			img_src=link['src']
			if basename(urlparse(img_src).path) in ['viewimage.php', 'dccon.php']: 
				img=urllib.urlopen(img_src.replace('dcimg1','dcimg2'))
				img_name=img.info().getheader('Content-Disposition')[21:]

				while os.path.isfile(dir_name+'/images/'+img_name): # 파일 이름 중복 시를 대비
					name, ext=os.path.splitext(img_name)
					img_name=name+'a'+ext

				open(dir_name+'/images/'+img_name, 'wb').write(img.read()) # save image file
				link['src']='images/'+img_name
		except:
			print img_src


	filename=dir_name+'/['+str(page_no)+'] '+soup.title.string+'.html'
	open(filename,'w').write(soup.encode('utf8')) # save html file
	
	print "ok"

def scrap():
	html=requests.get(domain+recommend_url).text
	soup=BeautifulSoup(html,'lxml')

	for link in soup.select('td > a'): # 개념글들의 url을 추출
		icon=link.get('class')
		if icon and icon[0] in ['icon_pic_b', 'icon_txt_b', 'sec_icon']:
			href=link.get('href')
			if not href in done_list:
				save_page(domain+href)
				done_list.append(href)


init()
scrap()
cleanup()

