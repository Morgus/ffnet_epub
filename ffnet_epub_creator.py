# ffnet_epub_creator.py
# Copyright (c) Aleksi Blinnikka 7-8.3.2014

import sys, os, zipfile, shutil, extra_files
from urllib.request import urlopen, Request
from subprocess import call
from scraper import Scraper

if __name__ == "__main__":
	if len(sys.argv) != 2 or sys.argv[1].endswith("help"):
		sys.exit("Usage: %s story-id" % sys.argv[0])
	story_id = sys.argv[1]
	# Scrape the first chapter, which should exist if the ID is correct
	scraper_ch1 = Scraper(story_id, 1)
	ch1 = scraper_ch1.parse()
	book_name = scraper_ch1.get_book_name()
	# Create temporary folders for the story
	os.makedirs(os.path.join(story_id, "Content", "Chapters"), exist_ok=True) # Python 3.2 required
	os.makedirs(os.path.join(story_id, "META-INF"), exist_ok=True)
	with open("%s/Content/Chapters/ch1.html" % story_id, encoding="utf-8", mode="w") as file:
		file.write(ch1)
	cover_address = scraper_ch1.get_story_image_address()

	# Download cover image
	print("Downloading cover ... ", end="")
	with open("%s/Content/cover.jpg" % story_id, "wb") as cover_image:
		# The CDN checks for Referer header
		req = Request(cover_address, headers={"Referer": ("https://www.fanfiction.net/s/%s/" % story_id)})
		cover_image.write(urlopen(req).read())
	print("Done")

	# Check the number of chapters and download the rest
	chapters = int(scraper_ch1.get_chapters())
	if chapters > 1:
		for i in range(2, chapters+1):
			scraper = Scraper(story_id, i)
			chapter = scraper.parse()
			with open("%s/Content/Chapters/ch%d.html" % (story_id, i), encoding="utf-8", mode="w") as file:
				file.write(chapter)

	# Tidy HTML files
	print("Converting to XHTML")
	for i in range(1, chapters+1):
		call("tidy -asxhtml -utf8 -m \"%s/Content/Chapters/ch%d.html\"" % (book_name, i))

	# Create mimetype file
	print("Creating mimetype file")
	extra_files.create_mimetype(story_id)

	# Create a simple stylesheet
	print("Creating stylesheet")
	extra_files.create_stylesheet(story_id)

	# Create titlepage
	print("Creating titlepage with the cover image")
	extra_files.create_titlepage(story_id)

	# Build TOC
	print("Creating table of contents")
	extra_files.create_toc(story_id, scraper_ch1.get_title(), chapters)

	# Create container.xml
	print("Creating container.xml")
	extra_files.create_container(story_id)

	# Create contents list
	print("Creating content.opf")
	extra_files.create_content_list(story_id, scraper_ch1.get_title(), scraper_ch1.get_author(), chapters)

	# Creating zip file
	print("Compressing files")
	with zipfile.ZipFile("%s.epub" % book_name, "w") as zip:
		zip.write("%s/META-INF/container.xml" % story_id, "META-INF/container.xml")
		zip.write("%s/mimetype" % story_id, "mimetype")
		zip.write("%s/Content/styles.css" % story_id, "Content/styles.css")
		zip.write("%s/Content/titlepage.html" % story_id, "Content/titlepage.html")
		zip.write("%s/Content/cover.jpg" % story_id, "Content/cover.jpg")
		zip.write("%s/Content/toc.ncx" % story_id, "Content/toc.ncx")
		zip.write("%s/Content/content.opf" % story_id, "Content/content.opf")
		for i in range(1, chapters+1):
			zip.write("%s/Content/Chapters/ch%d.html" % (story_id, i), "Content/Chapters/ch%d.html" % i)
	
	# Remove temporary files
	shutil.rmtree("%s/" % story_id)
