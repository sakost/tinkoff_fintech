import concurrent.futures
import os
import pathlib
import shutil
import tempfile
from io import BytesIO
from unittest import mock

import pytest

from app import exporter
from app.data import PageContent


@pytest.fixture(scope='module', autouse=True)
def temp_fs():
    old_dir = os.path.abspath(os.curdir)
    path = tempfile.mkdtemp()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_dir)
        shutil.rmtree(path)


def test_save_text():
    filename = pathlib.Path('filename.txt')
    exporter.save_text('some text', filename)
    assert filename.read_text() == 'some text'


@mock.patch('app.exporter.download_image')
def test_save_image(download_image_patch: mock.Mock):
    download_image_patch.return_value = BytesIO(b'some data')
    link = 'https://example.com/some_image.png?some_arg=1#something'
    exporter.save_image(link, pathlib.Path(os.curdir))
    assert os.path.exists('some_image.png')
    assert open('some_image.png', 'rb').read() == b'some data'


@pytest.mark.parametrize(
    'content',
    [
        PageContent(title='title1', text='some text1', images=()),
        PageContent(title='title2', text='some text2', images=('some image1',)),
        PageContent(
            title='title3', text='some text3', images=('some image1', 'some image 2')
        ),
    ],
)
@mock.patch('app.exporter.save_image')
@mock.patch('app.exporter.save_text')
def test_export_content(
    save_text_patch: mock.Mock,
    save_image_patch: mock.Mock,
    dummy_executor: concurrent.futures.Executor,
    content: PageContent,
):
    save_text_patch.return_value = None
    save_image_patch.return_value = None

    assert all(
        map(lambda x: x.done(), exporter.export_content(dummy_executor, content))
    )
    assert save_text_patch.call_args[0][0] == content.text
    assert save_text_patch.call_args[0][1].name == 'article.txt'
    if content.images:
        assert save_image_patch.call_args[0][0] == content.images[-1]
