import requests
import urllib3


def get_article_content(link: str) -> str:
    return requests.get(link).text


def get_main_page_content(page: int = 0) -> str:
    url = 'https://habr.com/ru/'
    if page != 0:
        url += f'page{page+1}/'
    return requests.get(url).text


def download_image(link: str) -> urllib3.HTTPResponse:
    response = requests.get(link, allow_redirects=True, stream=True)
    response.raise_for_status()
    response.raw.decode_content = True
    return response.raw
