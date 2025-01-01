from __future__ import annotations

import re

from ..utils import (
    write_string
)
from youtube_dl.preprocessor import (
    generic_video_id_regex_filter,
    regex_to_get_domain_from_url,
    regex_to_get_path_from_url,
    regexes_to_find_embedded_url_from_html_source, regex_to_determine_criteria_preprocessing_match
)

class URLOperations(object):
    """
    This class employs all URL-related operations and manipulations.

    """
    def __init__(self, opts=None):
        """
        """
        self.opts = opts
        self._url = None
        self._domain = None
        self._video_id_regex_filter = None

    @property
    def url(self) -> str:
        """
        Getter for the URL property.

        :return: string
        """
        return self._url

    @url.setter
    def url(self, url: str) -> None:
        """
        Setter for the URL property.

        :param url:
        :return:
        """
        self._url = url

    @url.deleter
    def url(self) -> None:
        """
        Deleter for the URL property.

        :return: None
        """
        del self._url

    @property
    def domain(self) -> str:
        """
        Getter for the DNS domain property.

        :return: str
        """
        return self._domain

    @domain.setter
    def domain(self, domain: str) -> None:
        """
        Setter for the DNS domain property.

        :param domain:
        :return:
        """
        self._domain = domain

    @domain.deleter
    def domain(self) -> None:
        """
        Deleter for the DNS domain property.

        :return: None
        """
        del self._domain

    @property
    def video_id_regex_filter(self) -> str:
        """
        Getter for video ID RegEx filter

        :return: str
        """
        return self._video_id_regex_filter

    @video_id_regex_filter.setter
    def video_id_regex_filter(self, video_id_regex_filter: str) -> None:
        """
        Setter for video ID RegEx filter

        :param video_id_regex_filter: str
        :return: None
        """
        self._video_id_regex_filter = video_id_regex_filter

    @video_id_regex_filter.deleter
    def video_id_regex_filter(self) -> None:
        """
        Deleter for video ID RegEx filter

        :return: None
        """
        del self._video_id_regex_filter

    def get_domain_from_url(self) -> str:
        """
        Get domain from a set URL object

        :return: str
        """
        compiled_regex_domain = re.compile(regex_to_get_domain_from_url)

        return compiled_regex_domain.findall(self.url)[0]

    def get_path_from_url(self) -> str:
        """
        Get path from a set URL object

        :return: str
        """
        compiled_regex_path = re.compile(regex_to_get_path_from_url)

        return compiled_regex_path.findall(self.url)[0]

    def number_of_url_tokens_for_preprocessing(self) -> int:
        """
        Count the number of tokens in a URL required for preprocessing.

        :return: int
        """
        try:
            compiled_regex: [str] = re.compile(regex_to_determine_criteria_preprocessing_match[self.domain])
        except KeyError as ke:
            write_string("[WARNING] Could not find a matching domain for pre-processing criteria.\n")
            return 0

        try:
            list_of_tokens: list = compiled_regex.findall(self.url)
        except IndexError as ie:
            write_string("[WARNING] Could not find a matching domain for pre-processing criteria.\n")
            return 0

        try:
            return len(list_of_tokens[0])
        except IndexError as ie:
            write_string("[WARNING] Could not find a matching domain for pre-processing criteria.\n")
            return 0

    def search_for_embedded_url_from_html_source(self, html_body: str) -> str:
        """
        Use a RegEx to search the HTML body source for the embedded URL

        :param html_body: str
        :return: str
        """
        self.domain = self.get_domain_from_url()
        if self.opts.verbose:
            write_string("[INFO] self.domain = %s\n" % self.domain)

        embedded_url: str = ""
        try:
            compiled_regex: [str] = re.compile(regexes_to_find_embedded_url_from_html_source[self.domain])
            embedded_url = compiled_regex.findall(html_body)[0]

            return embedded_url
        except IndexError as ie:
            write_string("[ERROR] Embedded URL not found in HTML source!\n")

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
