from __future__ import annotations

import random

from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request

from ..utils import (
    write_string
)
from .URLOperations import URLOperations
from youtube_dl.preprocessor import (
    HTTP_USER_AGENTS
)

class DownloadHTML(URLOperations):
    """
    This class will handle the download of HTML source from long URLs.

    """
    # Randomly choose from the list of HTTP user agents to use
    HTTP_AGENT_HEADER_DICT: dict = HTTP_USER_AGENTS[random.choice([*range(len(HTTP_USER_AGENTS))])]
    HTTP_TIMEOUT: int = 10

    def __init__(self, opts):
        """
        """
        super().__init__()

        self.opts = opts
        self._url = None
        self._http_status = None
        self._domain = None
        self._video_id_regex_filter = None

    @property
    def http_status(self) -> str:
        """
        Getter for the HTTP status property.

        :return: string
        """
        return self._http_status

    @http_status.setter
    def http_status(self, http_status: str) -> None:
        """
        Setter for the HTTP status property.

        :param http_status:
        :return:
        """
        self._http_status = http_status

    @http_status.deleter
    def http_status(self) -> None:
        """
        Deleter for the HTTP status property.

        :return: None
        """
        del self._http_status

    def make_http_request_to_remote_server(self, url: str, headers: dict = None) -> str:
        """
        This method will simply download the HTML source from a URL using a randomly chosen User-Agent from
        a dictionary.

        :param url: str: URL for remote HTTP service
        :param headers: dict: HTTP Agent header as a dictionary
        :return: str : Returns HTML body from remote server.
        """
        if self.opts.verbose:
            write_string("[INFO][PRE-PROCESSOR] headers = " + str(headers) + "\n")
        if headers is None:
            # HTTP_AGENT_HEADER_DICT is of type dict() that must be extracted
            headers = self.HTTP_AGENT_HEADER_DICT
        if self.opts.verbose:
            write_string("[INFO][PRE-PROCESSOR] headers = " + str(headers) + "\n")

        self._url = url
        if self.opts.verbose:
            write_string("[INFO][PRE-PROCESSOR] url = " + str(url) + "\n")

        request = Request(url, headers=headers or {})
        try:
            with urlopen(request, timeout=self.HTTP_TIMEOUT) as response:
                self._http_status = response.status
                body = response.read()

            character_set = response.headers.get_content_charset()
            decoded_body: str = body.decode(character_set)

            if self.opts.verbose:
                write_string("[INFO][PRE-PROCESSOR] HTTP Response status = " + str(self._http_status) + "\n")

            return decoded_body

        except HTTPError as he:
            write_string(he.status, he.reason)
        except URLError as ue:
            write_string(ue.reason)
        except TimeoutError:
            write_string("[ERROR][PRE-PROCESSOR]Request timed out elapsed past default of " + str(self.HTTP_TIMEOUT))
