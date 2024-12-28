from __future__ import annotations

import re
import urllib

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


class Preprocessor(object):
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

    def get_video_id_from_url(self, video_id_regex: str = generic_video_id_regex_filter) -> str:
        """
        Get the video ID from the URL. This should cover enough domains but the method can be overridden in a subclass.

        :param video_id_regex: str
        :return: str : Return video ID
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

    def reformat_full_url_for_embedded_url(self, url: str) -> str | None:
        """
        This will transform a URL of the long-form,

            https://www.bitchute.com/video/B1OGUWot5hU1

        , to the following embedded form,

            https://old.bitchute.com/video/B1OGUWot5hU1

        , where video extract occurs

        :param url: str
        :return: str | None
        """
        if self.opts.verbose:
            write_string("[debug2] url = " + url + "\n")

        self.url = url
        if self.opts.verbose:
            write_string("[debug2] self.url = " + self.url + "\n")

        # Get domain from URL
        self.domain = self.get_domain_from_url()
        if self.opts.verbose:
            write_string("[debug2] self.domain = " + self.domain + "\n")

        # Use the dictionary of domain-to-RegExs to map a domain to its RegEx filter for video id extraction.
        video_id: str = self.get_video_id_from_url(domain_to_video_id_regex_filters_dict[self.domain])
        write_string("[debug2] video_id = " + str(video_id) + "\n")
        if video_id == "" or video_id is None:
            raise ValueError

        path: str = domain_to_path_regex_filters_dict[self.domain]
        if path is not None or path != "":
            path = path + "/"
        if self.opts.verbose:
            write_string("[debug2] path = " + path + "\n")

        return "https://" + domain_to_new_domain_regex_filters_dict[self.get_domain_from_url()] + "/" + path + video_id
