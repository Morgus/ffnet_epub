# extra_files.py
# Copyright (c) Aleksi Blinnikka 8.3.2014

import time, sys

# Not much can be done to comment this, these files are required to be created for a working ePub.
# Each file is pretty much as simple as it can be while still having enough information.

def create_mimetype(story_id):
	with open("%s/mimetype" % story_id, encoding="utf-8", mode="w") as file:
		file.write("application/epub+zip")

def create_stylesheet(story_id):
	with open("%s/Content/styles.css" % story_id, encoding="utf-8", mode="w") as stylesheet:
		stylesheet.write(
"""@page {
	margin-bottom: 5pt;
	margin-top: 5pt;
}""")

def create_titlepage(story_id):
	with open("%s/Content/titlepage.html" % story_id, encoding="utf-8", mode="w") as titlepage:
		titlepage.write(
"""<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Cover</title></head>
<body><img alt="" height="100%" src="cover.jpg" /></body>
</html>""")

def create_toc(story_id, title, chapters):
	with open("%s/Content/toc.ncx" % story_id, encoding="utf-8", mode="w") as toc:
		toc.write(
"""<?xml version='1.0' encoding='utf-8'?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="eng">
<head>
<meta content="aleksi-blinnikka-python-epub-%s" name="dtb:uid"/>
<meta content="1" name="dtb:depth"/>
<meta content="0" name="dtb:totalPageCount"/>
<meta content="0" name="dtb:maxPageNumber"/>
</head>
<docTitle><text>%s</text></docTitle>
<navMap>""" % (story_id, title))
		for i in range(1, chapters+1):
			toc.write(
"""<navPoint id="a%d" playOrder="%d">
<navLabel><text>Chapter %d</text></navLabel>
<content src="Chapters/ch%d.html" />
</navPoint>""" % (i, i-1, i, i))
		toc.write(
"""</navMap>
</ncx>""")

def create_container(story_id):
	with open("%s/META-INF/container.xml" % story_id, encoding="utf-8", mode="w") as container:
		container.write(
"""<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles><rootfile full-path="Content/content.opf" media-type="application/oebps-package+xml" /></rootfiles>
</container>""")

def create_content_list(story_id, title, author, chapters):
	with open("%s/Content/content.opf" % story_id, encoding="utf-8", mode="w") as contents:
		contents.write(
"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="uuid-id" version="2.0">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
<dc:identifier id="uuid-id">aleksi-blinnikka-python-epub-%s</dc:identifier>
<dc:creator opf:file-as="%s" opf:role="aut">%s</dc:creator>""" % (story_id, author, author))
		time_struct = time.gmtime()
		# Format the current time correctly
		current_time = "%d-%02d-%02dT%02d:%02d:%02d+00:00" % (
		time_struct[0], time_struct[1], time_struct[2], time_struct[3], time_struct[4], time_struct[5]
		)
		contents.write(
"""<dc:title>%s</dc:title>
<dc:date>%s</dc:date>
<meta name="cover" content="cover.jpg" />
<dc:language>en</dc:language>
<dc:contributor opf:role="bkp"></dc:contributor>
</metadata>
<manifest>
<item href="cover.jpg" id="cover" media-type="image/jpeg" />
<item href="toc.ncx" id="ncx" media-type="application/x-dtbncx+xml" />
<item href="styles.css" id="styles" media-type="text/css" />
<item href="titlepage.html" id="titlepage" media-type="application/xhtml+xml" />""" % (title, current_time))
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
<guide><reference href="titlepage.html" type="cover" title="Cover"/></guide>
</package>""")

if __name__ == "__main__":
	sys.exit("Run from ffnet_epub_creator.py")
