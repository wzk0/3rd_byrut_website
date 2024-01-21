import api
from flask import Flask,render_template,request,url_for,redirect

app=Flask(__name__)

@app.route('/',methods=['GET','POST'])
def index():
	if request.method=='POST':
		game=request.form.get('game')
		return redirect(url_for('search',game=game,language='zh'))
	return render_template('index.html')

@app.route('/search/<language>/<game>',methods=['GET', 'POST'])
def search(game,language='zh'):
	if request.method=='POST':
		game=request.form.get('game')
		return redirect(url_for('search',game=game,language='zh'))
	data=api.search(game,language,if_translate=True,language=language)
	# data=api.search(game)
	return render_template('show.html',data=data,game=game,language=language)

@app.route('/game/<language>/<game>',methods=['GET', 'POST'])
def info_game(language,game):
	if request.method=='POST':
		game=request.form.get('game')
		return redirect(url_for('search',game=game,language='zh'))
	data=api.info('/'+game,if_translate=True,language=language)
	# data=api.info('/'+game)
	return render_template('game.html',data=data)

if __name__ == '__main__':
	app.run(debug=True)