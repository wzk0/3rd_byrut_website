import api
from flask import Flask,render_template,request,url_for,redirect
import random

app=Flask(__name__)
Language=False

@app.route('/',methods=['GET','POST'])
def index():
	if request.method=='POST':
		game=request.form.get('game')
		return redirect(url_for('search',game=game,language='zh',page='1'))
	data=api.top(random.randint(1,14),'top_main_all')
	return render_template('index.html',data=data,language='zh')

@app.route('/search/<language>/<game>/<page>',methods=['GET', 'POST'])
def search(game,language='zh',page='1'):
	if request.method=='POST':
		game=request.form.get('game')
		return redirect(url_for('search',game=game,language='zh',page='1'))
	if Language:
		data=api.search(game,page=page,if_translate=True,language=language)
	else:
		data=api.search(game,page=page)
	page=int(page)
	return render_template('show.html',data=data,game=game,language=language,page=page)

@app.route('/game/<language>/<game>',methods=['GET', 'POST'])
def info_game(language,game):
	if request.method=='POST':
		game=request.form.get('game')
		return redirect(url_for('search',game=game,language='zh',page='1'))
	if Language:
		data=api.info('/'+game,if_translate=True,language=language)
	else:
		data=api.info('/'+game)
	r_data=api.random_()
	return render_template('game.html',data=data,r_data=r_data,language=language)

@app.route('/api/<do>/<language>/<content>')
def give_api(do,language,content):
	if do=='search':
		if Language:
			return api.search(content,language,if_translate=True,language=language)
		else:
			return api.search(content)
	elif do=='info':
		if Language:
			return api.info('/'+content,if_translate=True,language=language)
		else:
			return api.info('/'+game)
	else:
		return 'error'

if __name__ == '__main__':
	app.run(debug=True)

if Language:
	pass
else:
	pass