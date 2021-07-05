import pytest
from requests_mock import Mocker

from app.connection import download_image, get_article_content, get_main_page_content


def test_get_article_content(requests_mock: Mocker):
    link = 'https://habr.ru/posts/1'
    data = '<html><head><title>test title</title></head><body>test body</body></html>'
    requests_mock.get(link, text=data)
    assert get_article_content(link) == data


@pytest.mark.parametrize(
    'link,content_file,page_num',
    [
        ['https://habr.com/ru/', 'tests/main_page1.html', 0],
        ['https://habr.com/ru/page2/', 'tests/main_page2.html', 1],
    ],
)
def test_get_main_page_content(
    link: str, content_file: str, page_num: int, requests_mock: Mocker
):
    with open(content_file, 'r') as file:
        text = file.read()
    requests_mock.get(link, text=text)
    assert get_main_page_content(page_num) == text


def test_download_image(requests_mock: Mocker):
    requests_mock.get('https://some_server.com/file.jpg', content=b'some string')
    assert download_image('https://some_server.com/file.jpg').read() == b'some string'
