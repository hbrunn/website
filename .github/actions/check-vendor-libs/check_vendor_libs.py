import argparse
import filecmp
import hashlib
import io
import json
import subprocess
import sys
import tarfile
import typing
import urllib.parse
from logging import getLogger
from pathlib import Path
from urllib.parse import parse_qs, urlparse, urlunparse
from http.client import HTTPSConnection

try:
    from typing import type_check_only
except ImportError:
    type_check_only = lambda x: x

__version__ = '0.1.0'
__desc__ = 'Enforce origin identity of vendored code'
_logger = getLogger("check-vendor-libs")


def check_paths(paths:list[str]) -> bool:
    """
    check a list of paths, possibly containing globs
    return False on mismatch/error
    """
    result = True

    for to_check in paths:
        for path in (Path(".").glob(to_check) if not to_check.startswith('/') else [Path(to_check)]):
            result &= check_path(path)

    return result


def check_path(path:Path, origins:dict[str, dict[str, typing.Any]] | None=None) -> bool:
    """
    check that every file in path is covered by an entry in vendor-libs.json,
    compare files with their declared origin, return False on mismatch/error
    """
    origins_file = None

    if origins is None:
        origins_file = path / 'vendor-libs.json'
        if not origins_file.exists():
            _logger.error(f'{origins_file} does not exist')
            return False
        try:
            origins = json.loads(origins_file.read_text())
        except json.decoder.JSONDecodeError:
            _logger.error(f'{origins_file} is not well-formed json')
            return False
        for filename, origin in origins.items():
            origin["__relative_name__"] = filename

    result = True

    for entry in path.iterdir():
        if entry == origins_file:
            continue
        if entry.name not in origins:
            if entry.is_dir():
                relative_origins = {
                    str(Path(*Path(filename).parts[1:])): origin
                    for filename, origin in origins.items()
                    if Path(filename).parts[:1] == entry.parts[-1:]
                }
                result &= check_path(entry, origins=relative_origins)
                continue
            _logger.error(f'{entry} has no declared origin')
            result = False
            continue

        origin = origins[entry.name]
        origin['__found__'] = True
        try:
            result &= compare(entry, origin)
        except ValueError:
            _logger.error(f'invalid origin for {entry}: {origin}')
            result = False
            continue

    for filename, origin in origins.items():
        if not origin.get('__found__') and len(Path(filename).parts) == 1:
            _logger.error(f'{path / filename} declared but not found')
            result = False

    return result


def compare(entry: Path, origin:dict[str, str]) -> bool:
    """
    compare a path with an origin dict. this means downloading the package from the
    purl key in origin, and comparing files/directories.
    return True if entry matches origin, False otherwise
    """
    purl = urlparse(origin['purl'])
    cache_dir = (
        Path.home()
        / ".cache"
        / "check-vendor-libs"
        / hashlib.sha256(urlunparse(purl[:5] + ('',)).encode()).hexdigest()
    )

    if not cache_dir.exists():
        download_url = get_download_url(purl)

        if not download_url:
            _logger.error(f'PURL {urlunparse(purl)} not supported')
            return False

        if not download_and_extract(download_url, cache_dir):
            return False

    origin_entry = cache_dir / purl.fragment / origin.get('vendor-name', entry.name)

    if entry.is_dir():
        result = True
        for dir_entry in entry.iterdir():
            new_fragment = str(Path(purl.fragment) / (dir_entry.name if dir_entry.is_dir() else ''))
            result &= compare(
                dir_entry, dict(
                    origin,
                    purl=urlunparse(purl[:5] + (new_fragment,)),
                )
            )
        return result

    if not origin_entry.exists():
        _logger.error(f"{entry} does not exist in origin {urlunparse(purl)}")
        return False

    if not filecmp.cmp(entry, origin_entry, shallow=False):
        _logger.error(f"{entry} differs from version in {urlunparse(purl)}")
        return False

    return True

