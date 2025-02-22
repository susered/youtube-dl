#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals

__license__ = 'Public Domain'

import io
import os
import random
import sys
import traceback
import urllib.error

from .options import (
    parseOpts,
)
from .compat import (
    compat_getpass,
    compat_register_utf8,
    compat_shlex_split,
    workaround_optparse_bug9161,
)
from .utils import (
    _UnsafeExtensionError,
    DateRange,
    decodeOption,
    DEFAULT_OUTTMPL,
    DownloadError,
    expand_path,
    match_filter_func,
    MaxDownloadsReached,
    preferredencoding,
    read_batch_urls,
    SameFileError,
    setproctitle,
    std_headers,
    write_string,
    render_table,
)
from .update import update_self
from .downloader import (
    FileDownloader,
)
from .extractor import gen_extractors, list_extractors
from .extractor.adobepass import MSO_INFO
from .YoutubeDL import YoutubeDL

from .preprocessor import (
    Preprocessor,
    DownloadHTML,
    URLOperations,
    regexes_to_find_embedded_url_from_html_source,
    domain_to_new_domain_regex_filters_dict,
    domain_to_video_id_regex_filters_dict,
    domain_to_path_regex_filters_dict,
    regex_to_determine_criteria_preprocessing_match
)


def _real_main(argv=None):
    # Compatibility fix for Windows
    compat_register_utf8()

    workaround_optparse_bug9161()

    setproctitle('youtube-dl')

    parser, opts, args = parseOpts(argv)

    # Set user agent
    if opts.user_agent is not None:
        std_headers['User-Agent'] = opts.user_agent

    # Set referer
    if opts.referer is not None:
        std_headers['Referer'] = opts.referer

    # Custom HTTP headers
    if opts.headers is not None:
        for h in opts.headers:
            if ':' not in h:
                parser.error('wrong header formatting, it should be key:value, not "%s"' % h)
            key, value = h.split(':', 1)
            if opts.verbose:
                write_string('[debug] Adding header from command line option %s:%s\n' % (key, value))
            std_headers[key] = value

    # Dump user agent
    if opts.dump_user_agent:
        write_string(std_headers['User-Agent'] + '\n', out=sys.stdout)
        sys.exit(0)

    # Batch file verification
    batch_urls = []
    if opts.batchfile is not None:
        try:
            if opts.batchfile == '-':
                batchfd = sys.stdin
            else:
                batchfd = io.open(
                    expand_path(opts.batchfile),
                    'r', encoding='utf-8', errors='ignore')
            batch_urls = read_batch_urls(batchfd)
            if opts.verbose:
                write_string('[debug] Batch file urls: ' + repr(batch_urls) + '\n')
        except IOError:
            sys.exit('ERROR: batch file %s could not be read' % opts.batchfile)

    # Let us create an object to process URL tokens
    url_operations = URLOperations.URLOperations(opts)
    # Preprocessing instantiated class
    url_preprocessing = Preprocessor.Preprocessor(opts)
    # Download the HTML from the URL to extract the embedded URL
    download_html = DownloadHTML.DownloadHTML(opts)
    # The following is the original routine for processing the commandline arguments:
    #all_urls = batch_urls + [url_preprocessing.reformat_full_url_for_embedded_url(url.strip()) for url in args]  # batch_urls are already striped in read_batch_urls

    # This is format for parsing URLs, as opposed to the aforementioned one-liner, was chosen to accommodate any
    # URLs that may need to be skipped, without exiting the whole invoked command.
    preproc_collect_urls_from_args: str = ""
    preproc_collected_urls_from_urls: list = []
    embedded_url: str = ""
    for url in args:
        # Simple assignment so url.strip() is only processed once
        url_strip: str = url.strip()
        # Set the "url" object attribute
        url_operations.url = url_strip
        # Get the DNS domain of the user-submitted URL
        url_operations.domain = url_operations.get_domain_from_url()
        # debug and verbose outputs
        if opts.verbose:
            write_string("[debug2] url_operations.domain = %s\n" % url_operations.domain)
        #
        regex_for_embedded_url = regexes_to_find_embedded_url_from_html_source.get(url_operations.domain)
        if opts.verbose:
            write_string("[debug2] regex_for_embedded_url = %s\n" % str(regex_for_embedded_url))
            write_string("[debug2] type(regex_for_embedded_url) = %s\n" % type(regex_for_embedded_url))

        domain_to_new_domain_regex_filter: str = domain_to_new_domain_regex_filters_dict.get(url_operations.domain)
        if opts.verbose:
            write_string("[debug2] domain_to_new_domain_regex_filter = %s\n" % domain_to_new_domain_regex_filter)

        # Count the number of tokens in the URL to determine if the URL meets the criteria for pre-processing
        is_url_fit_for_preprocessing: int = url_operations.number_of_url_tokens_for_preprocessing()
        if opts.verbose:
            write_string("[debug2] Token count for URL, %s, " % url_operations.url)
            write_string("is %s\n" % is_url_fit_for_preprocessing)

        # If we cannot find the RegEx related to the domain, then the URL/domain cannot be pre-processed
        if regex_for_embedded_url is not None and is_url_fit_for_preprocessing >= 1:
            # This first "try-except" converts a long URL to an embedded that can be processed
            try:
                # Retrieve the HTML source from the remote HTTPS service
                write_string("[INFO][PRE-PROCESSOR] Downloading HTML source page from %s\n" % url_strip)
                html_source = download_html.make_http_request_to_remote_server(url.strip())
                # Set the URL object
                url_operations.url = url.strip()
                # Search for the embedded URL in the downloaded HTML source
                embedded_url = url_operations.search_for_embedded_url_from_html_source(html_source)
                if embedded_url is not None or embedded_url != "":
                    preproc_collect_urls_from_args = embedded_url
                else:
                    preproc_collect_urls_from_args = url_strip
            except urllib.error.HTTPError as he:
                write_string('[ERROR][PRE-PROCESSOR] HTTP error occurred on URL %s:\n' % url_strip)
                traceback.print_tb(he.__traceback__)
        elif domain_to_new_domain_regex_filter is not None:
            # If the mapping contains a domain with its RegEx filter, then process the pattern further
            map_from_one_domain_to_another: str = domain_to_new_domain_regex_filters_dict.get(url_operations.domain)
            if opts.verbose:
                write_string("[debug2] map_from_one_domain_to_another = %s\n" % map_from_one_domain_to_another)
            map_domain_to_url_path: str = url_operations.get_path_from_url()
            if opts.verbose:
                write_string("[debug2] map_domain_to_url_path = %s\n" % map_domain_to_url_path)

            try:
                # Construct the URL for extraction
                url_string = "https://" + map_from_one_domain_to_another + "/" + map_domain_to_url_path
                write_string("[INFO][PRE-PROCESSOR] Converted %s to usable DNS domain for extraction " % url_strip)
                write_string("%s\n" % url_string)
                if opts.verbose:
                    write_string("[debug2] url_string = %s\n" % url_string)
                preproc_collect_urls_from_args = url_string
            except ValueError as ve:
                traceback.print_tb(sys.exc_info()[2])
        else:
            preproc_collect_urls_from_args = url_strip

        if opts.url_preprocessing is not None and opts.url_preprocessing is True:
            # This second "try-except" is for full video pages without any embedded
            try:
                preproc_collect_urls_from_args = url_preprocessing.reformat_full_url_for_embedded_url(url.strip())
            except (ValueError, IndexError) as vie:
                write_string("[INFO][PRE-PROCESSOR] Skipping url, %s, lack of a video ID in URL\n" % url_strip)

                if embedded_url is not None or embedded_url != "":
                    write_string("[INFO][PRE-PROCESSOR]Found embedded URL %s\n" % url_strip)
                    preproc_collect_urls_from_args = embedded_url
                else:
                    preproc_collect_urls_from_args = url.strip()

                if opts.verbose:
                    traceback.print_tb(vie.__traceback__)
            except TypeError as te:
                write_string("[ERROR][PRE-PROCESSOR] Skipping url, %s, due to bad URL formatting:\n" % url_strip)
                if opts.verbose:
                    traceback.print_tb(te.__traceback__)
                continue

        # Collect all the user-submitted URLs have been pre-processed into embeddable URLs
        if preproc_collect_urls_from_args != "" and preproc_collect_urls_from_args is not None:
            preproc_collected_urls_from_urls += [preproc_collect_urls_from_args]

    # Concatenate two different collected URLs between two different lists
    all_urls = batch_urls + preproc_collected_urls_from_urls
    # Remove duplicates from all_urls while keeping the original order submitted by the user
    all_urls = list(dict.fromkeys(all_urls))

    _enc = preferredencoding()
    all_urls = [url.decode(_enc, 'ignore') if isinstance(url, bytes) else url for url in all_urls]

    if opts.list_extractors:
        for ie in list_extractors(opts.age_limit):
            write_string(ie.IE_NAME + (' (CURRENTLY BROKEN)' if not ie._WORKING else '') + '\n', out=sys.stdout)
            matchedUrls = [url for url in all_urls if ie.suitable(url)]
            for mu in matchedUrls:
                write_string('  ' + mu + '\n', out=sys.stdout)
        sys.exit(0)
    if opts.list_extractor_descriptions:
        for ie in list_extractors(opts.age_limit):
            if not ie._WORKING:
                continue
            desc = getattr(ie, 'IE_DESC', ie.IE_NAME)
            if desc is False:
                continue
            if hasattr(ie, 'SEARCH_KEY'):
                _SEARCHES = ('cute kittens', 'slithering pythons', 'falling cat', 'angry poodle', 'purple fish', 'running tortoise', 'sleeping bunny', 'burping cow')
                _COUNTS = ('', '5', '10', 'all')
                desc += ' (Example: "%s%s:%s" )' % (ie.SEARCH_KEY, random.choice(_COUNTS), random.choice(_SEARCHES))
                desc += "\n"
            write_string(desc, out=sys.stdout)
        sys.exit(0)
    if opts.ap_list_mso:
        table = [[mso_id, mso_info['name']] for mso_id, mso_info in MSO_INFO.items()]
        write_string('Supported TV Providers:\n' + render_table(['mso', 'mso name'], table) + '\n', out=sys.stdout)
        sys.exit(0)

    # Conflicting, missing and erroneous options
    if opts.usenetrc and (opts.username is not None or opts.password is not None):
        parser.error('using .netrc conflicts with giving username/password')
    if opts.password is not None and opts.username is None:
        parser.error('account username missing\n')
    if opts.ap_password is not None and opts.ap_username is None:
        parser.error('TV Provider account username missing\n')
    if opts.outtmpl is not None and (opts.usetitle or opts.autonumber or opts.useid):
        parser.error('using output template conflicts with using title, video ID or auto number')
    if opts.autonumber_size is not None:
        if opts.autonumber_size <= 0:
            parser.error('auto number size must be positive')
    if opts.autonumber_start is not None:
        if opts.autonumber_start < 0:
            parser.error('auto number start must be positive or 0')
    if opts.usetitle and opts.useid:
        parser.error('using title conflicts with using video ID')
    if opts.username is not None and opts.password is None:
        opts.password = compat_getpass('Type account password and press [Return]: ')
    if opts.ap_username is not None and opts.ap_password is None:
        opts.ap_password = compat_getpass('Type TV provider account password and press [Return]: ')
    if opts.ratelimit is not None:
        numeric_limit = FileDownloader.parse_bytes(opts.ratelimit)
        if numeric_limit is None:
            parser.error('invalid rate limit specified')
        opts.ratelimit = numeric_limit
    if opts.min_filesize is not None:
        numeric_limit = FileDownloader.parse_bytes(opts.min_filesize)
        if numeric_limit is None:
            parser.error('invalid min_filesize specified')
        opts.min_filesize = numeric_limit
    if opts.max_filesize is not None:
        numeric_limit = FileDownloader.parse_bytes(opts.max_filesize)
        if numeric_limit is None:
            parser.error('invalid max_filesize specified')
        opts.max_filesize = numeric_limit
    if opts.sleep_interval is not None:
        if opts.sleep_interval < 0:
            parser.error('sleep interval must be positive or 0')
    if opts.max_sleep_interval is not None:
        if opts.max_sleep_interval < 0:
            parser.error('max sleep interval must be positive or 0')
        if opts.sleep_interval is None:
            parser.error('min sleep interval must be specified, use --min-sleep-interval')
        if opts.max_sleep_interval < opts.sleep_interval:
            parser.error('max sleep interval must be greater than or equal to min sleep interval')
    else:
        opts.max_sleep_interval = opts.sleep_interval
    if opts.ap_mso and opts.ap_mso not in MSO_INFO:
        parser.error('Unsupported TV Provider, use --ap-list-mso to get a list of supported TV Providers')

    if opts.no_check_extensions:
        _UnsafeExtensionError.lenient = True

    def parse_retries(retries):
        if retries in ('inf', 'infinite'):
            parsed_retries = float('inf')
        else:
            try:
                parsed_retries = int(retries)
            except (TypeError, ValueError):
                parser.error('invalid retry count specified')
        return parsed_retries
    if opts.retries is not None:
        opts.retries = parse_retries(opts.retries)
    if opts.fragment_retries is not None:
        opts.fragment_retries = parse_retries(opts.fragment_retries)
    if opts.buffersize is not None:
        numeric_buffersize = FileDownloader.parse_bytes(opts.buffersize)
        if numeric_buffersize is None:
            parser.error('invalid buffer size specified')
        opts.buffersize = numeric_buffersize
    if opts.http_chunk_size is not None:
        numeric_chunksize = FileDownloader.parse_bytes(opts.http_chunk_size)
        if not numeric_chunksize:
            parser.error('invalid http chunk size specified')
        opts.http_chunk_size = numeric_chunksize
    if opts.playliststart <= 0:
        raise ValueError('Playlist start must be positive')
    if opts.playlistend not in (-1, None) and opts.playlistend < opts.playliststart:
        raise ValueError('Playlist end must be greater than playlist start')
    if opts.extractaudio:
        if opts.audioformat not in ['best', 'aac', 'flac', 'mp3', 'm4a', 'opus', 'vorbis', 'wav']:
            parser.error('invalid audio format specified')
    if opts.audioquality:
        opts.audioquality = opts.audioquality.strip('k').strip('K')
        if not opts.audioquality.isdigit():
            parser.error('invalid audio quality specified')
    if opts.recodevideo is not None:
        if opts.recodevideo not in ['mp4', 'flv', 'webm', 'ogg', 'mkv', 'avi']:
            parser.error('invalid video recode format specified')
    if opts.convertsubtitles is not None:
        if opts.convertsubtitles not in ['srt', 'vtt', 'ass', 'lrc']:
            parser.error('invalid subtitle format specified')

    if opts.date is not None:
        date = DateRange.day(opts.date)
    else:
        date = DateRange(opts.dateafter, opts.datebefore)

    # Do not download videos when there are audio-only formats
    if opts.extractaudio and not opts.keepvideo and opts.format is None:
        opts.format = 'bestaudio/best'

    # --all-sub automatically sets --write-sub if --write-auto-sub is not given
    # this was the old behaviour if only --all-sub was given.
    if opts.allsubtitles and not opts.writeautomaticsub:
        opts.writesubtitles = True

    outtmpl = ((opts.outtmpl is not None and opts.outtmpl)
               or (opts.format == '-1' and opts.usetitle and '%(title)s-%(id)s-%(format)s.%(ext)s')
               or (opts.format == '-1' and '%(id)s-%(format)s.%(ext)s')
               or (opts.usetitle and opts.autonumber and '%(autonumber)s-%(title)s-%(id)s.%(ext)s')
               or (opts.usetitle and '%(title)s-%(id)s.%(ext)s')
               or (opts.useid and '%(id)s.%(ext)s')
               or (opts.autonumber and '%(autonumber)s-%(id)s.%(ext)s')
               or DEFAULT_OUTTMPL)
    if not os.path.splitext(outtmpl)[1] and opts.extractaudio:
        parser.error('Cannot download a video and extract audio into the same'
                     ' file! Use "{0}.%(ext)s" instead of "{0}" as the output'
                     ' template'.format(outtmpl))

    any_getting = opts.geturl or opts.gettitle or opts.getid or opts.getthumbnail or opts.getdescription or opts.getfilename or opts.getformat or opts.getduration or opts.dumpjson or opts.dump_single_json
    any_printing = opts.print_json
    download_archive_fn = expand_path(opts.download_archive) if opts.download_archive is not None else opts.download_archive

    # PostProcessors
    postprocessors = []
    if opts.metafromtitle:
        postprocessors.append({
            'key': 'MetadataFromTitle',
            'titleformat': opts.metafromtitle
        })
    if opts.extractaudio:
        postprocessors.append({
            'key': 'FFmpegExtractAudio',
            'preferredcodec': opts.audioformat,
            'preferredquality': opts.audioquality,
            'nopostoverwrites': opts.nopostoverwrites,
        })
    if opts.recodevideo:
        postprocessors.append({
            'key': 'FFmpegVideoConvertor',
            'preferedformat': opts.recodevideo,
        })
    # FFmpegMetadataPP should be run after FFmpegVideoConvertorPP and
    # FFmpegExtractAudioPP as containers before conversion may not support
    # metadata (3gp, webm, etc.)
    # And this post-processor should be placed before other metadata
    # manipulating post-processors (FFmpegEmbedSubtitle) to prevent loss of
    # extra metadata. By default ffmpeg preserves metadata applicable for both
    # source and target containers. From this point the container won't change,
    # so metadata can be added here.
    if opts.addmetadata:
        postprocessors.append({'key': 'FFmpegMetadata'})
    if opts.convertsubtitles:
        postprocessors.append({
            'key': 'FFmpegSubtitlesConvertor',
            'format': opts.convertsubtitles,
        })
    if opts.embedsubtitles:
        postprocessors.append({
            'key': 'FFmpegEmbedSubtitle',
        })
    if opts.embedthumbnail:
        already_have_thumbnail = opts.writethumbnail or opts.write_all_thumbnails
        postprocessors.append({
            'key': 'EmbedThumbnail',
            'already_have_thumbnail': already_have_thumbnail
        })
        if not already_have_thumbnail:
            opts.writethumbnail = True
    # XAttrMetadataPP should be run after post-processors that may change file
    # contents
    if opts.xattrs:
        postprocessors.append({'key': 'XAttrMetadata'})
    # Please keep ExecAfterDownload towards the bottom as it allows the user to modify the final file in any way.
    # So if the user is able to remove the file before your postprocessor runs it might cause a few problems.
    if opts.exec_cmd:
        postprocessors.append({
            'key': 'ExecAfterDownload',
            'exec_cmd': opts.exec_cmd,
        })
    external_downloader_args = None
    if opts.external_downloader_args:
        external_downloader_args = compat_shlex_split(opts.external_downloader_args)
    postprocessor_args = None
    if opts.postprocessor_args:
        postprocessor_args = compat_shlex_split(opts.postprocessor_args)
    match_filter = (
        None if opts.match_filter is None
        else match_filter_func(opts.match_filter))

    ydl_opts = {
        'usenetrc': opts.usenetrc,
        'username': opts.username,
        'password': opts.password,
        'twofactor': opts.twofactor,
        'videopassword': opts.videopassword,
        'ap_mso': opts.ap_mso,
        'ap_username': opts.ap_username,
        'ap_password': opts.ap_password,
        'quiet': (opts.quiet or any_getting or any_printing),
        'no_warnings': opts.no_warnings,
        'forceurl': opts.geturl,
        'forcetitle': opts.gettitle,
        'forceid': opts.getid,
        'forcethumbnail': opts.getthumbnail,
        'forcedescription': opts.getdescription,
        'forceduration': opts.getduration,
        'forcefilename': opts.getfilename,
        'forceformat': opts.getformat,
        'forcejson': opts.dumpjson or opts.print_json,
        'dump_single_json': opts.dump_single_json,
        'simulate': opts.simulate or any_getting,
        'skip_download': opts.skip_download,
        'format': opts.format,
        'listformats': opts.listformats,
        'outtmpl': outtmpl,
        'outtmpl_na_placeholder': opts.outtmpl_na_placeholder,
        'autonumber_size': opts.autonumber_size,
        'autonumber_start': opts.autonumber_start,
        'restrictfilenames': opts.restrictfilenames,
        'ignoreerrors': opts.ignoreerrors,
        'force_generic_extractor': opts.force_generic_extractor,
        'ratelimit': opts.ratelimit,
        'nooverwrites': opts.nooverwrites,
        'retries': opts.retries,
        'fragment_retries': opts.fragment_retries,
        'skip_unavailable_fragments': opts.skip_unavailable_fragments,
        'keep_fragments': opts.keep_fragments,
        'buffersize': opts.buffersize,
        'noresizebuffer': opts.noresizebuffer,
        'http_chunk_size': opts.http_chunk_size,
        'continuedl': opts.continue_dl,
        'noprogress': opts.noprogress,
        'progress_with_newline': opts.progress_with_newline,
        'playliststart': opts.playliststart,
        'playlistend': opts.playlistend,
        'playlistreverse': opts.playlist_reverse,
        'playlistrandom': opts.playlist_random,
        'noplaylist': opts.noplaylist,
        'logtostderr': opts.outtmpl == '-',
        'consoletitle': opts.consoletitle,
        'nopart': opts.nopart,
        'updatetime': opts.updatetime,
        'writedescription': opts.writedescription,
        'writeannotations': opts.writeannotations,
        'writeinfojson': opts.writeinfojson,
        'writethumbnail': opts.writethumbnail,
        'write_all_thumbnails': opts.write_all_thumbnails,
        'writesubtitles': opts.writesubtitles,
        'writeautomaticsub': opts.writeautomaticsub,
        'allsubtitles': opts.allsubtitles,
        'listsubtitles': opts.listsubtitles,
        'subtitlesformat': opts.subtitlesformat,
        'subtitleslangs': opts.subtitleslangs,
        'matchtitle': decodeOption(opts.matchtitle),
        'rejecttitle': decodeOption(opts.rejecttitle),
        'max_downloads': opts.max_downloads,
        'prefer_free_formats': opts.prefer_free_formats,
        'verbose': opts.verbose,
        'dump_intermediate_pages': opts.dump_intermediate_pages,
        'write_pages': opts.write_pages,
        'test': opts.test,
        'keepvideo': opts.keepvideo,
        'min_filesize': opts.min_filesize,
        'max_filesize': opts.max_filesize,
        'min_views': opts.min_views,
        'max_views': opts.max_views,
        'daterange': date,
        'cachedir': opts.cachedir,
        'youtube_print_sig_code': opts.youtube_print_sig_code,
        'age_limit': opts.age_limit,
        'download_archive': download_archive_fn,
        'cookiefile': opts.cookiefile,
        'nocheckcertificate': opts.no_check_certificate,
        'prefer_insecure': opts.prefer_insecure,
        'proxy': opts.proxy,
        'socket_timeout': opts.socket_timeout,
        'bidi_workaround': opts.bidi_workaround,
        'debug_printtraffic': opts.debug_printtraffic,
        'prefer_ffmpeg': opts.prefer_ffmpeg,
        'include_ads': opts.include_ads,
        'default_search': opts.default_search,
        'youtube_include_dash_manifest': opts.youtube_include_dash_manifest,
        'encoding': opts.encoding,
        'extract_flat': opts.extract_flat,
        'mark_watched': opts.mark_watched,
        'merge_output_format': opts.merge_output_format,
        'postprocessors': postprocessors,
        'fixup': opts.fixup,
        'source_address': opts.source_address,
        'call_home': opts.call_home,
        'sleep_interval': opts.sleep_interval,
        'max_sleep_interval': opts.max_sleep_interval,
        'external_downloader': opts.external_downloader,
        'list_thumbnails': opts.list_thumbnails,
        'playlist_items': opts.playlist_items,
        'xattr_set_filesize': opts.xattr_set_filesize,
        'match_filter': match_filter,
        'no_color': opts.no_color,
        'ffmpeg_location': opts.ffmpeg_location,
        'hls_prefer_native': opts.hls_prefer_native,
        'hls_use_mpegts': opts.hls_use_mpegts,
        'external_downloader_args': external_downloader_args,
        'postprocessor_args': postprocessor_args,
        'cn_verification_proxy': opts.cn_verification_proxy,
        'geo_verification_proxy': opts.geo_verification_proxy,
        'config_location': opts.config_location,
        'geo_bypass': opts.geo_bypass,
        'geo_bypass_country': opts.geo_bypass_country,
        'geo_bypass_ip_block': opts.geo_bypass_ip_block,
        'url_preprocessing': opts.url_preprocessing,
        # just for deprecation check
        'autonumber': opts.autonumber if opts.autonumber is True else None,
        'usetitle': opts.usetitle if opts.usetitle is True else None,
    }

    with YoutubeDL(ydl_opts) as ydl:
        # Update version
        if opts.update_self:
            update_self(ydl.to_screen, opts.verbose, ydl._opener)

        # Remove cache dir
        if opts.rm_cachedir:
            ydl.cache.remove()

        # Maybe do nothing
        if (len(all_urls) < 1) and (opts.load_info_filename is None):
            if opts.update_self or opts.rm_cachedir:
                sys.exit()

            ydl.warn_if_short_id(sys.argv[1:] if argv is None else argv)
            parser.error(
                'You must provide at least one URL.\n'
                'Type youtube-dl --help to see a list of all options.')
        # This is where the downloads are processed either by parsing of files or by singly listed URL on the
        # commandline
        try:
            if opts.load_info_filename is not None:
                retcode = ydl.download_with_info_file(expand_path(opts.load_info_filename))
            else:
                retcode = ydl.download(all_urls)
        except MaxDownloadsReached:
            ydl.to_screen('--max-download limit reached, aborting.')
            retcode = 101

    sys.exit(retcode)


def main(argv=None):
    try:
        _real_main(argv)
    except DownloadError:
        sys.exit(1)
    except SameFileError:
        sys.exit('ERROR: fixed output name but more than one file to download')
    except KeyboardInterrupt:
        sys.exit('\nERROR: Interrupted by user')


__all__ = ['main', 'YoutubeDL', 'gen_extractors', 'list_extractors']
