#!/usr/bin/env python
# 26.7.2014 Aleksi Blinnikka

from bs4 import BeautifulSoup

def parse(raw_html, chapter_no):
    soup = BeautifulSoup(raw_html)
    story_text = soup.find("div", id="storytext").extract()
    story_text.attrs = None
    return str(soup), chapter_no

def parse_ch1(raw_html):
    soup = BeautifulSoup(raw_html)
    return str(soup), chapter_num, story_info

# story_info = {
# "cover_url": ...
# "cover_headers": ...
# "ch_urls": ...
# "author": ...
# "title": ...
# }

