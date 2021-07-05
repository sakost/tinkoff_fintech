#!/usr/bin/env python
import argparse
import contextlib
import pathlib
import sys
from typing import NamedTuple, Optional, TextIO

# file buffer size
CHUNK_SIZE = 1024 * 1024 * 10  # 10 MiB


class Occurrence(NamedTuple):
    """
    this class represents substring occurrence in text
    """

    line_num: int
    text: str
    file_path: pathlib.Path


def parse_args(args: Optional[list[str]] = None) -> argparse.Namespace:
    """

    :param args: command line arguments
    :type args: `list[str]`
    :return: parsed arguments
    :rtype: `argparse.Namespace`
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'path',
        type=lambda x: pathlib.Path(x).absolute(),  # to avoid relative mispathing
        help='path where to search substring occurrence',
    )

    parser.add_argument(
        'substring',
        type=str,
        help='string to search',
    )

    return parser.parse_args(args)


def file_walk(search_path: pathlib.Path):
    """
    walking through `path` recursively and yielding only files
    :type search_path: `pathlib.Path`
    """
    if not search_path.is_dir():
        if search_path.is_file():
            yield search_path
        # if symlink or something similar
        return
    for file in search_path.iterdir():
        yield from file_walk(file)


def find_occurrences(file_path: pathlib.Path, file: TextIO, substring: str):
    """
    yielding occurrence of `substring` in `file` with external information
    :param file_path: for external information(path relative to current dir)
    :type file_path: `pathlib.Path`
    :param file: file where to search occurrences
    :type file: TextIO
    :type substring: str
    """
    for num, line in enumerate(file, start=1):
        if substring in line:
            line = line.strip()
            yield Occurrence(num, line, file_path)


def get_relative_path_view(file_path: pathlib.Path) -> str:
    """
    make relative path from current path to `file_path`
    :param file_path: absolute file path
    :type file_path: pathlib.Path
    :return: string that represents relative path to `file_path`
    :rtype: str
    """
    current_path = pathlib.Path().absolute()
    relative_path = file_path.relative_to(current_path)
    return str(relative_path)


def format_occurrence(occurrence: Occurrence) -> str:
    """
    :param occurrence: occurrence to format
    :type occurrence: Occurrence
    :return: formatted occurrence
    :rtype: str
    """
    return (
        f'{get_relative_path_view(occurrence.file_path)} '
        f'line={occurrence.line_num}: {occurrence.text}'
    )


def print_occurrence(occurrence: Occurrence):
    """
    prints the given occurrence to stdout
    :type occurrence: Occurrence
    """
    print(format_occurrence(occurrence))


def file_does_not_exists_handler(search_path: pathlib.Path):
    """
    :param search_path: path that not exists
    :type search_path: pathlib.Path
    :raises SystemExit
    """
    print(f'{get_relative_path_view(search_path)}: file does not exists')
    sys.exit(1)


def run(parsed_args: argparse.Namespace):
    if not parsed_args.path.exists():
        file_does_not_exists_handler(parsed_args.path)
    for file in file_walk(parsed_args.path):
        with contextlib.suppress(UnicodeDecodeError), file.open('r', CHUNK_SIZE) as f:
            for occurrence in find_occurrences(file, f, parsed_args.substring):
                print_occurrence(occurrence)


def main():
    run(parse_args(sys.argv[1:]))


if __name__ == '__main__':
    main()
