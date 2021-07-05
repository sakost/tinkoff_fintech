# pylint: disable=W0621
import pathlib
from io import StringIO
from typing import Optional, Union
from unittest import mock

import pytest

import myapp.app


class PathFactory:
    def get(self, path: Optional[Union[str, pathlib.Path]] = None):
        magic_mock = mock.MagicMock(spec=pathlib.Path)
        magic_mock.absolute.return_value = magic_mock
        magic_mock.exists.return_value = True
        if path is not None:
            magic_mock.relative_to.return_value = path
        return magic_mock


class FileFactory:
    def __init__(self, path_factory: PathFactory):
        self._path_factory = path_factory

    def get(
        self,
        path: Optional[Union[str, pathlib.Path]] = None,
        content: Optional[str] = None,
    ):
        file = self._path_factory.get(path)
        file.is_dir.return_value = False
        file.is_file.return_value = True

        if content is not None:
            file.open.return_value = StringIO(content)

        return file


class DirFactory:
    def __init__(self, path_factory: PathFactory):
        self._path_factory = path_factory

    def get(self, path: Optional[Union[str, pathlib.Path]] = None):
        directory = self._path_factory.get(path)
        directory.is_dir.return_value = True
        directory.is_file.return_value = False
        directory.iterdir.return_value = []

        return directory


@pytest.fixture()
def path_factory_fixture():
    return PathFactory()


@pytest.fixture()
def file_factory_fixture(path_factory_fixture):
    return FileFactory(path_factory_fixture)


@pytest.fixture()
def dir_factory_fixture(path_factory_fixture):
    return DirFactory(path_factory_fixture)


@pytest.fixture()
def occurrence_fixture(file_factory_fixture):
    relative_path = file_factory_fixture.get(path='venv/path/file')
    occurrence = myapp.app.Occurrence(1, 'string', relative_path)
    return occurrence
