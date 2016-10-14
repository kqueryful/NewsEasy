import re
import csv
import json
import glob
from urllib import request
import os.path
import sqlite3

from grabber import Grabber


def downloadFiles():
    grabber = Grabber()

    for id in grabber.get_grabber('fromSite'):
        grabber.download_article(id)


def tableSetup():
    try:
        # clear old tables
        c.execute("DROP TABLE Articles")
        c.execute("DROP TABLE Words")
        c.execute("DROP TABLE Examples")
    except sqlite3.OperationalError:
        pass
    try:
        # create new tables
        c.execute("CREATE TABLE Articles (newsid TEXT PRIMARY KEY, text TEXT)")
        c.execute("CREATE TABLE Words (word TEXT PRIMARY KEY, reading TEXT, frequency INTEGER, category TEXT, definition TEXT, alt TEXT, wiki TEXT, jdic TEXT)")
        c.execute(
            "CREATE TABLE Examples (word TEXT, sentence TEXT PRIMARY KEY, newsid TEXT)")
    except sqlite3.OperationalError:
        pass

    conn.commit()

if __name__ == '__main__':
    downloadFiles()

    # SQLite setup
    conn = sqlite3.connect('newsWeb.sqlite')
    c = conn.cursor()
    tableSetup()

    # for each article
    for files in glob.glob("news/*.out.json"):
        article = json.load(open(files, encoding="utf-8"))

        # parse text into sentences
        articleText = article["text"]
        c.execute("INSERT OR IGNORE INTO Articles (newsid, text) VALUES (?,?)",
                  (article["newsid"], articleText))
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

                # insert into sql
                try:
                    c.execute("INSERT INTO Words (word, reading, frequency, category) VALUES (?,?,?,?)",
                              (item["word"], reading, 1, item["class"]))
                except sqlite3.IntegrityError:
                    c.execute(
                        "UPDATE Words SET frequency = frequency + 1 WHERE word = ?", (item["word"],))

                # add examples
                for line in articleLines:
                    if item["word"] in line:
                        sentence = re.sub(
                            item["word"], "<b>" + item["word"] + "</b>", line.strip() + u"。")
                        c.execute("INSERT OR IGNORE INTO Examples VALUES (?,?,?)", (item[
                                  "word"], sentence, article["newsid"]))

            # defined words
            if item.get("dicid") != None and not item.get("dicid").isspace():
                # get readings
                reading = ""
                for index, val in enumerate(item["ruby"]):
                    try:
                        reading += item["ruby"][index]["r"]
                    except KeyError:
                        reading += item["ruby"][index]["s"]

                # find definitions
                dicid = re.sub("BE-", "", item["dicid"])
                dicPath = re.sub("json", "dic", files)
                dicFile = json.load(open(dicPath, encoding="utf-8"))

                defs = ""
                for entry in dicFile["reikai"]["entries"][dicid]:
                    # convert ruby-formatted furigana
                    strippedDef = re.sub("</*ruby>", "", entry["def"])
                    strippedDef = re.sub("</rb>", "", strippedDef)
                    strippedDef = re.sub("<rb>", " ", strippedDef)
                    strippedDef = re.sub("<rt>", "[", strippedDef)
                    strippedDef = re.sub("</rt>", "]", strippedDef)
                    defs += strippedDef + "<br>"
                defs = defs[:-4]

                # find alternate forms
                altList = []
                for version in dicFile["reikai"]["entries"][dicid][0]["hyouki"]:
                    version = re.sub(u"・", "", version)
                    if version != item["base"]:
                        altList.append(version)
                alt = ", ".join(altList)

                # insert into sql
                try:
                    c.execute("INSERT INTO Words (word, reading, frequency, alt, definition) VALUES (?,?,?,?,?)",
                              (item["base"], reading, 1, alt, defs))
                except sqlite3.IntegrityError:
                    c.execute(
                        "UPDATE Words SET frequency = frequency + 1 WHERE word = ?", (item["base"],))

                # add examples
                for line in articleLines:
                    if item["word"] in line:
                        sentence = re.sub(
                            item["word"], "<b>" + item["word"] + "</b>", line.strip() + u"。")
                        c.execute("INSERT OR IGNORE INTO Examples VALUES (?,?,?)", (item[
                                  "base"], sentence, article["newsid"]))

    conn.commit()
    c.close()
    conn.close()
