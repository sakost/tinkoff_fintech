import concurrent.futures
import os
import os.path as osp
import pathlib
import shutil
import urllib.parse

from .connection import download_image
from .data import PageContent
from .utils import escape_path

OUTPUT_PATH = pathlib.Path('data/')
OUTPUT_TEXT_FILENAME = 'article.txt'


def save_text(post_text: str, output_file: pathlib.Path) -> None:
    with output_file.open('w') as file:
        file.write(post_text)


def save_image(link: str, output_folder: pathlib.Path) -> None:
    image_file = download_image(link)
    url = urllib.parse.urlparse(link)
    output_file = output_folder / osp.basename(url.path)
    with output_file.open('wb') as file:
        shutil.copyfileobj(image_file, file)


def export_content(
    executor: concurrent.futures.Executor, content: PageContent
) -> list[concurrent.futures.Future[None]]:
    content_folder = (OUTPUT_PATH / escape_path(content.title)).absolute()
    os.makedirs(content_folder, exist_ok=True)

    save_text_future = executor.submit(
        save_text, content.text, content_folder / OUTPUT_TEXT_FILENAME
    )
    save_image_futures = []
    for image in content.images:
        save_image_futures.append(executor.submit(save_image, image, content_folder))

    return [save_text_future] + save_image_futures