def get_download_url(purl: urllib.parse.ParseResult) -> str:
    """
    extract and return a downloadable url from a purl
    """
    download_url = ''.join(parse_qs(purl.query).get('download_url') or [])
    if not download_url:
        parts = purl.path.split('/', 3)
        purl_type = parts[0]
        purl_namespace, purl_name, purl_version = [''] * 3

        if len(parts) == 3:
            purl_namespace, purl_name = parts[1:]
        elif len(parts) == 2:
            purl_namespace = ""
            purl_name, = parts[1:]

        if '@' in purl_name:
            purl_name, purl_version = purl_name.split('@', 1)

        download_url = {
            'github':
            f'https://github.com/{purl_namespace}/{purl_name}/archive/{purl_version}.tar.gz',
            'npm':
            f'https://registry.npmjs.org/{purl_namespace}{purl_namespace and "/" or ""}{purl_name}/-/{purl_name}-{purl_version}.tgz',
        }.get(purl_type) or ""
    return download_url

def download_and_extract(download_url: str, cache_dir: Path) -> bool:
    """
    download some package given by url and extract it to cache_dir
    """
    parsed_url = urlparse(download_url)
    if parsed_url.scheme not in SCHEME2DOWNLOAD:
        _logger.error(f'unsupported download url {download_url}')
        return False
    downloaded_file, mimetype = SCHEME2DOWNLOAD[parsed_url.scheme](parsed_url)
    if mimetype == 'application/octet-stream':
        mimetype = URLEXT2MIMETYPE.get(Path(parsed_url.path).suffix, mimetype)
    if mimetype not in MIMETYPE2EXTRACT:
        _logger.error(f'unsupported download format {mimetype}')
        return False
    return MIMETYPE2EXTRACT[mimetype](downloaded_file, cache_dir)


@type_check_only
class FileLike(typing.Protocol):
    def read(self, size: int) -> bytes:
        pass


def download_https(parsed_url: urllib.parse.ParseResult) -> typing.Tuple[FileLike, str]:
    """
    download a package via https, return (file like object, mimetype)
    """
    connection = HTTPSConnection(parsed_url.netloc)
    connection.request('GET', parsed_url.path)
    response = connection.getresponse()
    if response.status == 302:
        return download_https(urlparse(response.headers['location']))
    return response, response.headers['content-type']

def extract_tar_gz(file_obj: FileLike, cache_dir: Path) -> bool:
    """
    extract archive from file_obj to cache_dir
    """
    # ignore typing here because for our usage, file_obj just needs
    # to support read(), not the full _Fileobj tarfile defines
    archive = tarfile.open(fileobj=file_obj, mode='r:gz')  # type: ignore

    def skip_topmost_dir_filter(member, path):
        member = tarfile.data_filter(member, path)
        if not member:
            return member
        if member.isdir() and len(Path(member.name).parts) == 1:
            return None
        member.name = str(Path(*Path(member.name).parts[1:]))
        return member

    archive.extractall(path=cache_dir, filter=skip_topmost_dir_filter)
    archive.close()
    return True

SCHEME2DOWNLOAD = {
    'https': download_https,
}

MIMETYPE2EXTRACT = {
    'application/x-gzip': extract_tar_gz,
}

URLEXT2MIMETYPE = {
    '.tgz': 'application/x-gzip',
    '.gz': 'application/x-gzip',
}

def __main__():
    parser = argparse.ArgumentParser(description=__desc__)
    parser.add_argument(
        'paths', nargs='+', metavar='path',
        help='paths to be checked. paths need to contain a vendor-libs.json file, supports globs',
    )
    parser.add_argument('--no-error', action='store_true', help='do not exit with an errorlevel')
    args = parser.parse_args()

    result = check_paths(args.paths)

    return 0 if args.no_error else int(not result)

if __name__ == '__main__':
    sys.exit(__main__())
