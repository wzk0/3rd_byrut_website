import requests
from bs4 import BeautifulSoup
import baidu

domain='https://freetp.org'
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

def search(keyword,page=1,if_translate=False,language=None):
	soup=get_soup('/index.php',data={'do':'search','subaction':'search','story':keyword,'search_start':page,'result_from':1+page*10,'full_search':'0'})
	print(soup)
	result=[]
	for entry in soup.find_all('div',class_='base'):
		l_info=entry.find('div',class_='short-story gg')
		name=l_info.find('img')['alt']
		url=1
		print(entry)
		# url='/freetp'+entry.find('div',class_='heading').find('a')['href'].replace(domain+'/po-seti','')
		release_year='NULL'
		storage='NULL'
		rate='NULL'
		img=domain+entry.find('img')['src']
		if if_translate:
			short_about=translate(entry.find('p').text.replace('\n',''),language)+'...'
		else:
			short_about=entry.find('p').text.replace('\n','')+'...'
		result.append({'name':name,'url':url,'release_year':release_year,'storage':storage,'rate':rate,'img':img,'short_about':short_about,'src':'freetp'})
	return result

print(search('dead'))