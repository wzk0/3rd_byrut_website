import requests
from bs4 import BeautifulSoup
import os
import json
import random
import hashlib
import baidu
from random import choice

domain_byrut='https://thebyrut.org'
domain_repack='https://repack.info'
api='https://fanyi-api.baidu.com/api/trans/vip/translate'

# 使用百度翻译.
appid=baidu.appid
key=baidu.key

headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0'}

# 获取soup的通用函数.
def get_soup(part,params={},data={},way='byrut'):
	if way=='byrut':
		domain=domain_byrut
	elif way=='repack':
		domain=domain_repack
	req=requests.Session()
	r=req.post(domain+part,params=params,data=data,headers=headers)
	return BeautifulSoup(r.text,features='html5lib')

# 翻译api的调用, 如果不使用百度, 也可以修改这个函数自行替换, 最后传出的结果是翻译后的纯文本.
def translate(content,language):
	salt=''.join(random.sample('1234567890',10))
	params={'q':content,'from':'auto','to':language,'appid':appid,'salt':salt,'sign':hashlib.md5((appid+content+salt+key).encode('utf-8')).hexdigest()}
	return json.loads(requests.get(api,params=params).text)['trans_result'][0]['dst']

class byrut:
	domain=domain_byrut

	# 搜索函数, 必须传入keyword(关键词), page(页码), 是否翻译以及目标语言可选.
	def search(keyword,page=1,if_translate=False,language=None):
			soup=get_soup('/index.php',data={'do':'search','subaction':'search','search_start':page,'full_search':0,'story':keyword})
			result=[]
			for entry in soup.find_all('div',class_='short_search'):
				l_info=entry.find('div',class_='short_imgs')
				name=l_info.find('img')['alt']
				url='/byrut'+l_info.find('a')['href'].replace(byrut.domain,'')
				subtitles=entry.find('div',class_='shor_subtitles')
				release_year=subtitles.find('span').text.replace(' •','')
				storage=subtitles.find_all('span')[-1].text.replace('ГБ','G').replace('МБ','M').replace('B','').replace('Анонс','NULL')
				rate=int(entry.find('li',class_='current-rating').text)/100
				img=byrut.domain+l_info.find('img')['src']
				if if_translate:
					short_about=translate(entry.find('div',class_='shor_desc').text,language)+'...'
				else:
					short_about=entry.find('div',class_='shor_desc').text+'...'
				result.append({'name':name,'url':url,'release_year':release_year,'storage':storage,'rate':rate,'img':img,'short_about':short_about,'src':'Byrutor'})
			return result
	# 获取游戏信息函数, 必须传入游戏链接(去除主域名), 翻译相关同上.
	def info(url,if_translate=False,language=None):
			soup=get_soup(url)
			details=soup.find('div',class_='game_details')
			name=details.find('div',class_='hname').find('h1').text.replace('\n                ','')
			developer=details.find_all('li')[1].text.replace('Разработчик: ','')
			rate=int(details.find('li',class_='current-rating').text)/100
			img=byrut.domain+soup.find('img',class_='imgbox')['src']
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

class repack:
	domain=domain_repack

	def search(keyword,page=1,if_translate=False,language=None):
		soup=get_soup('/index.php',data={'do':'search','subaction':'search','story':keyword,'search_start':page},way='repack')
		result=[]
		for entry in soup.find_all('div',class_='entry'):
			l_info=entry.find('div',class_='entry__title h2').find('a')
			name=l_info.text.split(' | ')[0]
			url='/repack/'+l_info['href'].replace(repack.domain+'/repacks/','').replace('/','_')
			year=entry.find('div',class_='entry__info-wrapper').find_all('a')
			zero=0
			while zero<=len(year):
				if year[zero].text.isdigit():
					release_year=year[zero].text
					break
				else:
					pass
				zero+=1
			storage=entry.find('span',class_='entry__info-size').text.replace('B','')
			rate=float(entry.find('div','entry__rating').find('span').text)*2/10
			img=repack.domain+entry.find('img')['src']
			if if_translate:
				short_about=translate(entry.find('div',class_='entry__content-description').text[:200].replace('\t','').replace('\n',''),language)+'...'
			else:
				short_about=entry.find('div',class_='entry__content-description').text[:200].replace('\t','').replace('\n','')+'...'
			result.append({'name':name,'url':url,'release_year':release_year,'storage':storage,'rate':rate,'img':img,'short_about':short_about,'src':'Repack'})
		return result
	def info(url,if_translate=False,language=None):
		soup=get_soup('/repacks/'+url.replace('_','/'),way='repack')
		l_info=soup.find('div',class_='inner-entry__allinfo-wrapper clearfix')
		name=l_info.find('h1').text.split(' | ')[0]
		details=soup.find('div',class_='inner-entry__content-text').find_all('p')
		developer=details[2].text
		release_date=details[0].text.replace('Год выпуска: ','')
		rate=float(l_info.find('span',class_='entry__rating-value entry__rating-value_turquoise').text)*2/10
		img=repack.domain+l_info.find('img')['src']
		download=l_info.find('a',class_='download-torrent')['href']
		dl_times=l_info.find('span',class_='download-torrent__total-size').text.replace('Скачиваний: ','')
		try:
			storage=l_info.find('span',class_='entry__info-size').text.replace('B','')
		except:
			storage='NULL'
		update_time=l_info.find('span',class_='entry__date').text
		if if_translate:
			description=translate(details[-1].text,language)
		else:
			description=details[-1].text
		result={'name':name,'release_date':release_date,'developer':developer,'description':description,'rate':rate,'img':img,'download':download,'dl_times':dl_times,'update_time':update_time,'storage':storage}
		return result

# 获取排行榜, page为页码, way为排行榜类型, 必需.
def top(page,way):
	soup=get_soup('/engine/mods/custom/ajax.php',data={'name':way,'cstart':page,'action':'getpage'})
	result=[]
	for s in soup.find_all('div',class_='short_item'):
		img=s.find('div',class_='short_img').find('img')['src']
		if img.startswith(domain_byrut):
			pass
		else:
			img=domain_byrut+img
		l_info=s.find('div',class_='short_title').find('a')
		name=l_info.text
		url=l_info['href']
		storage=s.find('span',class_='size').text.replace('\n','').replace('    ','').replace('ГБ','G').replace('МБ','M').replace('Анонс','NULL')
		dl_times=s.find('span',class_='views').text.replace(' ','')
		release_year=s.find('span',class_='short_year').text.replace(' г.','')
		result.append({'name':name,'url':url.replace(domain_byrut,''),'img':img,'storage':storage,'dl_times':dl_times,'release_year':release_year,'src':'byrut'})
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