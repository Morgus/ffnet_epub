#!/usr/bin/env python
# 26.7.2014 Aleksi Blinnikka

import re
from bs4 import BeautifulSoup

BASE_URL = "http://www.fanfiction.net/s/{}/{}/"
RE_ID = "/s/([0-9]+)"
RE_CHAPTERS = "Chapters: ([0-9]+)"

def parse(raw_html, chapter_no):
    soup = BeautifulSoup(raw_html)

    charset_tag = soup.head.meta.extract()
    title_tag = soup.head.title.extract()
    style_tag = soup.new_tag("link", rel="stylesheet",
                        type="text/css", href="../styles.css")
    soup.head.clear()
    soup.head.append(charset_tag)
    soup.head.append(title_tag)
    soup.head.append(style_tag)

    story_text = soup.find("div", id="storytext").extract()
    story_text.attrs = None
    return str(soup), chapter_no

def parse_ch1(raw_html, url):
    story_info = {}
    soup = BeautifulSoup(raw_html)

    # Head
    charset_tag = soup.head.meta.extract()
    title_tag = soup.head.title.extract()
    style_tag = soup.new_tag("link", rel="stylesheet",
                        type="text/css", href="../styles.css")
    soup.head.clear()
    soup.head.append(charset_tag)
    soup.head.append(title_tag)
    soup.head.append(style_tag)

    # Info
    story_info["id"] = re.search(RE_ID, url).group(1)
    image_tag = soup.find("div", id="img_large").img
    if image_tag.get("data-original") != None:
        story_info["cover_url"] = "https:{}".format(image_tag["data-original"])
    else:
        story_info["cover_url"] = None
    story_info["cover_headers"] = \
            { "Referer": BASE_URL.format(story_info["id"], 1) }

    profile = soup.find("div", id="profile_top")
    story_info["title"] = profile.b.string
    story_info["author"] = profile.a.string
    # If there is no Chapters: text in the info section, there is only one
    chapter_num = 1
    if "Chapters:" in profile.get_text():
        chapter_num = re.search(RE_CHAPTERS, profile.get_text()).group(1)
    story_info["ch_urls"] = {}
    for ch in range(2, chapter_num+1):
        story_info["ch_urls"][ch] = BASE_URL.format(story_info["id"], ch)

    description = profile.find("div", class_="xcontrast_txt").string
    tags_span = profile.find("span", class_="xgray")
    tags = ""
    for string in tags_span.stripped_strings:
        tags = " ".join(tags, string)

    # Story
    story_text = soup.find("div", id="storytext").extract()
    story_text.attrs = None

    soup.body.clear()
    soup.body.attrs = None
    story_title = soup.new_tag("h1")
    story_title.string = story_info["title"]
    story_author = soup.new_tag("p")
    story_author.string = "By: {}".format(story_info["author"])
    story_desc = soup.new_tag("p")
    story_desc.string = description
    story_tags = soup.new_tag("p")
    story_tags.string = tags
    soup.body.append(story_title)
    soup.body.append(story_author)
    soup.body.append(story_desc)
    soup.body.append(story_tags)
    soup.body.append(story_text)

    return str(soup), chapter_num, story_info

