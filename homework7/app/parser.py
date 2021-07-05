from typing import Callable, Iterator

import bs4

from .connection import get_article_content, get_main_page_content
from .data import PageContent


class MainPageParser:
    POSTS_LIST_SELECTOR = (
        'body > div.layout > div.layout__row.layout__row_body > div'
        ' > section > div.content_left.js-content_left > div.posts_list'
    )

    def __init__(self, html: str):
        self.soup_parser = bs4.BeautifulSoup(html, 'html.parser')  # pragma: nocover

    def _get_posts(self) -> bs4.element.ResultSet:
        posts = (
            self.soup_parser.select_one(self.POSTS_LIST_SELECTOR)
            .select_one('ul.content-list_posts')
            .select('li.content-list__item_post')
        )
        return posts

    def iter_articles(self) -> Iterator[str]:
        posts = self._get_posts()
        for post in posts:
            article = post.article
            if article is None:
                continue
            title_link = article.select_one('.post__title').a
            yield title_link.attrs['href']

    def __iter__(self) -> Iterator[str]:
        return self.iter_articles()  # pragma: nocover

    def get_articles(self) -> list[str]:
        return list(self.iter_articles())  # pragma: nocover


class ArticleParser:
    CONTENT_BODY_SELECTOR = '#post-content-body'
    TITLE_SELECTOR = '.post__title-text'

    def __init__(self, html: str):
        self.soup_parser = bs4.BeautifulSoup(html, 'html.parser')

    def get_page_content(self) -> PageContent:
        raw_content = self.soup_parser.select_one(self.CONTENT_BODY_SELECTOR)
        raw_content.select('img')
        img_urls = self._get_images_urls(raw_content.select('img'))
        text = raw_content.text
        return PageContent(
            title=self.soup_parser.select_one(self.TITLE_SELECTOR).text,
            text=text,
            images=img_urls,
        )

    def iter_page_content(self) -> Iterator[PageContent]:
        yield self.get_page_content()

    def __iter__(self) -> Iterator[PageContent]:
        return self.iter_page_content()

    @staticmethod
    def _get_images_urls(images: list[bs4.Tag]) -> tuple[str, ...]:
        func: Callable[[bs4.Tag], str] = lambda x: x.get('src')
        return tuple(map(func, images))


def get_articles_links(page_number: int) -> list[str]:
    parser = MainPageParser(get_main_page_content(page_number))
    return parser.get_articles()


def parse_article(link: str) -> PageContent:
    content = get_article_content(link)
    parser = ArticleParser(content)
    return parser.get_page_content()
