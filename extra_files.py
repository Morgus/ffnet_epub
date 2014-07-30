#!/usr/bin/env python
# 2014 Aleksi Blinnikka

from datetime import datetime

MIMETYPE = "application/epub+zip"
STYLES_CSS = "@page {margin-bottom: 5pt; margin-top: 5pt;}"
TITLEPAGE_HTML = """\
<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" \
"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Cover</title></head>
<body><img alt="" height="100%" src="cover.jpg" /></body>
</html>"""
CONTAINER_XML = """\
<?xml version="1.0"?>
<container version="1.0" \
xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles><rootfile full-path="Content/content.opf" \
media-type="application/oebps-package+xml" /></rootfiles>
</container>"""

def toc(story_info, chapters):
    navpoints_list = ["""\
<navPoint id="a{0}" playOrder="{1}">
<navLabel><text>Chapter {0}</text></navLabel>
<content src="Chapters/ch{0}.html" />
</navPoint>""".format(i, i-1)
for i in range(1, chapters+1)]

    navpoints = "".join(navpoints_list)
    toc_string = "".join(["""\
<?xml version='1.0' encoding='utf-8'?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" \
xml:lang="eng">
<head><meta content="aleksi-blinnikka-python-epub-{}" name="dtb:uid"/>
<meta content="1" name="dtb:depth"/>
<meta content="0" name="dtb:totalPageCount"/>
<meta content="0" name="dtb:maxPageNumber"/></head>
<docTitle><text>{}</text></docTitle><navMap>
""".format(story_info["id"], story_info["title"]),
navpoints, "</navMap></ncx>"])
    return toc_string

def contents(story_info, chapters):
    t = datetime.utcnow()
    t = t.replace(microsecond=0)
    timestamp = "+".join([t.isoformat(), "00:00"])
    contents = ["""\
<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="uuid-id" \
version="2.0">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" \
xmlns:opf="http://www.idpf.org/2007/opf">
<dc:identifier id="uuid-id">aleksi-blinnikka-python-epub-{0}</dc:identifier>
<dc:creator opf:file-as="{1}" opf:role="aut">{1}</dc:creator>
<dc:title>{2}</dc:title><dc:date>{3}</dc:date>
<meta name="cover" content="cover.jpg" /><dc:language>en</dc:language>
<dc:contributor opf:role="bkp"></dc:contributor></metadata><manifest>
<item href="cover.jpg" id="cover" media-type="image/jpeg" />
<item href="toc.ncx" id="ncx" media-type="application/x-dtbncx+xml" />
<item href="styles.css" id="styles" media-type="text/css" />
<item href="titlepage.html" id="titlepage" \
media-type="application/xhtml+xml" />
""".format(story_info["id"], story_info["author"],
           story_info["title"], timestamp)]

    items_list = ["""\
<item href="Chapters/ch{0}.html" id="ch{0}" \
media-type="application/xhtml+xml" />
""".format(i) for i in range(1, chapters+1)]
    items = "".join(items_list)
    contents.append(items)
    contents.append(
            "</manifest><spine toc=\"ncx\"><itemref idref=\"titlepage\" />")

    itemref_list = ["<itemref idref=\"ch{}\" />".format(i)
                    for i in range(1, chapters+1)]
    itemrefs = "".join(itemref_list)
    contents.append(itemrefs)
    contents.append("""\
</spine>
<guide><reference href="titlepage.html" type="cover" title="Cover"/></guide>
</package>""")
    return "".join(contents)

