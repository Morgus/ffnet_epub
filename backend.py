#!/usr/bin/env python
# 26.7.2014 Aleksi Blinnikka

import concurrent.futures, zipfile, importlib, re, queue
from threading import BoundedSemaphore
from urllib.request import urlopen, Request
from extra_files import *

PARSERS = { "fanfiction.net": "ff_net" }
# Invalid filenames on Windows
INVALID_CHARS = re.compile("[/\\:*?\"<>|]")

dl_semaphore = None

_queue = None

def get_queue():
    global _queue
    if not _queue:
        _queue = queue.Queue()
    return _queue

def get_chapter(url, chapter_no, parse):
    raw_html = urlopen(url).read()
    dl_semaphore.release()
    html, chapter = parse(raw_html, chapter_no)
    get_queue().put("Chapter {} parsed".format(chapter))
    return html, chapter

def get_chapter1(url, parse):
    """Create the first chapter's HTML file and get story information"""
    raw_html = urlopen(url).read()
    html, chapters, story_info = parse(raw_html, url)
    get_queue().put("Chapter 1 parsed, {} chapters in total".format(chapters))
    return html, chapters, story_info

def get_parser(url):
    for key in PARSERS.keys():
        if key in url:
            parser = importlib.import_module("parsers.{}".format(PARSERS[key]))
            return parser.parse, parser.parse_ch1
    raise NoParser(url)

class NoParser(Exception):
    def __init__(self, url):
        self.url = url
    def __str__(self):
        return "No parser found for {}".format(repr(self.url))

def create_document(main_url, max_connections, filename):
    """Creates an EPUB document from a fanfic.
       
       main_url -- user given URL which should be the first chapter
       max_connections -- maximum number of simultaneous connections
           default: 2. This should be chosen with care as the Terms of Service
           of some of the websites states that you shouldn't cause more stress
           than a normal visitor
        filename -- optional filename for the resulting Epub document
            By default filename is: <author> - <title>.epub"""
    global dl_semaphore
    dl_semaphore = BoundedSemaphore(max_connections)
    parse, parse_ch1 = get_parser(main_url)

    html_ch1, chapter_num, story_info = get_chapter1(main_url, parse_ch1)
    chapters = {}
    chapters[1] = html_ch1

    if story_info["cover_url"]:
        cover_image_req = \
          Request(story_info["cover_url"], headers=story_info["cover_headers"])
        story_info["cover_image"] = urlopen(cover_image_req).read()
    else:
        story_info["cover_image"] = open("default.jpg", "rb").read()

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        chs_to_parse = []
        for ch in range(2, chapter_num+1):
            dl_semaphore.acquire()
            chs_to_parse.append(executor.submit(get_chapter,
                                        story_info["ch_urls"][ch], ch, parse))
        for future in concurrent.futures.as_completed(chs_to_parse):
            html, ch_no = future.result()
            chapters[ch_no] = html

    if not filename:
        filename = "{} - {}.epub".format(
                INVALID_CHARS.sub("-", story_info["author"]),
                INVALID_CHARS.sub("-", story_info["title"]))
    with zipfile.ZipFile(filename, "w") as f:
        f.writestr("mimetype", MIMETYPE)
        f.writestr("META-INF/container.xml", CONTAINER_XML)
        f.writestr("Content/titlepage.html", TITLEPAGE_HTML)
        f.writestr("Content/styles.css", STYLES_CSS)
        f.writestr("Content/cover.jpg", story_info["cover_image"])
        f.writestr("Content/toc.ncx", toc(story_info, chapter_num))
        f.writestr("Content/content.opf", contents(story_info, chapter_num))
        for ch in range(1, chapter_num+1):
            f.writestr("Content/Chapters/ch{}.html".format(ch), chapters[ch])

