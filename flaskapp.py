from flask import Flask, g, render_template, request, url_for
import sqlite3

from forms import SearchForm

app = Flask(__name__)
app.config['SECRET_KEY'] = b'\x19\x15\x95\xfa\x08\xcd\x08\xe58]d\xfd\xcf`\x1dy\xfc\x0f\xb6\xc7\xda>\x96-'
#todo: add support for flashes in base.html


def get_resource_as_string(name, charset='utf-8'):
    with app.open_resource(name) as f:
        return f.read().decode(charset)

# index page
@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
def index():
    form = SearchForm()
    g.db = sqlite3.connect('newsWeb.sqlite')

    if form.validate_on_submit():
        searchTerm = form.searchBox.data
        cur = g.db.execute('SELECT word, reading, frequency FROM Words WHERE word LIKE ? ORDER BY frequency DESC',
                           ("%" + searchTerm + "%", ))
        words = [dict(word=row[0], reading=row[1], frequency=row[2])
                 for row in cur.fetchall()]

    if request.method == 'GET':
        cur = g.db.execute(
            'SELECT word, reading, frequency FROM Words ORDER BY frequency DESC')
        words = [dict(word=row[0], reading=row[1], frequency=row[2])
                 for row in cur.fetchall()]

    g.db.close()
    return render_template('index.html', words=words, form=form)

# article page
#todo: panel to mouse over highlighted word definition
@app.route('/article/<name>/')
def word(name=None):
    form = SearchForm()
    g.db = sqlite3.connect('newsWeb.sqlite')
    cur = g.db.execute(
        'SELECT text, title FROM Articles WHERE newsid = ?', [name])
    #todo: only grab the first row in matched articles
    texts = [dict(text=row[0], title=row[1]) for row in cur.fetchall()]
    cur = g.db.execute(
        'SELECT DISTINCT Word FROM Examples WHERE newsid = ?', [name])
    words = [dict(word=row[0]) for row in cur.fetchall()]
    g.db.close()
    return render_template('article.html', texts=texts, name=name, words=words, form=form)

# word page
@app.route('/word/<name>/')
def article(name=None):
    form = SearchForm()
    g.db = sqlite3.connect('newsWeb.sqlite')
    cur = g.db.execute(
        'SELECT word, reading, rubyDefinition, frequency, category, alt FROM Words WHERE Words.word = ?', [name])
    wordInfo = [dict(word=row[0], reading=row[1], definition=row[2], frequency=row[
                     3], category=row[4], alt=row[5]) for row in cur.fetchall()]

    #todo: grab the article titles too
    cur = g.db.execute(
        'SELECT sentence, newsid FROM Examples WHERE word = ? ORDER BY length(sentence)', [name])
    sentences = [dict(sentence=row[0], newsid=row[1])
                 for row in cur.fetchall()]
    g.db.close()
    return render_template('word.html', wordInfo=wordInfo, sentences=sentences, form=form)

#todo: add summary page
#todo: add exports page (options to hide loan words)
# todo:0 add 404 error page

if __name__ == '__main__':
    app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string
    app.run(debug=True)
