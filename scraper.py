from urllib.request import urlopen
from bs4 import BeautifulSoup
import sys

# Story URL base
BASE_URL = "http://www.fanfiction.net/s/%s/%i/"

# Parses the story page removing all unnecessary sections
class Scraper:
	def __init__(self, story_id, chapter):
		print("Downloading ID: %s, Ch. %i ... " % (story_id, chapter), end="")
		try:
			html = urlopen(BASE_URL % (story_id, chapter)).read()
		except:
			sys.exit("Not found")
		print("Done")
		self.soup = BeautifulSoup(html)
		self.image_addr = None
		self.parsed = False

	# Get the number of chapters, used only after the parsing, otherwise returns None
	def get_chapters(self):
		if self.parsed == False:
			return None
		tag = self.soup.p.next_sibling.next_sibling
		list = tag.string.split()
		for i in range(0, len(list)):
			if list[i] == "Chapters:":
				return list[i+1]
		# Something odd happened
		return 1

	# This is done automatically before parsing or it can be done manually
	def get_story_image_address(self):
		if self.image_addr != None:
			return self.image_addr
		image_tag = self.soup.find("div", id="img_large").img
		if image_tag.get("data-original") != None:
			return image_tag["data-original"][2:]
		return image_tag["src"][2:]

	def parse(self):
		print("Parsing ... ", end="")
		self.image_addr = self.get_story_image_address()
		self.remove_scripts()
		self.remove_extras()
		self.parsed = True
		print("Done")
		# At this point the file is not valid xhtml, it needs to be run through tidy
		return self.soup.prettify()

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
		# horizontal lines are screwed up in the end result, they have to be fixed with a regex?
		hr_tags = story_text.find_all("hr")
		for hr_tag in hr_tags:
			hr_tag.attrs = None
		
		# Recreate html body with the extracted content
		self.soup.body.clear()
		del self.soup.body["style"]
		self.soup.body.append(story_title)
		self.soup.body.append(story_author)
		self.soup.body.append(story_desc)
		self.soup.body.append(story_tags)
		self.soup.body.append(story_text)

		# Add a link to a stylesheet for the ePub (always ../styles.css)
		def add_stylesheet(self):
			pass

if __name__ == "__main__":
	sys.exit("Run from ffnet_epub_creator.py")
