# pylint: disable=redefined-outer-name
from unittest import mock

import pytest

from app import parser


@pytest.fixture(scope='module')
def main_page_html() -> str:
    with open('tests/main_page1.html', 'r') as f:
        return f.read()


@pytest.fixture(scope='module')
def article_page_html() -> str:
    with open('tests/post1.html', 'r') as f:
        return f.read()


@pytest.fixture(scope='module')
def article_page_text() -> str:
    with open('tests/post1.txt', 'r') as f:
        return f.read()


class TestMainPageParser:
    def test_get_articles(self, main_page_html: str):
        assert parser.MainPageParser(main_page_html).get_articles() == [
            'https://habr.com/ru/post/554762/',
            'https://habr.com/ru/post/554760/',
            'https://habr.com/ru/post/554740/',
            'https://habr.com/ru/post/554758/',
            'https://habr.com/ru/post/554754/',
            'https://habr.com/ru/post/553470/',
            'https://habr.com/ru/company/itelma/blog/554746/',
            'https://habr.com/ru/company/wd/blog/554722/',
            'https://habr.com/ru/company/audiomania/blog/554556/',
            'https://habr.com/ru/company/lightmap/blog/554594/',
            'https://habr.com/ru/post/554724/',
            'https://habr.com/ru/company/itglobalcom/blog/554506/',
            'https://habr.com/ru/company/ruvds/blog/554286/',
            'https://habr.com/ru/company/digitalrightscenter/blog/554718/',
            'https://habr.com/ru/post/554686/',
            'https://habr.com/ru/post/554710/',
            'https://habr.com/ru/company/englishdom/blog/553812/',
            'https://habr.com/ru/company/unidata/blog/554716/',
            'https://habr.com/ru/post/553280/',
            'https://habr.com/ru/post/554714/',
        ]


class TestArticleParser:
    def test_get_page_content(self, article_page_text: str, article_page_html: str):
        content = parser.ArticleParser(article_page_html).get_page_content()
        title = 'Создаём компанию мечты: управление качеством данных'
        images = (
            'https://habrastorage.org/webt/lr/se/--/lrse--et28atrk8ffvepbgqvgy8.jpeg',
            'https://habrastorage.org/webt/mh/5z/ca/mh5zcankap_itac2bh2clptuiy4.jpeg',
            'https://habrastorage.org/webt/1c/yz/sn/1cyzsnuarsbpw9k6qepythkcwzq.jpeg',
            'https://habrastorage.org/webt/em/h5/g4/emh5g4uootfqirhhyfwz9kagqxi.jpeg',
            'https://habrastorage.org/webt/jd/fl/ny/jdflnyvvm2hpmv-hyv6rrodw9pi.jpeg',
            'https://habrastorage.org/webt/nx/tv/jm/nxtvjmfbrwqq5sggkrtsby2yurq.jpeg',
        )
        assert content.text == article_page_text
        assert content.title == title
        assert content.images == images


def test_get_articles_links(main_page_html: str) -> None:
    with mock.patch('app.parser.get_main_page_content') as patched:
        patched.return_value = main_page_html
        parser.get_articles_links(1)
        assert patched.call_count == 1


def test_parse_article(article_page_html: str) -> None:
    with mock.patch('app.parser.get_article_content') as patched:
        patched.return_value = article_page_html
        parser.parse_article('some link')
        assert patched.call_count == 1
