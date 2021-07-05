from dataclasses import dataclass


@dataclass(frozen=True)
class PageContent:
    title: str
    text: str
    images: tuple[str, ...]
