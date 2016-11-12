import re
from collections import defaultdict

from sqlalchemy import desc
from sqlalchemy import and_

from models import Word, Article, Example
from flaskapp import db


if __name__=='__main__':
    words = Word.query.filter_by(category='R').filter(Word.frequency>10).order_by(desc(Word.frequency))
    wordsDef = words

    highFreqWords = Word.query.filter_by(category='R').filter(Word.frequency>10).order_by(desc(Word.frequency))
    definedWordsQuery = Word.query.filter_by(category='R').order_by(desc(Word.frequency))
    definedWords = [r.word for r in definedWordsQuery]

    regex = re.compile(r"^[a-zA-Zア-ーａ-ｚＡ-Ｚ]+$")
    rubyStrip = r"<ruby><rb>(?P<kanji>[^<]+)</rb><rt>[^<]*</rt></ruby>"
    dependencies = defaultdict(list)





    for word in highFreqWords:
        if (regex.match(word.word) is None):
            strippedDef = re.sub(rubyStrip, r'\g<kanji>', word.definition)

            for defWord in definedWords:
                if defWord in strippedDef:
                    dependencies[word.word].append(defWord)
                elif not dependencies[word.word]:
                    dependencies[word.word] = []







    for word in dependencies:
        try:
            print (word, dependencies[word])
        except:
            pass
