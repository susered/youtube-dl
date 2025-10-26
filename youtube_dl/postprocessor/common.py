from __future__ import unicode_literals

import os

from ..utils import (
    PostProcessingError,
    cli_configuration_args,
    encodeFilename,
)


class PostProcessor(object):
    """Post Processor class.

    PostProcessor objects can be added to downloaders with their
    add_post_processor() method. When the downloader has finished a
    successful download, it will take its internal chain of PostProcessors
    and start calling the run() method on each one of them, first with
    an initial argument and then with the returned value of the previous
    PostProcessor.

    The chain will be stopped if one of them ever returns None or the end
    of the chain is reached.

    PostProcessor objects follow a "mutual registration" process similar
    to InfoExtractor objects.

    Optionally PostProcessor can use a list of additional command-line arguments
    with self._configuration_args.
    """

    _downloader = None

    def __init__(self, downloader=None):
        self._downloader = downloader

    def set_downloader(self, downloader):
        """Sets the downloader for this PP."""
        self._downloader = downloader

    def run(self, information):
        """Run the PostProcessor.

        The "information" argument is a dictionary like the ones
        composed by InfoExtractors. The only difference is that this
        one has an extra field called "filepath" that points to the
        downloaded file.

        This method returns a tuple, the first element is a list of the files
        that can be deleted, and the second of which is the updated
        information.

        In addition, this method may raise a PostProcessingError
        exception if post processing fails.
        """
        return [], information  # by default, keep file and do nothing

    def try_utime(self, path, atime, mtime, errnote='Cannot update utime of file'):
        try:
            os.utime(encodeFilename(path), (atime, mtime))
        except Exception:
            self._downloader.report_warning(errnote)

    def _configuration_args(self, default=[]):
        return cli_configuration_args(self._downloader.params, 'postprocessor_args', default)


class AudioConversionError(PostProcessingError):
    pass

class VideoPostProcessingTools(object):
    """Video processing tools.
    """
    _downloader = None

    def __init__(self, downloader=None):
        """

        """
        self._downloader = downloader

    @property
    def downloader(self):
        """
        :return str
        """
        return self._downloader

    @downloader.setter
    def downloader(self, downloader):
        """

        :param downloader:
        :return: None
        """
        self._downloader = downloader

    def compare_versions(self, version_1, version_2):
        """Determine if version_1 it greater than version_2 in the forms either
        (major: int, minor: int, patch: int) or "major: int,minor: int,patch: int".

        version_1: tuple
        version_2: tuple
        return: int : o means equal; -1 means version_1 < version_2; 1 means version_1 > version_2
        """

        try:
            if isinstance(version_1, str):
                version_1_tuple = tuple(map(int, version_1.split('.')))
            elif isinstance(version_1, tuple) or isinstance(version_1, int):
                version_1_tuple = tuple(map(int, version_1))
            else:
                raise TypeError

            if isinstance(version_2, str):
                version_2_tuple = tuple(map(int, version_2.split('.')))
            elif isinstance(version_2, tuple) or isinstance(version_2, int):
                version_2_tuple = tuple(map(int, version_2))
            else:
                raise TypeError

            for version1, version2 in zip(version_1_tuple, version_2_tuple):
                if version1 > version2:
                    return 1

                if version1 < version2:
                    return -1

            return 0

        except ValueError as ve:
            self._downloader.report_warning(ve)
        except TypeError as te:
            self._downloader.report_warning(te)
