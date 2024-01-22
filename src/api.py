import requests
from bs4 import BeautifulSoup
import os
import json
import random
import hashlib
import baidu
from random import choice

domain='https://thebyrut.org'
api='https://fanyi-api.baidu.com/api/trans/vip/translate'

# 使用百度翻译.
appid=baidu.appid
key=baidu.key

headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0'}

# 获取soup的通用函数.
def get_soup(part,params={},data={}):
	r=requests.post(domain+part,params=params,data=data,headers=headers)
	return BeautifulSoup(r.text,features='html5lib')

# 翻译api的调用, 如果不使用百度, 也可以修改这个函数自行替换, 最后传出的结果是翻译后的纯文本.
def translate(content,language):
	salt=''.join(random.sample('1234567890',10))
	params={'q':content,'from':'auto','to':language,'appid':appid,'salt':salt,'sign':hashlib.md5((appid+content+salt+key).encode('utf-8')).hexdigest()}
	return json.loads(requests.get(api,params=params).text)['trans_result'][0]['dst']

# 搜索函数, 必须传入keyword(关键词), page(页码), 是否翻译以及目标语言可选.
def search(keyword,page=1,if_translate=False,language=None):
	soup=get_soup('/index.php?do=search&subaction=search&search_start=%s&full_search=0&story=%s'%(page,keyword))
	result=[]
	for meta,storage,star,img,about in zip(soup.find_all('div',class_='short_titles'),soup.find_all('div',class_='shor_subtitles'),soup.find_all('div',class_='rate-stars'),soup.find_all('div',class_='short_imgs'),soup.find_all('div',class_='shor_desc')):
		name=meta.text.replace('\n        ','').replace('\n    ','')
		url=meta.find('a')['href'].replace(domain,'')
		release_year=storage.find_all('span')[0].text.replace(' •','')
		storage=storage.find_all('span')[-1].text.replace('ГБ','G').replace('МБ','M').replace('Анонс','NULL')
		rate=int(star.find('li').text)/100
		img=domain+img.find('img')['src']
		# 是否启用翻译, 下同.
		if if_translate:
			short_about=translate(about.text,language)+'...'
		else:
			short_about=about.text+'...'
		result.append({'name':name,'url':url,'release_year':release_year,'storage':storage,'rate':rate,'img':img,'short_about':short_about})
	return result

# 获取游戏信息函数, 必须传入游戏链接(去除主域名), 翻译相关同上.
def info(url,if_translate=False,language=None):
	soup=get_soup(url)
	details=soup.find('div',class_='game_details')
	name=details.find('div',class_='hname').find('h1').text.replace('\n                ','')
	developer=details.find_all('li')[1].text.replace('Разработчик: ','')
	rate=int(details.find('li',class_='current-rating').text)/100
	img=domain+soup.find('img',class_='imgbox')['src']
	download=soup.find('a',class_='itemtop_games')['href']
	dl_times=soup.find('div',class_='min-details').find('span').text.replace(' ','')
	try:
		storage=soup.find('div',class_='persize_bottom').find('span').text.replace('ГБ','G').replace('МБ','M')
	except:
		storage='NULL'
	if if_translate:
		try:
			release_date=translate(details.find('span',class_='dateym').text,language)
		except:
			release_date='NULL'
		description=translate(soup.find('div',class_='game_desc').text,language)
		update_time=translate(soup.find('div',class_='tquote').text.replace('Обновлено - ','').replace('.подробности обновления',''),language)
	else:
		try:
			release_date=details.find('span',class_='dateym').text
		except:
			release_date='NULL'
		description=soup.find('div',class_='game_desc').text
		update_time=soup.find('div',class_='tquote').text.replace('Обновлено - ','').replace('.подробности обновления','')
	result={'name':name,'release_date':release_date,'developer':developer,'description':description,'rate':rate,'img':img,'download':download,'dl_times':dl_times,'update_time':update_time,'storage':storage}
	return result

# 获取排行榜, page为页码, way为排行榜类型, 必需.
def top(page,way):
	soup=get_soup('/engine/mods/custom/ajax.php',data={'name':way,'cstart':page,'action':'getpage'})
	result=[]
	for s in soup.find_all('div',class_='short_item'):
		img=s.find('div',class_='short_img').find('img')['src']
		if img.startswith(domain):
			pass
		else:
			img=domain+img
		l_info=s.find('div',class_='short_title').find('a')
		name=l_info.text
		url=l_info['href']
		storage=s.find('span',class_='size').text.replace('\n','').replace('    ','').replace('ГБ','G').replace('МБ','M').replace('Анонс','NULL')
		dl_times=s.find('span',class_='views').text.replace(' ','')
		release_year=s.find('span',class_='short_year').text.replace(' г.','')
		result.append({'name':name,'url':url.replace(domain,''),'img':img,'storage':storage,'dl_times':dl_times,'release_year':release_year})
	return result

# 获取随机页码的随机排行榜.
def random_():
	way=['top_main_all','top_main_actual']
	result=random.choice(way)
	if result==way[0]:
		return top(random.randint(1,14),way[0])
	else:
		return top(random.randint(1,5),way[1])

# 下载函数, 本地可用.
def download(url):
	dl_info=info(url)
	os.system('wget \"%s\" -O \"%s\"'%(dl_info['download'],dl_info['name']))