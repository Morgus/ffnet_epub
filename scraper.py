from urllib.request import urlopen
from bs4 import BeautifulSoup
import sys

# Story URL base
BASE_URL = "http://www.fanfiction.net/s/%s/%i/"

# Parses the story page removing all unnecessary sections
class Parser:
	def __init__(self, story_id, chapter):
		try:
			html = urlopen(BASE_URL % (story_id, chapter)).read()
		except:
			sys.exit("Story %s, chapter %i not found" % (story_id, chapter))
		#print("Story %s, chapter %i downloaded" % (story_id, chapter))
		self.soup = BeautifulSoup(html)

	# Get the number of chapters
	def get_chapters(self):
		return 1

	def parse(self):
		self.remove_scripts()
		self.remove_extras()

	def remove_scripts(self):
		num_of_scripts = len(self.soup.find_all("script"))
		for i in range(0, num_of_scripts):
			self.soup.script.decompose()

	def remove_extras(self):
		# Remove extra info from head
		title_tag = self.soup.title.extract()
		self.soup.head.clear()
		self.soup.head.append(title_tag)
		# Only keep text content from the profile section
		profile = self.soup.find("div", id="profile_top")
		story_title = profile.b.extract()
		story_author = profile.a.extract()
		story_desc = profile.find("div", class_="xcontrast_txt").extract()
		story_tags = profile.find("span", class_="xgray").extract()
		# Extract story text
		story_text = self.soup.find("div", id="storytextp").extract()
		# Make extracted tags paragraphs (title h1, story text stays as a div)
		#del story_title["class"]
		story_title.attrs = None
		story_title.name = "h1"
		story_author.attrs = None
		story_author.name = "p"
		story_desc.attrs = None
		story_desc.name = "p"
		# Story tags have multiple links and other content, strip everything unnecessary
		story_tags.attrs = None
		story_tags.name = "p"
		story_tags_string = ""
		for string in story_tags.stripped_strings:
			story_tags_string += (string + " ")
		story_tags.clear()
		story_tags.string = story_tags_string
		story_text.attrs = None
		story_text.div.attrs = None
		
		# Recreate html body with the extracted content
		self.soup.body.clear()
		del self.soup.body["style"]
		self.soup.body.append(story_title)
		self.soup.body.append(story_author)
		self.soup.body.append(story_desc)
		self.soup.body.append(story_tags)
		self.soup.body.append(story_text)

	def print_test(self):
		print(self.soup.prettify())

if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.exit("Usage: %s story-id" % sys.argv[0])
	parser = Parser(sys.argv[1], 2)
	parser.parse()
	parser.print_test()
