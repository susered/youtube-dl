from __future__ import unicode_literals

# This RegEx filter works with a video ID as part of the URI
generic_video_id_regex_filter: str = r'\/([0-9a-zA-Z]*)-'
regex_to_get_domain_from_url: str = r'https?:\/\/([0-9a-zA-Z\.\-]*)\/.*'
regex_to_get_path_from_url: str = r'https?:\/\/[0-9a-zA-Z\.\-]*\/(.*)\/?'

domain_to_video_id_regex_filters_dict: dict = {
    'rumble.com': generic_video_id_regex_filter,
    'bitchute.com': r'.*\/video\/([0-9a-zA-Z]*)',
    'vimeo.com': r'.*\/([0-9a-zA-Z]*)',
}
domain_to_video_id_regex_filters_dict.setdefault('default', generic_video_id_regex_filter)

domain_to_path_regex_filters_dict: dict = {
    'rumble.com': 'embed',
    'bitchute.com': 'video',
    'vimeo.com': '',
}
domain_to_path_regex_filters_dict.setdefault('default', '')

domain_to_new_domain_regex_filters_dict: dict = {
    'rumble.com': 'rumble.com',
    'bitchute.com': 'old.bitchute.com',
    'vimeo.com': 'vimeo.com',
}
domain_to_new_domain_regex_filters_dict.setdefault('default', '')

#
#
regex_to_parse_out_embedurl_from_rumble_html_source: str = r'.*\",\"embedUrl\":\"(https?:\/\/.*\/)\",\"url\":.*'

regexes_to_find_embedded_url_from_html_source: dict = {
    'rumble.com': regex_to_parse_out_embedurl_from_rumble_html_source,
}
regexes_to_find_embedded_url_from_html_source.setdefault('default', 'default')

# Updated on 12/26/2024 from https://useragents.me/#most-common-desktop-useragents-json-csv
HTTP_USER_AGENTS: list = [
    {'ua1': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.1", "pct": 31.48'},
    {'ua2': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.3", "pct": 24.07'},
    {'ua3': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.3", "pct": 17.59'},
    {'ua4': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.", "pct": 7.41'},
    {'ua5': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.", "pct": 4.63'},
    {'ua6': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.", "pct": 3.7'},
    {'ua7': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Herring/97.1.8280.8", "pct": 2.78'},
    {'ua8': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.3", "pct": 1.85'},
    {'ua9': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 OPR/115.0.0.", "pct": 1.85'},
    {'ua10': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 AtContent/95.5.5462.5", "pct": 0.93'},
    {'ua11': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.1958", "pct": 0.93'},
    {'ua12': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.3", "pct": 0.93'},
    {'ua13': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.", "pct": 0.93'},
    {'ua14': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.3", "pct": 0.93'},
]
