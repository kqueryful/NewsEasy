import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = b'\x19\x15\x95\xfa\x08\xcd\x08\xe58]d\xfd\xcf`\x1dy\xfc\x0f\xb6\xc7\xda>\x96-'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'news.db')
app.logger.setLevel("DEBUG")

db = SQLAlchemy(app)
