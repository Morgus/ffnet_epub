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
	os.makedirs(os.path.join(book_name, "Content", "Chapters"), exist_ok=True) # Python 3.2 required
	os.makedirs(os.path.join(book_name, "META-INF"), exist_ok=True)
	with open("%s/Content/Chapters/ch1.html" % book_name, encoding="utf-8", mode="w") as file:
		file.write(ch1)
	cover_address = scraper_ch1.get_story_image_address()

	# Download cover image
	print("Downloading cover ... ", end="")
	with open("%s/Content/cover.jpg" % book_name, "wb") as cover_image:
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
			with open("%s/Content/Chapters/ch%d.html" % (book_name, i), encoding="utf-8", mode="w") as file:
				file.write(chapter)

	# Tidy HTML files
	print("Converting to XHTML")
	for i in range(1, chapters+1):
		call("tidy -asxhtml -utf8 -m \"%s/Content/Chapters/ch%d.html\"" % (book_name, i))

	# Create mimetype file
	print("Creating mimetype file")
	extra_files.create_mimetype(book_name)

	# Create a simple stylesheet
	print("Creating stylesheet")
	extra_files.create_stylesheet(book_name)

	# Create titlepage
	print("Creating titlepage with the cover image")
	extra_files.create_titlepage(book_name)

	# Build TOC
	print("Creating table of contents")
	extra_files.create_toc(book_name, scraper_ch1.get_title(), story_id, chapters)

	# Create container.xml
	print("Creating container.xml")
	extra_files.create_container(book_name)

	# Create contents list
	print("Creating content.opf")
	extra_files.create_content_list(book_name, scraper_ch1.get_title(), scraper_ch1.get_author(), story_id, chapters)

	# Creating zip file
	print("Compressing files")
	with zipfile.ZipFile("%s.epub" % book_name, "w") as zip:
		zip.write("%s/META-INF/container.xml" % book_name, "META-INF/container.xml")
		zip.write("%s/mimetype" % book_name, "mimetype")
		zip.write("%s/Content/styles.css" % book_name, "Content/styles.css")
		zip.write("%s/Content/titlepage.html" % book_name, "Content/titlepage.html")
		zip.write("%s/Content/cover.jpg" % book_name, "Content/cover.jpg")
		zip.write("%s/Content/toc.ncx" % book_name, "Content/toc.ncx")
		zip.write("%s/Content/content.opf" % book_name, "Content/content.opf")
		for i in range(1, chapters+1):
			zip.write("%s/Content/Chapters/ch%d.html" % (book_name, i), "Content/Chapters/ch%d.html" % i)
	
	# Remove temporary files
	shutil.rmtree("%s/" % book_name)
