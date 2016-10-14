from flask import Flask, g, render_template, request, url_for
import sqlite3

app = Flask(__name__)

def get_resource_as_string(name, charset='utf-8'):
    with app.open_resource(name) as f:
        return f.read().decode(charset)

# index page
@app.route('/', methods=["GET","POST"])
@app.route('/index', methods=["GET","POST"])
def index():
	g.db = sqlite3.connect('newsWeb.sqlite')
	if request.method != 'POST':
		cur = g.db.execute('SELECT word, reading, frequency FROM Words ORDER BY frequency DESC')
		words = [dict(word=row[0], reading=row[1], frequency=row[2]) for row in cur.fetchall()]
	else:
		cur = g.db.execute('SELECT word, reading, frequency FROM Words WHERE word LIKE ? ORDER BY frequency DESC', ("%"+request.form['word']+"%", ))
		words = [dict(word=row[0], reading=row[1], frequency=row[2]) for row in cur.fetchall()]
	g.db.close()
	return render_template('index.html', words=words)

# article page
@app.route('/article/<name>/')
def word(name=None):
	g.db = sqlite3.connect('newsWeb.sqlite')
	cur = g.db.execute ('SELECT text FROM Articles WHERE newsid = ?', [name])
	texts = [dict(text=row[0]) for row in cur.fetchall()]
	cur = g.db.execute ('SELECT DISTINCT Word FROM Examples WHERE newsid = ?', [name])
	words = [dict(word=row[0]) for row in cur.fetchall()]
	g.db.close()
	return render_template('article.html', texts=texts, name=name, words=words)

# word page
@app.route('/word/<name>/')
def article(name=None):
	g.db = sqlite3.connect('newsWeb.sqlite')
	cur = g.db.execute ('SELECT word, reading, definition, frequency, category, alt FROM Words WHERE Words.word = ?', [name])
	wordInfo = [dict(word=row[0], reading=row[1], definition=row[2], frequency=row[3], category=row[4], alt=row[5]) for row in cur.fetchall()]
	cur = g.db.execute('SELECT sentence, newsid FROM Examples WHERE word = ? ORDER BY length(sentence)', [name])
	sentences = [dict(sentence=row[0], newsid=row[1]) for row in cur.fetchall()]
	g.db.close()
	return render_template('word.html', wordInfo=wordInfo, sentences=sentences)

if __name__ == '__main__':
	app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string
	app.run(debug=True)
