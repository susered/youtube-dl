# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor
from .. import write_string
from ..compat import compat_str
from ..utils import (
    determine_ext,
    int_or_none,
    parse_iso8601,
    try_get, ExtractorError,
)

import re

class RumbleEmbedIE(InfoExtractor):
    DEBUG: bool = False
    _VALID_URL = r'https?://(?:www\.)?rumble\.com/embed/(?:[0-9a-z]+\.)?(?P<id>[0-9a-z]+)'
    _TESTS = [{
        'url': 'https://rumble.com/embed/v5pv5f',
        'md5': '36a18a049856720189f30977ccbb2c34',
        'info_dict': {
            'id': 'v5pv5f',
            'ext': 'mp4',
            'title': 'WMAR 2 News Latest Headlines | October 20, 6pm',
            'timestamp': 1571611968,
            'upload_date': '20191020',
        }
    }, {
        'url': 'https://rumble.com/embed/ufe9n.v5pv5f',
        'only_matching': True,
    }]

    def _real_extract(self, url: str) -> dict:
        """
        Extract the contents of the remote URL JSON

        :param url: str
        :return: dict
        """
        video_id = self._match_id(url)
        video = self._download_json(
            'https://rumble.com/embedJS/', video_id,
            query={'request': 'video', 'v': video_id})
        # In cases, where "video" does not return a 'dict' object, then we must raise an Exception with a possible
        # reason, which is most likely because the video does not exist.
        if not isinstance(video, dict):
            raise ExtractorError("%s is most likely not found" % url,
                                 None,
                                 cause="'video' object type of '%s' when it should be of 'dict' type" % str(video))
        title = video['title']

        formats = []
        for height, ua in (video.get('ua') or {}).items():
            for i in range(2):
                f_url = try_get(ua, lambda x: x[i], compat_str)
                if f_url:
                    ext = determine_ext(f_url)
                    f = {
                        'ext': ext,
                        'format_id': '%s-%sp' % (ext, height),
                        'height': int_or_none(height),
                        'url': f_url,
                    }
                    bitrate = try_get(ua, lambda x: x[i + 2]['bitrate'])
                    if bitrate:
                        f['tbr'] = int_or_none(bitrate)
                    formats.append(f)
        self._sort_formats(formats)

        author = video.get('author') or {}

        if self.DEBUG:
            write_string("[debug2] id: video_id = %s\n" % video_id)
            write_string("[debug2] title: title = %s\n" % title)
            write_string("[debug2] author: author = %s\n" % author)
            write_string("[debug2] formats: formats = %s\n" % formats)
            write_string("[debug2] thumbnail: thumbnail = %s\n" % video.get('i'))
            write_string("[debug2] timestamp: timestamp = %s\n" % parse_iso8601(video.get('pubDate')))
            write_string("[debug2] channel: channel = %s\n" % author.get('name'))
            write_string("[debug2] channel_url: channel_url = %s\n" % author.get('url'))
            write_string("[debug2] duration: duration = %s\n" % int_or_none(video.get('duration')))

        return {
            'id': video_id,
            'title': title,
            'formats': formats,
            'thumbnail': video.get('i'),
            'timestamp': parse_iso8601(video.get('pubDate')),
            'channel': author.get('name'),
            'channel_url': author.get('url'),
            'duration': int_or_none(video.get('duration')),
        }
