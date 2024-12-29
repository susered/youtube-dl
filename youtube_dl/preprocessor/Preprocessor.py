from __future__ import annotations

import re

from .URLOperations import URLOperations
from ..utils import (
    write_string
)
from youtube_dl.preprocessor import (
    domain_to_video_id_regex_filters_dict,
    domain_to_path_regex_filters_dict,
    domain_to_new_domain_regex_filters_dict,
    regex_to_get_domain_from_url,
    regex_to_get_path_from_url,
)

class Preprocessor(URLOperations):
    """
    This class file is for preprocessing URLs to get the URLs prepared as an embedded URL.
    """
    def __init__(self, opts):
        """
        """
        super().__init__()

        self.opts = opts
        self._url = None
        self._domain = None
        self._video_id_regex_filter = None

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
            write_string("[debug2] url = %s\n" % url)

        self.url = url
        if self.opts.verbose:
            write_string("[debug2] self.url = %s\n" % self.url)

        # Get domain from URL
        self.domain = self.get_domain_from_url()
        if self.opts.verbose:
            write_string("[debug2] self.domain = %s\n" % self.domain)

        # Use the dictionary of domain-to-RegExs to map a domain to its RegEx filter for video id extraction.
        video_id: str = self.get_video_id_from_url(domain_to_video_id_regex_filters_dict[self.domain])
        write_string("[debug2] video_id = %s\n" % video_id)
        if video_id == "" or video_id is None:
            raise ValueError

        path: str = domain_to_path_regex_filters_dict[self.domain]
        if path is not None or path != "":
            path = path + "/"
        if self.opts.verbose:
            write_string("[debug2] path = %s\n" % path)

        return "https://" + domain_to_new_domain_regex_filters_dict[self.get_domain_from_url()] + "/" + path + video_id
