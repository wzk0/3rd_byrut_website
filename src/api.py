import requests
from bs4 import BeautifulSoup
import os
import json
import random
import hashlib
import baidu

domain='https://thebyrut.org'
api='https://fanyi-api.baidu.com/api/trans/vip/translate'

# 使用百度翻译
appid=baidu.appid
key=baidu.key

headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0'}

# 获取soup的通用函数
def get_soup(part,params={}):
	r=requests.get(domain+part,params=params,headers=headers)
	return BeautifulSoup(r.text,features='html5lib')

# 翻译api的调用, 如果不使用百度, 也可以修改这个函数自行替换, 最后传出的结果是翻译后的纯文本
def translate(content,language):
	salt=''.join(random.sample('1234567890',10))
	params={'q':content,'from':'auto','to':language,'appid':appid,'salt':salt,'sign':hashlib.md5((appid+content+salt+key).encode('utf-8')).hexdigest()}
	return json.loads(requests.get(api,params=params).text)['trans_result'][0]['dst']

# 搜索函数, 必须传入keyword(关键词), page(页码), 是否翻译以及目标语言可选
def search(keyword,page=1,if_translate=False,language=None):
	soup=get_soup('/index.php?do=search&subaction=search&search_start=%s&full_search=0&story=%s'%(page,keyword))
	result=[]
	for meta,storage,star,img,about in zip(soup.find_all('div',class_='short_titles'),soup.find_all('div',class_='shor_subtitles'),soup.find_all('div',class_='rate-stars'),soup.find_all('div',class_='short_imgs'),soup.find_all('div',class_='shor_desc')):
		# 是否启用翻译, 下同
		if if_translate:
			result.append({'name':meta.text.replace('\n        ','').replace('\n    ',''),'url':meta.find('a')['href'].replace('https://thebyrut.org',''),'release_year':storage.find_all('span')[0].text.replace(' •',''),'storage':storage.find_all('span')[-1].text.replace('ГБ','G').replace('МБ','M').replace('Анонс','NULL'),'rate':int(star.find('li').text)/100,'img':domain+img.find('img')['src'],'short_about':translate(about.text,language)+'...'})
		else:
			result.append({'name':meta.text.replace('\n        ','').replace('\n    ',''),'url':meta.find('a')['href'].replace('https://thebyrut.org',''),'release_year':storage.find_all('span')[0].text.replace(' •',''),'storage':storage.find_all('span')[-1].text.replace('ГБ','G').replace('МБ','M').replace('Анонс','NULL'),'rate':int(star.find('li').text)/100,'img':domain+img.find('img')['src'],'short_about':about.text+'...'})
	return result

# 获取游戏信息函数, 必须传入游戏链接(去除主域名), 翻译相关同上
def info(url,if_translate=False,language=None):
	soup=get_soup(url)
	details=soup.find('div',class_='game_details')
	if if_translate:
		result={'name':details.find('div',class_='hname').find('h1').text.replace('\n                ',''),'release_date':translate(details.find('span',class_='dateym').text,language),'developer':details.find_all('li')[1].text.replace('Разработчик: ',''),'description':translate(soup.find('div',class_='game_desc').text,language),'rate':int(details.find('li',class_='current-rating').text)/100,'img':domain+soup.find('img',class_='imgbox')['src'],'download':soup.find('a',class_='itemtop_games')['href'],'dl_times':soup.find('div',class_='min-details').find('span').text.replace(' ',''),'update_time':translate(soup.find('div',class_='tquote').text.replace('Обновлено - ','').replace('.подробности обновления',''),language),'storage':soup.find('div',class_='persize_bottom').find('span').text.replace('ГБ','G').replace('МБ','M')}
	else:
		result={'name':details.find('div',class_='hname').find('h1').text.replace('\n                ',''),'release_date':details.find('span',class_='dateym').text,'developer':details.find_all('li')[1].text.replace('Разработчик: ',''),'description':soup.find('div',class_='game_desc').text,'rate':int(details.find('li',class_='current-rating').text)/100,'img':domain+soup.find('img',class_='imgbox')['src'],'download':soup.find('a',class_='itemtop_games')['href'],'dl_times':soup.find('div',class_='min-details').find('span').text.replace(' ',''),'update_time':soup.find('div',class_='tquote').text.replace('Обновлено - ','').replace('.подробности обновления',''),'storage':soup.find('div',class_='persize_bottom').find('span').text.replace('ГБ','G').replace('МБ','M')}
	return result

# 下载函数, 本地可用
def download(url):
	dl_info=info(url)
	os.system('wget \"%s\" -O \"%s\"'%(dl_info['download'],dl_info['name']))