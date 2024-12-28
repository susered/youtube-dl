from __future__ import annotations

import http
import random
import re
from typing import Any

from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request

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
    regexes_to_find_embedded_url_from_html_source,
    HTTP_USER_AGENTS
)


class DownloadHTML(object):
    """

    """
    # Randomly choose from the list of HTTP user agents to use
    HTTP_AGENT_HEADER: dict = HTTP_USER_AGENTS[random.choice([*range(len(HTTP_USER_AGENTS))])]
    HTTP_TIMEOUT: int = 10

    def __init__(self, opts):
        """
        """
        self.opts = opts
        self._url = None
        self._http_status = None
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
    def http_status(self) -> str:
        """

        :return: string
        """
        return self._http_status

    @http_status.setter
    def http_status(self, http_status: str) -> None:
        """

        :param http_status:
        :return:
        """
        self._http_status = http_status

    @http_status.deleter
    def http_status(self) -> None:
        """

        :return: None
        """
        del self._http_status

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

    def make_http_request_to_remote_server(self, url: str, headers: dict = None) -> str:
        """

        :param url: str: URL for remote HTTP service
        :param headers: dict: HTTP Agent header as a dictionary
        :return: str : Returns HTML body from remote server.
        """
        self._url = url

        if headers is None:
            headers = self.HTTP_AGENT_HEADER

        request = Request(url, headers=headers or {})
        try:
            with urlopen(request, timeout=self.HTTP_TIMEOUT) as response:
                self._http_status = response.status
                body = response.read()

            character_set = response.headers.get_content_charset()
            decoded_body: str = body.decode(character_set)

            return decoded_body

        except HTTPError as he:
            write_string(he.status, he.reason)
        except URLError as ue:
            write_string(ue.reason)
        except TimeoutError:
            write_string("Request timed out elapsed past default of " + str(self.HTTP_TIMEOUT))
