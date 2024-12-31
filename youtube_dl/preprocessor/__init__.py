from __future__ import unicode_literals

__author__ = ""
__copyright__ = ""
__license__ = ""
__version__ = ""
__maintainer__ = ""
__email__ = ""
__status__ = ""
__doc__ = """
The idea is that we map DNS domains, paths and video IDs to a working URL for extraction. This will alleviate any
code changes to the various extractors. 
"""

# This RegEx filter works with a video ID as part of the URI
generic_video_id_regex_filter: str = r'\/([0-9a-zA-Z]*)-'
regex_to_get_domain_from_url: str = r'https?:\/\/([0-9a-zA-Z\.\-]*)\/.*'
regex_to_get_path_from_url: str = r'https?:\/\/[0-9a-zA-Z\.\-]*\/(.*)\/?'

#
# This maps a DNS domain to the RegEx that will govern the video ID extraction
domain_to_video_id_regex_filters_dict: dict = {
    'rumble.com': generic_video_id_regex_filter,
    'www.bitchute.com': r'.*\/video\/([0-9a-zA-Z]*)',
    'vimeo.com': r'.*\/([0-9a-zA-Z]*)',
}
domain_to_video_id_regex_filters_dict.setdefault('default', generic_video_id_regex_filter)

#
# This maps a DNS domain to the URL path that contains the video ID
domain_to_path_regex_filters_dict: dict = {
    'rumble.com': 'embed',
    'bitchute.com': 'video',
    'www.bitchute.com': 'video',
    'vimeo.com': '',
}
domain_to_path_regex_filters_dict.setdefault('default', '')

#
# This maps a DNS domain to the DNS domain that has the embedded URL so the video can be downloaded
domain_to_new_domain_regex_filters_dict: dict = {
    'bitchute.com': 'old.bitchute.com',
    'www.bitchute.com': 'old.bitchute.com',
}
domain_to_new_domain_regex_filters_dict.setdefault('default', '')

#
# This is a dictionary mapping DNS domain to embedded URL RegEx
regex_to_parse_out_embedurl_from_rumble_html_source: str = r'.*\",\"embedUrl\":\"(https?:\/\/.*\/)\",\"url\":.*'
regexes_to_find_embedded_url_from_html_source: dict = {
    'rumble.com': regex_to_parse_out_embedurl_from_rumble_html_source,
}
regexes_to_find_embedded_url_from_html_source.setdefault('default', 'default')

#
# List of HTTP User-Agents for retrieving remote HTML source for videos
#
# Updated on 12/26/2024 from https://useragents.me/#most-common-desktop-useragents-json-csv
HTTP_USER_AGENTS: list = [
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.1'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.3'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.3'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Herring/97.1.8280.8'},
    {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.3'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 OPR/115.0.0.'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 AtContent/95.5.5462.5'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.1958'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.3'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.3'},
]
