import re
import json
import glob
from urllib import request
from grabber import Grabber
from sqliteInstance import SqliteInstance
from formatter import Formatter


def download_files():
    grabber = Grabber()

    for id in grabber.get_grabber('fromSite'):
        grabber.download_article(id)

if __name__ == '__main__':
    download_files()

    # setup
    db = SqliteInstance()
    db.table_setup()
    formatter = Formatter()

    # for each article
    for files in glob.glob("news/*.out.json"):
        article = json.load(open(files, encoding="utf-8"))

        # article prep
        text = article["text"]
        title = text.split(' ')[0]
        articleText = text[len(title):]
        fancyArticle = articleText
        articleLines = articleText.split(u"。")

        # for each word
        for item in article["morph"]:

            # proper nouns
            if item.get("class") in ['L', 'N', 'C'] and item["word"] != u"・":
                                # get readings
                reading = ""
                for index, val in enumerate(item["ruby"]):
                    try:
                        reading += item["ruby"][index]["r"]
                    except KeyError:
                        reading += item["ruby"][index]["s"]

                # add word
                db.add_word(item["word"], reading, category=item["class"])

                # add examples
                for line in articleLines:
                    if item["word"] in line:
                        sentence = formatter.bold_in_sentence(item["word"], line)
                        db.add_example(
                            item["word"], sentence, article["newsid"])

                # article highlighting
                fancyArticle = formatter.highlight(
                    item["word"], fancyArticle, item["class"])

            # defined words
            if item.get("dicid") != None and not item.get("dicid").isspace():
                # get reading
                reading = item["kana"]

                # match dicid BE-0000 to 0000
                dicid = item["dicid"][3:]

                # match json file to dic file
                dicPath = files[:-4] + 'dic'
                try:
                    dicFile = json.load(open(dicPath, encoding="utf-8"))
                except:
                    print(dicPath)

                ankiDefs = []
                rubyDefs = []
                for entry in dicFile["reikai"]["entries"][dicid]:
                    rubyDefs.append(entry["def"])
                    ankiDef = formatter.convert_to_ankiDef(entry["def"])
                    ankiDefs.append(ankiDef)

                ankiDefs = "<br>".join(ankiDefs)
                rubyDefs = "<br>".join(rubyDefs)

                # find alternate forms
                altList = []
                for version in dicFile["reikai"]["entries"][dicid][0]["hyouki"]:
                    version = re.sub(u"・", "", version)
                    if version != item["base"]:
                        altList.append(version)
                alt = ", ".join(altList)

                # add word
                db.add_word(item["base"], reading, alt=alt,
                            ankiDefs=ankiDefs, rubyDefs=rubyDefs)

                # add examples
                for line in articleLines:
                    if item["word"] in line:
                        sentence = formatter.bold_in_sentence(
                            item["word"], line)
                        db.add_example(
                            item["base"], sentence, article["newsid"])

                # article highlighting
                fancyArticle = formatter.highlight(item["word"], fancyArticle)

                # save article
        db.add_article(article["newsid"], title, fancyArticle, fancyArticle)

    db.commit()
    db.clean_up()
