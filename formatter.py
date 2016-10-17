import re


class Formatter:

    def convert_to_ankiDef(self, rubyDef):
        """
        converts a definition into Anki Japanese plugin formatting

        rubyDef (str): a ruby furigana formatted definition
        """

        ankiDef = re.sub("</*ruby>", "", rubyDef)
        ankiDef = re.sub("</rb>", "", ankiDef)
        ankiDef = re.sub("<rb>", " ", ankiDef)
        ankiDef = re.sub("<rt>", "[", ankiDef)
        ankiDef = re.sub("</rt>", "]", ankiDef)

        return ankiDef

    def bold_in_sentence(self, word, line):
        """
        return a sentence with a given word in bold

        word (str): the word to find
        line (str): the line to search in
        """
        return re.sub(word, "<b>" + word + "</b>", line.strip() + u"。")

    def highlight(self, word, article, type='R'):
        """
        returns a version of article with special words tagged

        word (str): the word to find
        article (str): the complete article
        type (str): mark for proper nouns or default to regular 'R'
        """
        # todo: something's not right with the regex. see k10010458811000
        return re.sub(word, "<span class='" + type + "'>" + word + "</span>", article)
