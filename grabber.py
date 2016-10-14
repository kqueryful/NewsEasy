import os.path
from urllib import request


class Grabber:
    """
    Download news article and dictionary JSON files from the web
    """

    def __init__(self):
        self.url = "http://www3.nhk.or.jp/news/easy"

        # make news directory if not already there
        if not os.path.exists("news"):
            os.makedirs("news")

    def get_grabber(self, option='fromSite'):
        """
        Get an instance that will return the next article ID,
        either from the current news list online or text file

        option (str):
                fromSite - NHK News Easy's recent article list
                fromFile - takes a list of article IDs
                rand - guesses valid article IDs
        """
        if option == 'fromSite':
            # download news-list
            request.urlretrieve("%s/news-list.json" %
                                (url), "news/news-list.json")

            # parse news-list
            data = json.loads(open("news/news-list.json",
                                   encoding="latin-1").readline()[3:])

            for day in data[0]:
                for index, val in enumerate(data[0][day]):
                    id = data[0][day][index]["news_id"]
                    yield id

        elif option == 'fromFile':
            idList = open('idList.txt')
            for id in idList:
                yield id.strip()

        elif option == 'rand':
            for i in range(1, 99999):
                id = "k10010%05d1000" % i
                yield id

    def download_article(self, id):
        """
        Download article files from the web.

        id (str): an article ID
        """
        # if new, download dictionary, json files
        dname = "news/%s.out.dic" % (id)
        jname = "news/%s.out.json" % (id)
        if not os.path.isfile(dname) or not os.path.isfile(jname):
            try:
                request.urlretrieve("%s/%s/%s.out.dic" %
                                    (self.url, id, id), dname)
                request.urlretrieve("%s/%s/%s.out.json" %
                                    (self.url, id, id), jname)
                print("downloaded %s" % id)
            except:
                pass

if __name__ == '__main__':
    # example usage
    grabber = Grabber()

    for id in grabber.get_grabber('fromSite'):
        grabber.download_article(id)
