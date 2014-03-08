import sys, os, time, zipfile, shutil
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
	# Create a folder for the story
	os.makedirs(os.path.join(book_name, "Content", "Chapters"), exist_ok=True) # Python 3.2 required
	with open("%s/Content/Chapters/ch1.html" % book_name, "w") as file:
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
			with open("%s/Content/Chapters/ch%d.html" % (book_name, i), "w") as file:
				file.write(chapter)

	# Tidy HTML files
	print("Converting to XHTML")
	for i in range(1, chapters+1):
		call("tidy -asxhtml -m \"%s/Content/Chapters/ch%d.html\"" % (book_name, i))

	# Create mimetype file
	print("Creating mimetype file")
	with open("%s/mimetype" % book_name, "w") as file:
		file.write("application/epub+zip")

	# Create a simple stylesheet
	print("Creating stylesheet")
	with open("%s/Content/styles.css" % book_name, "w") as stylesheet:
		stylesheet.write(
		"""@page {
	margin-bottom: 5pt;
	margin-top: 5pt;
}""")

	# Create titlepage
	print("Creating titlepage with the cover image")
	with open("%s/Content/titlepage.html" % book_name, "w") as titlepage:
		titlepage.write(
		"""<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Cover</title>
</head>
<body>
<img alt="" height="100%" src="cover.jpg" />
</body>
</html>""")

	# Build TOC
	print("Building table of contents")
	with open("%s/Content/toc.ncx" % book_name, "w") as toc:
		toc.write(
		"""<?xml version='1.0' encoding='utf-8'?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="eng">
<head>
<meta content="0c159d12-f5fe-4323-8194-f5c652b89f5c" name="dtb:uid"/>
<meta content="1" name="dtb:depth"/>
<meta content="0" name="dtb:totalPageCount"/>
<meta content="0" name="dtb:maxPageNumber"/>
</head>
<docTitle>
<text>""")
		toc.write(scraper_ch1.get_title())
		toc.write(
		"""</text>
</docTitle>
<navMap>""")
		for i in range(1, chapters+1):
			toc.write(
			"""<navPoint id="a%d" playOrder="%d">
<navLabel>
<text>Chapter %d</text>
</navLabel>
<content src="Chapters/ch%d.html" />
</navPoint>""" % (i, i-1, i, i))
		toc.write(
		"""</navMap>
</ncx>""")

	# Create container.xml
	print("Creating container.xml")
	os.makedirs(os.path.join(book_name, "META-INF"), exist_ok=True)
	with open("%s/META-INF/container.xml" % book_name, "w") as container:
		container.write(
		"""<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles>
<rootfile full-path="Content/content.opf" media-type="application/oebps-package+xml"/>
</rootfiles>
</container>""")

	# Create contents list
	with open("%s/Content/content.opf" % book_name, "w") as contents:
		contents.write(
		"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="uuid-id" version="2.0">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
<dc:identifier id="uuid-id">aleksi-blinnikka-python-epub-%s</dc:identifier>
<dc:creator opf:file-as="%s" opf:role="aut">%s</dc:creator>""" % (story_id, scraper.get_author(), scraper.get_author()))
		time_struct = time.gmtime()
		current_time = "%d-%02d-%02dT%02d:%02d:%02d+00:00" % (time_struct[0], time_struct[1], time_struct[2], time_struct[3], time_struct[4], time_struct[5])
		contents.write(
		"""<dc:date>%s</dc:date>
<meta name="cover" content="cover.jpg" />
<dc:language>en</dc:language>
<dc:contributor opf:role="bkp"></dc:contributor>
</metadata>
<manifest>
<item href="cover.jpg" id="cover" media-type="image/jpeg" />
<item href="toc.ncx" id="ncx" media-type="application/x-dtbncx+xml" />
<item href="styles.css" id="styles" media-type="text/css" />
<item href="titlepage.html" id="titlepage" media-type="application/xhtml+xml" />""" % current_time)
		for i in range(1, chapters+1):
			contents.write("""<item href="Chapters/ch%d.html" id="ch%d" media-type="application/xhtml+xml" />""" % (i, i))
		contents.write(
		"""</manifest>
<spine toc="ncx">
<itemref idref="titlepage" />""")
		for i in range(1, chapters+1):
			contents.write("""<itemref idref="ch%d" />""" % i)
		contents.write(
		"""</spine>
<guide>
<reference href="titlepage.html" type="cover" title="Cover"/>
</guide>
</package>""")

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
