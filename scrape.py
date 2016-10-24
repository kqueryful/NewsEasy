import json
import glob
import re

from models import Word, Article, Example
from flaskapp import db
from grabber import Grabber

def download_files():
    """
    download all files
    """
    grabber = Grabber()

    for id in grabber.get_grabber('fromSite'):
        grabber.download_article(id)

# helper functions
def is_proper_noun(category, word):
    """
    return true if word is a proper noun
    """
    return category in ['L', 'N', 'C'] and word not in [u"・", u"　"]

def is_defined(dicid):
    """
    return true if word has a definition
    """
    return dicid != None and not dicid.isspace()

def build_reading(ruby):
    """
    return a word's ruby-formatted reading
    """
    reading = ""
    for index, val in enumerate(ruby):
        try:
            reading += ruby[index]["r"]
        except KeyError:
            reading += ruby[index]["s"]
    return reading

def build_definition(dicPath, dicid):
    """
    return a word's ruby-formatted definition
    """
    try:
        dicFile = json.load(open(dicPath, encoding="utf-8"))
    except:
        print("Problems opening " + dicPath)

    rubyDefs = []
    for entry in dicFile["reikai"]["entries"][dicid]:
        rubyDefs.append(entry["def"])

    return "<br>".join(rubyDefs)

# main article scraping function
def scrape_article(path):
    words = {}
    examples = set()

    # for each article file
    for filename in glob.glob(path):
        article = ""
        id = filename[5:-9]
        dicPath = filename[:-4] + 'dic'
        a = Article(id=id)

        article_data = json.load(open(filename, encoding="utf-8"))

        # for every article element
        for item in article_data["morph"]:
            word = item["word"]
            base = item.get("base")
            category = item.get("class")
            dicid = item.get("dicid")
            definition = None
            reading = item.get("kana")
            tagged_word = word

            if is_proper_noun(category, word):
                reading = build_reading(item["ruby"])
                base = word

            elif is_defined(dicid):
                category = 'R'
                definition = build_definition(dicPath, dicid[3:])

            if is_proper_noun(category, word) or is_defined(dicid):
                tagged_word = "<a href='/word/{}'><span class='{}'>{}</span></a>".format(base, category, word)

                # prepare to save to DB
                if word not in words:
                    w = Word(word=word)
                    w.category = category
                    w.reading = reading
                    w.definition = definition
                    w.frequency = 1
                    words[word] = w
                else:
                    words[word].frequency += 1

            # build up article text
            article += tagged_word

        # take the first line, minus the last </S>
        a.title = article.split('<S>')[1][:-len("</S>")]

        # article text starts after the title
        a.text = article[len(a.title)+len("<S></S>"):]

        db.session.add(a)

        # get all examples
        strippedArticle = re.sub("</*S>", '', article)
        sentenceRegex = r"[^。]*[。]+"
        sentences = re.finditer(sentenceRegex, strippedArticle)

        for sentenceMatch in sentences:
            sentence = sentenceMatch.group()
            regex = r"<a href='/word/(?P<base>[^']+)'><span class='.'>(?P<word>[^<]+)</span></a>"
            matches = re.finditer(regex, sentence)
            sentence = re.sub(regex, "\g<word>", sentence)

            for word in matches:
                wordSentence = re.sub(word.group('word'), "<b>"+ word.group('word') +"</b>", sentence)

                # add example sentence to DB
                if wordSentence not in examples:
                    examples.add(wordSentence)
                    ex = Example(sentence=wordSentence)
                    ex.word_id = word.group('base')
                    ex.article_id = id
                    db.session.add(ex)

    for word in words:
        db.session.add(words[word])

    db.session.commit()

if __name__ == "__main__":
        # setup
        download_files()
        db.drop_all()
        db.create_all()

        # all article scraping
        scrape_article("news/*.out.json")
