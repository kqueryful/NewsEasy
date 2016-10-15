import sqlite3

class SqliteInstance:
	"""
	data persistence through SQLite
	"""

	def __init__(self):
		# SQLite setup
		self.conn = sqlite3.connect('newsWeb.sqlite')
		self.c = self.conn.cursor()

	def table_setup(self):
		"""
		Set up the tables
		"""
		try:
			# clear old tables
			self.c.execute("DROP TABLE Articles")
			self.c.execute("DROP TABLE Words")
			self.c.execute("DROP TABLE Examples")
		except sqlite3.OperationalError:
			pass
		try:
			# create new tables
			self.c.execute("CREATE TABLE Articles (newsid TEXT PRIMARY KEY, title TEXT, text TEXT, markup TEXT)")
			self.c.execute("CREATE TABLE Words (word TEXT PRIMARY KEY, reading TEXT, frequency INTEGER, category TEXT, rubyDefinition TEXT, ankiDefinition TEXT, alt TEXT, wiki TEXT, jdic TEXT)")
			self.c.execute("CREATE TABLE Examples (word TEXT, sentence TEXT PRIMARY KEY, newsid TEXT)")
		except sqlite3.OperationalError:
			pass

		self.conn.commit()

	def add_article(self, id, title, text, markup):
		"""
		Add an article to the DB

		id (str): the article ID
		title (str): the article's title
		text (str): the text of the article
		markup (str): article text with highlighting
		"""
		self.c.execute("INSERT OR IGNORE INTO Articles (newsid, title, text, markup) VALUES (?,?,?,?)", (id, title, text, markup))

	def add_word(self, word, reading, category='', alt='', rubyDefs='', ankiDefs=''):
		"""
		Add a word to the DB

		word (str): the word
		reading (str): the reading of the word
		category (str): 'L','N', 'C' if a proper noun, '' otherwise
		alt (str): any alternative spellings of the word
		defs (str): the word definition
		"""

		#todo:20 fix word frequencies
		if category != '':
			try:
				self.c.execute("INSERT INTO Words (word, reading, frequency, category) VALUES (?,?,?,?)", (word, reading, 1, category))
			except sqlite3.IntegrityError:
				self.c.execute("UPDATE Words SET frequency = frequency + 1 WHERE word = ?", (word,))
		else:
			try:
				self.c.execute("INSERT INTO Words (word, reading, frequency, alt, rubyDefinition, ankiDefinition) VALUES (?,?,?,?,?,?)", (word, reading, 1, alt, rubyDefs, ankiDefs))
			except sqlite3.IntegrityError:
				self.c.execute("UPDATE Words SET frequency = frequency + 1 WHERE word = ?", (word,))

	def add_example(self, word, sentence, id):
		"""
		Add example sentences for a word to the DB

		word (str): the word
		sentence (str): the sentence
		id (str): the article ID
		"""
		self.c.execute("INSERT OR IGNORE INTO Examples VALUES (?,?,?)", (word, sentence, id))


	def commit(self):
		self.conn.commit()

	def clean_up(self):
		"""
		Close DB objects
		"""
		self.c.close()
		self.conn.close()
