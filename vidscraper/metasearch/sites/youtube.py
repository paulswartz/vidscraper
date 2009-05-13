import cgi
import urllib
import urlparse

import feedparser

from vidscraper import util
from vidscraper.sites import youtube as youtube_scraper
from vidscraper.metasearch import defaults
from vidscraper.metasearch import util as metasearch_util

#'http://gdata.youtube.com/feeds/api/videos?vq=%s&amp;alt=rss'
YOUTUBE_QUERY_BASE = 'http://gdata.youtube.com/feeds/api/videos'


def parse_youtube_entry(entry):
    parsed_entry = {
        'title': entry['title'],
        'description': entry['summary'],
        'link': entry['link'],
        }
    parsed_entry['embed'] = youtube_scraper.get_embed(entry['link'])
    parsed_entry['flash_enclosure_url'] = \
        youtube_scraper.get_flash_enclosure_url(entry['link'])

    video_id = cgi.parse_qs(urlparse.urlsplit(entry['link'])[3])['v'][0]
    parsed_entry['thumbnail_url'] = \
        'http://img.youtube.com/vi/%s/default.jpg' % video_id

    return parsed_entry


def get_entries(include_terms, exclude_terms=None,
                order_by='relevant', **kwargs):

    search_string = metasearch_util.search_string_from_terms(
        include_terms, exclude_terms)

    # Note here that we can use more than 50
    # (metasearch.DEFAULT_MAX_RESULTS), but that requires doing multiple
    # queries for RSS "pagination" with youtube's API.  Maybe we should
    # implement that later.
    get_params = {
        'vq': search_string,
        'alt': 'rss',
        'max-results': defaults.DEFAULT_MAX_RESULTS}

    if order_by == 'latest':
        get_params['orderby'] = 'published'
    elif order_by == 'relevant':
        get_params['orderby'] = 'relevance'
    else:
        pass #TODO: throw an error here

    get_url = '%s?%s' % (YOUTUBE_QUERY_BASE, urllib.urlencode(get_params))

    parsed_feed = feedparser.parse(get_url)

    return [parse_youtube_entry(entry) for entry in parsed_feed.entries]


SUITE = {
    'id': 'youtube',
    'display_name': 'YouTube',
    'order_bys': ['latest', 'relevant'],
    'func': get_entries}