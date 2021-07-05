# pylint: disable=W0621, E0239, R0913
import argparse
import pathlib
from io import StringIO
from typing import Union
from unittest import mock

import pytest

import myapp.app


@pytest.mark.parametrize(
    'args, path, substring',
    [
        (['.', 'world'], pathlib.Path().absolute(), 'world'),
        (
            ['not_existing_directory', 'word'],
            pathlib.Path().absolute() / 'not_existing_directory',
            'word',
        ),
        (
            [str(pathlib.Path('path').absolute()), 'world'],
            pathlib.Path('path').absolute(),
            'world',
        ),
    ],
)
def test_valid_argument_parsing(
    args: list[str], path: Union[pathlib.Path, str], substring: str
):
    path = pathlib.Path(path)

    parsed_args = myapp.app.parse_args(args)

    assert isinstance(parsed_args.path, pathlib.Path)
    assert parsed_args.path == path
    assert parsed_args.substring == substring


@pytest.mark.parametrize(
    'args',
    [
        ([],),
        (['.'],),
        (['12'],),
        (['--help'],),
        (['.', 'world', 'world'],),
    ],
)
def test_invalid_argument_parsing(args: list[str]):
    # suppress sys.exit calling
    with pytest.raises(SystemExit):
        myapp.app.parse_args(args)


def test_walk(path_factory_fixture, dir_factory_fixture, file_factory_fixture):
    path = path_factory_fixture.get()
    path.is_file.return_value = False
    path.is_dir.return_value = False

    dir1 = dir_factory_fixture.get()
    dir2 = dir_factory_fixture.get()
    dir3 = dir_factory_fixture.get()

    file1 = file_factory_fixture.get()
    file2 = file_factory_fixture.get()
    file3 = file_factory_fixture.get()
    file4 = file_factory_fixture.get()
    file5 = file_factory_fixture.get()
    file6 = file_factory_fixture.get()

    # directories content
    dir3.iterdir.return_value = [file6]
    dir2.iterdir.return_value = [file4, dir3]
    dir1.iterdir.return_value = [file1, file2, file3, dir2, file5, path]

    assert list(myapp.app.file_walk(dir1)) == [
        file1,
        file2,
        file3,
        file4,
        file6,
        file5,
    ]  # normal use
    assert list(myapp.app.file_walk(path)) == []  # skip if path is symlink or similar
    assert list(myapp.app.file_walk(file1)) == [file1]  # iterate over just one file


def test_find_occurrences(file_factory_fixture):
    buffer = StringIO('string\n')

    path = file_factory_fixture.get(path='/file')

    assert list(myapp.app.find_occurrences(path, buffer, 'str')) == [
        myapp.app.Occurrence(1, 'string', path),
    ]
    buffer.seek(0)
    assert list(myapp.app.find_occurrences(path, buffer, 'car')) == []


@mock.patch('pathlib.Path', spec=pathlib.Path)
def test_get_relative_path_view(pathlib_mock, file_factory_fixture):
    relative_path = file_factory_fixture.get(path='dir/file')
    pathlib_mock.return_value = pathlib_mock

    output = myapp.app.get_relative_path_view(relative_path)

    relative_path.relative_to.assert_called_once()
    pathlib_mock.assert_called_once()
    pathlib_mock.absolute.assert_called_once()
    assert output == 'dir/file'


def test_format_occurrence(occurrence_fixture):
    assert (
        myapp.app.format_occurrence(occurrence_fixture)
        == 'venv/path/file line=1: string'
    )


def test_print_occurrence(capsys, occurrence_fixture):
    myapp.app.print_occurrence(occurrence_fixture)
    captured = capsys.readouterr()
    assert captured.out == 'venv/path/file line=1: string\n'


@mock.patch('pathlib.Path', spec=pathlib.Path)
def test_file_does_not_exists_handler(pathlib_mock, capsys, file_factory_fixture):
    with pytest.raises(SystemExit):
        myapp.app.file_does_not_exists_handler(
            file_factory_fixture.get(path='venv/path/file')
        )

    captured = capsys.readouterr()

    assert captured.out == 'venv/path/file: file does not exists\n'
    pathlib_mock.assert_called_once()


@mock.patch('myapp.app.file_walk')
@mock.patch('myapp.app.find_occurrences')
@mock.patch('myapp.app.print_occurrence')
def test_run(
    print_occurrence_mock,
    find_occurrences_mock,
    file_walk_mock,
    occurrence_fixture,
    file_factory_fixture,
):
    file_path_mock = file_factory_fixture.get(path='string')
    parsed_args = argparse.Namespace(substring='venv/path', path=file_path_mock)

    find_occurrences_mock.return_value = [occurrence_fixture]
    file_walk_mock.return_value = [
        file_factory_fixture.get(
            path='venv/path/file1', content='string\nsssubbbstring\n\nsubstring'
        ),
        file_factory_fixture.get(path='venv/path/file2', content='\nsssubbbstring'),
    ]

    myapp.app.run(parsed_args)

    file_walk_mock.assert_called_once_with(file_path_mock)

    print_occurrence_mock.assert_called_with(occurrence_fixture)
