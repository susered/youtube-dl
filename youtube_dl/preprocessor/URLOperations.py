from __future__ import annotations

import re

from ..utils import (
    write_string
)
from youtube_dl.preprocessor import (
    domain_to_video_id_regex_filters_dict,
    domain_to_path_regex_filters_dict,
    domain_to_new_domain_regex_filters_dict,
    generic_video_id_regex_filter,
    regex_to_get_domain_from_url,
    regex_to_get_path_from_url,
    regex_to_parse_out_embedurl_from_rumble_html_source,
    regexes_to_find_embedded_url_from_html_source
)


class URLOperations(object):
    """

    """
    def __init__(self, opts):
        """
        """
        self.opts = opts
        self._url = None
        self._domain = None
        self._video_id_regex_filter = None

    @property
    def url(self) -> str:
        """

        :return: string
        """
        return self._url

    @url.setter
    def url(self, url: str) -> None:
        """

        :param url:
        :return:
        """
        self._url = url

    @url.deleter
    def url(self) -> None:
        """

        :return: None
        """
        del self._url

    @property
    def domain(self) -> str:
        """

        :return: str
        """
        return self._domain

    @domain.setter
    def domain(self, domain: str) -> None:
        """

        :param domain:
        :return:
        """
        self._domain = domain

    @domain.deleter
    def domain(self) -> None:
        """

        :return: None
        """
        del self._domain

    @property
    def video_id_regex_filter(self) -> str:
        """

        :return: str
        """
        return self._video_id_regex_filter

    @video_id_regex_filter.setter
    def video_id_regex_filter(self, video_id_regex_filter: str) -> None:
        """

        :param video_id_regex_filter: str
        :return: None
        """
        self._video_id_regex_filter = video_id_regex_filter

    @video_id_regex_filter.deleter
    def video_id_regex_filter(self) -> None:
        """

        :return: None
        """
        del self._video_id_regex_filter

    def get_domain_from_url(self) -> str:
        """

        :return: str
        """

        compiled_regex_domain = re.compile(regex_to_get_domain_from_url)

        return compiled_regex_domain.findall(self.url)[0]

    def get_path_from_url(self) -> str:
        """

        :return: str
        """
        compiled_regex_path = re.compile(regex_to_get_path_from_url)

        return compiled_regex_path.findall(self.url)[0]

    def search_for_embedded_url_from_html_source(self, html_body: str) -> str:
        """

        :param html_body: str
        :return: str
        """
        self.domain = self.get_domain_from_url()
        compiled_regex: [str] = re.compile(regexes_to_find_embedded_url_from_html_source[self.domain])
        embedded_url: str = compiled_regex.findall(html_body)[0]

        return embedded_url

    def get_video_id_from_url(self, video_id_regex: str = generic_video_id_regex_filter) -> str:
        """
        Get the video ID from the URL. This should cover enough domains but the method can be overridden in a subclass.

        :param video_id_regex: str
        :return: str : Return video ID as a string
        """
        # Get the video_id embedded within the Rumble URL beginning with the path in the URL.
        regex_to_get_video_id_from_url: str = video_id_regex
        # Compile the RegEx
        compiled_regex: [str] = re.compile(regex_to_get_video_id_from_url)

        try:
            video_id = compiled_regex.findall(self.url)[0]
        except IndexError as ie:
            write_string("[ERROR] video_id pattern was not found in URL\n")
            return ""
        except TypeError as te:
            write_string("[ERROR] video_id should be of type 'str'\n")
            raise TypeError

        return video_id
