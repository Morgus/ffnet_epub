#!/usr/bin/env python
# 2014 Aleksi Blinnikka

import concurrent.futures
import zipfile
import importlib
import re
import queue
from threading import BoundedSemaphore
from urllib.request import urlopen, Request
from extra_files import MIMETYPE, STYLES_CSS, TITLEPAGE_HTML, CONTAINER_XML
from extra_files import toc, contents
try:
    import _thread
except ImportError:
    import _dummy_thread as _thread

PARSERS = {"fanfiction.net": "ff_net"}
# Invalid filenames on Windows
INVALID_CHARS = re.compile("[/\\:*?\"<>|]")

dl_semaphore = None
progress_queue = queue.Queue()


def get_chapter(url, chapter_no, parse):
    raw_html = urlopen(url).read()
    dl_semaphore.release()
    html, chapter = parse(raw_html, chapter_no)
    progress_queue.put((chapter, None))
    return html, chapter


def get_chapter1(url, parse):
    """Create the first chapter's HTML file and get story information"""
    raw_html = urlopen(url).read()
    html, chapters, story_info = parse(raw_html, url)
    progress_queue.put((1, chapters))
    return html, chapters, story_info


def get_parser(url):
    for key in PARSERS.keys():
        if key in url:
            parser = importlib.import_module("parsers.{}".format(PARSERS[key]))
            return parser.parse, parser.parse_ch1
    progress_queue.put((None, "No parser found for {}".format(repr(url))))
    _thread.exit()


class NoParser(Exception):
    def __init__(self, url):
        self.url = url
    def __str__(self):
        return "No parser found for {}".format(repr(self.url))


def create_document(main_url, max_connections=2, filepath=None):
    """Creates an EPUB document from a fanfic.

       main_url -- user given URL which should be the first chapter
       max_connections -- maximum number of simultaneous connections
           default: 2. This should be chosen with care as the Terms of Service
           of some of the websites states that you shouldn't cause more stress
           than a normal visitor.
       filepath -- optional path for the resulting Epub document
           By default filename is: %author - %title.epub in the current
           directory. %author and %title in the path are special, they're
           changed to the story author and title respectively."""
    global dl_semaphore
    dl_semaphore = BoundedSemaphore(max_connections)

    parse, parse_ch1 = get_parser(main_url)
    html_ch1, chapter_num, story_info = get_chapter1(main_url, parse_ch1)
    chapters = {}
    chapters[1] = html_ch1

    if story_info["cover_url"]:
        cover_image_req = Request(
            story_info["cover_url"], headers=story_info["cover_headers"])
        cover_image = urlopen(cover_image_req).read()
    else:
        cover_image = open("default.jpg", "rb").read()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_connections+3) \
            as executor:
        parse_chapters = []
        download_urls = story_info["chapter_urls"]
        for ch in range(2, chapter_num+1):
            dl_semaphore.acquire()
            parse_chapters.append(
                executor.submit(get_chapter, download_urls[ch], ch, parse))
        for future in concurrent.futures.as_completed(parse_chapters):
            html, chapter_no = future.result()
            chapters[chapter_no] = html

    if not filepath:
        filepath = "{} - {}.epub".format(
            INVALID_CHARS.sub("-", story_info["author"]),
            INVALID_CHARS.sub("-", story_info["title"]))
    else:
        filepath = filepath.replace(
            "%author", INVALID_CHARS.sub("-", story_info["author"]))
        filepath = filepath.replace(
            "%title", INVALID_CHARS.sub("-", story_info["title"]))

    with zipfile.ZipFile(filepath, "w") as f:
        f.writestr("mimetype", MIMETYPE)
        f.writestr("META-INF/container.xml", CONTAINER_XML)
        f.writestr("Content/titlepage.html", TITLEPAGE_HTML)
        f.writestr("Content/styles.css", STYLES_CSS)
        f.writestr("Content/cover.jpg", cover_image)
        f.writestr("Content/toc.ncx", toc(story_info, chapter_num))
        f.writestr("Content/content.opf", contents(story_info, chapter_num))
        for ch in range(1, chapter_num+1):
            f.writestr("Content/Chapters/ch{}.html".format(ch), chapters[ch])
