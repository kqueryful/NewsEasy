from flask import Flask, g, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import sqlite3
import os
import sys

sys.path.append("..")
from newsEasy import app, db

from forms import SearchForm
from models import Word, Example, Article

def get_resource_as_string(name, charset='utf-8'):
    with app.open_resource(name) as f:
        return f.read().decode(charset)

# index page
@app.route('/', methods=["GET", "POST"])
@app.route('/index', methods=["GET", "POST"])
def index():
    form = SearchForm()
    words = []
    titles = []
    searchTerm = ""
    wordsQuery = None
    titlesQuery = None
    wordsCount = None
    articlesCount = None


    if form.validate_on_submit():
        searchTerm = form.searchBox.data
        wordsQuery = Word.query.filter(Word.word.like('%' + searchTerm + '%')).order_by(Word.frequency.desc())
        words = wordsQuery.all()
        titlesQuery = Article.query.filter(Article.title.like('%' + searchTerm + '%'))
        titles = titlesQuery.all()

        if not ( words or titles):
            flash(u'Searched for 「{}」, but got no results.'.format(searchTerm), 'error')
        else:
            flash(u'Below are the results for 「{}」.'.format(searchTerm))

    elif request.method == 'POST':
        flash('Nothing typed into searchbar.', 'error')

    elif request.method == 'GET':
        wordsCount = Word.query.count()
        articlesCount = Article.query.count()
        words = Word.query.order_by(Word.frequency.desc()).limit(10)

    return render_template('index.html', words=words, wordsQuery=wordsQuery,
    titles=titles, titlesQuery=titlesQuery, wordsCount=wordsCount,
    articlesCount=articlesCount, form=form)


# article page
#todo:50 panel to mouse over highlighted word definition
@app.route('/article/<id>/')
def word(id=None):
    form = SearchForm()
    texts = Article.query.filter_by(id=id).first()
    examples = Example.query.filter_by(article_id=id).group_by(Example.word_id)

    return render_template('article.html', texts=texts, name=id, examples=examples, form=form)

# word page
#todo: display word frequency in _ articles on word page
@app.route('/word/<name>/')
def article(name=None):
    form = SearchForm()
    word = Word.query.filter_by(word=name).first()
    sentences = Example.query.filter_by(word_id=name).all()

    return render_template('word.html', word=word, sentences=sentences, form=form)

#todo:20 add summary page
#todo:10 add exports page (options to hide loan words)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string
    app.run(debug=True)
