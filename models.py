import sys

sys.path.append("..")
from newsEasy import db

class Word(db.Model):
    word = db.Column(db.Text, primary_key=True)
    category = db.Column(db.String(1), server_default='R')
    frequency = db.Column(db.Integer)
    reading = db.Column(db.String(100))
    definition = db.Column(db.Text)

    examples = db.relationship('Example', backref='word', lazy='dynamic')

    def __repr__(self):
        return "<Word {}>".format(self.word)

class Article(db.Model):
    id = db.Column(db.String(30), primary_key=True)
    title = db.Column(db.String(100))
    text = db.Column(db.Text)

    examples = db.relationship('Example', backref='article', lazy='dynamic')

    def __repr__(self):
        return "<Article {}>".format(self.id)

class Example(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sentence = db.Column(db.Text)

    word_id = db.Column(db.Text, db.ForeignKey('word.word'), nullable=False)
    article_id = db.Column(db.Text, db.ForeignKey('article.id'), nullable=False)

    def __repr__(self):
        return "<Example '{}'>".format(self.sentence)

if __name__ == "__main__":
    db.drop_all()
    db.create_all()

    tree = Word(word='tree')
    article = Article(id="k200")
    treeEx = Example(sentence="tree here.", word_id=tree.word, article_id=article.id)
    treeEx1 = Example(sentence="another tree.", word_id=tree.word, article_id=article.id)

    db.session.add(tree)
    db.session.add(article)
    db.session.add(treeEx)
    db.session.add(treeEx1)

    article.title = "tree title"
    db.session.add(article)

    treeEx2 = Example(sentence="tree sentence.")
    treeEx2.word_id = tree.word
    treeEx2.article_id = article.id
    db.session.add(treeEx2)

    db.session.commit()

    for ex in article.examples:
        print(ex.word.word)
