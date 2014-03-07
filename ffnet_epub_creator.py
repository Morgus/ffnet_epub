import sys, os
from scraper import Scraper

if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.exit("Usage: %s story-id" % sys.argv[0])
	story_id = sys.argv[1]
	scraper = Scraper(story_id, 1)
	ch1 = scraper.parse()
	os.makedirs(os.path.join(story_id, "Content", "Chapters"), exist_ok=True) # Python 3.2 required
	with open("%s/Content/Chapters/ch1.html" % story_id, "w") as file:
		file.write(ch1)
	cover_address = scraper.get_story_image_address()
	chapters = scraper.get_chapters()
	
	# tidy -asxhtml -m %s/Content/Chapters/ch%i.html
		